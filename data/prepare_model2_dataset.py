"""
AgriSmart AI — Model 2 Dataset Preparation & Content-Hash Deduplication
========================================================================
Prepares the combined dataset for Model 2 field-domain adaptation training:
  - PlantVillage Train + 80% PlantDoc Train -> data/processed_model2/train/
  - PlantVillage Val + 20% PlantDoc Val -> data/processed_model2/val/
  - PlantDoc TEST (data/plantdoc/test/) remains 100% UNTOUCHED and excluded.
  - PlantVillage TEST (data/processed/test/) remains 100% UNTOUCHED and excluded.

Guarantees & Safety:
  - Seed = 42 for deterministic 80/20 PlantDoc train/val split.
  - SHA256 Content-Hash Deduplication: Detects and excludes any image content
    that matches locked test sets (PlantDoc TEST / PlantVillage TEST) byte-for-byte.
  - Shortens extremely long PlantDoc filenames to prevent Windows MAX_PATH errors.
  - Saves metadata payload with counts and leakage-check results to data/model2_split_stats.json.

Usage:
    python data/prepare_model2_dataset.py
"""

import sys
import json
import os
import shutil
import random
import hashlib
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

PV_TRAIN_DIR = DATA_DIR / "processed" / "train"
PV_VAL_DIR = DATA_DIR / "processed" / "val"
PV_TEST_DIR = DATA_DIR / "processed" / "test"

PD_TRAIN_DIR = DATA_DIR / "plantdoc" / "train"
PD_TEST_DIR = DATA_DIR / "plantdoc" / "test"

MODEL2_OUT_DIR = DATA_DIR / "processed_model2"
MODEL2_TRAIN_DIR = MODEL2_OUT_DIR / "train"
MODEL2_VAL_DIR = MODEL2_OUT_DIR / "val"

STATS_OUT = DATA_DIR / "model2_split_stats.json"
CLASSES_JSON = ROOT_DIR / "models" / "classes.json"

SEED = 42
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def sanitize_folder_name(name: str) -> str:
    return name.replace("/", "_")


def make_safe_filename(prefix: str, original_name: str) -> str:
    """Ensure filename stays under 60 chars to prevent Windows MAX_PATH errors."""
    path_obj = Path(original_name)
    ext = path_obj.suffix.lower()
    stem = path_obj.stem
    if len(stem) > 40:
        short_hash = hashlib.md5(original_name.encode("utf-8")).hexdigest()[:10]
        stem = f"{stem[:25]}_{short_hash}"
    return f"{prefix}_{stem}{ext}"


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of raw file bytes for content-level duplicate detection."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def copy_or_link(src: Path, dst: Path):
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except Exception:
        shutil.copyfile(src, dst)


def prepare_model2_dataset():
    print("=" * 70)
    print(" AGRISMART AI — Model 2 Dataset Preparation & Deduplication")
    print("=" * 70)
    print(f"Seed:               {SEED}")
    print(f"PlantVillage Train: {PV_TRAIN_DIR}")
    print(f"PlantVillage Val:   {PV_VAL_DIR}")
    print(f"PlantDoc Train:     {PD_TRAIN_DIR}")
    print(f"Output Directory:   {MODEL2_OUT_DIR}")
    print(f"LOCKED Test Sets:   PlantDoc ({PD_TEST_DIR}) | PlantVillage ({PV_TEST_DIR})")
    print()

    # Sanity checks
    for path, desc in [
        (PV_TRAIN_DIR, "PlantVillage train dir"),
        (PV_VAL_DIR, "PlantVillage val dir"),
        (PD_TRAIN_DIR, "PlantDoc train dir"),
        (CLASSES_JSON, "classes.json"),
    ]:
        if not path.exists():
            print(f"[ERROR] Required path missing: {desc} at {path}")
            sys.exit(1)

    # Clean existing destination directory if partial
    if MODEL2_OUT_DIR.exists():
        shutil.rmtree(MODEL2_OUT_DIR, ignore_errors=True)

    # Load 28 classes
    with open(CLASSES_JSON, "r", encoding="utf-8") as f:
        classes_dict = json.load(f)
    class_names = [classes_dict[str(i)] for i in range(len(classes_dict))]
    sanitized_classes = [sanitize_folder_name(c) for c in class_names]

    # Pre-create destination directories
    for cls_name in sanitized_classes:
        (MODEL2_TRAIN_DIR / cls_name).mkdir(parents=True, exist_ok=True)
        (MODEL2_VAL_DIR / cls_name).mkdir(parents=True, exist_ok=True)

    # Build locked test content hashes
    print("[0/3] Indexing locked test set image content hashes (SHA256)...")
    locked_test_hashes = set()

    for test_dir in [PD_TEST_DIR, PV_TEST_DIR]:
        if test_dir.exists():
            for img_file in test_dir.rglob("*"):
                if img_file.is_file() and img_file.suffix.lower() in IMG_EXTS:
                    locked_test_hashes.add(compute_file_sha256(img_file))

    print(f"[OK] Indexed {len(locked_test_hashes)} unique locked test set content hashes.")

    counts = {
        "train": {"plantvillage": defaultdict(int), "plantdoc": defaultdict(int)},
        "val": {"plantvillage": defaultdict(int), "plantdoc": defaultdict(int)},
    }
    manifest = []
    copy_tasks = []
    excluded_duplicates = []

    # 1. Process PlantVillage Train
    print("[1/3] Gathering PlantVillage Train samples...")
    for cls_folder in PV_TRAIN_DIR.iterdir():
        if cls_folder.is_dir() and cls_folder.name in sanitized_classes:
            for img in sorted(cls_folder.iterdir()):
                if img.suffix.lower() in IMG_EXTS:
                    img_hash = compute_file_sha256(img)
                    if img_hash in locked_test_hashes:
                        excluded_duplicates.append({"path": str(img), "class": cls_folder.name, "reason": "PlantVillage TEST content match"})
                        continue

                    dst_filename = make_safe_filename("pv", img.name)
                    dst_path = MODEL2_TRAIN_DIR / cls_folder.name / dst_filename
                    copy_tasks.append((img, dst_path))
                    counts["train"]["plantvillage"][cls_folder.name] += 1
                    manifest.append({
                        "original_filename": img.name,
                        "filename": dst_filename,
                        "split": "train",
                        "domain": "plantvillage",
                        "class": cls_folder.name,
                        "sha256": img_hash,
                    })

    # 2. Process PlantVillage Val
    print("[2/3] Gathering PlantVillage Val samples...")
    for cls_folder in PV_VAL_DIR.iterdir():
        if cls_folder.is_dir() and cls_folder.name in sanitized_classes:
            for img in sorted(cls_folder.iterdir()):
                if img.suffix.lower() in IMG_EXTS:
                    img_hash = compute_file_sha256(img)
                    if img_hash in locked_test_hashes:
                        excluded_duplicates.append({"path": str(img), "class": cls_folder.name, "reason": "PlantVillage TEST content match"})
                        continue

                    dst_filename = make_safe_filename("pv", img.name)
                    dst_path = MODEL2_VAL_DIR / cls_folder.name / dst_filename
                    copy_tasks.append((img, dst_path))
                    counts["val"]["plantvillage"][cls_folder.name] += 1
                    manifest.append({
                        "original_filename": img.name,
                        "filename": dst_filename,
                        "split": "val",
                        "domain": "plantvillage",
                        "class": cls_folder.name,
                        "sha256": img_hash,
                    })

    # 3. Process PlantDoc Train (80/20 split using seed 42)
    print(f"[3/3] Splitting PlantDoc Train (80/20, seed={SEED}) & Deduplicating...")
    rng = random.Random(SEED)
    missing_classes_pd = []

    for cls_name in sanitized_classes:
        pd_cls_dir = PD_TRAIN_DIR / cls_name
        if not pd_cls_dir.exists() or not pd_cls_dir.is_dir():
            missing_classes_pd.append(cls_name)
            continue

        images = sorted([f for f in pd_cls_dir.iterdir() if f.suffix.lower() in IMG_EXTS])
        if not images:
            missing_classes_pd.append(cls_name)
            continue

        # Shuffle deterministically
        rng.shuffle(images)
        n_total = len(images)
        n_train = max(1, int(round(n_total * 0.8))) if n_total > 1 else 1

        pd_train_imgs = images[:n_train]
        pd_val_imgs = images[n_train:]

        for img in pd_train_imgs:
            img_hash = compute_file_sha256(img)
            if img_hash in locked_test_hashes:
                excluded_duplicates.append({"path": str(img), "class": cls_name, "reason": "PlantDoc TEST content match"})
                print(f"  [!] Excluded content duplicate from PlantDoc train: {img.name}")
                continue

            dst_filename = make_safe_filename("pd", img.name)
            dst_path = MODEL2_TRAIN_DIR / cls_name / dst_filename
            copy_tasks.append((img, dst_path))
            counts["train"]["plantdoc"][cls_name] += 1
            manifest.append({
                "original_filename": img.name,
                "filename": dst_filename,
                "split": "train",
                "domain": "plantdoc",
                "class": cls_name,
                "sha256": img_hash,
            })

        for img in pd_val_imgs:
            img_hash = compute_file_sha256(img)
            if img_hash in locked_test_hashes:
                excluded_duplicates.append({"path": str(img), "class": cls_name, "reason": "PlantDoc TEST content match"})
                print(f"  [!] Excluded content duplicate from PlantDoc val: {img.name}")
                continue

            dst_filename = make_safe_filename("pd", img.name)
            dst_path = MODEL2_VAL_DIR / cls_name / dst_filename
            copy_tasks.append((img, dst_path))
            counts["val"]["plantdoc"][cls_name] += 1
            manifest.append({
                "original_filename": img.name,
                "filename": dst_filename,
                "split": "val",
                "domain": "plantdoc",
                "class": cls_name,
                "sha256": img_hash,
            })

    # Execute file copy/link operations
    print(f"\nExecuting {len(copy_tasks)} file operations in parallel...")
    with ThreadPoolExecutor(max_workers=16) as executor:
        list(executor.map(lambda t: copy_or_link(*t), copy_tasks))
    print("[OK] File operations complete.")

    # 4. Content-Level Leakage Verification
    print("\n" + "=" * 70)
    print(" CONTENT-LEVEL SHA256 LEAKAGE VERIFICATION")
    print("=" * 70)

    train_hashes = {item["sha256"] for item in manifest if item["split"] == "train"}
    val_hashes = {item["sha256"] for item in manifest if item["split"] == "val"}

    train_val_hash_overlap = len(train_hashes & val_hashes)
    train_test_hash_overlap = len(train_hashes & locked_test_hashes)
    val_test_hash_overlap = len(val_hashes & locked_test_hashes)

    leakage_checks = {
        "train_vs_val_content_overlap": train_val_hash_overlap,
        "train_vs_test_content_overlap": train_test_hash_overlap,
        "val_vs_test_content_overlap": val_test_hash_overlap,
    }

    all_passed = True
    for check_name, count in leakage_checks.items():
        status = "PASSED (0 content overlap)" if count == 0 else f"FAILED ({count} content overlaps!)"
        print(f"  {check_name:<40}: {status}")
        if count != 0:
            all_passed = False

    if not all_passed:
        print("\n[CRITICAL ERROR] Content leakage detected! Stopping immediately.")
        sys.exit(1)

    # 5. Summary & Save Stats
    total_pv_train = sum(counts["train"]["plantvillage"].values())
    total_pv_val = sum(counts["val"]["plantvillage"].values())
    total_pd_train = sum(counts["train"]["plantdoc"].values())
    total_pd_val = sum(counts["val"]["plantdoc"].values())

    grand_total_train = total_pv_train + total_pd_train
    grand_total_val = total_pv_val + total_pd_val

    print("\n" + "=" * 70)
    print(" MODEL 2 DATA SPLIT SUMMARY")
    print("=" * 70)
    print(f"  TRAIN SET TOTAL:         {grand_total_train:>6}  (PlantVillage: {total_pv_train}, PlantDoc: {total_pd_train})")
    print(f"  VAL SET TOTAL:           {grand_total_val:>6}  (PlantVillage: {total_pv_val}, PlantDoc: {total_pd_val})")
    print(f"  EXCLUDED DUPLICATES:     {len(excluded_duplicates):>6}")
    print(f"  LOCKED PlantDoc TEST:    {len(list(PD_TEST_DIR.rglob('*'))) if PD_TEST_DIR.exists() else 0:>6}  (UNTOUCHED)")
    print(f"  LOCKED PlantVillage TEST: {len(list(PV_TEST_DIR.rglob('*'))) if PV_TEST_DIR.exists() else 0:>6} (UNTOUCHED)")
    print("=" * 70)

    stats_payload = {
        "pipeline": "AgriSmart AI Model 2 Field Domain Adaptation",
        "split_seed": SEED,
        "class_names": class_names,
        "sanitized_classes": sanitized_classes,
        "excluded_duplicates_count": len(excluded_duplicates),
        "excluded_duplicates": excluded_duplicates,
        "counts": {
            "train": {
                "total": grand_total_train,
                "plantvillage_total": total_pv_train,
                "plantdoc_total": total_pd_train,
                "per_class_plantvillage": dict(counts["train"]["plantvillage"]),
                "per_class_plantdoc": dict(counts["train"]["plantdoc"]),
            },
            "val": {
                "total": grand_total_val,
                "plantvillage_total": total_pv_val,
                "plantdoc_total": total_pd_val,
                "per_class_plantvillage": dict(counts["val"]["plantvillage"]),
                "per_class_plantdoc": dict(counts["val"]["plantdoc"]),
            },
        },
        "leakage_checks": leakage_checks,
        "leakage_passed": all_passed,
    }

    with open(STATS_OUT, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2)
    print(f"\n[OK] Saved split stats metadata: {STATS_OUT}")

    # Save manifest for data loader provenance tagging
    manifest_out = DATA_DIR / "model2_manifest.json"
    with open(manifest_out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Saved image manifest: {manifest_out}")

    return stats_payload


if __name__ == "__main__":
    prepare_model2_dataset()
