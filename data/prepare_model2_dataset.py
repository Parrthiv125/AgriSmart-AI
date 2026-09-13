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
  - Centralized SHA256 Content-Hash Deduplication: Detects and excludes any image
    whose raw bytes match locked test sets (PlantDoc TEST / PlantVillage TEST).
  - Shortens long PlantDoc filenames to prevent Windows MAX_PATH errors.
  - Runs authoritative audit_content_leakage() at completion.

Usage:
    python data/prepare_model2_dataset.py
"""

import sys
import json
import os
import shutil
import random
from pathlib import Path
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.common import (
    ROOT_DIR,
    DATA_DIR,
    CLASSES_JSON,
    PV_TRAIN_DIR,
    PV_VAL_DIR,
    PV_TEST_DIR,
    PD_TRAIN_DIR,
    PD_TEST_DIR,
    MODEL2_OUT_DIR,
    MODEL2_TRAIN_DIR,
    MODEL2_VAL_DIR,
    MODEL2_STATS_PATH,
    MODEL2_MANIFEST_PATH,
    SEED,
    IMG_EXTS,
    load_canonical_classes,
    sanitize_folder_name,
    make_safe_filename,
    compute_file_sha256,
)
from data.leakage_checker import audit_content_leakage


def copy_or_link(src: Path, dst: Path):
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

    # Clean existing destination directory completely to prevent stale files
    if MODEL2_OUT_DIR.exists():
        shutil.rmtree(MODEL2_OUT_DIR, ignore_errors=True)

    # Load canonical 28 classes
    class_names = load_canonical_classes()
    sanitized_classes = [sanitize_folder_name(c) for c in class_names]

    # Pre-create destination directories
    for cls_name in sanitized_classes:
        (MODEL2_TRAIN_DIR / cls_name).mkdir(parents=True, exist_ok=True)
        (MODEL2_VAL_DIR / cls_name).mkdir(parents=True, exist_ok=True)

    # Index locked test content hashes
    print("[0/3] Indexing locked test set image content hashes (SHA256)...")
    test_files = []
    for test_dir in [PD_TEST_DIR, PV_TEST_DIR]:
        if test_dir.exists():
            for root, _, filenames in os.walk(test_dir):
                for name in filenames:
                    if os.path.splitext(name)[1].lower() in IMG_EXTS:
                        test_files.append(Path(root) / name)

    with ThreadPoolExecutor(max_workers=32) as executor:
        test_hash_results = list(executor.map(compute_file_sha256, test_files))

    locked_test_hashes = set(test_hash_results)
    print(f"[OK] Indexed {len(locked_test_hashes)} unique locked test set content hashes across {len(test_files)} images.")

    counts = {
        "train": {"plantvillage": defaultdict(int), "plantdoc": defaultdict(int)},
        "val": {"plantvillage": defaultdict(int), "plantdoc": defaultdict(int)},
    }
    manifest = []
    copy_tasks = []
    excluded_duplicates = []

    # 1. Process PlantVillage Train
    print("[1/3] Gathering PlantVillage Train samples...")
    for cls_folder in sorted(PV_TRAIN_DIR.iterdir()):
        if cls_folder.is_dir() and cls_folder.name in sanitized_classes:
            for img in sorted(cls_folder.iterdir()):
                if img.suffix.lower() in IMG_EXTS:
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
                    })

    # 2. Process PlantVillage Val
    print("[2/3] Gathering PlantVillage Val samples...")
    for cls_folder in sorted(PV_VAL_DIR.iterdir()):
        if cls_folder.is_dir() and cls_folder.name in sanitized_classes:
            for img in sorted(cls_folder.iterdir()):
                if img.suffix.lower() in IMG_EXTS:
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
                    })

    # 3. Process PlantDoc Train (80/20 split using seed 42)
    print(f"[3/3] Splitting PlantDoc Train (80/20, seed={SEED}) & Deduplicating...")
    rng = random.Random(SEED)
    missing_classes_pd = []

    pd_candidates = []
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

        for img in images[:n_train]:
            pd_candidates.append((cls_name, img, "train"))
        for img in images[n_train:]:
            pd_candidates.append((cls_name, img, "val"))

    def process_pd_cand(item):
        cls_name, img, split = item
        return cls_name, img, split, compute_file_sha256(img)

    with ThreadPoolExecutor(max_workers=32) as executor:
        pd_results = list(executor.map(process_pd_cand, pd_candidates))

    for cls_name, img, split, img_hash in pd_results:
        if img_hash in locked_test_hashes:
            excluded_duplicates.append({"path": str(img), "class": cls_name, "reason": f"PlantDoc TEST content match ({split})"})
            print(f"  [!] Excluded true content duplicate from PlantDoc {split}: {img.name}")
            continue

        dst_filename = make_safe_filename("pd", img.name)
        dst_dir = MODEL2_TRAIN_DIR if split == "train" else MODEL2_VAL_DIR
        dst_path = dst_dir / cls_name / dst_filename
        copy_tasks.append((img, dst_path))
        counts[split]["plantdoc"][cls_name] += 1
        manifest.append({
            "original_filename": img.name,
            "filename": dst_filename,
            "split": split,
            "domain": "plantdoc",
            "class": cls_name,
        })

    # Execute file copy operations in parallel
    print(f"\nExecuting {len(copy_tasks)} file operations...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda t: copy_or_link(*t), copy_tasks))
    print("[OK] File operations complete.")

    # 4. Authoritative Content-Level Leakage Audit
    audit_results = audit_content_leakage(
        train_dir=MODEL2_TRAIN_DIR,
        val_dir=MODEL2_VAL_DIR,
        pd_test_dir=PD_TEST_DIR,
        pv_test_dir=PV_TEST_DIR,
        verbose=True,
    )

    if not audit_results["is_clean"]:
        print("\n[CRITICAL ERROR] Content leakage remains after dataset preparation! Stopping immediately.")
        sys.exit(1)

    # 5. Save Summary Stats Payload
    total_pv_train = sum(counts["train"]["plantvillage"].values())
    total_pv_val = sum(counts["val"]["plantvillage"].values())
    total_pd_train = sum(counts["train"]["plantdoc"].values())
    total_pd_val = sum(counts["val"]["plantdoc"].values())

    grand_total_train = total_pv_train + total_pd_train
    grand_total_val = total_pv_val + total_pd_val

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
        "audit_results": audit_results,
        "leakage_passed": audit_results["is_clean"],
    }

    with open(MODEL2_STATS_PATH, "w", encoding="utf-8") as f:
        json.dump(stats_payload, f, indent=2)
    print(f"\n[OK] Saved split stats metadata: {MODEL2_STATS_PATH}")

    with open(MODEL2_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Saved image manifest: {MODEL2_MANIFEST_PATH}")

    return stats_payload


if __name__ == "__main__":
    prepare_model2_dataset()
