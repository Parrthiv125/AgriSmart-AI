"""
AgriSmart AI — Dataset Split
==============================
Creates a reproducible train/val/test split from the downloaded PlantVillage images.

Usage:
    python data/split_dataset.py
    python data/split_dataset.py --train 0.80 --val 0.15 --test 0.05 --seed 42
"""

import sys
import json
import shutil
import random
import argparse
from pathlib import Path
from collections import defaultdict

from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from training.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR,
    TRAIN_RATIO, VAL_RATIO, TEST_RATIO, SEED, CLASSES,
)


def split_dataset(
    raw_dir: Path,
    out_dir: Path,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    seed: int = SEED,
    classes_filter=None,
):
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "Ratios must sum to 1.0"

    random.seed(seed)
    print(f"📂 Source: {raw_dir}")
    print(f"📁 Output: {out_dir}")
    print(f"   Split: {train_ratio:.0%} / {val_ratio:.0%} / {test_ratio:.0%}  |  Seed: {seed}")

    if not raw_dir.exists():
        print(f"❌ Raw data directory not found: {raw_dir}")
        print("   Run: python data/download_dataset.py")
        sys.exit(1)

    # Discover class directories
    class_dirs = sorted([d for d in raw_dir.iterdir() if d.is_dir()])
    if classes_filter:
        class_dirs = [d for d in class_dirs if d.name in set(classes_filter)]
        print(f"   Filtering to {len(class_dirs)} classes (from config CLASSES list)")

    print(f"   Found classes: {len(class_dirs)}\n")

    split_stats = defaultdict(lambda: defaultdict(int))

    for class_dir in tqdm(class_dirs, desc="Splitting classes"):
        class_name = class_dir.name
        images = sorted([
            f for f in class_dir.iterdir()
            if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}
        ])
        random.shuffle(images)

        n = len(images)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        # Remaining goes to test

        splits = {
            "train": images[:n_train],
            "val": images[n_train:n_train + n_val],
            "test": images[n_train + n_val:],
        }

        for split_name, split_images in splits.items():
            dest_dir = out_dir / split_name / class_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for img_path in split_images:
                dest = dest_dir / img_path.name
                if not dest.exists():
                    shutil.copy2(img_path, dest)
            split_stats[split_name][class_name] = len(split_images)

    # Summary
    print(f"\n{'='*55}")
    print(f"  ✅ Dataset split complete!")
    for split_name in ["train", "val", "test"]:
        total = sum(split_stats[split_name].values())
        print(f"  {split_name:<6}: {total:>6,} images  ({len(split_stats[split_name])} classes)")
    print(f"{'='*55}")

    # Save split stats
    stats_path = ROOT / "data" / "split_stats.json"
    with open(stats_path, "w") as f:
        json.dump({k: dict(v) for k, v in split_stats.items()}, f, indent=2)
    print(f"  Split stats: {stats_path}")

    return split_stats


def main():
    parser = argparse.ArgumentParser(description="Split PlantVillage dataset")
    parser.add_argument("--train", type=float, default=TRAIN_RATIO)
    parser.add_argument("--val", type=float, default=VAL_RATIO)
    parser.add_argument("--test", type=float, default=TEST_RATIO)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    split_dataset(
        raw_dir=RAW_DATA_DIR,
        out_dir=PROCESSED_DATA_DIR,
        train_ratio=args.train,
        val_ratio=args.val,
        test_ratio=args.test,
        seed=args.seed,
        classes_filter=CLASSES,
    )


if __name__ == "__main__":
    main()
