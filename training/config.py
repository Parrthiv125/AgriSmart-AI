"""
AgriSmart AI — Training Configuration
=====================================
All hyperparameters, paths, and settings live here.
Change values here; do NOT hard-code paths elsewhere.
"""

import os
from pathlib import Path

# ── Root Paths ─────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MODELS_DIR = ROOT_DIR / "models"
EVAL_DIR = ROOT_DIR / "evaluation" / "results"

RAW_DATA_DIR = DATA_DIR / "raw" / "plantvillage"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

TRAIN_DIR = PROCESSED_DATA_DIR / "train"
VAL_DIR = PROCESSED_DATA_DIR / "val"
TEST_DIR = PROCESSED_DATA_DIR / "test"

# ── Class Configuration ─────────────────────────────────────────────────────
CLASS_MAPPING_CSV = DATA_DIR / "class_mapping.csv"
DEVELOPMENT_CLASSES = [
    "Apple — Apple Scab",
    "Apple — Healthy",
    "Apple — Cedar Apple Rust",
    "Blueberry — Healthy",
    "Cherry — Healthy",
    "Corn — Cercospora Leaf Spot / Gray Leaf Spot",
    "Corn — Common Rust",
    "Corn — Northern Leaf Blight",
    "Grape — Black Rot",
    "Grape — Healthy",
    "Peach — Healthy",
    "Bell Pepper — Bacterial Spot",
    "Bell Pepper — Healthy",
    "Potato — Early Blight",
    "Potato — Late Blight",
    "Raspberry — Healthy",
    "Soybean — Healthy",
    "Squash — Powdery Mildew",
    "Strawberry — Healthy",
    "Tomato — Bacterial Spot",
    "Tomato — Early Blight",
    "Tomato — Late Blight",
    "Tomato — Leaf Mold",
    "Tomato — Septoria Leaf Spot",
    "Tomato — Spider Mites / Two-Spotted Spider Mite",
    "Tomato — Tomato Yellow Leaf Curl Virus",
    "Tomato — Tomato Mosaic Virus",
    "Tomato — Healthy"
]

CLASSES = DEVELOPMENT_CLASSES
CLASSES_JSON = MODELS_DIR / "classes.json"

# ── Model Configuration ─────────────────────────────────────────────────────
MODEL_NAME = "efficientnet_b2"      # timm model name
PRETRAINED = True                   # use ImageNet pretrained weights
IMAGE_SIZE = 260                    # EfficientNet-B2 native size

# ── Training Hyperparameters ────────────────────────────────────────────────
SEED = 42
BATCH_SIZE = 32
NUM_EPOCHS = 30
LEARNING_RATE = 1e-4
WEIGHT_DECAY = 1e-4
WARMUP_EPOCHS = 3
LR_SCHEDULER = "cosine"            # "cosine" | "step" | "plateau"
EARLY_STOPPING_PATIENCE = 7        # epochs without val Macro-F1 improvement

# ── Optimizer ───────────────────────────────────────────────────────────────
OPTIMIZER = "adamw"                 # "adamw" | "sgd"
MOMENTUM = 0.9                      # only used if OPTIMIZER == "sgd"

# ── Mixed Precision ─────────────────────────────────────────────────────────
USE_AMP = True                      # Automatic Mixed Precision (faster on GPU)

# ── Data Split ──────────────────────────────────────────────────────────────
TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

# ── Augmentation Flags ──────────────────────────────────────────────────────
# See preprocessing.py for exact transforms
USE_AUGMENTATION = True
AUGMENTATION_LEVEL = "medium"      # "light" | "medium" | "heavy"

# ── Normalization ───────────────────────────────────────────────────────────
# ImageNet statistics (used since we start from ImageNet pretrained weights)
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]

# ── Class Weighting ─────────────────────────────────────────────────────────
# Use inverse-frequency class weights to handle imbalance
USE_CLASS_WEIGHTS = True

# ── Output / Artifacts ──────────────────────────────────────────────────────
MODEL1_BASELINE_PATH = MODELS_DIR / "agrismart_best.pth"
MODEL2_FIELD_ADAPTED_PATH = MODELS_DIR / "agrismart_field_adapted_best.pth"
BEST_MODEL_PATH = MODEL2_FIELD_ADAPTED_PATH if MODEL2_FIELD_ADAPTED_PATH.exists() else MODEL1_BASELINE_PATH
LAST_MODEL_PATH = MODELS_DIR / "agrismart_field_adapted_last.pth"
EXPERIMENT_LOG = ROOT_DIR / "experiments_model2.csv"

# ── Confidence Thresholds ────────────────────────────────────────────────────
CONFIDENCE_HIGH = 0.80
CONFIDENCE_MEDIUM = 0.60
# < CONFIDENCE_MEDIUM → low confidence → prompt user for clearer image

# ── Hardware ─────────────────────────────────────────────────────────────────
NUM_WORKERS = 4                     # DataLoader workers; set 0 on Windows if issues
PIN_MEMORY = True                   # set False if RAM is limited

# ── Logging ──────────────────────────────────────────────────────────────────
LOG_EVERY_N_BATCHES = 50

# ── Ensure output directories exist ──────────────────────────────────────────
MODELS_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)
