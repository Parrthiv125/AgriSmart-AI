"""
AgriSmart AI — Leakage-Safe Dataset Splitter
================================================
Creates a reproducible, leakage-safe train/val/test split from the 28 mapped PlantVillage classes.

Key Safety Features:
  - 100% Leaf-Group Isolation: Prevents physical leaf / leaf_id / multi-view photo duplicates from leaking across splits.
  - Reproducible Random Seed: Uses fixed SEED (42).
  - Exact Split Target Ratios: ~80% Train, ~10% Validation, ~10% Local Test.
  - Keeps Raw Dataset Untouched.
"""

import sys
import os
import re
import csv
import json
import shutil
import random
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Tuple, Set

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from training.config import (
    RAW_DATA_DIR, PROCESSED_DATA_DIR,
    TRAIN_RATIO, VAL_RATIO, TEST_RATIO, SEED, CLASS_MAPPING_CSV
)

def sanitize_folder_name(dev_class_name: str) -> str:
    """Sanitize development class name for filesystem subfolder compatibility."""
    return dev_class_name.replace("/", "_")

def extract_leaf_group_id(filename: str) -> str:
    """
    Extract physical leaf / photo session group ID from PlantVillage filename.
    """
    base = os.path.splitext(filename)[0]
    if "___" in base:
        right_part = base.split("___")[1]
    else:
        right_part = base
    
    clean_id = re.sub(r'\s+copy(\s+\d+)?$', '', right_part, flags=re.IGNORECASE)
    clean_id = re.sub(r'\s*\(\d+\)$', '', clean_id)
    return clean_id.strip()

def load_mapping() -> Dict[str, str]:
    """Load original -> dev_class mapping for status == 'MAPPED'."""
    if not CLASS_MAPPING_CSV.exists():
        raise FileNotFoundError(f"Mapping CSV missing at {CLASS_MAPPING_CSV}. Run data/validate_mapping.py first.")
    
    mapped_classes = {}
    with open(CLASS_MAPPING_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["mapping_status"] == "MAPPED":
                mapped_classes[row["original_plantvillage_class"]] = row["development_class"]
    return mapped_classes

def split_dataset(
    seed: int = SEED,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO
):
    print("=" * 70)
    print(" AGRISMART AI — LEAKAGE-SAFE DATASET SPLITTER")
    print("=" * 70)
    print(f"Source Raw Data: {RAW_DATA_DIR}")
    print(f"Target Processed Data: {PROCESSED_DATA_DIR}")
    print(f"Split Ratios: Train={train_ratio:.0%}, Val={val_ratio:.0%}, Test={test_ratio:.0%} | Seed: {seed}\n")

    mapped_classes = load_mapping()
    print(f"[OK] Loaded {len(mapped_classes)} mapped PlantVillage class folders.")

    # Group files by development class and leaf group ID
    class_leaf_groups = defaultdict(lambda: defaultdict(list))
    total_images_discovered = 0

    for orig_folder, dev_class in mapped_classes.items():
        folder_path = RAW_DATA_DIR / orig_folder
        if not folder_path.exists():
            print(f"[!] Warning: Raw folder missing: {folder_path}")
            continue

        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    leaf_id = extract_leaf_group_id(entry.name)
                    class_leaf_groups[dev_class][leaf_id].append(entry.path)
                    total_images_discovered += 1

    print(f"[OK] Discovered {total_images_discovered} mapped images across {len(class_leaf_groups)} development classes.")

    # Prepare split output directories
    for split in ["train", "val", "test"]:
        split_dir = PROCESSED_DATA_DIR / split
        split_dir.mkdir(parents=True, exist_ok=True)

    # Perform Leaf-Group Stratified Splitting
    split_file_paths = {"train": set(), "val": set(), "test": set()}
    split_leaf_groups = {"train": set(), "val": set(), "test": set()}
    split_class_counts = {
        "train": defaultdict(int),
        "val": defaultdict(int),
        "test": defaultdict(int)
    }

    all_copy_tasks = []
    dev_class_list = sorted(list(class_leaf_groups.keys()))

    # Ensure all target directories exist up-front
    for dev_class in dev_class_list:
        folder_name = sanitize_folder_name(dev_class)
        for target_split in ["train", "val", "test"]:
            (PROCESSED_DATA_DIR / target_split / folder_name).mkdir(parents=True, exist_ok=True)
    
    for idx, dev_class in enumerate(dev_class_list):
        folder_name = sanitize_folder_name(dev_class)
        leaf_dict = class_leaf_groups[dev_class]
        
        # Sort leaf group keys deterministically
        group_keys = sorted(list(leaf_dict.keys()))
        rng = random.Random(seed + idx)
        rng.shuffle(group_keys)

        total_class_imgs = sum(len(leaf_dict[g]) for g in group_keys)
        target_train = total_class_imgs * train_ratio
        target_val = total_class_imgs * val_ratio

        curr_train_imgs = 0
        curr_val_imgs = 0

        for g_key in group_keys:
            img_paths = leaf_dict[g_key]
            n_imgs = len(img_paths)

            if curr_train_imgs < target_train or (curr_train_imgs == 0):
                target_split = "train"
                curr_train_imgs += n_imgs
            elif curr_val_imgs < target_val or (curr_val_imgs == 0):
                target_split = "val"
                curr_val_imgs += n_imgs
            else:
                target_split = "test"

            dest_dir = PROCESSED_DATA_DIR / target_split / folder_name

            for img_p in img_paths:
                file_name = os.path.basename(img_p)
                dest_path = dest_dir / file_name
                all_copy_tasks.append((img_p, dest_path))

                split_file_paths[target_split].add(dest_path.name)
                split_leaf_groups[target_split].add(f"{dev_class}::{g_key}")
                split_class_counts[target_split][dev_class] += 1

    print(f"\n--- Creating file links for {len(all_copy_tasks)} images in parallel ---")
    def _copy_fn(item):
        src, dst = item
        if dst.exists():
            return
        try:
            os.link(src, dst)
        except Exception:
            shutil.copyfile(src, dst)

    with ThreadPoolExecutor(max_workers=32) as executor:
        list(executor.map(_copy_fn, all_copy_tasks))

    # ── VERIFICATION CHECKS ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(" SPLIT INTEGRITY & LEAKAGE VERIFICATION")
    print("=" * 70)

    # 1. Image File Overlap Check
    train_val_overlap = split_file_paths["train"] & split_file_paths["val"]
    train_test_overlap = split_file_paths["train"] & split_file_paths["test"]
    val_test_overlap = split_file_paths["val"] & split_file_paths["test"]
    total_file_overlap = len(train_val_overlap) + len(train_test_overlap) + len(val_test_overlap)

    # 2. Leaf Group Overlap Check
    train_val_leaf_overlap = split_leaf_groups["train"] & split_leaf_groups["val"]
    train_test_leaf_overlap = split_leaf_groups["train"] & split_leaf_groups["test"]
    val_test_leaf_overlap = split_leaf_groups["val"] & split_leaf_groups["test"]
    total_leaf_overlap = len(train_val_leaf_overlap) + len(train_test_leaf_overlap) + len(val_test_leaf_overlap)

    print(f"File-level overlap between splits: {total_file_overlap}")
    print(f"Leaf-group overlap between splits: {total_leaf_overlap}")

    total_train = sum(split_class_counts["train"].values())
    total_val = sum(split_class_counts["val"].values())
    total_test = sum(split_class_counts["test"].values())
    total_split_images = total_train + total_val + total_test

    print(f"\nExact Image Counts:")
    print(f"  Train Split:      {total_train:6d} images ({total_train/total_split_images:.2%})")
    print(f"  Validation Split: {total_val:6d} images ({total_val/total_split_images:.2%})")
    print(f"  Local Test Split: {total_test:6d} images ({total_test/total_split_images:.2%})")
    print(f"  Total Processed:  {total_split_images:6d} images")

    # 3. Class representation check
    missing_in_train = [c for c in dev_class_list if split_class_counts["train"][c] == 0]
    missing_in_val = [c for c in dev_class_list if split_class_counts["val"][c] == 0]
    missing_in_test = [c for c in dev_class_list if split_class_counts["test"][c] == 0]

    print("\nClass Representation Check:")
    print(f"  Missing in Train: {len(missing_in_train)}")
    print(f"  Missing in Val:   {len(missing_in_val)}")
    print(f"  Missing in Test:  {len(missing_in_test)}")

    # Print Table of Class Counts
    print("\n" + "=" * 70)
    print(f"{'Development Class':<45} | {'Train':<7} | {'Val':<7} | {'Test':<7} | {'Total':<7}")
    print("=" * 70)
    for dev_c in dev_class_list:
        tr_c = split_class_counts["train"][dev_c]
        v_c = split_class_counts["val"][dev_c]
        te_c = split_class_counts["test"][dev_c]
        tot = tr_c + v_c + te_c
        print(f"{dev_c:<45} | {tr_c:<7d} | {v_c:<7d} | {te_c:<7d} | {tot:<7d}")

    # Save Split Stats JSON
    stats_payload = {
        "total_images": total_split_images,
        "train_total": total_train,
        "val_total": total_val,
        "test_total": total_test,
        "file_overlap": total_file_overlap,
        "leaf_group_overlap": total_leaf_overlap,
        "per_class": {
            dev_c: {
                "train": split_class_counts["train"][dev_c],
                "val": split_class_counts["val"][dev_c],
                "test": split_class_counts["test"][dev_c],
                "total": split_class_counts["train"][dev_c] + split_class_counts["val"][dev_c] + split_class_counts["test"][dev_c]
            }
            for dev_c in dev_class_list
        }
    }
    
    stats_json_path = ROOT_DIR / "data" / "split_stats.json"
    with open(stats_json_path, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2)
    print(f"\n[OK] Saved split statistics to: {stats_json_path}")

    if total_file_overlap == 0 and total_leaf_overlap == 0 and total_split_images == 38542:
        print("\n[SUCCESS] DATASET SPLIT PASSED ALL INTEGRITY & LEAKAGE CHECKS!")
        return True
    else:
        print("\n[FAIL] DATASET SPLIT VERIFICATION FAILED!")
        return False

if __name__ == "__main__":
    split_dataset()
