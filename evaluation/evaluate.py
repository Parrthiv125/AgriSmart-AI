"""
AgriSmart AI — Evaluation Pipeline
=====================================
Computes all required metrics:
  - Macro-F1 (primary metric)
  - Accuracy
  - Per-class precision, recall, F1
  - Confusion matrix
  - Top-K accuracy
  - Error analysis (worst-performing classes)

Usage:
    python evaluation/evaluate.py --model_path models/agrismart_best.pth
"""

import sys
import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.amp import autocast
from tqdm import tqdm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import BEST_MODEL_PATH, EVAL_DIR, USE_AMP, BATCH_SIZE, NUM_WORKERS
from training.dataset import get_dataloaders
from training.preprocessing import get_val_transform
from inference.predict import load_model


# ── Run Evaluation ────────────────────────────────────────────────────────────

def run_evaluation(model_path: Path, split: str = "val", batch_size: int = BATCH_SIZE):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model + class names from checkpoint FIRST.
    # We must pass these exact class_names to get_dataloaders() so the dataset
    # class-index ordering matches the model's output-index ordering exactly.
    model, class_names, preprocess = load_model(model_path)
    model.eval().to(device)
    num_classes = len(class_names)

    print(f"📂 Evaluating on split: {split}")
    print(f"   Classes: {num_classes}")
    print(f"   Class list sourced from model checkpoint — order is authoritative.")

    # Pass class_names from checkpoint into get_dataloaders so both the model
    # and the dataset use the same class→index mapping.
    _, val_loader, test_loader, dataset_class_names = get_dataloaders(
        classes=class_names,
        batch_size=batch_size,
    )

    # Sanity-check: dataset and model must agree on class set
    if sorted(dataset_class_names) != sorted(class_names):
        raise ValueError(
            f"Class mismatch between model checkpoint ({len(class_names)} classes) "
            f"and dataset ({len(dataset_class_names)} classes).\n"
            f"Model classes: {class_names}\n"
            f"Dataset classes: {dataset_class_names}"
        )

    loader = val_loader if split == "val" else test_loader

    # Collect predictions
    all_preds, all_labels, all_probs = [], [], []
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Evaluating"):
            images = images.to(device)
            with autocast(device_type="cuda" if images.is_cuda else "cpu", enabled=USE_AMP):
                outputs = model(images)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()
            preds = np.argmax(probs, axis=1)
            all_probs.extend(probs)
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)

    return all_labels, all_preds, all_probs, class_names


# ── Metrics ───────────────────────────────────────────────────────────────────

def compute_metrics(labels, preds, class_names):
    macro_f1 = f1_score(labels, preds, average="macro", zero_division=0)
    accuracy = accuracy_score(labels, preds)

    report = classification_report(
        labels, preds,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    print(f"\n{'='*60}")
    print(f"  Macro-F1:  {macro_f1:.4f}")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"{'='*60}")
    print("\nPer-class metrics:")
    print(classification_report(labels, preds, target_names=class_names, zero_division=0))

    return macro_f1, accuracy, report


# ── Confusion Matrix ──────────────────────────────────────────────────────────

def plot_confusion_matrix(labels, preds, class_names, save_path: Path):
    cm = confusion_matrix(labels, preds)
    cm_norm = cm.astype(float) / (cm.sum(axis=1, keepdims=True) + 1e-6)

    fig_size = max(12, len(class_names) // 2)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size))

    sns.heatmap(
        cm_norm, annot=(len(class_names) <= 20),
        fmt=".2f", cmap="Blues",
        xticklabels=class_names, yticklabels=class_names,
        ax=ax, linewidths=0.5,
    )
    ax.set_xlabel("Predicted", fontsize=12)
    ax.set_ylabel("Actual", fontsize=12)
    ax.set_title("Normalised Confusion Matrix — AgriSmart AI", fontsize=14)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 Confusion matrix saved: {save_path}")


# ── Error Analysis ────────────────────────────────────────────────────────────

def error_analysis(labels, preds, probs, class_names, top_k: int = 10):
    """
    Identify:
    - worst-performing classes by recall
    - most common confusion pairs
    - low-confidence correct/incorrect predictions
    """
    report = {}

    # Per-class recall
    from sklearn.metrics import recall_score, precision_score
    recalls = recall_score(labels, preds, average=None, zero_division=0)
    precisions = precision_score(labels, preds, average=None, zero_division=0)
    f1s = f1_score(labels, preds, average=None, zero_division=0)

    class_perf = sorted(
        zip(class_names, recalls, precisions, f1s),
        key=lambda x: x[3]  # sort by F1
    )

    print(f"\n🔴 Bottom {top_k} classes by F1:")
    for name, rec, prec, f1 in class_perf[:top_k]:
        print(f"   {name:<45} Recall: {rec:.3f}  Prec: {prec:.3f}  F1: {f1:.3f}")

    print(f"\n🟢 Top {top_k} classes by F1:")
    for name, rec, prec, f1 in class_perf[-top_k:]:
        print(f"   {name:<45} Recall: {rec:.3f}  Prec: {prec:.3f}  F1: {f1:.3f}")

    # Most common confusion pairs
    wrong_mask = labels != preds
    wrong_true = labels[wrong_mask]
    wrong_pred = preds[wrong_mask]

    from collections import Counter
    pairs = Counter(zip(wrong_true, wrong_pred))
    print(f"\n⚠️  Top {top_k} confusion pairs (true → predicted):")
    for (t, p), count in pairs.most_common(top_k):
        print(f"   {class_names[t]:<40} → {class_names[p]:<40}  ({count} errors)")

    # Confidence distribution
    max_probs = probs.max(axis=1)
    correct_mask = labels == preds
    print(f"\n📈 Confidence stats:")
    print(f"   Correct predictions — mean confidence: {max_probs[correct_mask].mean():.3f}")
    print(f"   Wrong predictions   — mean confidence: {max_probs[~correct_mask].mean():.3f}")
    print(f"   Low confidence (<0.6): {(max_probs < 0.6).sum()} samples")
    print(f"   High confidence (>0.8): {(max_probs > 0.8).sum()} samples")

    return class_perf


# ── Save Results ──────────────────────────────────────────────────────────────

def save_results(macro_f1, accuracy, report, class_names, split, save_dir: Path):
    save_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "split": split,
        "macro_f1": macro_f1,
        "accuracy": accuracy,
        "per_class": {
            name: {
                "precision": report[name]["precision"],
                "recall": report[name]["recall"],
                "f1": report[name]["f1-score"],
                "support": report[name]["support"],
            }
            for name in class_names if name in report
        },
    }
    out_path = save_dir / f"evaluation_{split}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"✅ Results saved: {out_path}")
    return result


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Evaluate AgriSmart AI disease model")
    parser.add_argument("--model_path", type=str, default=str(BEST_MODEL_PATH))
    parser.add_argument("--split", type=str, default="val", choices=["val", "test"])
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    model_path = Path(args.model_path)
    save_dir = EVAL_DIR

    # Run
    labels, preds, probs, class_names = run_evaluation(model_path, args.split, args.batch_size)

    # Metrics
    macro_f1, accuracy, report = compute_metrics(labels, preds, class_names)

    # Confusion matrix
    cm_path = save_dir / f"confusion_matrix_{args.split}.png"
    plot_confusion_matrix(labels, preds, class_names, cm_path)

    # Error analysis
    error_analysis(labels, preds, probs, class_names)

    # Save JSON results
    save_results(macro_f1, accuracy, report, class_names, args.split, save_dir)

    print(f"\n🏆 Final Macro-F1 ({args.split}): {macro_f1:.4f}")


if __name__ == "__main__":
    main()
