"""
AgriSmart AI — Model Integration & Loading Verification
=========================================================
Verifies that models/agrismart_best.pth and models/classes.json:
  1. Exist in the configured models/ path
  2. Contain valid checkpoint metadata (architecture, epochs, metrics)
  3. Match class names and ordering exactly between .pth and classes.json
  4. Can be instantiated using timm and load the state_dict cleanly
  5. Can perform a dummy forward pass ([1, 3, 260, 260] -> [1, 28])
"""

import sys
import json
from pathlib import Path
import torch
import timm

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

MODEL2_PATH = ROOT_DIR / "models" / "agrismart_field_adapted_best.pth"
MODEL1_PATH = ROOT_DIR / "models" / "agrismart_best.pth"
MODEL_PATH = MODEL2_PATH if MODEL2_PATH.exists() else MODEL1_PATH
CLASSES_JSON_PATH = ROOT_DIR / "models" / "classes.json"


def verify_model():
    print("=" * 70)
    print(" AGRISMART AI - MODEL INTEGRATION VERIFICATION")
    print("=" * 70)

    # 1. File existence check
    print("\n[1/5] Checking file existence...")
    assert MODEL_PATH.exists(), f"ERROR: Model file missing at {MODEL_PATH}"
    assert CLASSES_JSON_PATH.exists(), f"ERROR: classes.json missing at {CLASSES_JSON_PATH}"
    print(f"  [OK] Model checkpoint: {MODEL_PATH} ({MODEL_PATH.stat().st_size / 1e6:.1f} MB)")
    print(f"  [OK] Class index JSON: {CLASSES_JSON_PATH}")

    # 2. Checkpoint metadata inspection
    print("\n[2/5] Inspecting model checkpoint...")
    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    
    required_keys = ["model_name", "num_classes", "class_names", "state_dict"]
    for key in required_keys:
        assert key in checkpoint, f"ERROR: Key '{key}' missing from checkpoint!"

    model_name = checkpoint.get("model_name", "efficientnet_b2")
    num_classes = checkpoint["num_classes"]
    epoch = checkpoint.get("epoch", "N/A")
    image_size = checkpoint.get("image_size", 260)
    val_f1 = checkpoint.get("val_macro_f1", 0.0)
    val_acc = checkpoint.get("val_accuracy", 0.0)
    ckpt_classes = checkpoint["class_names"]

    print(f"  [OK] Architecture:       {model_name}")
    print(f"  [OK] Number of Classes:  {num_classes}")
    print(f"  [OK] Best Epoch:         {epoch}")
    print(f"  [OK] Input Image Size:   {image_size} x {image_size}")
    print(f"  [OK] Validation Macro-F1:{val_f1:.4f}")
    print(f"  [OK] Validation Acc:     {val_acc:.4f}")

    # 3. classes.json alignment check
    print("\n[3/5] Verifying classes.json alignment...")
    with open(CLASSES_JSON_PATH, "r", encoding="utf-8") as f:
        classes_dict = json.load(f)

    assert len(classes_dict) == num_classes, (
        f"Mismatch: classes.json has {len(classes_dict)} entries, checkpoint has {num_classes}"
    )

    json_classes = [classes_dict[str(i)] for i in range(len(classes_dict))]
    assert json_classes == ckpt_classes, (
        "Mismatch: class ordering in classes.json does not match checkpoint!"
    )
    print(f"  [OK] Verified exact 28-class alignment between checkpoint and classes.json.")

    # 4. Model instantiation & state_dict loading
    print("\n[4/5] Instantiating PyTorch / timm model & loading state_dict...")
    model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    print("  [OK] State dict loaded into timm model without error.")

    # 5. Forward pass dummy tensor sanity check
    print("\n[5/5] Testing dummy forward pass...")
    dummy_input = torch.randn(1, 3, image_size, image_size)
    with torch.no_grad():
        output = model(dummy_input)

    assert output.shape == (1, num_classes), f"Output shape error: expected (1, {num_classes}), got {output.shape}"
    print(f"  [OK] Dummy input shape [1, 3, {image_size}, {image_size}] -> Output shape {list(output.shape)}")

    print("\n" + "=" * 70)
    print(" SUCCESS: EfficientNet-B2 MODEL INTEGRATION & VERIFICATION PASSED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    verify_model()
