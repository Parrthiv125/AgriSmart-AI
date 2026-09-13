"""
AgriSmart AI -- PlantDoc Dataset Preparation
============================================
Organises the raw PlantDoc dataset into AgriSmart-named class folders
for evaluation against the existing 28-class baseline model.

Output structure:
    data/plantdoc/
    +-- train/           <- Future domain-adaptation use (DO NOT USE in Phase 1)
    |   +-- <AgriSmart sanitized class name>/
    +-- test/            <- EVALUATION ONLY against baseline model
        +-- <AgriSmart sanitized class name>/

Key rules:
  - Preserves PlantDoc's original train/test split.
  - Applies explicit 27-folder -> 28-class mapping from plantdoc_class_mapping.csv.
  - Uses hardlinks where possible; falls back to copyfile.
  - NEVER touches data/processed/ (PlantVillage splits).
  - Saves data/plantdoc_split_stats.json with image counts.

Usage:
    python data/prepare_plantdoc.py
"""

import sys
import csv
import json
import os
import shutil
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).resolve().parent.parent
PLANTDOC_RAW = ROOT_DIR / "data" / "raw" / "plantdoc"
PLANTDOC_OUT = ROOT_DIR / "data" / "plantdoc"
MAPPING_CSV = ROOT_DIR / "data" / "plantdoc_class_mapping.csv"
STATS_OUT = ROOT_DIR / "data" / "plantdoc_split_stats.json"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"   # PlantVillage splits -- never touch

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sanitize_folder_name(dev_class_name: str) -> str:
    """Match the sanitization used in split_dataset.py."""
    return dev_class_name.replace("/", "_")


def load_mapping() -> dict:
    mapping = {}
    with open(MAPPING_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["mapping_status"] == "MAPPED":
                mapping[row["plantdoc_folder"]] = row["agrismart_class"]
    return mapping


def copy_or_link(src: Path, dst: Path):
    if dst.exists():
        return
    try:
        os.link(src, dst)
    except Exception:
        shutil.copyfile(src, dst)


def prepare_split(
    split_name: str,
    mapping: dict,
    counts: dict,
) -> list:
    """Prepare one split (train or test). Returns list of copy tasks."""
    src_split = PLANTDOC_RAW / split_name
    dst_split = PLANTDOC_OUT / split_name

    if not src_split.exists():
        print(f"  [!] Source split not found: {src_split}")
        return []

    # Pre-create output class directories
    for agrismart_class in set(mapping.values()):
        folder_name = sanitize_folder_name(agrismart_class)
        (dst_split / folder_name).mkdir(parents=True, exist_ok=True)

    tasks = []
    for cls_dir in sorted(src_split.iterdir()):
        if not cls_dir.is_dir():
            continue

        if cls_dir.name not in mapping:
            print(f"  [!] UNMAPPED folder in {split_name}: '{cls_dir.name}' -- SKIPPED")
            continue

        agrismart_class = mapping[cls_dir.name]
        folder_name = sanitize_folder_name(agrismart_class)
        dst_dir = dst_split / folder_name

        images = [f for f in cls_dir.iterdir() if f.suffix.lower() in IMG_EXTS]
        for img in images:
            dst_path = dst_dir / img.name
            tasks.append((img, dst_path))
            counts[split_name][agrismart_class] += 1

    return tasks


def prepare_plantdoc():
    print("=" * 70)
    print(" AGRISMART AI -- PlantDoc Dataset Preparation")
    print("=" * 70)
    print(f"Source:  {PLANTDOC_RAW}")
    print(f"Output:  {PLANTDOC_OUT}")
    print(f"IMPORTANT: data/processed/ (PlantVillage) is NOT touched.")
    print()

    if not PLANTDOC_RAW.exists():
        print("[ERROR] PlantDoc raw data not found. Run: python data/download_plantdoc.py")
        sys.exit(1)

    mapping = load_mapping()
    print(f"[OK] Loaded {len(mapping)} MAPPED class entries.")

    PLANTDOC_OUT.mkdir(parents=True, exist_ok=True)
    counts = defaultdict(lambda: defaultdict(int))
    all_tasks = []

    for split in ["train", "test"]:
        print(f"\nProcessing split: {split.upper()}")
        tasks = prepare_split(split, mapping, counts)
        all_tasks.extend(tasks)
        print(f"  Queued {len(tasks)} file operations for {split}")

    # Execute file copies
    print(f"\nCopying {len(all_tasks)} files (parallel)...")
    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(lambda t: copy_or_link(*t), all_tasks))
    print("[OK] File operations complete.")

    # Verification
    print()
    print("=" * 70)
    print(" VERIFICATION")
    print("=" * 70)

    # 1. Verify no overlap with PlantVillage processed dirs
    pv_files = set()
    if PROCESSED_DIR.exists():
        for split in ["train", "val", "test"]:
            split_dir = PROCESSED_DIR / split
            if split_dir.exists():
                for cls in split_dir.iterdir():
                    if cls.is_dir():
                        for img in cls.iterdir():
                            if img.is_file():
                                pv_files.add(img.name)

    plantdoc_files = set()
    for split in ["train", "test"]:
        split_dir = PLANTDOC_OUT / split
        if split_dir.exists():
            for cls in split_dir.iterdir():
                if cls.is_dir():
                    for img in cls.iterdir():
                        if img.is_file():
                            plantdoc_files.add(img.name)

    overlap = pv_files & plantdoc_files
    print(f"  Filename overlap with PlantVillage processed/: {len(overlap)}")
    if overlap:
        print(f"  [!] WARNING: overlap detected: {list(overlap)[:5]}")

    # 2. Class counts per split
    print()
    for split in ["train", "test"]:
        total = sum(counts[split].values())
        print(f"  {split.upper()} split: {total} images across {len(counts[split])} classes")

    # 3. Full class breakdown
    all_agrismart_classes = sorted(set(mapping.values()))
    print()
    print(f"  {'AgriSmart Class':<45} {'Train':>6} {'Test':>6}")
    print(f"  {'-'*60}")
    for cls in all_agrismart_classes:
        tr = counts["train"].get(cls, 0)
        te = counts["test"].get(cls, 0)
        print(f"  {cls:<45} {tr:>6} {te:>6}")

    # Save stats
    stats_payload = {
        "source": "https://github.com/pratikkayal/PlantDoc-Dataset",
        "license": "CC-BY-4.0",
        "mapping_file": "data/plantdoc_class_mapping.csv",
        "output_dir": str(PLANTDOC_OUT.relative_to(ROOT_DIR)),
        "evaluation_note": (
            "data/plantdoc/test/ is the HELD-OUT external evaluation set for "
            "field-generalization testing of the AgriSmart baseline model. "
            "data/plantdoc/train/ is NOT used for training in Phase 1."
        ),
        "mapping_assumption": (
            "Corn leaf blight -> Corn -- Northern Leaf Blight: "
            "NLB is the dominant corn blight in PlantDoc images. "
            "Documented as evaluation mapping assumption."
        ),
        "splits": {
            split: {
                "total": sum(counts[split].values()),
                "per_class": dict(counts[split]),
            }
            for split in ["train", "test"]
        },
    }

    with open(STATS_OUT, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2)
    print(f"\n[OK] Saved split stats: {STATS_OUT}")

    if overlap:
        print("\n[WARN] Filename overlap detected (see above).")
    else:
        print("\n[PASS] PlantDoc preparation PASSED -- 0 overlap with PlantVillage splits.")

    return stats_payload


if __name__ == "__main__":
    prepare_plantdoc()
