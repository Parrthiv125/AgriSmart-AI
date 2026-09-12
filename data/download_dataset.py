"""
AgriSmart AI — Dataset Download from Hugging Face
====================================================
Downloads the PlantVillage dataset and organises it
into the expected folder structure.

Usage:
    python data/download_dataset.py

Requires: pip install datasets huggingface-hub
"""

import sys
import json
import shutil
from pathlib import Path
from collections import defaultdict

from tqdm import tqdm
from PIL import Image

# Allow running from project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


RAW_DIR = ROOT / "data" / "raw" / "plantvillage"
STATS_FILE = ROOT / "data" / "dataset_stats.json"

HF_DATASET_ID = "mohanty/PlantVillage"


def download_plantvillage():
    print(f"📥 Downloading PlantVillage from Hugging Face: {HF_DATASET_ID}")
    print("   This may take several minutes on first run...\n")

    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ Missing: pip install datasets huggingface-hub")
        sys.exit(1)

    dataset = load_dataset(HF_DATASET_ID, trust_remote_code=True)
    print(f"✅ Dataset loaded. Splits: {list(dataset.keys())}")

    # Use 'train' split (PlantVillage on HF uses 'train')
    split = "train"
    data = dataset[split]
    print(f"   Total samples: {len(data)}")

    # Inspect columns
    print(f"   Columns: {data.column_names}")

    # Save images to disk
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    class_counts = defaultdict(int)
    corrupted = []

    print(f"\n💾 Saving images to {RAW_DIR} ...")
    for idx, sample in enumerate(tqdm(data, desc="Saving")):
        # Hugging Face PlantVillage: sample has 'image' (PIL) and 'label' (int or str)
        image = sample.get("image") or sample.get("img")
        label = sample.get("label")

        if image is None or label is None:
            continue

        # Get class name
        if hasattr(data.features["label"], "names"):
            class_name = data.features["label"].names[label]
        else:
            class_name = str(label)

        # Create class directory
        class_dir = RAW_DIR / class_name
        class_dir.mkdir(exist_ok=True)

        # Save image
        img_path = class_dir / f"{idx:06d}.jpg"
        try:
            if not img_path.exists():
                if isinstance(image, Image.Image):
                    image.convert("RGB").save(img_path, "JPEG", quality=95)
                else:
                    # bytes
                    with open(img_path, "wb") as f:
                        f.write(image)
            class_counts[class_name] += 1
        except Exception as e:
            corrupted.append({"idx": idx, "class": class_name, "error": str(e)})

    # Save stats
    stats = {
        "source": HF_DATASET_ID,
        "total_images": sum(class_counts.values()),
        "total_classes": len(class_counts),
        "class_counts": dict(sorted(class_counts.items())),
        "corrupted": corrupted,
    }

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print(f"\n{'='*55}")
    print(f"  ✅ Download complete!")
    print(f"  Total images:  {stats['total_images']:,}")
    print(f"  Total classes: {stats['total_classes']}")
    print(f"  Corrupted:     {len(corrupted)}")
    print(f"  Saved to:      {RAW_DIR}")
    print(f"  Stats:         {STATS_FILE}")
    print(f"{'='*55}")
    print("\nPer-class counts:")
    for cls, count in sorted(class_counts.items(), key=lambda x: x[0]):
        print(f"  {cls:<50} {count:>5} images")

    return stats


if __name__ == "__main__":
    download_plantvillage()
