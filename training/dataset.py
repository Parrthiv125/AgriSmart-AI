"""
AgriSmart AI — Dataset Loading
================================
Handles:
  - Loading PlantVillage from disk (ImageFolder)
  - Class filtering (official hackathon class list)
  - Class weight computation for imbalanced training
  - Download from Hugging Face Hub
"""

import os
import json
import shutil
import random
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Set

import torch
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision.datasets import ImageFolder
from torchvision import transforms
from PIL import Image
from tqdm import tqdm

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from training.config import (
    TRAIN_DIR, VAL_DIR, TEST_DIR, CLASSES, CLASSES_JSON,
    BATCH_SIZE, NUM_WORKERS, PIN_MEMORY, SEED, USE_CLASS_WEIGHTS,
)
from training.preprocessing import get_train_transform, get_val_transform


# ── Dataset Loading ──────────────────────────────────────────────────────────

def _match_class(folder_name: str, allowed_set: Set[str]) -> Optional[str]:
    """Match disk folder name to official development class string."""
    if folder_name in allowed_set:
        return folder_name
    # Check slash sanitization matching
    for allowed in allowed_set:
        if allowed.replace("/", "_") == folder_name:
            return allowed
    return None

def _filter_classes(dataset: ImageFolder, allowed_classes: Optional[List[str]]) -> ImageFolder:
    """Filter an ImageFolder to only include `allowed_classes`."""
    if allowed_classes is None:
        return dataset

    allowed_set = set(allowed_classes)
    
    # Build mapping from dataset folder index to target class index
    folder_to_target = {}
    for idx, folder in enumerate(dataset.classes):
        matched = _match_class(folder, allowed_set)
        if matched:
            folder_to_target[idx] = (matched, allowed_classes.index(matched) if matched in allowed_classes else 0)

    filtered_samples = []
    for path, label in dataset.samples:
        if label in folder_to_target:
            matched_name, target_idx = folder_to_target[label]
            filtered_samples.append((path, target_idx))

    dataset.classes = allowed_classes
    dataset.class_to_idx = {c: i for i, c in enumerate(allowed_classes)}
    dataset.samples = filtered_samples
    dataset.targets = [s[1] for s in filtered_samples]
    return dataset


def get_dataset(split: str, transform=None, classes: Optional[List[str]] = None):
    """
    Load a split of the PlantVillage dataset.

    Args:
        split: "train" | "val" | "test"
        transform: torchvision transforms to apply
        classes: optional list of class names to include

    Returns:
        ImageFolder dataset
    """
    dirs = {"train": TRAIN_DIR, "val": VAL_DIR, "test": TEST_DIR}
    if split not in dirs:
        raise ValueError(f"Unknown split '{split}'. Use 'train', 'val', or 'test'.")

    data_dir = dirs[split]
    if not data_dir.exists():
        raise FileNotFoundError(
            f"Data directory not found: {data_dir}\n"
            "Run: python data/download_dataset.py && python data/split_dataset.py"
        )

    dataset = ImageFolder(root=str(data_dir), transform=transform)

    # Filter to official hackathon classes if specified
    filter_classes = classes if classes is not None else CLASSES
    if filter_classes:
        dataset = _filter_classes(dataset, filter_classes)

    return dataset


def compute_class_weights(dataset: ImageFolder) -> torch.Tensor:
    """Compute inverse-frequency class weights for imbalanced classes."""
    class_counts = torch.zeros(len(dataset.classes))
    for _, label in dataset.samples:
        class_counts[label] += 1

    # Inverse frequency: rare classes get higher weight
    weights = 1.0 / (class_counts + 1e-6)
    weights = weights / weights.sum() * len(dataset.classes)
    return weights


def get_weighted_sampler(dataset: ImageFolder) -> WeightedRandomSampler:
    """Create a WeightedRandomSampler for balanced mini-batches."""
    class_weights = compute_class_weights(dataset)
    sample_weights = [class_weights[label] for _, label in dataset.samples]
    return WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True,
    )


def get_dataloaders(
    classes: Optional[List[str]] = None,
    batch_size: int = BATCH_SIZE,
    num_workers: int = NUM_WORKERS,
) -> Tuple[DataLoader, DataLoader, DataLoader, List[str]]:
    """
    Build train / val / test DataLoaders.

    Returns:
        (train_loader, val_loader, test_loader, class_names)
    """
    train_ds = get_dataset("train", transform=get_train_transform(), classes=classes)
    val_ds   = get_dataset("val",   transform=get_val_transform(),   classes=classes)
    test_ds  = get_dataset("test",  transform=get_val_transform(),   classes=classes)

    class_names = train_ds.classes

    # Use weighted sampler to handle class imbalance during training
    sampler = get_weighted_sampler(train_ds) if USE_CLASS_WEIGHTS else None

    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        sampler=sampler,
        shuffle=(sampler is None),
        num_workers=num_workers,
        pin_memory=PIN_MEMORY,
        drop_last=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=PIN_MEMORY,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=PIN_MEMORY,
    )

    return train_loader, val_loader, test_loader, class_names


def save_class_mapping(class_names: List[str], path: Path = CLASSES_JSON):
    """Save class index→name mapping as JSON."""
    mapping = {str(i): name for i, name in enumerate(class_names)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"✅ Class mapping saved to {path}")


def load_class_mapping(path: Path = CLASSES_JSON) -> List[str]:
    """Load class names from classes.json. Returns list indexed by class index."""
    if not path.exists():
        raise FileNotFoundError(f"classes.json not found at {path}. Train the model first.")
    with open(path) as f:
        mapping = json.load(f)
    # Sort by integer key to preserve index order
    return [mapping[str(i)] for i in range(len(mapping))]


# ── Dataset Inspection ────────────────────────────────────────────────────────

def inspect_dataset(data_dir: Path) -> Dict:
    """
    Inspect a dataset directory. Returns per-class image counts.
    Also detects empty folders and attempts to open each image (corruption check).
    """
    stats = {}
    corrupted = []
    empty_dirs = []

    for class_dir in sorted(data_dir.iterdir()):
        if not class_dir.is_dir():
            continue
        image_files = list(class_dir.glob("*.[jJpP][pPnN][gG]*")) + \
                      list(class_dir.glob("*.jpeg")) + \
                      list(class_dir.glob("*.JPEG"))

        if len(image_files) == 0:
            empty_dirs.append(class_dir.name)
            continue

        stats[class_dir.name] = len(image_files)

        # Quick corruption check (open & verify)
        for img_path in image_files:
            try:
                with Image.open(img_path) as img:
                    img.verify()
            except Exception:
                corrupted.append(str(img_path))

    return {
        "class_counts": stats,
        "total_classes": len(stats),
        "total_images": sum(stats.values()),
        "empty_dirs": empty_dirs,
        "corrupted_files": corrupted,
    }
