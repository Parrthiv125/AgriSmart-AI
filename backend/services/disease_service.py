"""
AgriSmart Disease Prediction Service
=====================================
Production inference module for the AgriSmart backend.

Usage:
    from backend.services.disease_service import predict_disease, warm_up

    # Optional: pre-load model at startup
    warm_up()

    # Predict from file path
    result = predict_disease("path/to/leaf.jpg")
    # Returns:
    # {
    #   "crop":        "Tomato",
    #   "disease":     "Early Blight",
    #   "display_name": "Tomato — Early Blight",
    #   "confidence":  0.9123,
    #   "class_index": 20,
    #   "disease_id":  "tomato_early_blight",
    # }

Design rules:
  - Model is loaded ONCE and cached at module level.
  - Uses GPU if CUDA available, else CPU.
  - Preprocessing is identical to training/validation pipeline.
  - Missing or corrupt images raise an explicit error — never silently fabricated.
  - No confidence thresholds, no knowledge-base text (kept in a separate layer).
  - Safe for concurrent FastAPI calls (model.eval() + torch.no_grad()).
"""

from __future__ import annotations

import re
import csv
import sys
import logging
from pathlib import Path
from typing import Optional, Union

import torch
import torch.nn.functional as F
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

# ── Paths ─────────────────────────────────────────────────────────────────────
_BACKEND_DIR  = Path(__file__).resolve().parent          # backend/services/
_ROOT_DIR     = _BACKEND_DIR.parent.parent               # project root
_MODELS_DIR   = _ROOT_DIR / "models"
_MAPPING_CSV  = _ROOT_DIR / "data" / "class_mapping.csv"

DEFAULT_MODEL_PATH = _MODELS_DIR / "agrismart_final.pth"

log = logging.getLogger(__name__)

# ── Module-level model cache ───────────────────────────────────────────────────
_cache: dict = {}   # keyed by resolved model path string


# ── Preprocessing ──────────────────────────────────────────────────────────────
# Must exactly match the val transform used during training.
_INFERENCE_TRANSFORM = transforms.Compose([
    transforms.Resize(292),
    transforms.CenterCrop(260),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# ── Class metadata helpers ─────────────────────────────────────────────────────

def _parse_class_name(display_name: str) -> tuple[str, str]:
    """
    Split a display name like 'Tomato — Early Blight' into (crop, disease).
    Falls back to (display_name, 'Unknown') if the separator is missing.
    """
    # Support both em-dash and plain dash separators in display names
    sep = " — " if " — " in display_name else " - " if " - " in display_name else None
    if sep:
        parts = display_name.split(sep, 1)
        return parts[0].strip(), parts[1].strip()
    return display_name.strip(), "Unknown"


def _make_disease_id(display_name: str) -> str:
    """Convert 'Tomato — Early Blight' to 'tomato_early_blight'."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", display_name)
    return "_".join(cleaned.lower().split())


# ── Model loading ──────────────────────────────────────────────────────────────

def _load_model(model_path: Path) -> tuple:
    """
    Load and cache the model.  Returns (model, class_names, device).

    The checkpoint is expected to contain:
        - 'model_state_dict': full EfficientNet-B2 state dict
        - 'class_names':      list of 28 friendly display names
    """
    import timm

    cache_key = str(model_path.resolve())
    if cache_key in _cache:
        return _cache[cache_key]

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model checkpoint not found: {model_path}\n"
            "Ensure 'models/agrismart_final.pth' exists before starting the service."
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    log.info(f"Loading model from {model_path} on {device}")

    ckpt = torch.load(model_path, map_location=device, weights_only=False)

    if "model_state_dict" not in ckpt:
        raise KeyError(
            f"Checkpoint at {model_path} is missing 'model_state_dict'. "
            "Check that agrismart_final.pth was created from experiment_C_best.pth."
        )
    if "class_names" not in ckpt:
        raise KeyError(
            f"Checkpoint at {model_path} is missing 'class_names'. "
            "The authoritative class ordering must be embedded in the checkpoint."
        )

    class_names: list[str] = ckpt["class_names"]
    num_classes = len(class_names)

    if num_classes != 28:
        raise ValueError(
            f"Expected 28 classes in checkpoint, found {num_classes}. "
            "Ensure agrismart_final.pth is the Experiment C champion checkpoint."
        )

    model = timm.create_model("efficientnet_b2", pretrained=False, num_classes=num_classes)
    missing, unexpected = model.load_state_dict(ckpt["model_state_dict"], strict=True)
    if missing or unexpected:
        raise RuntimeError(
            f"State dict mismatch — missing: {missing}, unexpected: {unexpected}"
        )

    model.eval()
    model.to(device)

    log.info(f"Model loaded. Classes: {num_classes}, device: {device}")
    _cache[cache_key] = (model, class_names, device)
    return model, class_names, device


def warm_up(model_path: Optional[Path] = None) -> None:
    """
    Pre-load and cache the model.  Call once at application startup.
    This avoids a cold-start latency on the first prediction request.
    """
    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    _load_model(path)
    log.info("AgriSmart disease service warmed up.")


# ── Public prediction API ──────────────────────────────────────────────────────

def predict_disease(
    image_input: Union[str, Path, "Image.Image"],
    model_path: Optional[Path] = None,
    top_k: int = 3,
) -> dict:
    """
    Predict the plant disease from a leaf image.

    Args:
        image_input:  File path (str/Path) or an already-opened PIL Image.
        model_path:   Override model path. Defaults to models/agrismart_final.pth.
        top_k:        Number of top predictions to include in the response.

    Returns:
        {
            "crop":         "Tomato",
            "disease":      "Early Blight",
            "display_name": "Tomato — Early Blight",
            "confidence":   0.9123,
            "class_index":  20,
            "disease_id":   "tomato_early_blight",
            "top_k": [
                {"display_name": ..., "crop": ..., "disease": ...,
                 "confidence": ..., "class_index": ...},
                ...
            ],
        }

    Raises:
        FileNotFoundError:    Image file does not exist.
        UnidentifiedImageError: File is not a valid image.
        ValueError:           Image is corrupt or cannot be decoded.
        FileNotFoundError:    Model checkpoint is missing.
        RuntimeError:         State dict mismatch (corrupt checkpoint).
    """
    path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
    model, class_names, device = _load_model(path)

    # ── Load image (fail hard on missing/corrupt) ──────────────────────────────
    if isinstance(image_input, (str, Path)):
        image_path = Path(image_input)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        try:
            img = Image.open(image_path).convert("RGB")
        except UnidentifiedImageError as e:
            raise UnidentifiedImageError(
                f"Cannot identify image file '{image_path}': {e}"
            ) from e
        except Exception as e:
            raise ValueError(f"Failed to open image '{image_path}': {e}") from e
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise TypeError(
            f"image_input must be a file path (str/Path) or PIL Image, "
            f"got {type(image_input)}"
        )

    # ── Preprocess ─────────────────────────────────────────────────────────────
    tensor = _INFERENCE_TRANSFORM(img).unsqueeze(0).to(device)  # [1, C, H, W]

    # ── Inference ──────────────────────────────────────────────────────────────
    with torch.no_grad():
        logits = model(tensor)
        probs  = F.softmax(logits, dim=1)[0].cpu()

    # ── Top-1 ──────────────────────────────────────────────────────────────────
    top_idx    = int(probs.argmax())
    confidence = float(probs[top_idx])
    display    = class_names[top_idx]
    crop, disease = _parse_class_name(display)
    disease_id    = _make_disease_id(display)

    # ── Top-K ──────────────────────────────────────────────────────────────────
    top_indices = probs.argsort(descending=True)[:top_k].tolist()
    top_results = []
    for idx in top_indices:
        dn = class_names[idx]
        c, d = _parse_class_name(dn)
        top_results.append({
            "display_name": dn,
            "crop":         c,
            "disease":      d,
            "confidence":   round(float(probs[idx]), 4),
            "class_index":  idx,
        })

    return {
        "crop":         crop,
        "disease":      disease,
        "display_name": display,
        "confidence":   round(confidence, 4),
        "class_index":  top_idx,
        "disease_id":   disease_id,
        "top_k":        top_results,
    }
