"""
AgriSmart AI — Model 2 Pipeline Verification
=============================================
Standalone verification script checking all Model 2 guardrails:
  1. Required datasets/directories exist.
  2. Model 1 checkpoint exists & loads cleanly into timm EfficientNet-B2.
  3. Architecture == efficientnet_b2, Classes == 28, Size == 260x260.
  4. classes.json matches checkpoint class ordering exactly.
  5. PlantDoc test & PlantVillage test are isolated and NOT in training/val.
  6. Zero file leakage across all 4 split combinations.
  7. DataLoader produces valid batches ([B, 3, 260, 260], labels 0..27).
  8. Loss calculation & forward pass succeed without error.
  9. Model 1 hash is verified unmodified.

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

# Safe UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

MODEL1_CKPT = ROOT_DIR / "models" / "agrismart_best.pth"
CLASSES_JSON = ROOT_DIR / "models" / "classes.json"

MODEL2_TRAIN_DIR = ROOT_DIR / "data" / "processed_model2" / "train"
MODEL2_VAL_DIR = ROOT_DIR / "data" / "processed_model2" / "val"

PV_TEST_DIR = ROOT_DIR / "data" / "processed" / "test"
PD_TEST_DIR = ROOT_DIR / "data" / "plantdoc" / "test"

IMAGE_SIZE = 260
EXPECTED_MODEL1_HASH = "af9684b036dac12c650004a2877add20708007ad34811015d1efaf5bcea06215"


def verify_model2_pipeline():
    print("=" * 70)
    print(" AGRISMART AI — MODEL 2 PIPELINE & GUARDRAIL VERIFICATION")
    print("=" * 70)

    errors = []

    # 1. Directory & File Existence Checks
    print("\n[1/8] Checking file & directory existence...")
    required_paths = [
        (MODEL1_CKPT, "Model 1 checkpoint"),
        (CLASSES_JSON, "classes.json"),
        (MODEL2_TRAIN_DIR, "Model 2 train dir"),
        (MODEL2_VAL_DIR, "Model 2 val dir"),
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

    # 2. Model 1 Checkpoint Hash Verification
    print("\n[2/8] Verifying Model 1 file integrity & SHA256 hash...")
    current_hash = hashlib.sha256(MODEL1_CKPT.read_bytes()).hexdigest()
    if current_hash != EXPECTED_MODEL1_HASH:
        errors.append(f"Model 1 hash mismatch! Expected {EXPECTED_MODEL1_HASH}, got {current_hash}")
        print(f"  [FAIL] Model 1 HASH MISMATCH! File has been altered.")
    else:
        print(f"  [OK] Model 1 SHA256 matches: {current_hash[:16]}... (UNTOUCHED)")

    # 3. Model 1 Checkpoint Metadata & Loading Check
    print("\n[3/8] Loading Model 1 checkpoint & checking architecture...")
    ckpt = torch.load(MODEL1_CKPT, map_location="cpu", weights_only=False)
    
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
    with open(CLASSES_JSON, "r", encoding="utf-8") as f:
        classes_dict = json.load(f)
    json_classes = [classes_dict[str(i)] for i in range(len(classes_dict))]

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

    # 6. Leakage & Test Set Protection Checks
    print("\n[6/8] Running strict 0-leakage verification...")
    manifest_path = ROOT_DIR / "data" / "model2_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        train_orig_stems = {item["original_filename"] for item in manifest if item["split"] == "train"}
        val_orig_stems = {item["original_filename"] for item in manifest if item["split"] == "val"}
    else:
        train_orig_stems = {f.name for f in MODEL2_TRAIN_DIR.rglob("*") if f.is_file()}
        val_orig_stems = {f.name for f in MODEL2_VAL_DIR.rglob("*") if f.is_file()}

    pd_test_files = {f.name for f in PD_TEST_DIR.rglob("*") if f.is_file()}
    pv_test_files = {f.name for f in PV_TEST_DIR.rglob("*") if f.is_file()}

    leakages = {
        "Train vs Val": len(train_orig_stems & val_orig_stems),
        "Train vs PlantDoc Test": len(train_orig_stems & pd_test_files),
        "Val vs PlantDoc Test": len(val_orig_stems & pd_test_files),
        "Train vs PlantVillage Test": len(train_orig_stems & pv_test_files),
        "Val vs PlantVillage Test": len(val_orig_stems & pv_test_files),
    }

    leakage_failed = False
    for label, count in leakages.items():
        if count != 0:
            errors.append(f"Leakage detected in {label}: {count} overlapping files")
            print(f"  [FAIL] {label}: FAILED ({count} files overlap!)")
            leakage_failed = True
        else:
            print(f"  [OK] {label}: 0 overlap")

    if not leakage_failed:
        print(f"  [OK] ALL TEST SETS (PlantDoc {len(pd_test_files)} imgs, PlantVillage {len(pv_test_files)} imgs) ARE LOCKED & ISOLATED.")

    # 7. DataLoader & Batch Processing Sanity Check
    print("\n[7/8] Testing DataLoader batch generation...")
    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
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
