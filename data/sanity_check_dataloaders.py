"""
AgriSmart AI — DataLoader Sanity Test
======================================
Loads batches from train_loader, val_loader, and test_loader.
Verifies:
  - Batch loading success
  - Tensor shapes: (batch_size, 3, 260, 260)
  - Label validity: integers in [0, 27]
  - Preprocessing & augmentation execution without error
"""

import sys
from pathlib import Path
import torch

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from training.config import BATCH_SIZE, IMAGE_SIZE, DEVELOPMENT_CLASSES
from training.dataset import get_dataloaders

def run_dataloader_sanity_test():
    print("=" * 70)
    print(" DATALOADER & PREPROCESSING SANITY TEST")
    print("=" * 70)

    train_loader, val_loader, test_loader, class_names = get_dataloaders(
        classes=DEVELOPMENT_CLASSES,
        batch_size=BATCH_SIZE,
        num_workers=0  # num_workers=0 for safe inline Windows sanity test
    )

    print(f"[OK] Initialized DataLoaders for {len(class_names)} development classes.")
    print(f"     Train loader batches: {len(train_loader)}")
    print(f"     Val loader batches:   {len(val_loader)}")
    print(f"     Test loader batches:  {len(test_loader)}")

    # 1. Test Train Batch (with Augmentation)
    print("\n--- Testing Train DataLoader (Augmentation Active) ---")
    train_images, train_labels = next(iter(train_loader))
    print(f"  Train Image Tensor Shape: {train_images.shape}")
    print(f"  Train Label Tensor Shape: {train_labels.shape}")
    print(f"  Train Image Value Range:  [{train_images.min():.2f}, {train_images.max():.2f}]")
    print(f"  Train Sample Labels:      {train_labels[:8].tolist()}")

    assert train_images.shape == (BATCH_SIZE, 3, IMAGE_SIZE, IMAGE_SIZE), f"Unexpected train shape {train_images.shape}"
    assert train_labels.min() >= 0 and train_labels.max() < len(DEVELOPMENT_CLASSES), f"Invalid train label range [{train_labels.min()}, {train_labels.max()}]"

    # 2. Test Val Batch (Deterministic, No Augmentation)
    print("\n--- Testing Val DataLoader (Deterministic Preprocessing) ---")
    val_images, val_labels = next(iter(val_loader))
    print(f"  Val Image Tensor Shape:   {val_images.shape}")
    print(f"  Val Label Tensor Shape:   {val_labels.shape}")
    print(f"  Val Image Value Range:    [{val_images.min():.2f}, {val_images.max():.2f}]")

    assert val_images.shape[0] <= BATCH_SIZE and val_images.shape[1:] == (3, IMAGE_SIZE, IMAGE_SIZE), f"Unexpected val shape {val_images.shape}"
    assert val_labels.min() >= 0 and val_labels.max() < len(DEVELOPMENT_CLASSES), f"Invalid val label range [{val_labels.min()}, {val_labels.max()}]"

    # 3. Test Local Test Batch (Deterministic, No Augmentation)
    print("\n--- Testing Local Test DataLoader (Deterministic Preprocessing) ---")
    test_images, test_labels = next(iter(test_loader))
    print(f"  Test Image Tensor Shape:  {test_images.shape}")
    print(f"  Test Label Tensor Shape:  {test_labels.shape}")
    print(f"  Test Image Value Range:   [{test_images.min():.2f}, {test_images.max():.2f}]")

    assert test_images.shape[0] <= BATCH_SIZE and test_images.shape[1:] == (3, IMAGE_SIZE, IMAGE_SIZE), f"Unexpected test shape {test_images.shape}"
    assert test_labels.min() >= 0 and test_labels.max() < len(DEVELOPMENT_CLASSES), f"Invalid test label range [{test_labels.min()}, {test_labels.max()}]"

    print("\n" + "=" * 70)
    print(" [SUCCESS] DATALOADER SANITY TEST PASSED ALL CHECKS!")
    print("=" * 70)

if __name__ == "__main__":
    run_dataloader_sanity_test()
