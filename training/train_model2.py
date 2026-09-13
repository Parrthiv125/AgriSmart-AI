"""
AgriSmart AI — Model 2 Field-Domain Adaptation Training Script
===============================================================
Trains Model 2 (efficientnet_b2) for field-domain adaptation using:
  - Combined Train: PlantVillage Train + 80% PlantDoc Train (data/processed_model2/train)
  - Combined Val:   PlantVillage Val + 20% PlantDoc Val (data/processed_model2/val)
  - PyTorch WeightedRandomSampler for configurable PlantDoc oversampling weight
  - Field-oriented augmentations (flips, rotations, color jitter, affine)
  - Starting weights loaded from Model 1 (models/agrismart_best.pth)

Guarantees & Guardrails:
  - NEVER modifies or overwrites models/agrismart_best.pth.
  - NEVER touches or evaluates data/plantdoc/test (233 locked test images).
  - Output checkpoint: models/agrismart_field_adapted_best.pth.
  - Logs metrics to experiments_model2.csv and models/agrismart_field_adapted_metadata.json.

Usage:
    python training/train_model2.py --dry-run
    python training/train_model2.py --epochs 25 --plantdoc-oversample-factor 5.0
"""

import sys
import json
import csv
import time
import argparse
import random
from pathlib import Path
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
from torch.amp import GradScaler, autocast
from torchvision import datasets, transforms
from PIL import Image
from tqdm import tqdm
import timm
from sklearn.metrics import f1_score, accuracy_score

# Safe UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Default Paths
MODEL1_CKPT_PATH = ROOT_DIR / "models" / "agrismart_best.pth"
CLASSES_JSON = ROOT_DIR / "models" / "classes.json"
MODEL2_TRAIN_DIR = ROOT_DIR / "data" / "processed_model2" / "train"
MODEL2_VAL_DIR = ROOT_DIR / "data" / "processed_model2" / "val"
MODEL2_CKPT_OUT = ROOT_DIR / "models" / "agrismart_field_adapted_best.pth"
MODEL2_LAST_OUT = ROOT_DIR / "models" / "agrismart_field_adapted_last.pth"
MODEL2_METADATA_OUT = ROOT_DIR / "models" / "agrismart_field_adapted_metadata.json"
MODEL2_EXP_LOG = ROOT_DIR / "experiments_model2.csv"
PLANTDOC_TEST_DIR = ROOT_DIR / "data" / "plantdoc" / "test"

# Config constants
IMAGE_SIZE = 260
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]
SEED = 42


def set_seed(seed: int = SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_field_transforms():
    """Field-oriented data augmentations for Model 2 training."""
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.2),
        transforms.RandomRotation(degrees=20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])

    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])

    return train_transform, val_transform


def build_sampler(dataset: datasets.ImageFolder, plantdoc_oversample_factor: float = 5.0):
    """
    Constructs WeightedRandomSampler weighting PlantDoc samples by plantdoc_oversample_factor.
    PlantDoc samples are identified by filename starting with 'pd_'.
    """
    weights = []
    pd_count = 0
    pv_count = 0

    for path, _ in dataset.samples:
        filename = Path(path).name
        if filename.startswith("pd_"):
            weights.append(plantdoc_oversample_factor)
            pd_count += 1
        else:
            weights.append(1.0)
            pv_count += 1

    weights_tensor = torch.tensor(weights, dtype=torch.double)
    generator = torch.Generator().manual_seed(SEED)

    sampler = WeightedRandomSampler(
        weights=weights_tensor,
        num_samples=len(weights),
        replacement=True,
        generator=generator,
    )

    print(f"[OK] WeightedRandomSampler built: {pv_count} PV samples (w=1.0) | {pd_count} PD samples (w={plantdoc_oversample_factor})")
    return sampler, pv_count, pd_count


def load_model1_weights(checkpoint_path: Path, num_classes: int, device: torch.device):
    """Load EfficientNet-B2 initialized with Model 1 (models/agrismart_best.pth) state_dict."""
    if not checkpoint_path.exists():
        print(f"[WARN] Model 1 checkpoint not found at {checkpoint_path}. Fallback to pretrained ImageNet.")
        model = timm.create_model("efficientnet_b2", pretrained=True, num_classes=num_classes)
        return model, "imagenet_pretrained"

    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model_name = ckpt.get("model_name", "efficientnet_b2")
    model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
    model.load_state_dict(ckpt["state_dict"])
    model.to(device)

    val_f1_save = ckpt.get("val_macro_f1", 0.0)
    print(f"[OK] Model 1 weights loaded cleanly from {checkpoint_path.name}")
    print(f"     Base Architecture: {model_name} | Best Epoch: {ckpt.get('epoch')} | Base Val F1: {val_f1_save:.4f}")
    return model, str(checkpoint_path)


def train_one_epoch(model, loader, criterion, optimizer, scaler, device, epoch, is_dry_run=False):
    model.train()
    total_loss = 0.0
    all_preds, all_labels = [], []

    pbar = tqdm(loader, desc=f"Epoch {epoch+1} [Train]", leave=False)
    for batch_idx, (images, labels) in enumerate(pbar):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        with autocast(device_type="cuda" if images.is_cuda else "cpu", enabled=True):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        total_loss += loss.item()
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

        if is_dry_run and batch_idx >= 1:
            break

    avg_loss = total_loss / (batch_idx + 1)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    accuracy = accuracy_score(all_labels, all_preds)
    return avg_loss, macro_f1, accuracy


@torch.no_grad()
def validate(model, loader, criterion, device, is_dry_run=False):
    model.eval()
    total_loss = 0.0
    all_preds, all_labels = [], []

    for batch_idx, (images, labels) in enumerate(tqdm(loader, desc="[Val]", leave=False)):
        images, labels = images.to(device), labels.to(device)
        with autocast(device_type="cuda" if images.is_cuda else "cpu", enabled=True):
            outputs = model(images)
            loss = criterion(outputs, labels)

        total_loss += loss.item()
        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())

        if is_dry_run and batch_idx >= 1:
            break

    avg_loss = total_loss / (batch_idx + 1)
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    accuracy = accuracy_score(all_labels, all_preds)
    return avg_loss, macro_f1, accuracy


def log_experiment_model2(row: dict):
    path = MODEL2_EXP_LOG
    file_exists = path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def run_training_model2(
    model1_path: Path = MODEL1_CKPT_PATH,
    model2_out_path: Path = MODEL2_CKPT_OUT,
    epochs: int = 25,
    batch_size: int = 32,
    lr: float = 1e-4,
    weight_decay: float = 1e-4,
    plantdoc_oversample_factor: float = 5.0,
    is_dry_run: bool = False,
):
    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 70)
    print(" AGRISMART AI — MODEL 2 FIELD-DOMAIN ADAPTATION TRAINING")
    print("=" * 70)
    print(f"  Device:                      {device}")
    print(f"  Base Model 1 Checkpoint:     {model1_path}")
    print(f"  Output Model 2 Checkpoint:   {model2_out_path}")
    print(f"  PlantDoc Oversample Factor:  {plantdoc_oversample_factor}")
    print(f"  Epochs:                      {'1 (DRY RUN)' if is_dry_run else epochs}")
    print(f"  Batch Size:                  {batch_size}")
    print(f"  Learning Rate:               {lr}")
    print(f"  LOCKED PlantDoc Test Dir:    {PLANTDOC_TEST_DIR} (UNTOUCHED)")
    print()

    # Verify input paths
    if not MODEL2_TRAIN_DIR.exists() or not MODEL2_VAL_DIR.exists():
        print("[ERROR] Model 2 processed datasets missing. Run: python data/prepare_model2_dataset.py first.")
        sys.exit(1)

    # Load 28 classes
    with open(CLASSES_JSON, "r", encoding="utf-8") as f:
        classes_dict = json.load(f)
    class_names = [classes_dict[str(i)] for i in range(len(classes_dict))]
    num_classes = len(class_names)

    # Transforms & Datasets
    train_transform, val_transform = get_field_transforms()
    train_dataset = datasets.ImageFolder(MODEL2_TRAIN_DIR, transform=train_transform)
    val_dataset = datasets.ImageFolder(MODEL2_VAL_DIR, transform=val_transform)

    # Build Sampler
    sampler, pv_train_count, pd_train_count = build_sampler(train_dataset, plantdoc_oversample_factor)

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, sampler=sampler, num_workers=0, pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True
    )

    print(f"[OK] DataLoaders built: Train={len(train_dataset)} | Val={len(val_dataset)} | Classes={num_classes}")

    # Load Model 1 weights or resume from Model 2 last checkpoint
    start_epoch = 0
    best_val_f1 = 0.0
    best_epoch = 0

    criterion = nn.CrossEntropyLoss()

    if MODEL2_LAST_OUT.exists() and not is_dry_run:
        print(f"[RESUME] Found existing last checkpoint at {MODEL2_LAST_OUT.name}")
        ckpt_last = torch.load(MODEL2_LAST_OUT, map_location=device, weights_only=False)
        model = timm.create_model("efficientnet_b2", pretrained=False, num_classes=num_classes)
        model.load_state_dict(ckpt_last["state_dict"])
        model.to(device)
        start_epoch = ckpt_last.get("epoch", 0)
        best_val_f1 = ckpt_last.get("best_val_f1", 0.0)
        best_epoch = ckpt_last.get("best_epoch", 0)
        base_ckpt_desc = f"Resumed from {MODEL2_LAST_OUT.name} (epoch {start_epoch})"

        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, last_epoch=start_epoch - 1 if start_epoch > 0 else -1)
        scaler = GradScaler("cuda" if torch.cuda.is_available() else "cpu", enabled=True)

        if "optimizer_state" in ckpt_last:
            optimizer.load_state_dict(ckpt_last["optimizer_state"])
        if "scheduler_state" in ckpt_last:
            scheduler.load_state_dict(ckpt_last["scheduler_state"])
        print(f"[OK] Successfully resumed from epoch {start_epoch}. Continuing to epoch {epochs}...")
    else:
        model, base_ckpt_desc = load_model1_weights(model1_path, num_classes, device)
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        scaler = GradScaler("cuda" if torch.cuda.is_available() else "cpu", enabled=True)

    experiment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    num_epochs_to_run = 1 if is_dry_run else epochs

    if start_epoch >= num_epochs_to_run and not is_dry_run:
        print(f"[OK] Training already complete ({start_epoch}/{num_epochs_to_run} epochs). Skipping training.")
    else:
        print(f"\n[RUN] Training Model 2 from epoch {start_epoch + 1} to {num_epochs_to_run}...")
        for epoch in range(start_epoch, num_epochs_to_run):
            t0 = time.time()
            train_loss, train_f1, train_acc = train_one_epoch(
                model, train_loader, criterion, optimizer, scaler, device, epoch, is_dry_run
            )
            val_loss, val_f1, val_acc = validate(
                model, val_loader, criterion, device, is_dry_run
            )
            elapsed = time.time() - t0

            scheduler.step()
            current_lr = optimizer.param_groups[0]["lr"]

            print(
                f"Epoch {epoch+1:03d}/{num_epochs_to_run} | "
                f"Train Loss: {train_loss:.4f} F1: {train_f1:.4f} Acc: {train_acc:.4f} | "
                f"Val Loss: {val_loss:.4f} F1: {val_f1:.4f} Acc: {val_acc:.4f} | "
                f"LR: {current_lr:.2e} | {elapsed:.1f}s"
            )

            # Save best model
            if val_f1 > best_val_f1 or is_dry_run:
                best_val_f1 = val_f1
                best_epoch = epoch + 1
                torch.save({
                    "epoch": best_epoch,
                    "model_name": "efficientnet_b2",
                    "num_classes": num_classes,
                    "class_names": class_names,
                    "image_size": IMAGE_SIZE,
                    "state_dict": model.state_dict(),
                    "optimizer_state": optimizer.state_dict(),
                    "val_macro_f1": val_f1,
                    "val_accuracy": val_acc,
                    "base_checkpoint": base_ckpt_desc,
                    "plantdoc_oversample_factor": plantdoc_oversample_factor,
                }, model2_out_path)
                print(f"   [OK] Model 2 best checkpoint saved -> {model2_out_path.name}")

            # Save last checkpoint for resume support
            torch.save({
                "epoch": epoch + 1,
                "state_dict": model.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "scheduler_state": scheduler.state_dict(),
                "best_val_f1": best_val_f1,
                "best_epoch": best_epoch,
            }, MODEL2_LAST_OUT)

        # Log
        log_experiment_model2({
            "experiment_id": experiment_id,
            "epoch": epoch + 1,
            "model": "efficientnet_b2",
            "plantdoc_oversample_factor": plantdoc_oversample_factor,
            "train_loss": round(train_loss, 4),
            "train_f1": round(train_f1, 4),
            "train_acc": round(train_acc, 4),
            "val_loss": round(val_loss, 4),
            "val_f1": round(val_f1, 4),
            "val_acc": round(val_acc, 4),
            "best_val_f1": round(best_val_f1, 4),
            "is_dry_run": is_dry_run,
        })

    # Save metadata payload
    metadata_payload = {
        "model_label": "AgriSmart AI Model 2 -- Field-Domain Adaptation",
        "timestamp": datetime.now().isoformat(),
        "architecture": "efficientnet_b2",
        "image_size": IMAGE_SIZE,
        "num_classes": num_classes,
        "class_names": class_names,
        "base_checkpoint": str(model1_path.relative_to(ROOT_DIR)),
        "output_checkpoint": str(model2_out_path.relative_to(ROOT_DIR)),
        "hyperparameters": {
            "optimizer": "AdamW",
            "scheduler": "CosineAnnealingLR",
            "learning_rate": lr,
            "weight_decay": weight_decay,
            "batch_size": batch_size,
            "epochs": epochs,
            "seed": SEED,
            "amp_enabled": True,
        },
        "sampling_strategy": {
            "method": "WeightedRandomSampler",
            "plantdoc_oversample_factor": plantdoc_oversample_factor,
            "plantvillage_weight": 1.0,
            "pv_train_samples": pv_train_count,
            "pd_train_samples": pd_train_count,
        },
        "dataset_split": {
            "train_total": len(train_dataset),
            "val_total": len(val_dataset),
            "locked_plantdoc_test": 233,
        },
        "training_results": {
            "best_epoch": best_epoch,
            "best_val_macro_f1": float(best_val_f1),
            "is_dry_run": is_dry_run,
        },
        "guardrail_status": {
            "model1_unmodified": True,
            "plantdoc_test_untouched": True,
            "plantdoc_test_evaluated": False,
        },
    }

    with open(MODEL2_METADATA_OUT, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)
    print(f"\n[OK] Model 2 metadata saved -> {MODEL2_METADATA_OUT}")

    print("=" * 70)
    print(" MODEL 2 PIPELINE VERIFICATION / TRAINING SUMMARY")
    print("=" * 70)
    print(f"  Status:               {'DRY-RUN PASSED' if is_dry_run else 'TRAINING COMPLETE'}")
    print(f"  Best Val Macro-F1:    {best_val_f1:.4f}")
    print(f"  Best Epoch:           {best_epoch}")
    print(f"  Model 2 Checkpoint:   {model2_out_path}")
    print(f"  Model 1 Checkpoint:   {model1_path} (UNTOUCHED)")
    print(f"  PlantDoc Test Set:    {PLANTDOC_TEST_DIR} (LOCKED & UNTOUCHED)")
    print("=" * 70)

    return metadata_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgriSmart AI Model 2 Field Adaptation Training")
    parser.add_argument("--dry-run", action="store_true", help="Run 1 epoch / fast sanity check")
    parser.add_argument("--plantdoc-oversample-factor", type=float, default=5.0, help="PlantDoc sample weight factor")
    parser.add_argument("--epochs", type=int, default=25, help="Total training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    args = parser.parse_args()

    run_training_model2(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        plantdoc_oversample_factor=args.plantdoc_oversample_factor,
        is_dry_run=args.dry_run,
    )
