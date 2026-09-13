# 🌿 AgriSmart AI

> **AI-Powered Crop Disease Detection & Farm Intelligence System**  
> Built for Smart India Hackathon (SIH) / AI/ML Hackathon · 2026

---

## 🎯 Problem Statement & Capability

Crop diseases cause severe agricultural yield losses globally, threatening smallholder farmer livelihoods and food security. Early visual identification is critical to preventing widespread crop failure, yet farmers often lack access to timely expert diagnosis. 

**AgriSmart AI** provides fast, automated visual crop disease diagnosis directly from leaf images. By identifying specific disease symptoms and calculating prediction confidence, AgriSmart AI delivers immediate precautionary guidance to help farmers protect crop health and take targeted field action.

---

## 🚦 Current Project Status

| Phase | Capability / Module | Status | Details / Deliverables |
|---|---|---|---|
| **Phase 1** | Dataset Setup & 38→28 Class Mapping | ✅ Completed | 38,542 mapped images, 0 corrupt |
| **Phase 1** | Leakage-Safe Leaf-Group Splitting | ✅ Completed | 80/10/10 split, 0 physical leaf leakage |
| **Phase 2** | Model Architecture & Augmentation | ✅ Completed | EfficientNet-B2 (`timm`), 260x260 input |
| **Phase 2** | GPU Model Training & Fine-Tuning | ✅ Completed | 2-stage training on Colab GPU (Best Epoch 23) |
| **Phase 2** | Evaluation & Held-Out Testing | ✅ Completed | **0.9961 Test Macro-F1** across 3,835 test images |
| **Phase 3** | Local Model Integration & Verification | ✅ Completed | Weights & class JSON integrated (`models/verify_model.py`) |
| **Phase 4** | Inference Engine CLI & Python API | ✅ Completed | `inference/predict.py` with precaution lookup |
| **Phase 5** | External Field-Generalization Test | ✅ Completed | PlantDoc test set: **0.2311 Macro-F1** (domain gap measured) |
| **Phase 6** | FastAPI REST Server (`POST /predict`) | 🔄 Next Phase | Planned REST API server |
| **Phase 7** | Interactive Web Frontend | 🔄 Next Phase | Planned web user interface |

*Note: Core ML training, evaluation, external field-generalization testing, and local model integration are 100% completed and verified. REST API backend and Web Frontend modules are scheduled for the next development phase.*

---

## 📊 Datasets & 28 Development Classes

### Primary Training Dataset — PlantVillage
- **Source:** Hugging Face ([`mohanty/PlantVillage`](https://huggingface.co/datasets/mohanty/PlantVillage))
- **License:** CC0 / Public Domain
- **Citation:** Hughes, D. P., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics*. arXiv:1511.08060.
- **Mapped Dataset Size:** 38,542 images across 28 development classes (from 38 original folders).
- **Nature:** Controlled laboratory conditions — isolated leaves on uniform backgrounds.

### External Field-Generalization Dataset — PlantDoc
- **Source:** GitHub ([`pratikkayal/PlantDoc-Dataset`](https://github.com/pratikkayal/PlantDoc-Dataset))
- **License:** Creative Commons Attribution 4.0 International (CC-BY-4.0)
- **Citation:** Singh, D. et al. (2020). *PlantDoc: A Dataset for Visual Plant Disease Detection*. CoDS-COMAD 2020. DOI: 10.1145/3371158.3371196
- **Size:** 2,524 images (2,291 train / 233 test) across 28 classes (internet-scraped real-world field images).
- **Nature:** Real-world conditions — variable lighting, backgrounds, clutter; significantly harder than PlantVillage.
- **Mapping:** Explicit 28-folder → 28-class mapping documented in `data/plantdoc_class_mapping.csv`.

### Leakage-Safe Leaf-Group Split Methodology
To prevent severe data leakage caused by multi-view photos of the same physical leaf appearing in both training and test sets, split logic is performed strictly at the **leaf group** (`leaf_id`) level using fixed random seeds (`SEED=42`).

- **Train Split (80.02%)**: 30,841 images
- **Validation Split (10.03%)**: 3,866 images
- **Held-Out Test Split (9.95%)**: 3,835 images
- **Leakage Verification**: `0` file-level overlap, `0` leaf-group overlap across splits.

---

## 🧠 Model Architecture & Training

- **Backbone Architecture**: `EfficientNet-B2` (pretrained on ImageNet via `timm`)
- **Input Resolution**: `260 x 260` RGB pixels
- **Training Strategy**: 2-stage transfer learning (3 warmup epochs freezing backbone, followed by full fine-tuning with Cosine Annealing LR scheduler and AdamW optimizer)
- **Data Augmentation**: Training-time field sensor degradation (JPEG compression artifact simulation, random crop/scaling, rotation, color jitter, Gaussian noise, and occlusion erasing). Validation/Test uses clean resize and ImageNet normalization.

---

## 📈 Evaluation & Results

### ⚠️ Three Distinct Test Evaluations — Do NOT conflate

| Test Set | Source | Images | Macro-F1 | Accuracy | Nature |
|---|---|---|---|---|---|
| **PlantVillage Validation** | PlantVillage (in-domain) | 3,866 | **0.9979** | **99.79%** | Lab, controlled |
| **PlantVillage Local Test** | PlantVillage (in-domain) | 3,835 | **0.9961** | **99.71%** | Lab, controlled |
| **PlantDoc External Test** | PlantDoc (field images) | 233 | **0.2311** | **27.47%** | Real-world field |
| **Organizer Hidden Test** | SIH Competition | — | *TBD* | *TBD* | Official metric |

### PlantVillage In-Domain Results (Primary Training Metric)
Evaluated on the held-out leakage-safe PlantVillage test split:

| Metric | Validation | Held-Out Test |
|---|---|---|
| Macro-F1 | 0.9979 | **0.9961** |
| Accuracy | 99.79% | **99.71%** |
| Best Checkpoint | Epoch 23 | Epoch 23 |

### External PlantDoc Field-Generalization Results
Evaluated on the **original PlantDoc test split (233 images, 27 classes)** — a completely separate dataset of internet-scraped real-world field images **not used in training**.

| Metric | Result |
|---|---|
| **Macro-F1** | **0.2311** |
| **Accuracy** | **27.47%** |
| Images evaluated | 233 |
| Classes with F1 = 0 | 8 of 27 evaluated |
| Best class (Raspberry — Healthy) | F1 = 0.667 |

This large drop (0.9961 → 0.2311) confirms the **lab-to-field domain gap**: the baseline model was trained exclusively on controlled PlantVillage images and has not been adapted for real-world field conditions. This result is **expected and informative** — it establishes the baseline for domain adaptation work.

> **Note on the Organizer Hidden Test Set:** The official SIH/competition score uses the organizer's private held-out images. Neither PlantVillage local test nor PlantDoc results should be compared directly to it.

---

## 📂 Repository Structure & Key Model Files

```text
AgriSmart-AI/
├── README.md                           ← Main project documentation
├── requirements.txt                    ← Environment dependencies
├── AgriSmart_AI_Training_Colab.ipynb   ← Self-contained Colab training notebook
│
├── models/                             ← Integrated Model Artifacts
│   ├── README.md                       ← Model weights documentation
│   ├── agrismart_best.pth              ← Trained EfficientNet-B2 PyTorch weights (Epoch 23, 93.6 MB)
│   ├── classes.json                    ← 28-class index mapping
│   └── verify_model.py                 ← Model loading & forward-pass verification script
│
├── data/                               ← Dataset Pipeline
│   ├── README.md                       ← Dataset download & split documentation
│   ├── class_mapping.csv               ← 38 -> 28 PlantVillage class translation table
│   ├── plantdoc_class_mapping.csv      ← 28-folder -> 28-class PlantDoc mapping
│   ├── plantdoc_mapping.json           ← Machine-readable PlantDoc mapping dict
│   ├── download_dataset.py             ← PlantVillage downloader (HF data.zip)
│   ├── download_plantdoc.py            ← PlantDoc downloader (GitHub ZIP)
│   ├── inspect_plantdoc.py             ← PlantDoc health audit script
│   ├── prepare_plantdoc.py             ← PlantDoc -> AgriSmart class organizer
│   ├── validate_mapping.py             ← PlantVillage class mapping validator
│   ├── split_dataset.py                ← Leaf-group isolated 80/10/10 splitter
│   └── sanity_check_dataloaders.py     ← DataLoader verification script
│
├── training/                           ← Training Modules
│   ├── config.py                       ← Hyperparameters & paths configuration
│   ├── dataset.py                      ← Custom PyTorch Dataset classes
│   ├── preprocessing.py                ← Augmentation & transform pipelines
│   └── train.py                        ← Local training execution script
│
└── inference/                          ← Inference Engine
    └── predict.py                      ← CLI & Python API for disease prediction
```

---

## ⚙️ Setup & Verification Instructions

### 1. Clone & Setup Environment
```bash
git clone https://github.com/Parrthiv125/AgriSmart-AI.git
cd AgriSmart-AI
python -m venv venv

# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Reproducible Model Verification
Verify that the integrated EfficientNet-B2 model loads state weights and class mappings correctly:
```bash
python models/verify_model.py
```

### 3. Run Disease Prediction (CLI)
Predict crop disease class and view precautionary guidance for any leaf image:
```bash
python inference/predict.py --image path/to/leaf_photo.jpg
```

### 4. Run Disease Prediction (Python API)
```python
from inference.predict import predict

result = predict("path/to/leaf_photo.jpg")
print("Predicted Class:", result["class"])
print("Confidence:", result["confidence"])
print("Precaution:", result["precaution"])
```

---

## ⚠️ Limitations & Field Generalization

1. **Lab vs Field Domain Gap (Measured)**: External evaluation on the PlantDoc field dataset yielded Macro-F1 = 0.2311 vs 0.9961 on PlantVillage — confirming a significant domain gap. The baseline model was trained only on controlled lab images. Domain adaptation (fine-tuning on PlantDoc or mixed data) is the planned next step.
2. **Diagnostic Disclaimer**: AgriSmart AI provides automated screening and precautionary guidance. It is intended to assist farmers and extension workers, not replace qualified agronomists.
3. **Low-Confidence Handling**: Predictions with confidence below thresholds trigger a low-confidence warning advising the user to provide a clearer, better-lit leaf photo.
4. **PlantDoc Coverage**: The PlantDoc test split does not include images for `Tomato — Spider Mites / Two-Spotted Spider Mite` (0 test images in that split), so that class is excluded from the external field evaluation.

---

## 📜 License & Citation

- **License**: MIT License
- **PlantVillage Dataset**: CC0 Public Domain ([Hughes & Salathé, 2015](https://huggingface.co/datasets/mohanty/PlantVillage))
- **PlantDoc Dataset**: CC-BY-4.0 ([Singh et al., CoDS-COMAD 2020](https://github.com/pratikkayal/PlantDoc-Dataset))

---

*"AgriSmart AI turns visual crop diagnosis into actionable agricultural decisions."*
