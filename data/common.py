"""
AgriSmart AI — Centralized Constants, Paths & Common Utilities
================================================================
Single source of truth for repository paths, hyperparameters,
canonical 28-class ordering, and SHA256 file hashing.
"""

import sys
import json
import hashlib
from pathlib import Path

# Repository Root
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Core Directories
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"
TESTS_DIR = ROOT_DIR / "tests"

# Classes & Checkpoint Definitions
CLASSES_JSON = MODELS_DIR / "classes.json"
MODEL1_CKPT_PATH = MODELS_DIR / "agrismart_best.pth"
EXPECTED_MODEL1_HASH = "af9684b036dac12c650004a2877add20708007ad34811015d1efaf5bcea06215"

# Dataset Directories
RAW_PV_DIR = DATA_DIR / "raw" / "plantvillage"
PV_COLOR_DIR = RAW_PV_DIR / "raw" / "color"
PV_TRAIN_DIR = DATA_DIR / "processed" / "train"
PV_VAL_DIR = DATA_DIR / "processed" / "val"
PV_TEST_DIR = DATA_DIR / "processed" / "test"

RAW_PD_DIR = DATA_DIR / "raw" / "plantdoc"
PD_TRAIN_DIR = DATA_DIR / "plantdoc" / "train"
PD_TEST_DIR = DATA_DIR / "plantdoc" / "test"

MODEL2_OUT_DIR = DATA_DIR / "processed_model2"
MODEL2_TRAIN_DIR = MODEL2_OUT_DIR / "train"
MODEL2_VAL_DIR = MODEL2_OUT_DIR / "val"
MODEL2_MANIFEST_PATH = DATA_DIR / "model2_manifest.json"
MODEL2_STATS_PATH = DATA_DIR / "model2_split_stats.json"

# Output Model 2 Artifacts
MODEL2_CKPT_OUT = MODELS_DIR / "agrismart_field_adapted_best.pth"
MODEL2_LAST_OUT = MODELS_DIR / "agrismart_field_adapted_last.pth"
MODEL2_METADATA_OUT = MODELS_DIR / "agrismart_field_adapted_metadata.json"
MODEL2_EXP_LOG = ROOT_DIR / "experiments_model2.csv"

# Global Constants
IMAGE_SIZE = 260
SEED = 42
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def compute_file_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of raw file bytes for content identity checking."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_canonical_classes() -> list[str]:
    """Load canonical 28-class list in exact index order (0..27)."""
    if not CLASSES_JSON.exists():
        raise FileNotFoundError(f"Missing canonical classes file at {CLASSES_JSON}")
    with open(CLASSES_JSON, "r", encoding="utf-8") as f:
        classes_dict = json.load(f)
    return [classes_dict[str(i)] for i in range(len(classes_dict))]


def sanitize_folder_name(name: str) -> str:
    """Sanitize class folder name (e.g. replace '/' with '_')."""
    return name.replace("/", "_")


def make_safe_filename(prefix: str, original_name: str) -> str:
    """Ensure filename stem stays under 40 chars to prevent Windows MAX_PATH errors."""
    path_obj = Path(original_name)
    ext = path_obj.suffix.lower()
    stem = path_obj.stem
    if len(stem) > 40:
        short_hash = hashlib.md5(original_name.encode("utf-8")).hexdigest()[:10]
        stem = f"{stem[:25]}_{short_hash}"
    return f"{prefix}_{stem}{ext}"
