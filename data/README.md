# Dataset — Download, Class Mapping & Preparation

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
- Do **NOT** train models or create splits until explicitly commanded.
- The raw dataset is kept completely **untouched and intact**. Unmapped classes are retained in raw storage without deletion.

---

## 28-Class Development Label Set & Mapping

The project maps the 38 original PlantVillage raw class folders to the **28 official Development Classes**.

### Class Mapping Summary

| # | Development Class | Mapped Raw PlantVillage Directory | Status | Image Count |
|---|---|---|---|---|
| 1 | Apple — Apple Scab | `Apple___Apple_scab` | MAPPED | 630 |
| 2 | Apple — Healthy | `Apple___healthy` | MAPPED | 1,645 |
| 3 | Apple — Cedar Apple Rust | `Apple___Cedar_apple_rust` | MAPPED | 275 |
| 4 | Blueberry — Healthy | `Blueberry___healthy` | MAPPED | 1,502 |
| 5 | Cherry — Healthy | `Cherry_(including_sour)___healthy` | MAPPED | 854 |
| 6 | Corn — Cercospora Leaf Spot / Gray Leaf Spot | `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` | MAPPED | 513 |
| 7 | Corn — Common Rust | `Corn_(maize)___Common_rust_` | MAPPED | 1,192 |
| 8 | Corn — Northern Leaf Blight | `Corn_(maize)___Northern_Leaf_Blight` | MAPPED | 985 |
| 9 | Grape — Black Rot | `Grape___Black_rot` | MAPPED | 1,180 |
| 10 | Grape — Healthy | `Grape___healthy` | MAPPED | 423 |
| 11 | Peach — Healthy | `Peach___healthy` | MAPPED | 360 |
| 12 | Bell Pepper — Bacterial Spot | `Pepper,_bell___Bacterial_spot` | MAPPED | 997 |
| 13 | Bell Pepper — Healthy | `Pepper,_bell___healthy` | MAPPED | 1,478 |
| 14 | Potato — Early Blight | `Potato___Early_blight` | MAPPED | 1,000 |
| 15 | Potato — Late Blight | `Potato___Late_blight` | MAPPED | 1,000 |
| 16 | Raspberry — Healthy | `Raspberry___healthy` | MAPPED | 371 |
| 17 | Soybean — Healthy | `Soybean___healthy` | MAPPED | 5,090 |
| 18 | Squash — Powdery Mildew | `Squash___Powdery_mildew` | MAPPED | 1,835 |
| 19 | Strawberry — Healthy | `Strawberry___healthy` | MAPPED | 456 |
| 20 | Tomato — Bacterial Spot | `Tomato___Bacterial_spot` | MAPPED | 2,127 |
| 21 | Tomato — Early Blight | `Tomato___Early_blight` | MAPPED | 1,000 |
| 22 | Tomato — Late Blight | `Tomato___Late_blight` | MAPPED | 1,909 |
| 23 | Tomato — Leaf Mold | `Tomato___Leaf_Mold` | MAPPED | 952 |
| 24 | Tomato — Septoria Leaf Spot | `Tomato___Septoria_leaf_spot` | MAPPED | 1,771 |
| 25 | Tomato — Spider Mites / Two-Spotted Spider Mite | `Tomato___Spider_mites Two-spotted_spider_mite` | MAPPED | 1,676 |
| 26 | Tomato — Tomato Yellow Leaf Curl Virus | `Tomato___Tomato_Yellow_Leaf_Curl_Virus` | MAPPED | 5,357 |
| 27 | Tomato — Tomato Mosaic Virus | `Tomato___Tomato_mosaic_virus` | MAPPED | 373 |
| 28 | Tomato — Healthy | `Tomato___healthy` | MAPPED | 1,591 |

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

## Dataset Statistics Overview

| Metric | Value |
|---|---|
| Total Raw PlantVillage Images | 54,305 |
| Total Original Classes | 38 |
| Mapped Development Classes | 28 |
| Total Mapped Images | 38,542 |
| Total Unmapped Images (Retained in Raw) | 15,763 |
| Zero-Count Development Classes | 0 |
| Ambiguous Mappings | 0 |
| Corrupt / Unreadable Mapped Images | 0 |

---

## Reproducible Pipeline Commands

### 1. Download Raw Dataset
```bash
python data/download_dataset.py
```

### 2. Run Class Mapping & Validation Pipeline
```bash
python data/validate_mapping.py
```
This script:
- Creates/updates `data/class_mapping.csv`
- Saves `models/classes.json` and `data/development_classes.json` containing the 28 development classes
- Verifies image integrity and readability across all mapped images
- Validates 1-to-1 mapping uniqueness and reports counts

---

## Artifacts Generated

- `data/class_mapping.csv`: Complete mapping table mapping original classes to development classes.
- `models/classes.json`: List of 28 development classes for model runtime configuration.
- `data/development_classes.json`: Canonical reference for the 28 development classes.
