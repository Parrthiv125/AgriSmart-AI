"""
AgriSmart AI — Fast Dataset Download & Extraction from Hugging Face
=====================================================================
Downloads the PlantVillage dataset from Hugging Face (mohanty/PlantVillage)
and uses fast system-level extraction (unzip) to extract ONLY raw/color images.

Guarantees:
  - Idempotent: Skips download/extraction if valid dataset exists.
  - Fast system-level extraction via system `unzip` (fallback to ZipFile).
  - Automatically detects RGB images at data/raw/plantvillage/raw/color/.
  - Excludes grayscale and segmented image sets.

Usage:
    python data/download_dataset.py
"""

import sys
import os
import json
import shutil
import subprocess
import zipfile
import time
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw" / "plantvillage"
STATS_FILE = ROOT / "data" / "dataset_stats.json"
HF_DATASET_ID = "mohanty/PlantVillage"
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_existing_rgb_dir(raw_dir: Path) -> Path:
    """Check if a valid RGB dataset is already extracted."""
    candidates = [
        raw_dir / "raw" / "color",
        raw_dir / "color",
        raw_dir / "PlantVillage" / "color",
        raw_dir,
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            subdirs = [d for d in candidate.iterdir() if d.is_dir()]
            if len(subdirs) >= 28:
                img_count = sum(
                    1 for d in subdirs for f in d.iterdir()
                    if f.is_file() and f.suffix.lower() in IMG_EXTS
                )
                if img_count >= 30000:
                    return candidate
    return None


def extract_with_system_unzip(zip_path: Path, target_dir: Path) -> bool:
    """Fast system-level unzip extraction of raw/color/ subset."""
    unzip_bin = shutil.which("unzip")
    if not unzip_bin:
        return False

    print(f"⚡ Using fast system-level '{unzip_bin}' for extraction...")
    target_dir.mkdir(parents=True, exist_ok=True)
    cmd = [unzip_bin, "-q", "-o", str(zip_path), "raw/color/*", "-d", str(target_dir)]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception as e:
        print(f"[!] System unzip failed ({e}), falling back to Python zipfile...")
        return False


def extract_with_python_zipfile(zip_path: Path, target_dir: Path):
    """Fallback Python extraction for raw/color/ subset."""
    print("📦 Extracting raw/color/ subset with Python ZipFile...")
    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        color_members = [
            m for m in zf.namelist()
            if m.startswith("raw/color/") and not m.endswith("/")
        ]
        zf.extractall(path=target_dir, members=color_members)


def download_plantvillage():
    print("=" * 70)
    print(" AGRISMART AI — PLANTVILLAGE DATASET DOWNLOAD")
    print("=" * 70)

    # 1. Idempotency Check
    existing_dir = find_existing_rgb_dir(RAW_DIR)
    if existing_dir:
        img_count = sum(
            1 for d in existing_dir.iterdir() if d.is_dir()
            for f in d.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS
        )
        print(f"[OK] Valid RGB dataset already present at: {existing_dir}")
        print(f"     Subdirectories: {len(list(existing_dir.iterdir()))} | Total RGB images: {img_count}")
        print("[SKIP] Download and extraction skipped.")
        return {
            "source": HF_DATASET_ID,
            "status": "already_present",
            "active_rgb_dir": str(existing_dir.relative_to(ROOT)),
            "total_images": img_count,
        }

    # 2. Download from Hugging Face
    print(f"📥 Downloading PlantVillage from Hugging Face: {HF_DATASET_ID}")
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("[ERROR] Missing dependency: pip install huggingface-hub")
        sys.exit(1)

    print("Downloading data.zip (approx 2GB) if not cached...")
    zip_path = hf_hub_download(repo_id=HF_DATASET_ID, filename="data.zip", repo_type="dataset")
    print(f"[OK] Downloaded / Cached at: {zip_path}")

    # 3. Extraction
    t0 = time.time()
    extracted = extract_with_system_unzip(Path(zip_path), RAW_DIR)
    if not extracted:
        extract_with_python_zipfile(Path(zip_path), RAW_DIR)
    elapsed = time.time() - t0
    print(f"[OK] Extraction completed in {elapsed:.1f} seconds.")

    # 4. Verify Extracted RGB Directory
    rgb_dir = find_existing_rgb_dir(RAW_DIR) or (RAW_DIR / "raw" / "color")
    class_counts = defaultdict(int)
    if rgb_dir.exists():
        for cls_dir in rgb_dir.iterdir():
            if cls_dir.is_dir():
                c = sum(1 for f in cls_dir.iterdir() if f.is_file() and f.suffix.lower() in IMG_EXTS)
                class_counts[cls_dir.name] = c

    total_images = sum(class_counts.values())
    stats = {
        "source": HF_DATASET_ID,
        "active_rgb_dir": str(rgb_dir.relative_to(ROOT)) if rgb_dir.exists() else str(RAW_DIR.relative_to(ROOT)),
        "total_images": total_images,
        "total_classes": len(class_counts),
        "class_counts": dict(sorted(class_counts.items())),
    }

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print("\n" + "=" * 70)
    print(" EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"  Active RGB Directory: {stats['active_rgb_dir']}")
    print(f"  Total RGB Images:     {stats['total_images']:,}")
    print(f"  Total Classes:        {stats['total_classes']}")
    print(f"  Stats Saved:          {STATS_FILE}")
    print("=" * 70)

    return stats


if __name__ == "__main__":
    download_plantvillage()
