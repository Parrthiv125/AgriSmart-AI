"""
AgriSmart AI — Training Script
================================
Full training pipeline:
  1. Load dataset (train/val)
  2. Build EfficientNet-B2 model (or configured backbone)
  3. Train with AMP, early stopping, Macro-F1 monitoring
  4. Log each epoch to experiments.csv
  5. Save best model by validation Macro-F1

Usage:
    python training/train.py

Or from project root:
    python -m training.train
"""

import sys
import json
import csv
import time
import random
import warnings
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import GradScaler, autocast
from tqdm import tqdm
import timm
from sklearn.metrics import f1_score, accuracy_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import (
    MODEL_NAME, PRETRAINED, IMAGE_SIZE, SEED,
    NUM_EPOCHS, LEARNING_RATE, WEIGHT_DECAY, WARMUP_EPOCHS,
    LR_SCHEDULER, EARLY_STOPPING_PATIENCE, OPTIMIZER, MOMENTUM,
    USE_AMP, BATCH_SIZE, BEST_MODEL_PATH, LAST_MODEL_PATH,
    EXPERIMENT_LOG, CLASSES, CLASSES_JSON, MODELS_DIR, LOG_EVERY_N_BATCHES,
)
from training.dataset import get_dataloaders, save_class_mapping, compute_class_weights


# ── Reproducibility ───────────────────────────────────────────────────────────

def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ── Model ─────────────────────────────────────────────────────────────────────

def build_model(num_classes: int, model_name: str = MODEL_NAME) -> nn.Module:
    """Build a pretrained backbone with a custom classification head."""
    model = timm.create_model(
        model_name,
        pretrained=PRETRAINED,
        num_classes=num_classes,
    )
    print(f"✅ Model: {model_name} | Classes: {num_classes} | Pretrained: {PRETRAINED}")
    return model


# ── Optimiser & Scheduler ─────────────────────────────────────────────────────

def build_optimizer(model: nn.Module) -> optim.Optimizer:
    if OPTIMIZER == "adamw":
        return optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY)
    elif OPTIMIZER == "sgd":
        return optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=MOMENTUM,
                         weight_decay=WEIGHT_DECAY, nesterov=True)
    else:
        raise ValueError(f"Unknown optimizer: {OPTIMIZER}")


def build_scheduler(optimizer: optim.Optimizer, num_epochs: int):
    if LR_SCHEDULER == "cosine":
        return optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    elif LR_SCHEDULER == "step":
        return optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)
    elif LR_SCHEDULER == "plateau":
        return optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=3, factor=0.5)
    else:
        raise ValueError(f"Unknown scheduler: {LR_SCHEDULER}")


# ── Training Loop ─────────────────────────────────────────────────────────────

def train_one_epoch(model, loader, criterion, optimizer, scaler, device, epoch):
    model.train()
    total_loss = 0.0
    all_preds, all_labels = [], []

    pbar = tqdm(loader, desc=f"Epoch {epoch+1} [Train]", leave=False)
    for batch_idx, (images, labels) in enumerate(pbar):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        with autocast(device_type="cuda" if images.is_cuda else "cpu", enabled=USE_AMP):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

        if batch_idx % LOG_EVERY_N_BATCHES == 0:
            pbar.set_postfix(loss=f"{loss.item():.4f}")

    avg_loss = total_loss / len(loader)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    accuracy = accuracy_score(all_labels, all_preds)
    return avg_loss, macro_f1, accuracy


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    all_preds, all_labels = [], []

    for images, labels in tqdm(loader, desc="[Val]", leave=False):
        images, labels = images.to(device), labels.to(device)
        with autocast(device_type="cuda" if images.is_cuda else "cpu", enabled=USE_AMP):
            outputs = model(images)
            loss = criterion(outputs, labels)

        total_loss += loss.item()
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

    avg_loss = total_loss / len(loader)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    accuracy = accuracy_score(all_labels, all_preds)
    return avg_loss, macro_f1, accuracy


# ── Experiment Logging ────────────────────────────────────────────────────────

def log_experiment(row: dict):
    """Append one experiment row to experiments.csv."""
    path = EXPERIMENT_LOG
    file_exists = path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ── Main Training Function ────────────────────────────────────────────────────

def train():
    set_seed()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🖥️  Device: {device}")

    # ── Data ──────────────────────────────────────────────────────────────────
    print("📂 Loading datasets...")
    train_loader, val_loader, test_loader, class_names = get_dataloaders(classes=CLASSES)
    num_classes = len(class_names)
    print(f"   Classes: {num_classes}  |  Train: {len(train_loader.dataset)}  |  Val: {len(val_loader.dataset)}")

    # Save class mapping
    save_class_mapping(class_names)

    # ── Model ─────────────────────────────────────────────────────────────────
    model = build_model(num_classes).to(device)

    # ── Loss ──────────────────────────────────────────────────────────────────
    class_weights = compute_class_weights(train_loader.dataset).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # ── Optimizer & Scheduler ──────────────────────────────────────────────────
    optimizer = build_optimizer(model)
    scheduler = build_scheduler(optimizer, NUM_EPOCHS)
    device_type = "cuda" if torch.cuda.is_available() else "cpu"
    scaler = GradScaler(device_type, enabled=USE_AMP)

    # ── Training Loop ──────────────────────────────────────────────────────────
    best_val_f1 = 0.0
    epochs_no_improve = 0
    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\n🚀 Starting training | Model: {MODEL_NAME} | Epochs: {NUM_EPOCHS}")
    print("=" * 60)

    for epoch in range(NUM_EPOCHS):
        # Warmup: freeze backbone for first WARMUP_EPOCHS, then unfreeze
        if epoch == 0:
            print("🔒 Warming up (head only)...")
            for name, param in model.named_parameters():
                if "classifier" not in name and "head" not in name and "fc" not in name:
                    param.requires_grad = False
        elif epoch == WARMUP_EPOCHS:
            print("🔓 Unfreezing all layers...")
            for param in model.parameters():
                param.requires_grad = True

        t0 = time.time()
        train_loss, train_f1, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, scaler, device, epoch
        )
        val_loss, val_f1, val_acc = validate(model, val_loader, criterion, device)
        elapsed = time.time() - t0

        # Scheduler step
        if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(val_f1)
        else:
            scheduler.step()

        current_lr = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch {epoch+1:03d}/{NUM_EPOCHS} | "
            f"Train Loss: {train_loss:.4f}  F1: {train_f1:.4f}  Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f}  F1: {val_f1:.4f}  Acc: {val_acc:.4f} | "
            f"LR: {current_lr:.2e} | {elapsed:.1f}s"
        )

        # ── Save best model ──
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            epochs_no_improve = 0
            torch.save({
                "epoch": epoch + 1,
                "model_name": MODEL_NAME,
                "num_classes": num_classes,
                "class_names": class_names,
                "image_size": IMAGE_SIZE,
                "state_dict": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "val_macro_f1": val_f1,
                "val_accuracy": val_acc,
            }, BEST_MODEL_PATH)
            print(f"   ✅ Best model saved (Val Macro-F1: {best_val_f1:.4f})")
        else:
            epochs_no_improve += 1

        # ── Save last checkpoint ──
        torch.save({
            "epoch": epoch + 1,
            "state_dict": model.state_dict(),
        }, LAST_MODEL_PATH)

        # ── Log experiment ──
        log_experiment({
            "experiment_id": experiment_id,
            "epoch": epoch + 1,
            "model": MODEL_NAME,
            "image_size": IMAGE_SIZE,
            "batch_size": BATCH_SIZE,
            "lr": current_lr,
            "train_loss": round(train_loss, 4),
            "train_f1": round(train_f1, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_f1": round(val_f1, 4),
            "val_acc": round(val_acc, 4),
            "best_val_f1": round(best_val_f1, 4),
        })

        # ── Early stopping ──
        if epochs_no_improve >= EARLY_STOPPING_PATIENCE:
            print(f"\n⏹️  Early stopping after {EARLY_STOPPING_PATIENCE} epochs without improvement.")
            break

    print(f"\n🏆 Training complete. Best Val Macro-F1: {best_val_f1:.4f}")
    print(f"   Model saved: {BEST_MODEL_PATH}")
    return best_val_f1


if __name__ == "__main__":
    train()
