"""
AgriSmart AI — Preprocessing & Augmentation Pipeline
======================================================
Defines deterministic inference/validation transforms and configurable,
field-generalizing training data augmentations.

Training transforms include:
  - Resize & Random Crop / Zoom
  - Horizontal & Vertical Flips
  - Random Rotation
  - Brightness, Contrast & Color Variation
  - Mild Gaussian Blur
  - Mild Gaussian Noise
  - JPEG Compression Degradation
  - Random Erasing (Occlusion simulation)

Validation / Test / Inference transforms:
  - Deterministic Resize + ToTensor + Normalization (NO random augmentation)
"""

import sys
import io
import random
from pathlib import Path

import torch
import torchvision.transforms as T
from PIL import Image

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import IMAGE_SIZE, NORM_MEAN, NORM_STD, AUGMENTATION_LEVEL, USE_AUGMENTATION


# ── Custom Field Degradation Transforms ──────────────────────────────────────

class AddGaussianNoise(object):
    """Adds mild Gaussian noise to image tensor for field sensor robustness."""
    def __init__(self, std: float = 0.03, p: float = 0.2):
        self.std = std
        self.p = p

    def __call__(self, tensor: torch.Tensor) -> torch.Tensor:
        if random.random() < self.p:
            noise = torch.randn_like(tensor) * self.std
            return torch.clamp(tensor + noise, 0.0, 1.0)
        return tensor


class JPEGCompressionDegradation(object):
    """Simulates JPEG compression artifacts common in low-bandwidth farmer uploads."""
    def __init__(self, quality_min: int = 35, quality_max: int = 80, p: float = 0.2):
        self.quality_min = quality_min
        self.quality_max = quality_max
        self.p = p

    def __call__(self, img: Image.Image) -> Image.Image:
        if random.random() < self.p:
            quality = random.randint(self.quality_min, self.quality_max)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality)
            buffer.seek(0)
            return Image.open(buffer).convert("RGB")
        return img


# ── Inference / Validation Transform ─────────────────────────────────────────

def get_inference_transform(image_size: int = IMAGE_SIZE):
    """
    Deterministic transform for validation, test, and production inference.
    NO random augmentations applied.
    """
    return T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])


def get_val_transform(image_size: int = IMAGE_SIZE):
    """Same as inference transform — deterministic validation/test preprocessing."""
    return get_inference_transform(image_size=image_size)


# ── Training Transform ────────────────────────────────────────────────────────

def get_train_transform(level: str = AUGMENTATION_LEVEL, image_size: int = IMAGE_SIZE):
    """
    Training transform with realistic agricultural field image augmentation.

    level="light"  : safe minimal augmentation
    level="medium" : recommended for PlantVillage → field generalisation
    level="heavy"  : aggressive augmentation
    """
    if not USE_AUGMENTATION:
        return get_val_transform(image_size=image_size)

    if level == "light":
        return T.Compose([
            T.RandomResizedCrop(image_size, scale=(0.85, 1.0)),
            T.RandomHorizontalFlip(p=0.5),
            T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05),
            T.ToTensor(),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ])

    elif level == "medium":
        return T.Compose([
            JPEGCompressionDegradation(quality_min=40, quality_max=85, p=0.25),
            T.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.2),
            T.RandomRotation(degrees=20),
            T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.08),
            T.GaussianBlur(kernel_size=3, sigma=(0.1, 1.2)),
            T.ToTensor(),
            AddGaussianNoise(std=0.03, p=0.2),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
            T.RandomErasing(p=0.2, scale=(0.02, 0.1), ratio=(0.3, 3.3), value=0),
        ])

    elif level == "heavy":
        return T.Compose([
            JPEGCompressionDegradation(quality_min=30, quality_max=75, p=0.35),
            T.RandomResizedCrop(image_size, scale=(0.7, 1.0)),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomVerticalFlip(p=0.3),
            T.RandomRotation(degrees=30),
            T.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.12),
            T.RandomGrayscale(p=0.08),
            T.GaussianBlur(kernel_size=5, sigma=(0.1, 2.0)),
            T.ToTensor(),
            AddGaussianNoise(std=0.05, p=0.3),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
            T.RandomErasing(p=0.3, scale=(0.02, 0.15), ratio=(0.3, 3.3), value=0),
        ])

    else:
        raise ValueError(f"Unknown augmentation level: {level}. Use 'light', 'medium', or 'heavy'.")


# ── Robustness Test Transforms ────────────────────────────────────────────────

def get_robustness_transforms(image_size: int = IMAGE_SIZE):
    """
    Returns a dict of named transforms representing degraded input conditions for robustness evaluation.
    """
    base = [T.Resize((image_size, image_size))]
    norm = [T.ToTensor(), T.Normalize(mean=NORM_MEAN, std=NORM_STD)]

    return {
        "normal": T.Compose(base + norm),
        "blur_mild": T.Compose(base + [T.GaussianBlur(kernel_size=5, sigma=1.5)] + norm),
        "blur_heavy": T.Compose(base + [T.GaussianBlur(kernel_size=11, sigma=3.0)] + norm),
        "brightness_dark": T.Compose(base + [T.ColorJitter(brightness=(0.2, 0.4))] + norm),
        "brightness_bright": T.Compose(base + [T.ColorJitter(brightness=(1.8, 2.5))] + norm),
        "low_contrast": T.Compose(base + [T.ColorJitter(contrast=(0.2, 0.4))] + norm),
        "noise": T.Compose(base + [
            T.ToTensor(),
            T.Lambda(lambda x: torch.clamp(x + 0.05 * torch.randn_like(x), 0, 1)),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]),
        "jpeg_compression": T.Compose(base + [
            T.Lambda(lambda img: JPEGCompressionDegradation(quality_min=20, quality_max=20, p=1.0)(img))
        ] + norm),
        "occlusion": T.Compose(base + [
            T.ToTensor(),
            T.RandomErasing(p=1.0, scale=(0.1, 0.25), ratio=(0.5, 2.0), value=0),
            T.Normalize(mean=NORM_MEAN, std=NORM_STD),
        ]),
    }
