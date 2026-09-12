# Model Weights & Integration Suite

## Integrated Production Checkpoint

- **Model Checkpoint:** `models/agrismart_best.pth` (93.6 MB)
- **Class Mapping:** `models/classes.json`
- **Verification Script:** `models/verify_model.py`
- **Architecture:** EfficientNet-B2 (`timm`)
- **Number of Classes:** 28 canonical development classes
- **Input Resolution:** 260 x 260 RGB pixels
- **Best Epoch:** Epoch 23
- **Validation Macro-F1:** 0.9979
- **Validation Accuracy:** 0.9979
- **Held-Out Test Macro-F1:** 0.9961
- **Held-Out Test Accuracy:** 0.9971
- **Integration Commit:** `a777dfa`

---

## Model Verification

To verify that the checkpoint weights and class mapping load correctly in PyTorch and timm:

```bash
python models/verify_model.py
```

This verification script performs:
1. File presence and size checks for `agrismart_best.pth` and `classes.json`.
2. Checkpoint metadata inspection (architecture, classes, epoch, image size, validation metrics).
3. 1-to-1 class index alignment verification between `classes.json` and checkpoint `class_names`.
4. PyTorch / `timm` model instantiation and `state_dict` loading.
5. Dummy input forward pass (`[1, 3, 260, 260]` tensor $\rightarrow$ `[1, 28]` output tensor).

---

## Checkpoint Structure

Each `.pth` checkpoint saved by the AgriSmart AI training pipeline contains:

```python
{
    "epoch": 23,                        # epoch at which best val Macro-F1 was achieved
    "model_name": "efficientnet_b2",    # timm model architecture name
    "num_classes": 28,                  # number of development classes
    "class_names": [...],               # ordered canonical class name list
    "image_size": 260,                  # expected input image resolution
    "state_dict": dict,                 # trained model parameter weights
    "optimizer_state": dict,            # optimizer state
    "val_macro_f1": 0.997947,           # validation Macro-F1 score
    "val_accuracy": 0.997931,           # validation accuracy
}
```

---

## Class Mapping (`models/classes.json`)

`models/classes.json` maps model output class indices (`"0"` through `"27"`) to canonical development class names:

```json
{
  "0": "Apple — Apple Scab",
  "1": "Apple — Cedar Apple Rust",
  "2": "Apple — Healthy",
  ...
  "27": "Tomato — Healthy"
}
```

> ⚠️ Do NOT manually edit `classes.json`. It must remain synchronized with the checkpoint `class_names`.
