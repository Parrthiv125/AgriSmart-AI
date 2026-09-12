"""
AgriSmart AI — Smoke Test
==========================
Runs 2 train batches + 1 val batch through the full pipeline:
  - DataLoaders load correctly
  - Forward pass works
  - Loss computes
  - Backward pass works
  - Checkpoint saving works

Usage:
    python training/smoke_test.py
"""

import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.amp import GradScaler, autocast
from sklearn.metrics import f1_score

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import (
    MODEL_NAME, PRETRAINED, IMAGE_SIZE, SEED, CLASSES,
    USE_AMP, BEST_MODEL_PATH, MODELS_DIR,
)
from training.dataset import get_dataloaders, save_class_mapping, compute_class_weights
from training.train import build_model, build_optimizer, build_scheduler, set_seed

SMOKE_BATCHES = 2   # number of batches to run
SMOKE_BATCH_SIZE = 8  # small batch to avoid heavy memory usage


def smoke_test():
    print("AgriSmart AI -- Smoke Test")
    print("=" * 50)

    set_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # -- Data
    print("\n[DATA] Loading DataLoaders (small batch)...")
    train_loader, val_loader, _, class_names = get_dataloaders(
        classes=CLASSES,
        batch_size=SMOKE_BATCH_SIZE,
    )
    num_classes = len(class_names)
    print(f"   Classes: {num_classes}")
    print(f"   First 5 classes: {class_names[:5]}")

    # -- Model
    print("\n[MODEL] Building model...")
    model = build_model(num_classes).to(device)

    # -- Loss
    class_weights = compute_class_weights(train_loader.dataset).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    # -- Optimizer
    optimizer = build_optimizer(model)
    device_type = "cuda" if torch.cuda.is_available() else "cpu"
    scaler = GradScaler(device_type, enabled=USE_AMP)

    # -- Train 2 Batches
    print(f"\n[TRAIN] Running {SMOKE_BATCHES} train batches...")
    model.train()
    train_iter = iter(train_loader)

    all_preds, all_labels = [], []
    for batch_idx in range(SMOKE_BATCHES):
        t0 = time.time()
        images, labels = next(train_iter)
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        with autocast(device_type=device_type, enabled=USE_AMP):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        preds = outputs.argmax(dim=1).cpu().numpy()
        all_preds.extend(preds)
        all_labels.extend(labels.cpu().numpy())
        elapsed = time.time() - t0
        print(f"   Batch {batch_idx+1}: Loss={loss.item():.4f}  shape={list(images.shape)}  time={elapsed:.2f}s")

    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    print(f"   Smoke train Macro-F1: {macro_f1:.4f}  (low is expected -- random weights on random batch)")

    # -- Val 1 Batch
    print("\n[VAL] Running 1 val batch...")
    model.eval()
    val_iter = iter(val_loader)
    images, labels = next(val_iter)
    images, labels = images.to(device), labels.to(device)

    with torch.no_grad():
        with autocast(device_type=device_type, enabled=USE_AMP):
            outputs = model(images)
            val_loss = criterion(outputs, labels)

    print(f"   Val Loss: {val_loss.item():.4f}  OK")

    # -- Checkpoint Save
    print("\n[SAVE] Testing checkpoint save/load...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    smoke_ckpt = MODELS_DIR / "smoke_test_checkpoint.pth"
    torch.save({
        "epoch": 0,
        "model_name": MODEL_NAME,
        "num_classes": num_classes,
        "class_names": class_names,
        "image_size": IMAGE_SIZE,
        "state_dict": model.state_dict(),
        "val_macro_f1": 0.0,
        "val_accuracy": 0.0,
    }, smoke_ckpt)
    print(f"   Saved: {smoke_ckpt}")

    # Load it back
    ckpt = torch.load(smoke_ckpt, map_location="cpu")
    assert ckpt["num_classes"] == num_classes
    assert ckpt["class_names"] == class_names
    print(f"   Loaded back: classes={ckpt['num_classes']}  OK")

    # Cleanup
    smoke_ckpt.unlink()
    print("   Temp checkpoint removed.")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("✅ Smoke test PASSED. Pipeline is ready for full training.")
    print("=" * 50)


if __name__ == "__main__":
    smoke_test()
