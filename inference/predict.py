"""
AgriSmart AI — Inference / Prediction
=======================================
Provides:
  1. load_model()     — load trained weights + class mapping
  2. predict()        — predict disease from image path or PIL image
  3. CLI entry point  — python inference/predict.py --image leaf.jpg

The predict() function is the canonical inference interface.
It must be importable from anywhere in the project.

Usage (CLI):
    python inference/predict.py --image path/to/leaf.jpg

Usage (Python):
    from inference.predict import predict
    result = predict("leaf.jpg")
    print(result["class"], result["confidence"])
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Union, Tuple, List, Dict, Optional

import torch
import torch.nn.functional as F
from PIL import Image
import timm
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import (
    BEST_MODEL_PATH, CLASSES_JSON, IMAGE_SIZE, NORM_MEAN, NORM_STD,
    CONFIDENCE_HIGH, CONFIDENCE_MEDIUM,
)
from training.preprocessing import get_inference_transform

# ── Disease Precaution Knowledge Base ────────────────────────────────────────
# Responsible, documented precautionary guidance per disease class.
# Expand this dict as the official class list becomes known.

PRECAUTIONS: Dict[str, str] = {
    "Tomato___Early_blight": (
        "🌿 Tomato Early Blight (Alternaria solani): Remove and destroy affected leaves. "
        "Apply copper-based fungicide or mancozeb. Avoid overhead irrigation. "
        "Rotate crops; do not plant tomatoes in the same soil for ≥2 years."
    ),
    "Tomato___Late_blight": (
        "⚠️ Tomato Late Blight (Phytophthora infestans): Highly destructive. "
        "Immediately remove and burn affected plants. Apply metalaxyl or chlorothalonil fungicide. "
        "Ensure good air circulation. Monitor neighbouring crops."
    ),
    "Tomato___Leaf_Mold": (
        "🍃 Tomato Leaf Mold (Passalora fulva): Improve ventilation in greenhouse/field. "
        "Reduce humidity. Apply fungicide (copper or chlorothalonil). Avoid wetting foliage."
    ),
    "Tomato___Septoria_leaf_spot": (
        "🌱 Septoria Leaf Spot: Remove infected leaves. Apply fungicide at first sign. "
        "Mulch to reduce soil splash. Practice crop rotation."
    ),
    "Tomato___Spider_mites Two-spotted_spider_mite": (
        "🕷️ Spider Mites: Apply miticide or neem oil. Increase humidity. "
        "Avoid water stress. Introduce predatory mites if available."
    ),
    "Tomato___Target_Spot": (
        "🎯 Target Spot (Corynespora cassiicola): Remove affected leaves. "
        "Apply fungicide. Improve air circulation. Avoid overcrowding."
    ),
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": (
        "🦠 Yellow Leaf Curl Virus (TYLCV — whitefly-transmitted): No cure. "
        "Remove and destroy infected plants immediately. Control whitefly population "
        "with insecticides/reflective mulch. Use resistant varieties if available."
    ),
    "Tomato___Tomato_mosaic_virus": (
        "🦠 Tomato Mosaic Virus: No cure. Remove infected plants. Disinfect tools. "
        "Control aphids. Use certified virus-free seeds."
    ),
    "Tomato___healthy": (
        "✅ Healthy tomato plant. Continue good agricultural practices: "
        "regular irrigation, balanced fertilization, and pest monitoring."
    ),
    "Potato___Early_blight": (
        "🌿 Potato Early Blight: Apply mancozeb or copper fungicide. "
        "Remove infected foliage. Ensure adequate potassium nutrition. Practice crop rotation."
    ),
    "Potato___Late_blight": (
        "⚠️ Potato Late Blight (Phytophthora infestans): Extremely destructive — historic cause "
        "of famines. Apply metalaxyl-based fungicide immediately. Destroy infected plant material. "
        "Do not store potentially infected tubers."
    ),
    "Potato___healthy": (
        "✅ Healthy potato plant. Monitor regularly for late blight, especially in wet/humid conditions."
    ),
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": (
        "🌽 Gray Leaf Spot: Apply fungicide (strobilurin or triazole). "
        "Practice crop rotation. Use resistant hybrids. Ensure proper plant spacing."
    ),
    "Corn_(maize)___Common_rust_": (
        "🌽 Common Rust (Puccinia sorghi): Apply fungicide if severe. "
        "Use resistant varieties. Monitor regularly during wet conditions."
    ),
    "Corn_(maize)___Northern_Leaf_Blight": (
        "🌽 Northern Leaf Blight (Exserohilum turcicum): Apply foliar fungicide at early sign. "
        "Use resistant hybrids. Practice crop rotation."
    ),
    "Corn_(maize)___healthy": (
        "✅ Healthy maize. Continue monitoring for rust, blight, and pests."
    ),
    # ── Fallback for any unknown class ──────────────────────────────────────
    "_default": (
        "⚠️ Consult a local agronomist or extension officer for confirmed diagnosis and treatment. "
        "This prediction is provided for informational purposes only."
    ),
}


def get_precaution(class_name: str) -> str:
    """Return precautionary guidance for a predicted class."""
    return PRECAUTIONS.get(class_name, PRECAUTIONS["_default"])


def get_confidence_level(confidence: float) -> str:
    if confidence >= CONFIDENCE_HIGH:
        return "High"
    elif confidence >= CONFIDENCE_MEDIUM:
        return "Medium"
    else:
        return "Low"


# ── Model Loading ─────────────────────────────────────────────────────────────

_model_cache = {}  # module-level cache to avoid reloading on repeated calls


def load_model(model_path: Optional[Path] = None):
    """
    Load trained AgriSmart AI model.

    Returns:
        (model, class_names, transform)
    """
    global _model_cache

    if model_path is None:
        model_path = BEST_MODEL_PATH

    model_path = Path(model_path)
    cache_key = str(model_path)

    if cache_key in _model_cache:
        return _model_cache[cache_key]

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}\n"
            "Run training first: python training/train.py"
        )

    checkpoint = torch.load(model_path, map_location="cpu")

    model_name = checkpoint.get("model_name", "efficientnet_b2")
    num_classes = checkpoint["num_classes"]
    class_names = checkpoint["class_names"]

    model = timm.create_model(model_name, pretrained=False, num_classes=num_classes)
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    transform = get_inference_transform()

    _model_cache[cache_key] = (model, class_names, transform)
    return model, class_names, transform


# ── Prediction ────────────────────────────────────────────────────────────────

def predict(
    image_input: Union[str, Path, "Image.Image"],
    model_path: Optional[Path] = None,
    top_k: int = 3,
) -> Dict:
    """
    Predict crop disease from an image.

    Args:
        image_input: file path (str/Path) or PIL Image
        model_path: optional path to model weights (defaults to BEST_MODEL_PATH)
        top_k: number of top predictions to return

    Returns:
        {
          "class": "Tomato Early Blight",
          "confidence": 0.914,
          "confidence_level": "High",
          "precaution": "...",
          "top_k": [{"class": ..., "confidence": ...}, ...],
          "low_confidence_warning": None or str
        }
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, class_names, transform = load_model(model_path)
    model = model.to(device)

    # Load image
    if isinstance(image_input, (str, Path)):
        image_input = Path(image_input)
        if not image_input.exists():
            raise FileNotFoundError(f"Image not found: {image_input}")
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")

    # Preprocess
    tensor = transform(img).unsqueeze(0).to(device)  # [1, C, H, W]

    # Inference
    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1)[0].cpu().numpy()

    # Top-1 prediction
    top_idx = int(np.argmax(probs))
    confidence = float(probs[top_idx])
    class_name = class_names[top_idx]
    confidence_level = get_confidence_level(confidence)
    precaution = get_precaution(class_name)

    # Top-K predictions
    top_k_indices = np.argsort(probs)[::-1][:top_k]
    top_k_results = [
        {"class": class_names[i], "confidence": float(probs[i])}
        for i in top_k_indices
    ]

    # Low-confidence warning
    low_confidence_warning = None
    if confidence_level == "Low":
        low_confidence_warning = (
            "⚠️ The model is not confident about this prediction. "
            "Please upload a clearer, well-lit image of the affected leaf."
        )

    return {
        "class": class_name,
        "confidence": round(confidence, 4),
        "confidence_level": confidence_level,
        "precaution": precaution,
        "top_k": top_k_results,
        "low_confidence_warning": low_confidence_warning,
    }


# ── CLI Entry Point ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AgriSmart AI — Crop Disease Prediction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python inference/predict.py --image leaf.jpg
  python inference/predict.py --image photos/tomato.png --top_k 5
        """
    )
    parser.add_argument("--image", required=True, help="Path to leaf image")
    parser.add_argument("--model_path", type=str, default=None, help="Path to model weights")
    parser.add_argument("--top_k", type=int, default=3, help="Number of top predictions")
    args = parser.parse_args()

    model_path = Path(args.model_path) if args.model_path else None

    try:
        result = predict(args.image, model_path=model_path, top_k=args.top_k)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Pretty print
    print("\n" + "=" * 50)
    print("  🌿 AgriSmart AI — Disease Prediction")
    print("=" * 50)
    print(f"  Disease:     {result['class']}")
    print(f"  Confidence:  {result['confidence']*100:.1f}%  [{result['confidence_level']}]")

    if result["low_confidence_warning"]:
        print(f"\n  {result['low_confidence_warning']}")

    print(f"\n  📋 Precaution:")
    for line in result["precaution"].split(". "):
        if line.strip():
            print(f"     {line.strip()}.")

    print(f"\n  🔢 Top-{args.top_k} predictions:")
    for i, item in enumerate(result["top_k"], 1):
        print(f"     {i}. {item['class']:<45}  {item['confidence']*100:.1f}%")

    print("=" * 50)


if __name__ == "__main__":
    main()
