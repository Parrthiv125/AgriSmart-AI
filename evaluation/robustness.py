"""
AgriSmart AI — Robustness Testing
===================================
Tests model Macro-F1 under degraded image conditions that simulate
real-world field photography (blur, darkness, compression, noise, etc.)

Produces a robustness table and comparison plot.

Usage:
    python evaluation/robustness.py --model_path models/agrismart_best.pth
"""

import sys
import json
import argparse
from pathlib import Path

import numpy as np
import torch
from torch.amp import autocast
from tqdm import tqdm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score

from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import BEST_MODEL_PATH, EVAL_DIR, VAL_DIR, USE_AMP, BATCH_SIZE, NUM_WORKERS
from training.preprocessing import get_robustness_transforms, get_val_transform
from inference.predict import load_model


def evaluate_under_condition(model, transform, data_dir, class_names, device, batch_size):
    """Run inference with a specific transform and return Macro-F1."""
    dataset = ImageFolder(root=str(data_dir), transform=transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False,
                        num_workers=NUM_WORKERS, pin_memory=True)

    all_preds, all_labels = [], []
    model.eval()
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            with autocast(device_type="cuda" if images.is_cuda else "cpu", enabled=USE_AMP):
                outputs = model(images)
            preds = outputs.argmax(dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.numpy())

    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return macro_f1


def run_robustness_tests(model_path: Path, data_split_dir: Path = VAL_DIR,
                          batch_size: int = BATCH_SIZE):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load model
    model, class_names, _ = load_model(model_path)
    model.eval().to(device)

    # Get all robustness transforms
    transforms = get_robustness_transforms()

    print(f"\n🧪 Robustness Testing — {len(transforms)} conditions")
    print(f"   Data dir: {data_split_dir}")
    print(f"   Classes: {len(class_names)}")
    print("=" * 55)

    results = {}
    baseline_f1 = None

    for condition_name, transform in transforms.items():
        macro_f1 = evaluate_under_condition(
            model, transform, data_split_dir, class_names, device, batch_size
        )
        results[condition_name] = macro_f1

        if condition_name == "normal":
            baseline_f1 = macro_f1

        drop = ""
        if baseline_f1 is not None and condition_name != "normal":
            drop = f"  (Δ {macro_f1 - baseline_f1:+.4f})"

        print(f"  {condition_name:<25}  Macro-F1: {macro_f1:.4f}{drop}")

    print("=" * 55)
    return results


def plot_robustness(results: dict, save_path: Path):
    conditions = list(results.keys())
    scores = list(results.values())
    colors = ["#2ecc71" if c == "normal" else "#e74c3c" for c in conditions]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(conditions, scores, color=colors, alpha=0.85, edgecolor="white")
    ax.axhline(results.get("normal", 0), color="#2ecc71", linestyle="--",
               alpha=0.7, linewidth=1.5, label="Baseline (normal)")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Macro-F1", fontsize=12)
    ax.set_title("AgriSmart AI — Robustness Under Input Degradation", fontsize=14)
    ax.legend()
    plt.xticks(rotation=30, ha="right")
    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{score:.3f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"📊 Robustness plot saved: {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Robustness testing for AgriSmart AI")
    parser.add_argument("--model_path", type=str, default=str(BEST_MODEL_PATH))
    parser.add_argument("--split", type=str, default="val", choices=["val", "test"])
    parser.add_argument("--batch_size", type=int, default=BATCH_SIZE)
    args = parser.parse_args()

    from training.config import VAL_DIR, TEST_DIR
    data_dir = VAL_DIR if args.split == "val" else TEST_DIR

    results = run_robustness_tests(
        model_path=Path(args.model_path),
        data_split_dir=data_dir,
        batch_size=args.batch_size,
    )

    # Save results
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    results_path = EVAL_DIR / "robustness_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Robustness results saved: {results_path}")

    # Plot
    plot_path = EVAL_DIR / "robustness_chart.png"
    plot_robustness(results, plot_path)

    # Print table
    print("\n📋 Robustness Summary Table:")
    print(f"  {'Condition':<25}  {'Macro-F1':>10}")
    print("  " + "-" * 38)
    baseline = results.get("normal", 0)
    for cond, score in results.items():
        delta = f"({score - baseline:+.4f})" if cond != "normal" else ""
        print(f"  {cond:<25}  {score:>8.4f}  {delta}")


if __name__ == "__main__":
    main()
