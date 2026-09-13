"""
AgriSmart AI -- PlantDoc Dataset Download
==========================================
Downloads the PlantDoc dataset via GitHub ZIP archive.

NOTE: git clone fails on Windows because PlantDoc contains a filename with
a '?' character ('IMG_1629.JPG?1507122477.jpg'), which is illegal on NTFS.
The ZIP download approach handles this by sanitizing filenames on extraction.

Source: https://github.com/pratikkayal/PlantDoc-Dataset
License: Creative Commons Attribution 4.0 International (CC-BY-4.0)

Usage:
    python data/download_plantdoc.py

Requirements: requests (pip install requests)
"""

import sys
import io
import re
import os
import shutil
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PLANTDOC_RAW = ROOT_DIR / "data" / "raw" / "plantdoc"
PLANTDOC_ZIP_URL = (
    "https://github.com/pratikkayal/PlantDoc-Dataset/archive/refs/heads/master.zip"
)

EXPECTED_TRAIN_CLASSES = [
    "Apple Scab Leaf", "Apple leaf", "Apple rust leaf",
    "Bell_pepper leaf spot", "Bell_pepper leaf",
    "Blueberry leaf", "Cherry leaf",
    "Corn Gray leaf spot", "Corn leaf blight", "Corn rust leaf",
    "Peach leaf", "Potato leaf early blight", "Potato leaf late blight",
    "Raspberry leaf", "Soyabean leaf", "Squash Powdery mildew leaf",
    "Strawberry leaf",
    "Tomato Early blight leaf", "Tomato Septoria leaf spot",
    "Tomato leaf bacterial spot", "Tomato leaf late blight",
    "Tomato leaf mosaic virus", "Tomato leaf yellow virus",
    "Tomato leaf", "Tomato mold leaf",
    "Tomato two spotted spider mites leaf",
    "grape leaf black rot", "grape leaf",
]

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename for Windows NTFS compatibility.
    Strips query-string artifacts (e.g. '?1507122477') that appear in some
    PlantDoc filenames because images were scraped from the web.
    """
    # Remove anything from '?' onward (web query strings embedded in filenames)
    name = re.sub(r'\?.*$', '', name)
    # Replace any remaining illegal Windows characters just in case
    for ch in r'\/:*"<>|':
        name = name.replace(ch, '_')
    return name.strip()


def download_via_zip() -> bool:
    """Download PlantDoc ZIP from GitHub and extract with filename sanitization."""
    try:
        import requests
    except ImportError:
        print("[ERROR] 'requests' not installed. Run: pip install requests")
        return False

    tmp_zip = ROOT_DIR / "data" / "plantdoc_master.zip"
    tmp_extract = ROOT_DIR / "data" / "plantdoc_tmp_extract"

    # -- Download --
    print(f"[INFO] Downloading: {PLANTDOC_ZIP_URL}")
    try:
        with requests.get(PLANTDOC_ZIP_URL, stream=True, timeout=300) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(tmp_zip, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = 100 * downloaded / total
                        mb = downloaded / 1_048_576
                        print(f"\r  {pct:.1f}%  ({mb:.1f} MB)", end="", flush=True)
        print()
        print(f"[OK] Downloaded {downloaded / 1_048_576:.1f} MB")
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        tmp_zip.unlink(missing_ok=True)
        return False

    # -- Extract with filename sanitization --
    print(f"[INFO] Extracting with filename sanitization...")
    PLANTDOC_RAW.mkdir(parents=True, exist_ok=True)
    skipped = []
    extracted = 0

    with zipfile.ZipFile(tmp_zip, "r") as zf:
        for member in zf.infolist():
            # Strip the top-level folder (PlantDoc-Dataset-master/)
            parts = member.filename.split("/", 1)
            if len(parts) < 2 or not parts[1]:
                continue  # skip root dir entry
            rel_path = parts[1]  # e.g. train/Apple Scab Leaf/img.jpg

            # Sanitize each path component
            path_parts = rel_path.split("/")
            sanitized_parts = [sanitize_filename(p) if p else p for p in path_parts]
            sanitized_rel = "/".join(sanitized_parts)

            dest = PLANTDOC_RAW / Path(sanitized_rel)

            if member.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                continue

            # Only extract image files
            suffix = Path(sanitized_parts[-1]).suffix.lower()
            if suffix not in IMG_EXTS and suffix != "":
                # Allow non-image files too (README, LICENSE) but skip others
                if suffix not in {".md", ".txt", ".pdf", ".png"}:
                    continue

            dest.parent.mkdir(parents=True, exist_ok=True)

            # Skip if dest already exists (resume support)
            if dest.exists():
                extracted += 1
                continue

            try:
                with zf.open(member) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                extracted += 1
            except Exception as e:
                skipped.append({"member": member.filename, "error": str(e)})

    # Cleanup temp files
    tmp_zip.unlink(missing_ok=True)

    print(f"[OK] Extracted {extracted} files")
    if skipped:
        print(f"[WARN] Skipped {len(skipped)} files during extraction:")
        for s in skipped[:5]:
            print(f"  - {s['member']}: {s['error']}")

    return PLANTDOC_RAW.exists()


def verify_structure(root: Path) -> dict:
    """Check PlantDoc folder structure and count images per class."""
    counts = {}
    for split in ["train", "test"]:
        split_dir = root / split
        if not split_dir.exists():
            print(f"  [!] WARNING: {split_dir} not found")
            continue
        counts[split] = {}
        for cls_dir in sorted(split_dir.iterdir()):
            if cls_dir.is_dir():
                imgs = [
                    f for f in cls_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in IMG_EXTS
                ]
                counts[split][cls_dir.name] = len(imgs)
    return counts


def download_plantdoc():
    print("=" * 65)
    print(" AGRISMART AI -- PlantDoc Dataset Download")
    print("=" * 65)
    print(f"Source:  {PLANTDOC_ZIP_URL}")
    print(f"License: Creative Commons Attribution 4.0 International")
    print(f"Target:  {PLANTDOC_RAW}")
    print(f"Note:    Using ZIP download (git clone fails on Windows NTFS")
    print(f"         due to '?' chars in PlantDoc filenames).")
    print()

    if PLANTDOC_RAW.exists():
        existing_train = PLANTDOC_RAW / "train"
        if existing_train.exists() and any(existing_train.iterdir()):
            print(f"[OK] PlantDoc already present at {PLANTDOC_RAW}")
            print("     Skipping download. Running verification only...")
            print()
        else:
            print(f"[!] Incomplete download detected. Re-downloading...")
            shutil.rmtree(PLANTDOC_RAW, ignore_errors=True)
            if not download_via_zip():
                print("[ERROR] Download failed.")
                sys.exit(1)
    else:
        if not download_via_zip():
            print("[ERROR] Download failed.")
            sys.exit(1)

    counts = verify_structure(PLANTDOC_RAW)

    # Report
    print()
    print("=" * 65)
    print(" STRUCTURE VERIFICATION")
    print("=" * 65)

    all_ok = True
    for split, class_counts in counts.items():
        total = sum(class_counts.values())
        print(f"\n{split.upper()} split: {len(class_counts)} classes, {total} images")
        print(f"  {'Class':<47} Images")
        print(f"  {'-'*54}")
        for cls, n in sorted(class_counts.items()):
            flag = ""
            if split == "train" and cls not in EXPECTED_TRAIN_CLASSES:
                flag = "  <- UNEXPECTED"
                all_ok = False
            print(f"  {cls:<47} {n}{flag}")

    # Check for missing/extra classes
    if "train" in counts:
        found = set(counts["train"].keys())
        missing = [c for c in EXPECTED_TRAIN_CLASSES if c not in found]
        extra = [c for c in found if c not in EXPECTED_TRAIN_CLASSES]
        if missing:
            print(f"\n[!] Missing expected train classes: {missing}")
            all_ok = False
        if extra:
            print(f"\n[!] Unexpected extra train classes: {extra}")

    if all_ok:
        print(f"\n[PASS] PlantDoc structure verified successfully.")
    else:
        print(f"\n[WARN] Structure has unexpected entries -- review before proceeding.")

    return counts


if __name__ == "__main__":
    download_plantdoc()
