"""
AgriSmart AI — Dataset Inspector
==================================
READ-ONLY inspection of the downloaded PlantVillage dataset.

Reports:
  - Total image count
  - Class names and per-class image counts
  - Min / max / mean images per class
  - Unreadable / corrupt image detection
  - Empty class directories
  - Dataset directory structure

Does NOT modify any files.
Does NOT train anything.
Does NOT split or move files.

Usage:
    python data/inspect_dataset.py
    python data/inspect_dataset.py --dir data/raw/plantvillage
    python data/inspect_dataset.py --dir data/processed/train
"""

import sys
import argparse
import json
from pathlib import Path
from collections import defaultdict

from PIL import Image
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from training.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def inspect_directory(data_dir: Path, verify_images: bool = True) -> dict:
    """
    Inspect a dataset directory (one level of class subdirectories).

    Args:
        data_dir: path to directory containing class subdirectories
        verify_images: if True, attempt to open each image to detect corruption

    Returns:
        dict with full inspection report
    """
    if not data_dir.exists():
        return {
            "error": f"Directory does not exist: {data_dir}",
            "path": str(data_dir),
        }

    # Discover class directories
    class_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()])

    if not class_dirs:
        return {
            "error": "No class subdirectories found.",
            "path": str(data_dir),
            "tip": "Expected structure: data_dir/ClassName/image.jpg",
        }

    class_counts = {}
    empty_classes = []
    corrupt_images = []
    unreadable_images = []
    total_images = 0

    for class_dir in tqdm(class_dirs, desc="Inspecting classes"):
        class_name = class_dir.name

        # Collect all image files (case-insensitive extension match)
        image_files = [
            f for f in class_dir.iterdir()
            if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
        ]

        # Count non-image files
        non_image_files = [
            f for f in class_dir.iterdir()
            if f.is_file() and f.suffix.lower() not in IMAGE_EXTENSIONS
        ]

        if len(image_files) == 0:
            empty_classes.append(class_name)
            class_counts[class_name] = 0
            continue

        class_counts[class_name] = len(image_files)
        total_images += len(image_files)

        if verify_images:
            for img_path in image_files:
                try:
                    with Image.open(img_path) as img:
                        img.verify()  # verify header — does not decode full image
                except Exception as e:
                    corrupt_images.append({
                        "path": str(img_path),
                        "error": str(e),
                    })

    # Statistics
    counts = list(class_counts.values())
    non_empty_counts = [c for c in counts if c > 0]

    stats = {
        "total_classes": len(class_dirs),
        "non_empty_classes": len(non_empty_counts),
        "empty_classes": empty_classes,
        "total_images": total_images,
        "corrupt_images_count": len(corrupt_images),
        "corrupt_images": corrupt_images,
    }

    if non_empty_counts:
        stats["min_images_per_class"] = min(non_empty_counts)
        stats["max_images_per_class"] = max(non_empty_counts)
        stats["mean_images_per_class"] = round(sum(non_empty_counts) / len(non_empty_counts), 1)
        stats["median_images_per_class"] = sorted(non_empty_counts)[len(non_empty_counts) // 2]

    stats["class_counts"] = class_counts
    return stats


def print_report(stats: dict, data_dir: Path):
    """Pretty-print inspection report to stdout."""
    print("\n" + "=" * 65)
    print("  AgriSmart AI — Dataset Inspection Report")
    print("=" * 65)
    print(f"  Directory: {data_dir}")

    if "error" in stats:
        print(f"\n  ❌ ERROR: {stats['error']}")
        if "tip" in stats:
            print(f"     {stats['tip']}")
        print("=" * 65)
        return

    print(f"\n  📊 Summary")
    print(f"  {'Total classes:':<35} {stats['total_classes']}")
    print(f"  {'Non-empty classes:':<35} {stats['non_empty_classes']}")
    print(f"  {'Total images:':<35} {stats['total_images']:,}")

    if stats.get("min_images_per_class") is not None:
        print(f"  {'Min images per class:':<35} {stats['min_images_per_class']}")
        print(f"  {'Max images per class:':<35} {stats['max_images_per_class']}")
        print(f"  {'Mean images per class:':<35} {stats['mean_images_per_class']}")
        print(f"  {'Median images per class:':<35} {stats['median_images_per_class']}")

    # Empty class directories
    if stats["empty_classes"]:
        print(f"\n  ⚠️  Empty class directories ({len(stats['empty_classes'])}):")
        for name in stats["empty_classes"]:
            print(f"     - {name}")
    else:
        print(f"\n  ✅ No empty class directories.")

    # Corrupt images
    if stats["corrupt_images_count"] > 0:
        print(f"\n  ❌ Corrupt/unreadable images ({stats['corrupt_images_count']}):")
        for item in stats["corrupt_images"][:20]:  # show first 20
            print(f"     {item['path']}")
            print(f"       Error: {item['error']}")
        if stats["corrupt_images_count"] > 20:
            print(f"     ... and {stats['corrupt_images_count'] - 20} more.")
    else:
        print(f"  ✅ No corrupt images detected.")

    # Per-class breakdown
    print(f"\n  📋 Per-class image counts:")
    print(f"  {'Class Name':<50} {'Images':>8}")
    print("  " + "-" * 60)

    class_counts = stats.get("class_counts", {})
    for class_name, count in sorted(class_counts.items()):
        marker = "⚠️ " if count == 0 else "   "
        print(f"  {marker}{class_name:<48} {count:>8,}")

    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="AgriSmart AI — Read-only dataset inspection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data/inspect_dataset.py
  python data/inspect_dataset.py --dir data/raw/plantvillage
  python data/inspect_dataset.py --dir data/processed/train --no-verify
  python data/inspect_dataset.py --save-json data/dataset_inspection.json
        """
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=str(RAW_DATA_DIR),
        help=f"Directory to inspect (default: {RAW_DATA_DIR})"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip image corruption verification (faster)"
    )
    parser.add_argument(
        "--save-json",
        type=str,
        default=None,
        help="Optional path to save inspection results as JSON"
    )
    args = parser.parse_args()

    data_dir = Path(args.dir)
    verify = not args.no_verify

    print(f"\n🔍 Inspecting: {data_dir}")
    if not verify:
        print("   (skipping image corruption check)")

    stats = inspect_directory(data_dir, verify_images=verify)
    print_report(stats, data_dir)

    # Optionally inspect all splits if raw doesn't exist but processed does
    if "error" in stats and data_dir == RAW_DATA_DIR and PROCESSED_DATA_DIR.exists():
        print(f"\n💡 Raw data not found. Checking processed splits instead...\n")
        for split in ["train", "val", "test"]:
            split_dir = PROCESSED_DATA_DIR / split
            if split_dir.exists():
                print(f"\n{'─'*65}")
                print(f"  Split: {split}")
                split_stats = inspect_directory(split_dir, verify_images=False)
                print_report(split_stats, split_dir)

    # Save JSON if requested
    if args.save_json and "error" not in stats:
        save_path = Path(args.save_json)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        # Remove full corrupt list for cleaner JSON (keep count only)
        json_stats = {k: v for k, v in stats.items() if k != "corrupt_images"}
        json_stats["corrupt_image_paths"] = [
            item["path"] for item in stats.get("corrupt_images", [])
        ]
        with open(save_path, "w") as f:
            json.dump(json_stats, f, indent=2)
        print(f"\n💾 Inspection results saved: {save_path}")


if __name__ == "__main__":
    main()
