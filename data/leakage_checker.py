"""
AgriSmart AI — Single Authoritative Content-Level Leakage Checker
===================================================================
Defines the single authoritative leakage auditing rule across the codebase:
    CONTENT IDENTITY = SHA256(file bytes)

Filename or path string similarity ALONE is NOT leakage.

Functions:
  - audit_content_leakage(): Scans train/val dirs against locked test sets.
    Classifies overlaps into:
      1. TRUE DUPLICATES (Identical SHA256 hash match with test image) -> CRITICAL LEAKAGE
      2. FILENAME-ONLY COLLISIONS (Same filename, different SHA256) -> SAFE NON-LEAKAGE
      3. TRAIN vs VAL OVERLAP (Identical SHA256 between train and val) -> SPLIT LEAKAGE
"""

import os
import sys
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data.common import (
    ROOT_DIR,
    PD_TEST_DIR,
    PV_TEST_DIR,
    MODEL2_TRAIN_DIR,
    MODEL2_VAL_DIR,
    IMG_EXTS,
    compute_file_sha256,
)

# Safe UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def audit_content_leakage(
    train_dir: Path = MODEL2_TRAIN_DIR,
    val_dir: Path = MODEL2_VAL_DIR,
    pd_test_dir: Path = PD_TEST_DIR,
    pv_test_dir: Path = PV_TEST_DIR,
    verbose: bool = True,
) -> dict:
    """
    Audits training and validation image sets for true SHA256 content leakage
    against locked test sets.

    Returns:
        dict containing audit statistics, true duplicates list, filename collisions list,
        and boolean `is_clean`.
    """
    if verbose:
        print("=" * 70)
        print(" AGRISMART AI — SHA256 CONTENT-LEVEL LEAKAGE AUDIT")
        print("=" * 70)
        print(f"Rule: CONTENT IDENTITY = SHA256(raw file bytes)")
        print(f"Train Dir: {train_dir}")
        print(f"Val Dir:   {val_dir}")
        print(f"Locked Test Dirs: PlantDoc ({pd_test_dir}) | PlantVillage ({pv_test_dir})")
        print()

    # 1. Index locked test set content hashes and filename maps
    test_hashes = {}
    test_filenames = defaultdict(list)
    test_dirs = [d for d in [pd_test_dir, pv_test_dir] if d.exists()]

    def fast_scan_images(directory: Path) -> list[Path]:
        if not directory.exists():
            return []
        files = []
        for root, _, filenames in os.walk(directory):
            for name in filenames:
                ext = os.path.splitext(name)[1].lower()
                if ext in IMG_EXTS:
                    files.append(Path(root) / name)
        return files

    test_files = []
    for tdir in test_dirs:
        test_files.extend(fast_scan_images(tdir))

    from concurrent.futures import ThreadPoolExecutor

    def process_test_file(img):
        return img, compute_file_sha256(img)

    with ThreadPoolExecutor(max_workers=32) as executor:
        results = list(executor.map(process_test_file, test_files))

    for img, sha in results:
        test_hashes[sha] = img
        test_filenames[img.name].append((img, sha))

    if verbose:
        print(f"[1/3] Indexed {len(test_hashes)} unique SHA256 hashes across {len(test_files)} locked test images.")

    # 2. Audit Train and Val datasets
    train_files = fast_scan_images(train_dir)
    val_files = fast_scan_images(val_dir)

    with ThreadPoolExecutor(max_workers=32) as executor:
        train_results = list(executor.map(process_test_file, train_files))
        val_results = list(executor.map(process_test_file, val_files))

    true_duplicates = []
    filename_collisions = []
    seen_collisions = set()

    train_hashes = {}
    val_hashes = {}

    # Scan Train
    for img, sha in train_results:
        train_hashes[sha] = img

        if sha in test_hashes:
            test_match = test_hashes[sha]
            true_duplicates.append({
                "split": "train",
                "source_path": str(img),
                "test_match_path": str(test_match),
                "sha256": sha,
                "file_size": img.stat().st_size,
            })

        if img.name in test_filenames:
            for test_file, test_sha in test_filenames[img.name]:
                if sha != test_sha and (str(img), str(test_file)) not in seen_collisions:
                    seen_collisions.add((str(img), str(test_file)))
                    filename_collisions.append({
                        "split": "train",
                        "filename": img.name,
                        "source_path": str(img),
                        "test_match_path": str(test_file),
                        "train_sha256": sha,
                        "test_sha256": test_sha,
                        "train_size": img.stat().st_size,
                        "test_size": test_file.stat().st_size,
                    })

    # Scan Val
    for img, sha in val_results:
        val_hashes[sha] = img

        if sha in test_hashes:
            test_match = test_hashes[sha]
            true_duplicates.append({
                "split": "val",
                "source_path": str(img),
                "test_match_path": str(test_match),
                "sha256": sha,
                "file_size": img.stat().st_size,
            })

        if img.name in test_filenames:
            for test_file, test_sha in test_filenames[img.name]:
                if sha != test_sha and (str(img), str(test_file)) not in seen_collisions:
                    seen_collisions.add((str(img), str(test_file)))
                    filename_collisions.append({
                        "split": "val",
                        "filename": img.name,
                        "source_path": str(img),
                        "test_match_path": str(test_file),
                        "val_sha256": sha,
                        "test_sha256": test_sha,
                        "val_size": img.stat().st_size,
                        "test_size": test_file.stat().st_size,
                    })

    # Train vs Val Overlap
    train_val_overlap_hashes = set(train_hashes.keys()) & set(val_hashes.keys())
    train_val_overlaps = [
        {
            "train_path": str(train_hashes[sha]),
            "val_path": str(val_hashes[sha]),
            "sha256": sha,
        }
        for sha in train_val_overlap_hashes
    ]

    is_clean = (len(true_duplicates) == 0) and (len(train_val_overlaps) == 0)

    if verbose:
        print(f"[2/3] Scanned {len(train_files)} Train images & {len(val_files)} Val images.")
        print(f"[3/3] Leakage Analysis Results:")
        print(f"  - True Test Content Duplicates (SHA256 Match): {len(true_duplicates)}")
        print(f"  - Filename-Only Collisions (Safe Non-Duplicates): {len(filename_collisions)}")
        print(f"  - Train vs Val Content Overlap (SHA256 Match):    {len(train_val_overlaps)}")
        print()

        if true_duplicates:
            print("[CRITICAL LEAKAGE DETECTED] True SHA256 Content Duplicates:")
            for dup in true_duplicates:
                print(f"  [!] Split: {dup['split']} | File: {Path(dup['source_path']).name}")
                print(f"      Source: {dup['source_path']}")
                print(f"      Target: {dup['test_match_path']}")
                print(f"      SHA256: {dup['sha256']}")

        if filename_collisions:
            print("[INFO] Filename-Only Collisions (Preserved as Safe Non-Duplicates):")
            for col in filename_collisions[:5]:  # show up to 5 examples
                print(f"  [i] Filename: {col['filename']}")
                print(f"      Train/Val: {col['source_path']} (SHA: {col['train_sha256' if 'train_sha256' in col else 'val_sha256'][:10]}...)")
                print(f"      Test:      {col['test_match_path']} (SHA: {col['test_sha256'][:10]}...)")
            if len(filename_collisions) > 5:
                print(f"      ... and {len(filename_collisions) - 5} more filename-only collisions.")

        print("=" * 70)
        if is_clean:
            print(" [PASS] LEAKAGE AUDIT PASSED: ZERO SHA256 CONTENT LEAKAGE DETECTED.")
        else:
            print(" [FAIL] LEAKAGE AUDIT FAILED: UNRESOLVED CONTENT LEAKAGE DETECTED.")
        print("=" * 70)

    return {
        "is_clean": is_clean,
        "scanned_train": len(train_files),
        "scanned_val": len(val_files),
        "indexed_test_hashes": len(test_hashes),
        "true_duplicates_count": len(true_duplicates),
        "true_duplicates": true_duplicates,
        "filename_collisions_count": len(filename_collisions),
        "filename_collisions": filename_collisions,
        "train_val_overlap_count": len(train_val_overlaps),
        "train_val_overlaps": train_val_overlaps,
    }


if __name__ == "__main__":
    audit_content_leakage()
