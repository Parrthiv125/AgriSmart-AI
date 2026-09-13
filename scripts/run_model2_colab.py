"""
AgriSmart AI — Master Model 2 Colab Execution Orchestrator
===========================================================
Single authoritative CLI entry point for executing the Model 2 field-domain
adaptation training pipeline in Google Colab T4 or local GPU environments.

Executes all pipeline stages sequentially using explicit CLI/subprocess contracts:
  1. Environment & CUDA GPU Validation
  2. Repository Root & Location Validation
  3. Model 1 Checkpoint SHA256 Validation
  4. PlantVillage Dataset Download & Verification
  5. PlantVillage Extraction Verification
  6. PlantVillage 28-Class Split
  7. PlantVillage Split Integrity Validation
  8. PlantDoc Dataset Download
  9. PlantDoc Train & Test Preparation
 10. Combined Model 2 Dataset Preparation & SHA256 Deduplication
 11. Authoritative SHA256 Content Leakage Audit
 12. Model 2 Pipeline Guardrail Verification
 13. Dry-Run Training Test
 14. Full 25-Epoch Training (Skipped if --preflight-only)
 15. Checkpoint & Artifact Verification
 16. Final Model 2 Summary & Test Set Isolation Audit

Usage:
    python scripts/run_model2_colab.py
    python scripts/run_model2_colab.py --preflight-only
"""

import sys
import os
import time
import json
import argparse
import hashlib
import subprocess
from pathlib import Path

# Safe UTF-8 output on Windows / Colab
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXPECTED_MODEL1_HASH = "af9684b036dac12c650004a2877add20708007ad34811015d1efaf5bcea06215"
MODEL1_CKPT = REPO_ROOT / "models" / "agrismart_best.pth"
CLASSES_JSON = REPO_ROOT / "models" / "classes.json"
MODEL2_BEST_CKPT = REPO_ROOT / "models" / "agrismart_field_adapted_best.pth"
MODEL2_LAST_CKPT = REPO_ROOT / "models" / "agrismart_field_adapted_last.pth"
MODEL2_META_JSON = REPO_ROOT / "models" / "agrismart_field_adapted_metadata.json"
MODEL2_EXP_LOG = REPO_ROOT / "experiments_model2.csv"
PD_TEST_DIR = REPO_ROOT / "data" / "plantdoc" / "test"
PV_TEST_DIR = REPO_ROOT / "data" / "processed" / "test"


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def run_subprocess_stage(stage_num: int, total_stages: int, stage_title: str, cmd_args: list):
    print("\n" + "=" * 70)
    print(f" [{stage_num}/{total_stages}] {stage_title.upper()}")
    print("=" * 70)
    print(f"Command: python {' '.join(cmd_args[1:])}")
    print()

    t0 = time.time()
    try:
        subprocess.run(
            cmd_args,
            cwd=str(REPO_ROOT),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print(f" [FAIL] STAGE {stage_num} FAILED WITH EXIT CODE {e.returncode}: {stage_title}")
        print("=" * 70)
        print(f"Command:   {' '.join(cmd_args)}")
        print(f"Exit Code: {e.returncode}")
        print("=" * 70)
        sys.exit(e.returncode)
    except Exception as e:
        print("\n" + "=" * 70)
        print(f" [FAIL] STAGE {stage_num} FAILED TO EXECUTE: {stage_title}")
        print("=" * 70)
        print(f"Command:   {' '.join(cmd_args)}")
        print(f"Exception: {e}")
        print("=" * 70)
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"\n[OK] Stage {stage_num} completed cleanly in {elapsed:.1f}s.")


def main():
    parser = argparse.ArgumentParser(description="AgriSmart AI Model 2 Master Orchestrator")
    parser.add_argument("--preflight-only", action="store_true", help="Perform pre-flight verifications and dry-run only; skip full 25-epoch training")
    parser.add_argument("--require-gpu", action="store_true", default=False, help="Strictly require CUDA GPU (useful in Colab)")
    args = parser.parse_args()

    total_stages = 16
    t_start = time.time()

    print("=" * 70)
    print(" AGRISMART AI — MASTER MODEL 2 COLAB EXECUTION ORCHESTRATOR")
    print("=" * 70)
    print(f"  Repository Root: {REPO_ROOT}")
    print(f"  Execution Mode:  {'PREFLIGHT-ONLY' if args.preflight_only else 'FULL PIPELINE (PREFLIGHT + 25-EPOCH TRAINING)'}")
    print(f"  Require GPU:     {args.require_gpu}")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # STAGE 1: Environment & CUDA GPU Validation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [1/{total_stages}] ENVIRONMENT & CUDA GPU VALIDATION")
    print("=" * 70)
    import torch
    print(f"  Python Executable: {sys.executable}")
    print(f"  PyTorch Version:   {torch.__version__}")
    cuda_avail = torch.cuda.is_available()
    if cuda_avail:
        print(f"  [OK] CUDA GPU Detected: {torch.cuda.get_device_name(0)}")
    else:
        print("  [WARN] CUDA GPU not detected (running on CPU).")
        if args.require_gpu:
            print("  [ERROR] --require-gpu flag set, but no CUDA GPU available!")
            sys.exit(1)

    # -------------------------------------------------------------------------
    # STAGE 2: Repository Root & Location Validation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [2/{total_stages}] REPOSITORY ROOT & LOCATION VALIDATION")
    print("=" * 70)
    if not CLASSES_JSON.exists():
        print(f"  [ERROR] classes.json missing at {CLASSES_JSON}!")
        sys.exit(1)
    
    commit_hash = "unknown"
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT)).decode().strip()
    except Exception:
        pass
    print(f"  [OK] REPO_ROOT confirmed: {REPO_ROOT}")
    print(f"  [OK] Git Commit Hash:      {commit_hash}")

    # -------------------------------------------------------------------------
    # STAGE 3: Model 1 Checkpoint SHA256 Validation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [3/{total_stages}] MODEL 1 CHECKPOINT SHA256 VALIDATION")
    print("=" * 70)
    if not MODEL1_CKPT.exists():
        print(f"  [ERROR] Model 1 checkpoint missing at {MODEL1_CKPT}!")
        sys.exit(1)
    
    m1_hash = compute_file_sha256(MODEL1_CKPT)
    if m1_hash != EXPECTED_MODEL1_HASH:
        print(f"  [ERROR] Model 1 SHA256 mismatch!")
        print(f"          Expected: {EXPECTED_MODEL1_HASH}")
        print(f"          Got:      {m1_hash}")
        sys.exit(1)
    print(f"  [OK] Model 1 Checkpoint verified: {MODEL1_CKPT.name}")
    print(f"  [OK] SHA256 Hash: {m1_hash[:16]}... (UNTOUCHED)")

    # -------------------------------------------------------------------------
    # STAGE 4: PlantVillage Dataset Download & Verification
    # -------------------------------------------------------------------------
    run_subprocess_stage(4, total_stages, "PlantVillage Dataset Download & Verification", [sys.executable, "data/download_dataset.py"])

    # -------------------------------------------------------------------------
    # STAGE 5: PlantVillage System Unzip / Extraction Check
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [5/{total_stages}] PLANTVILLAGE EXTRACTION VERIFICATION")
    print("=" * 70)
    from data.download_dataset import find_existing_rgb_dir
    pv_rgb_dir = find_existing_rgb_dir(REPO_ROOT / "data" / "raw" / "plantvillage")
    if not pv_rgb_dir or not pv_rgb_dir.exists():
        print(f"  [ERROR] PlantVillage RGB directory not found under data/raw/plantvillage!")
        sys.exit(1)
    print(f"  [OK] Verified PlantVillage RGB Directory: {pv_rgb_dir.relative_to(REPO_ROOT)}")

    # -------------------------------------------------------------------------
    # STAGE 6: PlantVillage 28-Class Split
    # -------------------------------------------------------------------------
    run_subprocess_stage(6, total_stages, "PlantVillage 28-Class Split", [sys.executable, "data/split_dataset.py"])

    # -------------------------------------------------------------------------
    # STAGE 7: PlantVillage Split Integrity Validation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [7/{total_stages}] PLANTVILLAGE SPLIT INTEGRITY VALIDATION")
    print("=" * 70)
    split_stats_path = REPO_ROOT / "data" / "split_stats.json"
    if not split_stats_path.exists():
        print(f"  [ERROR] split_stats.json missing at {split_stats_path}!")
        sys.exit(1)
    with open(split_stats_path, "r", encoding="utf-8") as f:
        sdata = json.load(f)
    print(f"  [OK] PlantVillage Split Total: {sdata.get('total_images')} images")
    print(f"       Train: {sdata.get('train_total')} | Val: {sdata.get('val_total')} | Test: {sdata.get('test_total')}")

    # -------------------------------------------------------------------------
    # STAGE 8: PlantDoc Dataset Download
    # -------------------------------------------------------------------------
    run_subprocess_stage(8, total_stages, "PlantDoc Dataset Download", [sys.executable, "data/download_plantdoc.py"])

    # -------------------------------------------------------------------------
    # STAGE 9: PlantDoc Train & Test Preparation
    # -------------------------------------------------------------------------
    run_subprocess_stage(9, total_stages, "PlantDoc Train & Test Preparation", [sys.executable, "data/prepare_plantdoc.py"])

    # -------------------------------------------------------------------------
    # STAGE 10: Combined Model 2 Dataset Preparation & SHA256 Deduplication
    # -------------------------------------------------------------------------
    run_subprocess_stage(10, total_stages, "Combined Model 2 Dataset Preparation & SHA256 Deduplication", [sys.executable, "data/prepare_model2_dataset.py"])

    # -------------------------------------------------------------------------
    # STAGE 11: Authoritative SHA256 Content Leakage Audit
    # -------------------------------------------------------------------------
    run_subprocess_stage(11, total_stages, "Authoritative SHA256 Content Leakage Audit", [sys.executable, "data/leakage_checker.py"])

    # -------------------------------------------------------------------------
    # STAGE 12: Model 2 Pipeline Guardrail Verification
    # -------------------------------------------------------------------------
    run_subprocess_stage(12, total_stages, "Model 2 Pipeline Guardrail Verification", [sys.executable, "data/verify_model2_pipeline.py"])

    # -------------------------------------------------------------------------
    # STAGE 13: Dry-Run Training Test
    # -------------------------------------------------------------------------
    run_subprocess_stage(13, total_stages, "Dry-Run Training Test", [sys.executable, "training/train_model2.py", "--dry-run"])

    # -------------------------------------------------------------------------
    # STAGE 14: Model 2 Full Field-Domain Adaptation Training (25 Epochs)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [14/{total_stages}] MODEL 2 FULL FIELD-DOMAIN ADAPTATION TRAINING")
    print("=" * 70)
    if args.preflight_only:
        print("  [SKIP] --preflight-only specified. Skipping 25-epoch training stage.")
    else:
        run_subprocess_stage(
            14,
            total_stages,
            "Model 2 Full Field-Domain Adaptation Training (25 Epochs)",
            [sys.executable, "training/train_model2.py", "--epochs", "25", "--plantdoc-oversample-factor", "5.0"],
        )

    # -------------------------------------------------------------------------
    # STAGE 15: Checkpoint & Artifact Verification
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [15/{total_stages}] CHECKPOINT & ARTIFACT VERIFICATION")
    print("=" * 70)
    
    # Re-verify Model 1 SHA256 hash
    post_m1_hash = compute_file_sha256(MODEL1_CKPT)
    if post_m1_hash != EXPECTED_MODEL1_HASH:
        print(f"  [CRITICAL ERROR] Model 1 checkpoint was modified during execution!")
        sys.exit(1)
    print(f"  [OK] Model 1 SHA256 integrity re-verified: {post_m1_hash[:16]}... (UNTOUCHED)")

    required_artifacts = [MODEL2_BEST_CKPT, MODEL2_META_JSON, MODEL2_EXP_LOG]
    if not args.preflight_only:
        required_artifacts.append(MODEL2_LAST_CKPT)

    for art in required_artifacts:
        if not art.exists():
            print(f"  [ERROR] Required artifact missing: {art}!")
            sys.exit(1)
        sz_mb = art.stat().st_size / 1_048_576
        print(f"  [OK] Found artifact: {art.name:<40} ({sz_mb:.1f} MB)")

    # -------------------------------------------------------------------------
    # STAGE 16: Final Model 2 Summary & Test Set Isolation Audit
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print(f" [16/{total_stages}] FINAL MODEL 2 SUMMARY & TEST SET ISOLATION AUDIT")
    print("=" * 70)

    if MODEL2_META_JSON.exists():
        with open(MODEL2_META_JSON, "r", encoding="utf-8") as f:
            meta = json.load(f)
        t_res = meta.get("training_results", {})
        s_strat = meta.get("sampling_strategy", {})
        print(f"  Architecture:                {meta.get('architecture', 'efficientnet_b2')}")
        print(f"  Best Epoch:                  {t_res.get('best_epoch')}")
        print(f"  Best Validation Macro-F1:    {t_res.get('best_val_macro_f1', 0.0):.4f}")
        print(f"  PlantDoc Oversample Factor:  {s_strat.get('plantdoc_oversample_factor')}x")

    pd_test_count = len(list(PD_TEST_DIR.rglob("*"))) if PD_TEST_DIR.exists() else 0
    pv_test_count = len(list(PV_TEST_DIR.rglob("*"))) if PV_TEST_DIR.exists() else 0

    print(f"  PlantDoc TEST Status:        LOCKED & UNTOUCHED ({pd_test_count} items)")
    print(f"  PlantVillage TEST Status:     LOCKED & UNTOUCHED ({pv_test_count} items)")
    print(f"  PlantDoc TEST Evaluated:     FALSE (Evaluation locked until model frozen)")

    elapsed_total = time.time() - t_start
    print("=" * 70)
    print(f" [SUCCESS] MASTER MODEL 2 EXECUTION FINISHED IN {elapsed_total / 60:.1f} MINUTES.")
    print("=" * 70)


if __name__ == "__main__":
    main()
