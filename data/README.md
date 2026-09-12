# Dataset — Download, Class Mapping, Splitting & Preprocessing

## Source

**Primary Dataset:** PlantVillage  
**Hugging Face Hub:** https://huggingface.co/datasets/mohanty/PlantVillage  
**Total Raw Images:** 54,305 images  
**Raw Classes:** 38 classes  
**License:** CC0 / Public Domain  

**Citation:**
```
Hughes, D. P., & Salathé, M. (2015).
An open access repository of images on plant health to enable the development
of mobile disease diagnostics.
arXiv:1511.08060
```

---

## ⚠️ Important Guidelines

- The **raw dataset (`data/raw/plantvillage`) is NOT committed** to git tracking.
- The **processed split images (`data/processed/`) are NOT committed** to git tracking.
- Do **NOT** train models until explicitly commanded.
- The raw dataset remains completely **untouched and intact**. Unmapped classes are retained in raw storage without deletion.

---

## 28-Class Development Label Set & Mapping

The project maps the 38 original PlantVillage raw class folders to the **28 official Development Classes**.

### Class Mapping & Split Counts Table

| # | Development Class | Mapped Raw PlantVillage Directory | Status | Train (80%) | Val (10%) | Test (10%) | Total |
|---|---|---|---|---|---|---|---|
| 1 | Apple — Apple Scab | `Apple___Apple_scab` | MAPPED | 504 | 63 | 63 | 630 |
| 2 | Apple — Healthy | `Apple___healthy` | MAPPED | 1,316 | 165 | 164 | 1,645 |
| 3 | Apple — Cedar Apple Rust | `Apple___Cedar_apple_rust` | MAPPED | 220 | 28 | 27 | 275 |
| 4 | Blueberry — Healthy | `Blueberry___healthy` | MAPPED | 1,202 | 151 | 149 | 1,502 |
| 5 | Cherry — Healthy | `Cherry_(including_sour)___healthy` | MAPPED | 684 | 86 | 84 | 854 |
| 6 | Corn — Cercospora Leaf Spot / Gray Leaf Spot | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | MAPPED | 411 | 52 | 50 | 513 |
| 7 | Corn — Common Rust | `Corn_(maize)___Common_rust_` | MAPPED | 954 | 120 | 118 | 1,192 |
| 8 | Corn — Northern Leaf Blight | `Corn_(maize)___Northern_Leaf_Blight` | MAPPED | 788 | 99 | 98 | 985 |
| 9 | Grape — Black Rot | `Grape___Black_rot` | MAPPED | 944 | 118 | 118 | 1,180 |
| 10 | Grape — Healthy | `Grape___healthy` | MAPPED | 339 | 43 | 41 | 423 |
| 11 | Peach — Healthy | `Peach___healthy` | MAPPED | 288 | 36 | 36 | 360 |
| 12 | Bell Pepper — Bacterial Spot | `Pepper,_bell___Bacterial_spot` | MAPPED | 798 | 100 | 99 | 997 |
| 13 | Bell Pepper — Healthy | `Pepper,_bell___healthy` | MAPPED | 1,183 | 148 | 147 | 1,478 |
| 14 | Potato — Early Blight | `Potato___Early_blight` | MAPPED | 800 | 100 | 100 | 1,000 |
| 15 | Potato — Late Blight | `Potato___Late_blight` | MAPPED | 800 | 100 | 100 | 1,000 |
| 16 | Raspberry — Healthy | `Raspberry___healthy` | MAPPED | 297 | 38 | 36 | 371 |
| 17 | Soybean — Healthy | `Soybean___healthy` | MAPPED | 4,072 | 509 | 509 | 5,090 |
| 18 | Squash — Powdery Mildew | `Squash___Powdery_mildew` | MAPPED | 1,468 | 184 | 183 | 1,835 |
| 19 | Strawberry — Healthy | `Strawberry___healthy` | MAPPED | 365 | 46 | 45 | 456 |
| 20 | Tomato — Bacterial Spot | `Tomato___Bacterial_spot` | MAPPED | 1,702 | 213 | 212 | 2,127 |
| 21 | Tomato — Early Blight | `Tomato___Early_blight` | MAPPED | 800 | 100 | 100 | 1,000 |
| 22 | Tomato — Late Blight | `Tomato___Late_blight` | MAPPED | 1,528 | 191 | 190 | 1,909 |
| 23 | Tomato — Leaf Mold | `Tomato___Leaf_Mold` | MAPPED | 762 | 96 | 94 | 952 |
| 24 | Tomato — Septoria Leaf Spot | `Tomato___Septoria_leaf_spot` | MAPPED | 1,417 | 178 | 176 | 1,771 |
| 25 | Tomato — Spider Mites / Two-Spotted Spider Mite | `Tomato___Spider_mites Two-spotted_spider_mite` | MAPPED | 1,341 | 168 | 167 | 1,676 |
| 26 | Tomato — Tomato Yellow Leaf Curl Virus | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | MAPPED | 4,286 | 536 | 535 | 5,357 |
| 27 | Tomato — Tomato Mosaic Virus | `Tomato___Tomato_mosaic_virus` | MAPPED | 299 | 38 | 36 | 373 |
| 28 | Tomato — Healthy | `Tomato___healthy` | MAPPED | 1,273 | 160 | 158 | 1,591 |
| **TOTAL** | — | — | — | **30,841** | **3,866** | **3,835** | **38,542** |

---

## Unmapped Original PlantVillage Classes (10)

The following 10 raw PlantVillage classes are **excluded** from the 28-class development set and marked as `UNMAPPED` in `data/class_mapping.csv`. To maintain strict diagnostic boundaries, they were **not silently merged** into unrelated classes.

| Original Raw Folder | Status | Reason / Notes | Image Count |
|---|---|---|---|
| `Apple___Black_rot` | UNMAPPED | Excluded from 28-class development set | 621 |
| `Cherry_(including_sour)___Powdery_mildew` | UNMAPPED | Excluded from 28-class development set | 1,052 |
| `Corn_(maize)___healthy` | UNMAPPED | Excluded from 28-class development set | 1,162 |
| `Grape___Esca_(Black_Measles)` | UNMAPPED | Excluded from 28-class development set | 1,383 |
| `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` | UNMAPPED | Excluded from 28-class development set | 1,076 |
| `Orange___Haunglongbing_(Citrus_greening)` | UNMAPPED | Excluded from 28-class development set | 5,507 |
| `Peach___Bacterial_spot` | UNMAPPED | Excluded from 28-class development set | 2,297 |
| `Potato___healthy` | UNMAPPED | Excluded from 28-class development set | 152 |
| `Strawberry___Leaf_scorch` | UNMAPPED | Excluded from 28-class development set | 1,109 |
| `Tomato___Target_Spot` | UNMAPPED | Excluded from 28-class development set | 1,404 |

---

## Dataset Statistics & Split Overview

| Metric | Value |
|---|---|
| Total Raw PlantVillage Images | 54,305 |
| Total Original Classes | 38 |
| Mapped Development Classes | 28 |
| Total Mapped Images | 38,542 |
| Train Split (80.02%) | 30,841 images |
| Validation Split (10.03%) | 3,866 images |
| Local Test Split (9.95%) | 3,835 images |
| Total Unmapped Images (Retained in Raw) | 15,763 |
| File-Level Overlap | 0 |
| Leaf-Group / Photo Session Overlap | 0 |
| Corrupt / Unreadable Mapped Images | 0 |

---

## Preprocessing & Augmentation Pipeline

### 1. Preprocessing (Validation, Test & Inference)
- **Resize:** `(260, 260)` (EfficientNet-B2 native resolution)
- **ToTensor:** Converts PIL RGB image to `[0.0, 1.0]` float tensor
- **Normalization:** ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`
- **Deterministic:** NO random augmentations during validation, test, or deployment inference.

### 2. Field Generalization Augmentation (Training-Only)
Configurable via `training/config.py` (`USE_AUGMENTATION=True`, `AUGMENTATION_LEVEL="medium"`):
- **JPEG Compression Degradation:** Simulates low-bandwidth farmer photo uploads (Quality 40–85)
- **Random Crop & Zoom:** `RandomResizedCrop(260, scale=(0.8, 1.0))`
- **Flips:** Horizontal flip ($p=0.5$), Vertical flip ($p=0.2$)
- **Rotation:** `RandomRotation(degrees=20)`
- **Brightness, Contrast & Color Variation:** `ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.08)`
- **Mild Blur:** `GaussianBlur(kernel_size=3, sigma=(0.1, 1.2))`
- **Mild Gaussian Noise:** Additive sensor noise ($std=0.03, p=0.2$)
- **Occlusion Simulation:** `RandomErasing(p=0.2)`

---

## Reproducible Pipeline Commands

### 1. Run Class Mapping & Validation Pipeline
```bash
python data/validate_mapping.py
```

### 2. Execute Leakage-Safe Dataset Split
```bash
python data/split_dataset.py
```

### 3. Run DataLoader & Preprocessing Sanity Check
```bash
python data/sanity_check_dataloaders.py
```

---

## Artifacts Generated

- `data/class_mapping.csv`: Mapping table translating 38 PlantVillage classes to 28 development classes.
- `data/split_stats.json`: Split statistics containing exact train/val/test counts per class.
- `data/development_classes.json`: Reference list of the 28 development classes.
- `models/classes.json`: Model runtime class list.
