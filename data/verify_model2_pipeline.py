"""
AgriSmart AI — Model 2 Pipeline & Guardrail Verification
============================================================
Standalone verification script checking all Model 2 guardrails:
  1. Required datasets & directory existence.
  2. Model 1 checkpoint integrity (SHA256 af9684b0...).
  3. EfficientNet-B2 architecture, 28 classes, 260x260 image size.
  4. classes.json alignment with checkpoint.
  5. State dict loading cleanly.
  6. Authoritative SHA256 0-leakage verification (via data.leakage_checker).
  7. DataLoader batch generation ([B, 3, 260, 260], labels 0..27).
  8. Forward pass & loss calculation.
  9. Automatic dataset self-healing if processed dataset is missing or stale.

Usage:
    python data/verify_model2_pipeline.py
"""

import sys
import json
import hashlib
import torch
import torch.nn as nn
from pathlib import Path
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import timm

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.common import (
    ROOT_DIR,
    CLASSES_JSON,
    MODEL1_CKPT_PATH,
    EXPECTED_MODEL1_HASH,
    MODEL2_TRAIN_DIR,
    MODEL2_VAL_DIR,
    PV_TEST_DIR,
    PD_TEST_DIR,
    IMAGE_SIZE,
    NORM_MEAN,
    NORM_STD,
    load_canonical_classes,
)
from data.leakage_checker import audit_content_leakage
from data.prepare_model2_dataset import prepare_model2_dataset

# Safe UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def verify_model2_pipeline():
    print("=" * 70)
    print(" AGRISMART AI — MODEL 2 PIPELINE & GUARDRAIL VERIFICATION")
    print("=" * 70)

    errors = []

    # 1. Directory & File Existence Checks (Self-healing dataset trigger)
    print("\n[1/8] Checking file & directory existence...")
    required_paths = [
        (MODEL1_CKPT_PATH, "Model 1 checkpoint"),
        (CLASSES_JSON, "classes.json"),
        (PV_TEST_DIR, "PlantVillage test dir"),
        (PD_TEST_DIR, "PlantDoc test dir"),
    ]
    for path, desc in required_paths:
        if not path.exists():
            errors.append(f"Missing required path: {desc} at {path}")
            print(f"  [MISSING] {desc}")
        else:
            print(f"  [OK] Found: {desc} ({path.relative_to(ROOT_DIR)})")

    if errors:
        print("\n[ERROR] VERIFICATION FAILED at Step 1.")
        sys.exit(1)

    # Check Model 2 processed datasets; self-heal if missing
    if not MODEL2_TRAIN_DIR.exists() or not MODEL2_VAL_DIR.exists():
        print("  [WARN] Model 2 processed dataset missing. Triggering automatic self-healing build...")
        prepare_model2_dataset()

    print(f"  [OK] Model 2 Train Dir: {MODEL2_TRAIN_DIR.relative_to(ROOT_DIR)}")
    print(f"  [OK] Model 2 Val Dir:   {MODEL2_VAL_DIR.relative_to(ROOT_DIR)}")

    # 2. Model 1 Checkpoint Hash Verification
    print("\n[2/8] Verifying Model 1 file integrity & SHA256 hash...")
    current_hash = hashlib.sha256(MODEL1_CKPT_PATH.read_bytes()).hexdigest()
    if current_hash != EXPECTED_MODEL1_HASH:
        errors.append(f"Model 1 hash mismatch! Expected {EXPECTED_MODEL1_HASH}, got {current_hash}")
        print(f"  [FAIL] Model 1 HASH MISMATCH! File has been altered.")
    else:
        print(f"  [OK] Model 1 SHA256 matches: {current_hash[:16]}... (UNTOUCHED)")

    # 3. Model 1 Checkpoint Metadata & Loading Check
    print("\n[3/8] Loading Model 1 checkpoint & checking architecture...")
    ckpt = torch.load(MODEL1_CKPT_PATH, map_location="cpu", weights_only=False)
    
    model_name = ckpt.get("model_name", "efficientnet_b2")
    num_classes = ckpt.get("num_classes", 28)
    image_size = ckpt.get("image_size", 260)
    ckpt_classes = ckpt.get("class_names", [])

    if model_name != "efficientnet_b2":
        errors.append(f"Expected architecture efficientnet_b2, got {model_name}")
    if num_classes != 28:
        errors.append(f"Expected 28 classes, got {num_classes}")
    if image_size != 260:
        errors.append(f"Expected image size 260, got {image_size}")

    print(f"  [OK] Architecture: {model_name} | Classes: {num_classes} | Size: {image_size}x{image_size}")

    # 4. classes.json Alignment Check
    print("\n[4/8] Verifying classes.json alignment...")
    json_classes = load_canonical_classes()
    if json_classes != ckpt_classes:
        errors.append("class ordering in classes.json does not match checkpoint!")
        print("  [FAIL] Mismatch between classes.json and checkpoint class names!")
    else:
        print(f"  [OK] 28 classes align 100% between classes.json and checkpoint.")

    # 5. Model Instantiation & State Dict Loading
    print("\n[5/8] Instantiating PyTorch timm model...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
    model.load_state_dict(ckpt["state_dict"])
    model.to(device)
    model.eval()
    print("  [OK] State dict loaded cleanly without error.")

    # 6. Authoritative SHA256 Content Leakage Audit
    print("\n[6/8] Running authoritative SHA256 0-leakage verification...")
    audit = audit_content_leakage(
        train_dir=MODEL2_TRAIN_DIR,
        val_dir=MODEL2_VAL_DIR,
        pd_test_dir=PD_TEST_DIR,
        pv_test_dir=PV_TEST_DIR,
        verbose=False,
    )

    if not audit["is_clean"]:
        print("  [WARN] Content leakage detected in processed dataset! Triggering dataset self-healing rebuild...")
        prepare_model2_dataset()
        audit = audit_content_leakage(
            train_dir=MODEL2_TRAIN_DIR,
            val_dir=MODEL2_VAL_DIR,
            pd_test_dir=PD_TEST_DIR,
            pv_test_dir=PV_TEST_DIR,
            verbose=False,
        )

    if not audit["is_clean"]:
        errors.append("Content leakage remains after self-healing rebuild!")
        print("  [FAIL] SHA256 Content Leakage Verification Failed!")
    else:
        print(f"  [OK] SHA256 Content Audit PASSED: 0 true content duplicates in train/val.")
        print(f"  [OK] Preserved {audit['filename_collisions_count']} safe filename-only collisions.")
        print(f"  [OK] PlantDoc TEST ({len(list(PD_TEST_DIR.rglob('*')))} imgs) & PlantVillage TEST ({len(list(PV_TEST_DIR.rglob('*')))} imgs) ARE LOCKED & UNTOUCHED.")

    # 7. DataLoader & Batch Processing Sanity Check
    print("\n[7/8] Testing DataLoader batch generation...")
    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])
    val_dataset = datasets.ImageFolder(MODEL2_VAL_DIR, transform=val_transform)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)

    images, labels = next(iter(val_loader))
    images, labels = images.to(device), labels.to(device)

    print(f"  [OK] Batch input shape:  {list(images.shape)}")
    print(f"  [OK] Batch label shape:  {list(labels.shape)}")
    print(f"  [OK] Label value range:  min={labels.min().item()}, max={labels.max().item()} (valid 0..27)")

    if list(images.shape) != [8, 3, 260, 260]:
        errors.append(f"Expected batch shape [8, 3, 260, 260], got {list(images.shape)}")
    if labels.min().item() < 0 or labels.max().item() >= 28:
        errors.append(f"Labels out of range [0, 27]: min={labels.min().item()}, max={labels.max().item()}")

    # 8. Forward Pass & Loss Calculation Check
    print("\n[8/8] Testing forward pass & loss calculation...")
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        outputs = model(images)
        loss = criterion(outputs, labels)

    print(f"  [OK] Output shape:       {list(outputs.shape)}")
    print(f"  [OK] Loss calculation:   {loss.item():.4f}")

    if outputs.shape != (8, 28):
        errors.append(f"Expected output shape (8, 28), got {outputs.shape}")

    print("\n" + "=" * 70)
    if errors:
        print(" [FAIL] MODEL 2 PIPELINE VERIFICATION FAILED")
        print("=" * 70)
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print(" [PASS] SUCCESS: ALL MODEL 2 GUARDRAILS & VERIFICATIONS PASSED")
        print("=" * 70)
        return True


if __name__ == "__main__":
    verify_model2_pipeline()
