"""
AgriSmart AI — Grad-CAM Explainability
========================================
Generates class activation heatmaps using pytorch-grad-cam.

Requires: pip install grad-cam
"""

import sys
import io
import base64
import numpy as np
from pathlib import Path
from PIL import Image

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import BEST_MODEL_PATH, IMAGE_SIZE, NORM_MEAN, NORM_STD
from training.preprocessing import get_inference_transform
from inference.predict import load_model


def generate_gradcam(
    image_input,
    model_path=None,
    alpha: float = 0.5,
) -> str:
    """
    Generate a Grad-CAM heatmap for the given image.

    Args:
        image_input: PIL Image or file path
        model_path: optional path to model weights
        alpha: blend ratio for overlay (0=original, 1=pure heatmap)

    Returns:
        Base64-encoded JPEG string of the heatmap overlay
    """
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.image import show_cam_on_image

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, class_names, transform = load_model(model_path)
    model = model.to(device).eval()

    # Load image
    if isinstance(image_input, (str, Path)):
        img = Image.open(image_input).convert("RGB")
    else:
        img = image_input.convert("RGB")

    # Resize for display
    img_resized = img.resize((IMAGE_SIZE, IMAGE_SIZE))
    img_array = np.array(img_resized) / 255.0  # [H,W,3] float32 in [0,1]

    # Prepare tensor
    tensor = transform(img).unsqueeze(0).to(device)

    # Find the last convolutional layer (EfficientNet-B2)
    target_layer = _get_target_layer(model)

    with GradCAM(model=model, target_layers=[target_layer]) as cam:
        # targets=None → use top predicted class
        grayscale_cam = cam(input_tensor=tensor, targets=None)
        grayscale_cam = grayscale_cam[0]  # [H, W]

    # Overlay heatmap on original image
    overlay = show_cam_on_image(
        img_array.astype(np.float32),
        grayscale_cam,
        use_rgb=True,
        image_weight=1 - alpha,
    )

    # Encode to base64
    pil_overlay = Image.fromarray(overlay)
    buffer = io.BytesIO()
    pil_overlay.save(buffer, format="JPEG", quality=85)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return b64


def _get_target_layer(model):
    """
    Return the last convolutional layer for Grad-CAM.
    Handles EfficientNet (timm), ConvNeXt, ResNet.
    """
    model_name = type(model).__name__.lower()

    # timm EfficientNet
    if hasattr(model, "conv_head"):
        return model.conv_head

    # timm ConvNeXt
    if hasattr(model, "stages"):
        return model.stages[-1].blocks[-1]

    # timm ResNet
    if hasattr(model, "layer4"):
        return model.layer4[-1]

    # Generic fallback: last conv layer found by traversal
    last_conv = None
    for module in model.modules():
        if isinstance(module, torch.nn.Conv2d):
            last_conv = module
    if last_conv:
        return last_conv

    raise ValueError("Could not automatically determine target layer for Grad-CAM.")
