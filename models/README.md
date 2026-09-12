# Model Weights

## Production Model

**File:** `agrismart_best.pth`  
**Architecture:** EfficientNet-B2 (timm)  
**Status:** *(To be trained — see training instructions)*

---

## How to Obtain Model Weights

### Option 1: Train from scratch (recommended for reproducibility)
```bash
# 1. Prepare dataset
python data/download_dataset.py
python data/split_dataset.py

# 2. Train
python training/train.py

# Weights saved automatically to: models/agrismart_best.pth
```

### Option 2: Download pre-trained weights
*(Link to be added after training and GitHub Release)*

---

## Model Checkpoint Contents

Each `.pth` checkpoint contains:

```python
{
    "epoch": int,               # epoch at which this checkpoint was saved
    "model_name": str,          # timm model name (e.g. "efficientnet_b2")
    "num_classes": int,         # number of disease classes
    "class_names": List[str],   # ordered class name list
    "image_size": int,          # expected input image size
    "state_dict": dict,         # model weights
    "optimizer_state": dict,    # optimizer state (for resuming training)
    "val_macro_f1": float,      # validation Macro-F1 at this checkpoint
    "val_accuracy": float,      # validation accuracy at this checkpoint
}
```

---

## Class Mapping

`models/classes.json` contains the class index → name mapping:

```json
{
  "0": "Apple___Apple_scab",
  "1": "Apple___Black_rot",
  ...
}
```

This file is generated automatically during training and **must match** the weights file.

> ⚠️ Do NOT manually edit `classes.json`. Always regenerate it together with new weights.

---

## File Structure

```
models/
├── README.md               ← This file
├── agrismart_best.pth      ← Best model (by val Macro-F1) — NOT in git
├── agrismart_last.pth      ← Last checkpoint — NOT in git
└── classes.json            ← Class mapping — tracked in git once training is done
```
