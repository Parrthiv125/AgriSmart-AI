"""
AgriSmart AI -- External PlantDoc Evaluation
=============================================
Evaluates the existing baseline model (models/agrismart_best.pth)
against the PlantDoc test split as an external field-generalization test.

This is NOT the competition organizer hidden test set.

Label: "External PlantDoc Evaluation -- Baseline Model"

Evaluation uses the same preprocessing as training/inference:
  - RGB images
  - Resize to 260x260
  - ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

Outputs:
  evaluation/results/plantdoc_external_eval.json
  evaluation/results/plantdoc_confusion_matrix.png

Usage:
    python evaluation/evaluate_plantdoc.py

Run AFTER:
    python data/download_plantdoc.py
    python data/prepare_plantdoc.py
"""

import sys
import json
from pathlib import Path
from datetime import datetime

import torch
import torch.nn as nn
import numpy as np
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Paths
CHECKPOINT_PATH = ROOT_DIR / "models" / "agrismart_best.pth"
CLASSES_JSON = ROOT_DIR / "models" / "classes.json"
PLANTDOC_TEST = ROOT_DIR / "data" / "plantdoc" / "test"
RESULTS_DIR = ROOT_DIR / "evaluation" / "results"
EVAL_JSON_OUT = RESULTS_DIR / "plantdoc_external_eval.json"
CONFUSION_PNG_OUT = RESULTS_DIR / "plantdoc_confusion_matrix.png"
MAPPING_CSV = ROOT_DIR / "data" / "plantdoc_class_mapping.csv"

# Preprocessing constants -- must match training exactly
IMAGE_SIZE = 260
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sanitize_folder_name(name: str) -> str:
    return name.replace("/", "_")


def load_model(checkpoint_path: Path, num_classes: int, device: torch.device):
    """Load EfficientNet-B2 from checkpoint -- same logic as inference/predict.py."""
    import timm
    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)
    model_name = ckpt.get("model_name", "efficientnet_b2")
    model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
    model.load_state_dict(ckpt["state_dict"])
    model.to(device)
    model.eval()
    print(f"[OK] Loaded: {model_name} | Classes: {num_classes}")
    print(f"     Checkpoint epoch: {ckpt.get('epoch', 'N/A')}")
    print(f"     Val Macro-F1 at save: {ckpt.get('val_macro_f1', 0.0):.4f}")
    return model


def preprocess_image(image_path: Path) -> torch.Tensor:
    """Preprocess a single image exactly as used during training."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.BILINEAR)
    arr = np.array(img, dtype=np.float32) / 255.0
    mean = np.array(NORM_MEAN, dtype=np.float32)
    std = np.array(NORM_STD, dtype=np.float32)
    arr = (arr - mean) / std
    tensor = torch.from_numpy(arr.transpose(2, 0, 1)).unsqueeze(0)  # (1, 3, H, W)
    return tensor


def build_dataset(test_dir: Path, class_names: list) -> tuple:
    """
    Build (image_path, label_idx) pairs from the structured PlantDoc test dir.
    Uses sanitized folder names matching the AgriSmart class names.
    """
    samples = []
    class_to_idx = {
        sanitize_folder_name(name): idx
        for idx, name in enumerate(class_names)
    }

    missing_folders = []
    for folder in sorted(test_dir.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name not in class_to_idx:
            print(f"  [!] Folder not in AgriSmart classes: '{folder.name}' -- SKIPPED")
            missing_folders.append(folder.name)
            continue
        label_idx = class_to_idx[folder.name]
        for img_path in sorted(folder.iterdir()):
            if img_path.suffix.lower() in IMG_EXTS:
                samples.append((img_path, label_idx))

    return samples, missing_folders


def run_evaluation(
    model: nn.Module,
    samples: list,
    class_names: list,
    device: torch.device,
    batch_size: int = 32,
):
    """Run inference over all samples in batches, return predictions and labels."""
    all_preds = []
    all_labels = []
    errors = []

    n = len(samples)
    print(f"\nRunning inference on {n} images...")

    for i in range(0, n, batch_size):
        batch_samples = samples[i: i + batch_size]
        batch_tensors = []
        batch_labels = []

        for img_path, label in batch_samples:
            try:
                tensor = preprocess_image(img_path)
                batch_tensors.append(tensor)
                batch_labels.append(label)
            except Exception as e:
                errors.append({"file": str(img_path), "error": str(e)})
                continue

        if not batch_tensors:
            continue

        batch_input = torch.cat(batch_tensors, dim=0).to(device)
        with torch.no_grad():
            outputs = model(batch_input)
            preds = outputs.argmax(dim=1).cpu().numpy()

        all_preds.extend(preds.tolist())
        all_labels.extend(batch_labels)

        if (i // batch_size + 1) % 5 == 0 or i + batch_size >= n:
            print(f"  Processed {min(i + batch_size, n)}/{n}", end="\r")

    print()
    if errors:
        print(f"  [!] {len(errors)} images failed to load.")

    return np.array(all_labels), np.array(all_preds), errors


def compute_metrics(labels: np.ndarray, preds: np.ndarray, class_names: list) -> dict:
    from sklearn.metrics import (
        f1_score, accuracy_score, precision_recall_fscore_support,
        confusion_matrix,
    )

    macro_f1 = f1_score(labels, preds, average="macro", zero_division=0)
    accuracy = accuracy_score(labels, preds)

    precisions, recalls, f1s, supports = precision_recall_fscore_support(
        labels, preds, average=None, zero_division=0, labels=list(range(len(class_names)))
    )

    per_class = {}
    for i, cls_name in enumerate(class_names):
        per_class[cls_name] = {
            "precision": float(precisions[i]),
            "recall": float(recalls[i]),
            "f1": float(f1s[i]),
            "support": int(supports[i]),
        }

    cm = confusion_matrix(labels, preds, labels=list(range(len(class_names))))

    return {
        "macro_f1": float(macro_f1),
        "accuracy": float(accuracy),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
    }


def plot_confusion_matrix(
    cm: list,
    class_names: list,
    out_path: Path,
):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cm_arr = np.array(cm)
    n = len(class_names)

    # Normalize by row (true class) for readability
    row_sums = cm_arr.sum(axis=1, keepdims=True).clip(min=1)
    cm_norm = cm_arr.astype(float) / row_sums

    fig, ax = plt.subplots(figsize=(18, 16))
    im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)

    # Short labels for readability
    short_labels = [c.split(" -- ")[-1][:25] if " -- " in c else c[-25:] for c in class_names]
    # Handle em-dash separator
    short_labels = []
    for c in class_names:
        if " \u2014 " in c:
            short_labels.append(c.split(" \u2014 ")[-1][:25])
        else:
            short_labels.append(c[-25:])

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(short_labels, rotation=90, fontsize=7)
    ax.set_yticklabels(short_labels, fontsize=7)

    # Annotate cells with raw counts
    for i in range(n):
        for j in range(n):
            count = cm_arr[i, j]
            if count > 0:
                color = "white" if cm_norm[i, j] > 0.6 else "black"
                ax.text(
                    j, i, str(int(count)),
                    ha="center", va="center", fontsize=6, color=color
                )

    ax.set_xlabel("Predicted Class", fontsize=11)
    ax.set_ylabel("True Class (PlantDoc)", fontsize=11)
    ax.set_title(
        "External PlantDoc Evaluation -- Baseline EfficientNet-B2\n"
        "Confusion Matrix (row-normalized; cells show raw counts)",
        fontsize=12, pad=12,
    )

    plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[OK] Confusion matrix saved: {out_path}")


def print_report(metrics: dict, class_names: list, n_images: int, n_errors: int):
    print()
    print("=" * 70)
    print(" EXTERNAL PLANTDOC EVALUATION -- BASELINE MODEL RESULTS")
    print("=" * 70)
    print(f"  Evaluated images:  {n_images} ({n_errors} load errors)")
    print(f"  Macro-F1:          {metrics['macro_f1']:.4f}")
    print(f"  Accuracy:          {metrics['accuracy']:.4f}")
    print()
    print(f"  {'Class':<45} {'Prec':>6} {'Rec':>6} {'F1':>6} {'N':>5}")
    print(f"  {'-'*73}")
    for cls in class_names:
        m = metrics["per_class"].get(cls, {})
        print(
            f"  {cls:<45} "
            f"{m.get('precision', 0):>6.3f} "
            f"{m.get('recall', 0):>6.3f} "
            f"{m.get('f1', 0):>6.3f} "
            f"{m.get('support', 0):>5}"
        )
    print("=" * 70)


def evaluate_plantdoc():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=" * 70)
    print(" AGRISMART AI -- External PlantDoc Evaluation")
    print("=" * 70)
    print(f"  Label: External PlantDoc Evaluation -- Baseline Model")
    print(f"  Model:  {CHECKPOINT_PATH}")
    print(f"  Data:   {PLANTDOC_TEST}")
    print(f"  Device: {device}")
    print(f"  Preprocessing: RGB, {IMAGE_SIZE}x{IMAGE_SIZE}, ImageNet normalization")
    print()

    # Sanity checks
    for path, desc in [
        (CHECKPOINT_PATH, "Model checkpoint"),
        (CLASSES_JSON, "classes.json"),
        (PLANTDOC_TEST, "PlantDoc test dir"),
    ]:
        if not path.exists():
            print(f"[ERROR] Missing: {desc} at {path}")
            sys.exit(1)

    # Load class names
    with open(CLASSES_JSON) as f:
        classes_dict = json.load(f)
    class_names = [classes_dict[str(i)] for i in range(len(classes_dict))]
    num_classes = len(class_names)
    print(f"[OK] {num_classes} AgriSmart classes loaded from {CLASSES_JSON.name}")

    # Load model
    model = load_model(CHECKPOINT_PATH, num_classes, device)

    # Build dataset
    samples, missing = build_dataset(PLANTDOC_TEST, class_names)
    print(f"[OK] {len(samples)} images found in PlantDoc test split")
    if missing:
        print(f"[!]  {len(missing)} folders skipped (not in 28-class mapping)")

    if len(samples) == 0:
        print("[ERROR] No images found. Run data/prepare_plantdoc.py first.")
        sys.exit(1)

    # Run evaluation
    labels, preds, errors = run_evaluation(model, samples, class_names, device)

    # Compute metrics
    metrics = compute_metrics(labels, preds, class_names)

    # Print report
    print_report(metrics, class_names, len(samples), len(errors))

    # Plot confusion matrix
    plot_confusion_matrix(metrics["confusion_matrix"], class_names, CONFUSION_PNG_OUT)

    # Save JSON
    output_payload = {
        "evaluation_label": "External PlantDoc Evaluation -- Baseline Model",
        "timestamp": datetime.now().isoformat(),
        "model": {
            "checkpoint": "models/agrismart_best.pth",
            "architecture": "efficientnet_b2",
            "num_classes": num_classes,
        },
        "data": {
            "dataset": "PlantDoc (Singh et al., CoDS-COMAD 2020)",
            "source": "https://github.com/pratikkayal/PlantDoc-Dataset",
            "license": "CC-BY-4.0",
            "split": "test (original PlantDoc test split, preserved intact)",
            "mapping_file": "data/plantdoc_class_mapping.csv",
            "mapping_assumption": (
                "Corn leaf blight -> Corn -- Northern Leaf Blight: "
                "NLB is the dominant corn blight in PlantDoc. Documented assumption."
            ),
            "total_images": len(samples),
            "load_errors": len(errors),
        },
        "preprocessing": {
            "image_size": IMAGE_SIZE,
            "color_mode": "RGB",
            "normalization_mean": NORM_MEAN,
            "normalization_std": NORM_STD,
            "note": "Identical to training/inference preprocessing pipeline",
        },
        "results": {
            "macro_f1": metrics["macro_f1"],
            "accuracy": metrics["accuracy"],
        },
        "per_class_metrics": metrics["per_class"],
        "confusion_matrix": metrics["confusion_matrix"],
        "warnings": [
            "This is an EXTERNAL field-generalization test only.",
            "Do NOT compare directly to PlantVillage local test results.",
            "The official competition organizer hidden test set remains the competition metric.",
        ],
        "load_errors": errors,
    }

    with open(EVAL_JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)
    print(f"[OK] Evaluation JSON saved: {EVAL_JSON_OUT}")

    print()
    print("=" * 70)
    print(" SUMMARY")
    print("=" * 70)
    print(f"  External PlantDoc Macro-F1: {metrics['macro_f1']:.4f}")
    print(f"  External PlantDoc Accuracy: {metrics['accuracy']:.4f}")
    print(f"  Images evaluated:           {len(samples)}")
    print(f"  Results: {EVAL_JSON_OUT}")
    print(f"  Matrix:  {CONFUSION_PNG_OUT}")

    return output_payload


if __name__ == "__main__":
    evaluate_plantdoc()
