"""
AgriSmart AI — Preprocessing & Augmentation
=============================================
Defines train and inference transforms.

Training transforms: augmentation + normalization
Inference transforms: resize + center-crop + normalization (NO augmentation)

Both use ImageNet statistics since the backbone is pretrained on ImageNet.
"""

import torchvision.transforms as T
import torch
import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import IMAGE_SIZE, NORM_MEAN, NORM_STD, AUGMENTATION_LEVEL


# ── Inference Transform (used at prediction time) ───────────────────────────

def get_inference_transform():
    """
    Deterministic transform for inference.
    MUST match training val transform (no augmentation).
    """
    return T.Compose([
        T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])


# ── Validation Transform ─────────────────────────────────────────────────────

def get_val_transform():
    """Same as inference transform — no augmentation during validation."""
    return get_inference_transform()


# ── Training Transform ────────────────────────────────────────────────────────

def get_train_transform(level: str = AUGMENTATION_LEVEL):
    """
    Training transform with realistic agricultural image augmentation.

    level="light"  : safe minimal augmentation
    level="medium" : recommended for PlantVillage → field generalisation
    level="heavy"  : aggressive, use with care
    """
    if level == "light":
        return T.Compose([
            T.Resize((IMAGE_SIZE + 32, IMAGE_SIZE + 32)),
            T.RandomCrop(IMAGE_SIZE),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.3),
            T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
            T.ToTensor(),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ])

    elif level == "medium":
        return T.Compose([
            T.Resize((IMAGE_SIZE + 40, IMAGE_SIZE + 40)),
            T.RandomCrop(IMAGE_SIZE),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.3),
            T.RandomRotation(degrees=20),
            T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
            T.RandomGrayscale(p=0.05),
            T.GaussianBlur(kernel_size=3, sigma=(0.1, 1.5)),
            T.ToTensor(),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
            # Random erasing simulates partial occlusion
            T.RandomErasing(p=0.2, scale=(0.02, 0.1), ratio=(0.3, 3.3), value=0),
        ])

    elif level == "heavy":
        return T.Compose([
            T.Resize((IMAGE_SIZE + 60, IMAGE_SIZE + 60)),
            T.RandomCrop(IMAGE_SIZE),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.4),
            T.RandomRotation(degrees=30),
            T.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.15),
            T.RandomGrayscale(p=0.10),
            T.GaussianBlur(kernel_size=5, sigma=(0.1, 2.5)),
            T.ToTensor(),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
            T.RandomErasing(p=0.3, scale=(0.02, 0.2), ratio=(0.3, 3.3), value=0),
        ])

    else:
        raise ValueError(f"Unknown augmentation level: {level}. Use 'light', 'medium', or 'heavy'.")


# ── Robustness Test Transforms ────────────────────────────────────────────────
# Used in evaluation/robustness.py to test model under degraded conditions.

def get_robustness_transforms(image_size: int = IMAGE_SIZE):
    """
    Returns a dict of named transforms representing degraded input conditions.
    Apply AFTER the base resize/crop, BEFORE normalization.
    """
    base = [T.Resize((image_size, image_size))]
    norm = [T.ToTensor(), T.Normalize(mean=NORM_MEAN, std=NORM_STD)]

    return {
        "normal": T.Compose(base + norm),

        "blur_mild": T.Compose(base + [
            T.GaussianBlur(kernel_size=5, sigma=1.5)
        ] + norm),

        "blur_heavy": T.Compose(base + [
            T.GaussianBlur(kernel_size=11, sigma=3.0)
        ] + norm),

        "brightness_dark": T.Compose(base + [
            T.ColorJitter(brightness=(0.2, 0.4))
        ] + norm),

        "brightness_bright": T.Compose(base + [
            T.ColorJitter(brightness=(1.8, 2.5))
        ] + norm),

        "low_contrast": T.Compose(base + [
            T.ColorJitter(contrast=(0.2, 0.4))
        ] + norm),

        "noise": T.Compose(base + [
            T.ToTensor(),
            # Add Gaussian noise as a custom lambda
            T.Lambda(lambda x: torch.clamp(x + 0.05 * torch.randn_like(x), 0, 1)),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]),

        "jpeg_compression": T.Compose(base + [
            # Simulate JPEG artefacts via quality reduction
            T.Lambda(lambda img: _simulate_jpeg(img, quality=20))
        ] + norm),

        "occlusion": T.Compose(base + [
            T.ToTensor(),
            T.RandomErasing(p=1.0, scale=(0.1, 0.25), ratio=(0.5, 2.0), value=0),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]),
    }


def _simulate_jpeg(pil_img, quality: int = 20):
    """Simulate JPEG compression artefacts using PIL."""
    import io
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    from PIL import Image
    return Image.open(buffer).convert("RGB")
