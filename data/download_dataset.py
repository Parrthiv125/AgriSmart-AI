"""
AgriSmart AI — Dataset Download from Hugging Face
====================================================
Downloads the PlantVillage dataset and organises it
into the expected folder structure.

Usage:
    python data/download_dataset.py

Requires: pip install huggingface-hub pillow tqdm
"""

import sys
import json
import zipfile
import shutil
import concurrent.futures
from pathlib import Path
from collections import defaultdict
import os

# Allow running from project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw" / "plantvillage"
STATS_FILE = ROOT / "data" / "dataset_stats.json"
HF_DATASET_ID = "mohanty/PlantVillage"

def extract_file(zip_path, member, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zf:
        with zf.open(member) as src:
            with open(extract_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)

def download_plantvillage():
    print(f"📥 Downloading PlantVillage from Hugging Face: {HF_DATASET_ID}")
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("❌ Missing: pip install huggingface-hub")
        sys.exit(1)

    print("Downloading data.zip (approx 2GB) if not cached...")
    zip_path = hf_hub_download(repo_id=HF_DATASET_ID, filename="data.zip", repo_type="dataset")
    print(f"✅ Downloaded/Found at: {zip_path}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    class_counts = defaultdict(int)
    corrupted = []

    print(f"\n💾 Extracting RGB images to {RAW_DIR} ...")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        color_files = [f for f in zf.namelist() if f.startswith('raw/color/') and not f.endswith('/')]
    
    tasks = []
    
    # Pre-create all directories
    for f in color_files:
        parts = f.split('/')
        if len(parts) >= 4:
            class_dir = RAW_DIR / parts[2]
            class_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"Starting parallel extraction of {len(color_files)} files...")
    
    import time
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count() * 4) as executor:
        for file_path in color_files:
            parts = file_path.split('/')
            if len(parts) < 4:
                continue
            class_name = parts[2]
            file_name = parts[-1]
            img_path = RAW_DIR / class_name / file_name
            
            if not img_path.exists():
                tasks.append(
                    (executor.submit(extract_file, zip_path, file_path, img_path), class_name, file_path)
                )
            else:
                class_counts[class_name] += 1
                
        for i, (future, class_name, file_path) in enumerate(tasks):
            try:
                future.result()
                class_counts[class_name] += 1
            except Exception as e:
                corrupted.append({"file": file_path, "class": class_name, "error": str(e)})
            
            if (i + 1) % 5000 == 0:
                print(f"Extracted {i + 1}/{len(tasks)} files...")

    print(f"Extraction took {time.time() - start_time:.1f} seconds")

    stats = {
        "source": HF_DATASET_ID,
        "total_images": sum(class_counts.values()),
        "total_classes": len(class_counts),
        "class_counts": dict(sorted(class_counts.items())),
        "corrupted": corrupted,
    }

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\n{'='*55}")
    print(f"  ✅ Extraction complete!")
    print(f"  Total images:  {stats['total_images']:,}")
    print(f"  Total classes: {stats['total_classes']}")
    print(f"  Corrupted:     {len(corrupted)}")
    print(f"  Saved to:      {RAW_DIR}")
    print(f"{'='*55}")

    return stats


if __name__ == "__main__":
    download_plantvillage()
