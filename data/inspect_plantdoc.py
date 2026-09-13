"""
AgriSmart AI -- PlantDoc Dataset Inspector
==========================================
Scans the downloaded PlantDoc dataset and reports:
  - Total images (train + test)
  - Images per class per split
  - Corrupt/unreadable files
  - Mapping coverage against AgriSmart 28-class system

Usage:
    python data/inspect_plantdoc.py

Run AFTER: python data/download_plantdoc.py
"""

import sys
import csv
import json
from pathlib import Path
from collections import defaultdict

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[!] Pillow not installed -- skipping image integrity checks")

ROOT_DIR = Path(__file__).resolve().parent.parent
PLANTDOC_RAW = ROOT_DIR / "data" / "raw" / "plantdoc"
MAPPING_CSV = ROOT_DIR / "data" / "plantdoc_class_mapping.csv"
STATS_OUT = ROOT_DIR / "data" / "plantdoc_inspection_stats.json"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_mapping() -> dict:
    mapping = {}
    if not MAPPING_CSV.exists():
        print(f"[!] Mapping CSV not found: {MAPPING_CSV}")
        return mapping
    with open(MAPPING_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["mapping_status"] == "MAPPED":
                mapping[row["plantdoc_folder"]] = row["agrismart_class"]
    return mapping


def inspect_split(split_dir: Path, mapping: dict) -> dict:
    result = {}
    if not split_dir.exists():
        return result

    for cls_dir in sorted(split_dir.iterdir()):
        if not cls_dir.is_dir():
            continue
        images = [f for f in cls_dir.iterdir() if f.suffix.lower() in IMG_EXTS]
        corrupted = []

        if PIL_AVAILABLE:
            for img_path in images:
                try:
                    with Image.open(img_path) as img:
                        img.verify()
                except Exception as e:
                    corrupted.append({"file": img_path.name, "error": str(e)})

        agrismart = mapping.get(cls_dir.name, "UNMAPPED")
        result[cls_dir.name] = {
            "count": len(images),
            "corrupted": len(corrupted),
            "corrupted_files": corrupted,
            "agrismart_class": agrismart,
        }
    return result


def inspect_plantdoc():
    print("=" * 70)
    print(" AGRISMART AI -- PlantDoc Dataset Inspection")
    print("=" * 70)
    print(f"Dataset root: {PLANTDOC_RAW}")
    print()

    if not PLANTDOC_RAW.exists():
        print("[ERROR] PlantDoc dataset not found. Run: python data/download_plantdoc.py")
        sys.exit(1)

    mapping = load_mapping()
    print(f"[OK] Loaded {len(mapping)} MAPPED class entries from {MAPPING_CSV.name}")
    print()

    stats = {}
    grand_total = 0
    grand_corrupt = 0
    unmapped_found = []

    for split in ["train", "test"]:
        split_dir = PLANTDOC_RAW / split
        split_stats = inspect_split(split_dir, mapping)
        stats[split] = split_stats

        split_total = sum(v["count"] for v in split_stats.values())
        split_corrupt = sum(v["corrupted"] for v in split_stats.values())
        grand_total += split_total
        grand_corrupt += split_corrupt

        unmapped = [k for k, v in split_stats.items() if v["agrismart_class"] == "UNMAPPED"]
        unmapped_found.extend([(split, k) for k in unmapped])

        print(f"{'='*70}")
        print(f" {split.upper()} SPLIT -- {len(split_stats)} classes, {split_total} images")
        print(f"{'='*70}")
        print(f"  {'PlantDoc Folder':<44} {'AgriSmart Class':<35} {'Imgs':>5} {'Corrupt':>7}")
        print(f"  {'-'*97}")
        for cls_name, info in split_stats.items():
            agrismart = info["agrismart_class"]
            if agrismart == "UNMAPPED":
                agrismart = "[!] UNMAPPED"
            print(
                f"  {cls_name:<44} {agrismart:<35} "
                f"{info['count']:>5} {info['corrupted']:>7}"
            )
        print(f"\n  Subtotal: {split_total} images, {split_corrupt} corrupted")
        print()

    # Summary
    print("=" * 70)
    print(" INSPECTION SUMMARY")
    print("=" * 70)
    print(f"  Total images:    {grand_total}")
    print(f"  Total corrupted: {grand_corrupt}")
    print(f"  Unmapped folders: {len(unmapped_found)}")
    if unmapped_found:
        for split, cls in unmapped_found:
            print(f"    [{split}] {cls}")

    # Coverage check
    all_agrismart = set(mapping.values())
    covered_in_test = set()
    if "test" in stats:
        for info in stats["test"].values():
            if info["agrismart_class"] != "UNMAPPED":
                covered_in_test.add(info["agrismart_class"])

    print(f"\n  AgriSmart classes covered in PlantDoc test: {len(covered_in_test)}/28")

    classes_json = ROOT_DIR / "models" / "classes.json"
    if classes_json.exists():
        with open(classes_json) as f:
            all_28 = set(json.load(f).values())
        not_covered = sorted(all_28 - covered_in_test)
        if not_covered:
            print(f"\n  AgriSmart classes NOT represented in PlantDoc test:")
            for c in not_covered:
                print(f"    - {c}")

    # Save
    output = {
        "grand_total_images": grand_total,
        "grand_total_corrupted": grand_corrupt,
        "unmapped_folders": [{"split": s, "folder": f} for s, f in unmapped_found],
        "agrismart_classes_covered_in_test": len(covered_in_test),
        "splits": stats,
    }
    with open(STATS_OUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n[OK] Saved inspection report: {STATS_OUT}")

    if grand_corrupt == 0 and len(unmapped_found) == 0:
        print("\n[PASS] PlantDoc inspection PASSED -- 0 corrupt files, 0 unmapped folders.")
    else:
        print("\n[WARN] Inspection completed with warnings. Review above.")

    return output


if __name__ == "__main__":
    inspect_plantdoc()
