# ðŸŒ¿ AgriSmart AI

> **Intelligent Agriculture for a Sustainable Future**
> AI-Powered Visual Crop Disease Detection & Localized Farm Decision Support
> *Developed for the Smart India Hackathon (SIH) 2026 Challenge*

---

## ðŸ“Œ 1. Project Overview

### Problem Statement
Crop diseases pose an existential threat to global food security, smallholder farmer livelihoods, and agricultural supply chains. Early, accurate visual identification is critical to arresting contagion and minimizing yield loss. However, smallholder farmers often lack access to timely agronomic expertise, extension officers, or expensive lab diagnostics.

### Target Users
- **Smallholder Farmers & Growers**: Need fast, actionable identification of foliar disease symptoms in the field using a smartphone or laptop camera.
- **Agricultural Extension Workers & Field Officers**: Need a reliable offline/local diagnostic tool during village-level advisory visits.
- **Agronomy Students & Researchers**: Need a reproducible, benchmarked computer vision pipeline for plant pathology.

### What the System Actually Does
**AgriSmart AI** is an end-to-end, production-ready crop health diagnostic platform:
1. **Captures leaf imagery** via live camera feed or local file upload through a responsive, mobile-first React web frontend.
2. **Executes deep learning inference** via an asynchronous FastAPI REST backend powered by **Field-Adapted Model 2** (an `EfficientNet-B2` convolutional neural network trained on combined laboratory and field imagery).
3. **Diagnoses 28 crop-disease/health conditions** across 12 crop families, outputting categorical disease labels, statistical confidence scores, and confidence bands (High / Medium / Low).
4. **Delivers actionable agronomic precautions**, including cultural and organic mitigation advice tailored to the diagnosed condition.
5. **Maintains account-isolated local scan history and farmer profiles** directly within the browser's `localStorage` for multi-user device sharing without requiring cloud databases.

---

## âœ¨ 2. Final Implemented Features

- ðŸ§  **AI Crop Disease Diagnosis**: Real-time classification covering **28 distinct crop-disease and healthy classes** across 12 agricultural crops (Apple, Bell Pepper, Blueberry, Cherry, Corn/Maize, Grape, Peach, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato).
- ðŸŒ¾ **Field-Adapted Model 2 Checkpoint**: Integrated production model weights (`models/agrismart_field_adapted_best.pth`, 93.6 MB) specifically adapted for real-world field photography conditions (variable lighting, complex foliage backgrounds, natural blur).
- ðŸ“Š **Confidence & Uncertainty Reporting**: Explicit percentage confidence scores with categorical levels (`High` $\ge 80\%$, `Medium` $60\text{â€“}79\%$, `Low` $< 60\%$) and automated warnings on low-confidence observations.
- ðŸ“‹ **Agronomic Precaution Knowledge Base**: Documented, responsible precautionary guidance and cultural/organic treatment recommendations accompanying every diagnosed disease.
- âš¡ **High-Performance FastAPI REST Server**: Asynchronous Python backend (`backend/main.py`) providing `POST /predict`, health check endpoints (`GET /health`), and interactive OpenAPI/Swagger documentation (`/docs`).
- ðŸ“± **Modern Farmer-Centric Frontend**: Built with React 19, TypeScript, Vite, and Tailwind CSS. Features live camera capture, drag-and-drop file upload, instant image previews, interactive disease catalog, and metric dashboards.
- ðŸ”’ **Account-Specific Profile & History Isolation**: Multi-tenant client-side session management. Different registered or logged-in users on the same device have isolated scan histories and profiles stored under deterministic `localStorage` keys (`agrismart_profile_<userId>`, `agrismart_history_<userId>`).
- ðŸŒ **Multilingual Interface Translations**: Full localized UI translations for English (`en`), Hindi (`hi`), and Gujarati (`gu`) covering navigation, buttons, disease names, and dashboard metrics.

---

## ðŸš« 3. Features NOT Implemented (Transparent Boundary)

To ensure strict academic and competition integrity, the following features are **explicitly NOT implemented** in this repository:

- âŒ **No Out-of-Distribution (OOD) / Non-Leaf Rejection Layer**: The model is a 28-class closed-set classifier. Uploading non-leaf objects, flowers, or unsupported crops will still be classified into the nearest of the 28 supported classes.
- âŒ **No Cloud Database / Remote Backend DB**: There is no PostgreSQL, MySQL, Supabase, or Firebase database connected. All user credentials, profiles, and scan histories exist solely in the browser's client-side `localStorage`.
- âŒ **No Cloud Image Storage**: Uploaded leaf images are processed in-memory by FastAPI and displayed via ephemeral browser Object URLs. Images are not permanently stored in AWS S3, Cloudinary, or remote disks.
- âŒ **No Automated Irrigation / IoT Hardware**: No physical soil moisture sensors, telemetry, or microcontroller hardware integrations.
- âŒ **No Live Weather API**: Live meteorological forecast feeds are not integrated into the prediction pipeline.
- âŒ **No Autonomous Agentic AI / LLM Multi-Agent Orchestrators**: Diagnostic results are generated strictly by the EfficientNet-B2 neural network and rule-based agronomic lookups.

---

## ðŸ—ï¸ 4. System Architecture

```text
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                        CLIENT LAYER (Browser)                          â”‚
â”‚                                                                        â”‚
â”‚   React 19 + TypeScript + Vite + Tailwind CSS (Port 5173 / 3000)      â”‚
â”‚   â”œâ”€â”€ CameraCapture / Drag-and-Drop File Upload                        â”‚
â”‚   â”œâ”€â”€ I18n Context (English / Hindi / Gujarati)                        â”‚
â”‚   â”œâ”€â”€ Client Auth & Isolated localStorage (Profile & History)          â”‚
â”‚   â””â”€â”€ Result Display (Disease Card, Confidence Meter, Precautions)     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚ HTTP POST /predict (multipart/form-data)
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                       BACKEND API LAYER (FastAPI)                      â”‚
â”‚                                                                        â”‚
â”‚   Uvicorn ASGI Server (Port 8000)                                      â”‚
â”‚   â”œâ”€â”€ CORS Middleware & Request Validation (Pydantic)                  â”‚
â”‚   â”œâ”€â”€ Image Processing & Preprocessing (PIL, 260x260, ImageNet Norm)   â”‚
â”‚   â””â”€â”€ Preloaded Model 2 Instance (Singleton Memory Cache)              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚ PyTorch Tensor Forward Pass
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                       DEEP LEARNING MODEL LAYER                        â”‚
â”‚                                                                        â”‚
â”‚   EfficientNet-B2 Neural Network (`timm`)                              â”‚
â”‚   â”œâ”€â”€ Model Checkpoint: models/agrismart_field_adapted_best.pth (93MB) â”‚
â”‚   â”œâ”€â”€ 28-Class Linear Classification Head (Softmax Probabilities)      â”‚
â”‚   â””â”€â”€ Canonical Inference Engine (`inference/predict.py`)              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚ Returns PredictionResult JSON
                                    â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   STRUCTURED API RESPONSE PAYLOAD                      â”‚
â”‚                                                                        â”‚
â”‚   {                                                                    â”‚
â”‚     "class_label": "Tomato â€” Early Blight",                            â”‚
â”‚     "confidence": 0.9642,                                              â”‚
â”‚     "confidence_pct": "96.4%",                                         â”‚
â”‚     "confidence_level": "High",                                        â”‚
â”‚     "precaution": "Remove and destroy affected leaves. Apply copper...",â”‚
â”‚     "top_predictions": [...]                                           â”‚
â”‚   }                                                                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Runtime Ports and Endpoints
| Component | Default Host / Port | Key Endpoints |
|---|---|---|
| **FastAPI REST Server** | `http://127.0.0.1:8000` | `POST /predict`, `GET /health`, `GET /docs` |
| **React Web Application** | `http://localhost:5173` | `/`, `/dashboard`, `/scan`, `/history`, `/help` |

---

## ðŸ§  5. Machine Learning Pipeline & Methodology

### Architecture Specifications
- **Backbone**: `EfficientNet-B2` (pretrained on ImageNet-1k via `timm`)
- **Input Dimension**: `260 x 260` RGB pixels (native EfficientNet-B2 resolution)
- **Parameters**: 9.1 million parameters
- **Normalization**: Standard ImageNet channel constants ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$)
- **Loss Function**: Cross-Entropy Loss with AdamW optimizer and Cosine Annealing learning rate scheduling.

### The 28 Supported Crop & Disease Classes
```text
 0: Apple â€” Apple Scab                          14: Potato â€” Late Blight
 1: Apple â€” Cedar Apple Rust                    15: Raspberry â€” Healthy
 2: Apple â€” Healthy                             16: Soybean â€” Healthy
 3: Bell Pepper â€” Bacterial Spot                17: Squash â€” Powdery Mildew
 4: Bell Pepper â€” Healthy                       18: Strawberry â€” Healthy
 5: Blueberry â€” Healthy                         19: Tomato â€” Bacterial Spot
 6: Cherry â€” Healthy                            20: Tomato â€” Early Blight
 7: Corn â€” Cercospora Leaf Spot / Gray Leaf Spot21: Tomato â€” Healthy
 8: Corn â€” Common Rust                          22: Tomato â€” Late Blight
 9: Corn â€” Northern Leaf Blight                 23: Tomato â€” Leaf Mold
10: Grape â€” Black Rot                           24: Tomato â€” Septoria Leaf Spot
11: Grape â€” Healthy                             25: Tomato â€” Spider Mites / Two-Spotted Spider Mite
12: Peach â€” Healthy                             26: Tomato â€” Tomato Mosaic Virus
13: Potato â€” Early Blight                       27: Tomato â€” Tomato Yellow Leaf Curl Virus
```

### Why Model 2 (Field-Adapted) Was Created
Standard laboratory datasets such as **PlantVillage** contain leaves photographed on uniform gray/black paper in controlled indoor lighting. Models trained exclusively on laboratory imagery suffer from the **lab-to-field domain gap**â€”they fail significantly when presented with real-world field photographs featuring sunlight variations, dirt, shadows, and cluttered background foliage.

To solve this, **Model 2** was engineered:
1. **Base Initialization**: Initialized from trained Model 1 weights.
2. **Domain Mixture**: Fine-tuned on a merged training distribution combining PlantVillage laboratory imagery with real field photographs from the **PlantDoc** training set.
3. **Sensor-Aware Augmentation**: Augmented with simulated field degradations (JPEG compression artifact simulation, random Gaussian blur, color jitter, affine perspective shifts, and random occlusion cropping).

---

## ðŸ“ˆ 6. Verified Evaluation Results & Benchmarks

The following table presents the verified empirical evaluation results comparing the laboratory-only baseline (Model 1) against the field-adapted model (Model 2).

### Comprehensive Benchmark Summary

| Model Checkpoint | Target Domain & Training Source | PlantDoc External Test Macro-F1 (Field) | PlantDoc External Test Accuracy (Field) | Internal Validation Macro-F1 | Internal Validation Accuracy |
|---|---|---|---|---|---|
| **Model 1 Baseline** (`agrismart_best.pth`) | Lab-only (PlantVillage) | **0.2311** (23.11%) | **0.2747** (27.47%) | 0.9979 | 99.79% |
| **Model 2 Field-Adapted** (`agrismart_field_adapted_best.pth`) | Lab + Field Mixed Training | **0.5904** (59.04%) | **0.6309** (63.09%) | **0.9555** | **96.86%** |
| **Improvement ($\Delta$)** | â€” | **+0.3593 (+155.5% relative)** | **+0.3562 (+129.7% relative)** | *Field generalized* | *Field generalized* |

> âš ï¸ **Critical Clarification on Scores:**
> - **Internal Validation (0.9555 Macro-F1 / 0.9686 Accuracy)** represents Model 2 performance on the internal validation split (8,636 images).
> - **PlantDoc External Test (0.5904 Macro-F1 / 0.6309 Accuracy)** represents zero-leakage evaluation on the external 233-image field test set.
> - **Do NOT represent validation performance as the official hidden SIH organizer score.** The official SIH evaluation score is determined independently by competition judges using their private held-out test set.

---

## ðŸ—„ï¸ 7. Dataset Governance & Data Leakage Prevention

### Primary Datasets
1. **PlantVillage Dataset**:
   - Source: Hugging Face (`mohanty/PlantVillage`) | License: CC0 / Public Domain
   - 38,542 images mapped into the 28 AgriSmart class taxonomy.
   - Controlled laboratory setting.
2. **PlantDoc Dataset**:
   - Source: GitHub (`pratikkayal/PlantDoc-Dataset`) | License: CC-BY-4.0
   - 2,524 images (2,291 train / 233 test) of internet-sourced real field photographs across agricultural crops.

### Zero-Leakage Protocol
To guarantee strict statistical validity and eliminate data leakage:
- **Leaf-Group Isolation**: Split logic in `data/split_dataset.py` groups multi-view photos of the same physical leaf (`leaf_id`) into the same split partition, preventing the model from memorizing identical leaves across train and test sets.
- **Locked Test-Set Isolation**: The 233 PlantDoc test images and PlantVillage held-out test images were **NEVER included in training or hyperparameter tuning** for either Model 1 or Model 2.
- **Cryptographic Audit**: All split datasets are verified via SHA256 file hashes to ensure zero overlap between train, validation, and test directories.

---

## ðŸ“ 8. Metrics, Artifacts & Checkpoint Files

| Artifact | File Path | Description |
|---|---|---|
| **Active Production Model (Model 2)** | [`models/agrismart_field_adapted_best.pth`](file:///d:/Agrismart_AI/models/agrismart_field_adapted_best.pth) | Best field-adapted weights (Epoch 17, 93.6 MB) |
| **Baseline Model (Model 1)** | [`models/agrismart_best.pth`](file:///d:/Agrismart_AI/models/agrismart_best.pth) | Lab-trained baseline weights (Epoch 23, 93.6 MB) |
| **Class Taxonomy** | [`models/classes.json`](file:///d:/Agrismart_AI/models/classes.json) | 28-class JSON index mapping |
| **Model Verification Script** | [`models/verify_model.py`](file:///d:/Agrismart_AI/models/verify_model.py) | Verifies weight integrity, architecture, and forward pass |
| **Model 2 Training Logs** | [`experiments_model2.csv`](file:///d:/Agrismart_AI/experiments_model2.csv) | Per-epoch loss, accuracy, and macro-F1 logs |
| **Canonical Inference Interface** | [`inference/predict.py`](file:///d:/Agrismart_AI/inference/predict.py) | CLI and Python API prediction interface |

---

## ðŸ’» 9. Installation & Running Guide (Windows Clean Clone)

Follow these exact step-by-step commands to run the complete system on Windows PowerShell.

### Prerequisites
- **Python**: Version `3.10` or higher (tested on Python `3.12`)
- **Node.js**: Version `18.0.0` or higher (tested on Node `v22.18.0` / npm `10.8.2`)
- **Git**: Installed and available in PowerShell PATH

### Step 1: Clone the Repository
```powershell
git clone https://github.com/Parrthiv125/AgriSmart-AI.git
cd AgriSmart-AI
```

### Step 2: Set Up Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Verify Model Weights & Checkpoint Integrity
```powershell
python models/verify_model.py
```
*Expected output: `SUCCESS: EfficientNet-B2 MODEL INTEGRATION & VERIFICATION PASSED`*

### Step 5: Start the FastAPI Backend Server (Terminal 1)
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend is now active at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.*

### Step 6: Install Frontend Dependencies & Start React App (Terminal 2)
Open a new PowerShell terminal:
```powershell
cd d:\Agrismart_AI\frontend
npm install
npm run dev
```
*Frontend is now active at `http://localhost:5173`.*

---

## ðŸ“¡ 10. Prediction Usage & API Specification

### Option A: Via FastAPI REST API (`POST /predict`)

#### Example Request (`curl`):
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/leaf_sample.jpg"
```

#### Example JSON Response:
```json
{
  "class_label": "Tomato â€” Early Blight",
  "confidence": 0.9642,
  "disease": "Tomato â€” Early Blight",
  "confidence_pct": "96.4%",
  "confidence_level": "High",
  "precaution": "Remove and destroy affected leaves. Apply copper-based fungicide or mancozeb. Avoid overhead irrigation. Rotate crops; do not plant tomatoes in the same soil for >=2 years.",
  "low_confidence_warning": null,
  "top_predictions": [
    {
      "class": "Tomato â€” Early Blight",
      "confidence": 0.9642
    },
    {
      "class": "Tomato â€” Septoria Leaf Spot",
      "confidence": 0.0215
    },
    {
      "class": "Tomato â€” Target Spot",
      "confidence": 0.0084
    }
  ]
}
```

### Option B: Via Python CLI / Scripting

```bash
# Run CLI prediction on a single image
python inference/predict.py --image path/to/leaf.jpg
```

```python
# Import canonical prediction function in Python
from inference.predict import predict

result = predict("path/to/leaf.jpg", top_k=3)
print(f"Diagnosed: {result['class']} ({result['confidence']*100:.1f}%)")
print(f"Precaution: {result['precaution']}")
```

---

## ðŸ–¥ï¸ 11. Frontend Usage & Storage Architecture

### User Workflow
1. **Authentication**: Users can sign in or register with their name, email, farm name, and location.
2. **Leaf Capture**: Users navigate to `/scan` and choose either live camera capture or image file upload.
3. **Inference & Diagnosis**: The frontend posts the file to the live `/predict` FastAPI endpoint and displays the diagnostic result with confidence meters and agronomic guidance.
4. **Scan History**: Completed scans are stored immediately in the active user's scan history.
5. **Dashboard**: Displays aggregated grower metrics (total scans, healthy vs. diseased ratio, and crop breakdown).

### Client-Side Isolation Architecture
- **No Cloud Sync**: Profile data and scan histories are stored strictly within the client browser's `localStorage`.
- **Deterministic Keys**: Each user's data is isolated under separate keys (`agrismart_profile_<userId>` and `agrismart_history_<userId>`).
- **Safe Session Management**: Logging out clears only the active session pointer (`agrismart_active_user_id`), preserving saved profile and scan records. When the same user logs back in, their previous scans and farm details are restored immediately.

---

## âš ï¸ 12. Known Limitations & Technical Disclosures

1. **Closed-Set Classification**: The model assumes the input is a leaf from one of the 28 supported categories. Non-agricultural objects, weed foliage, or unsupported crop leaves will be mapped to the closest mathematical match among the 28 classes.
2. **Field Complexity & Noise**: Extreme occlusions, severe motion blur, or multi-pathogen co-infections may lower diagnostic confidence or cause misclassification.
3. **Statistical Confidence vs. Agronomic Certainty**: Softmax confidence reflects neural network activation distribution, not a biological guarantee. Low-confidence predictions should always be verified by an agricultural extension specialist.
4. **Ephemeral Storage**: Uploaded leaf images generate temporary browser object URLs; image files themselves are not permanently stored on disk or in the cloud.
5. **Advisory Tool**: AgriSmart AI provides decision-support guidance; it is not a replacement for certified agricultural laboratory assays.

---

## ðŸ” 13. Security & Environment Configuration

- **Zero Hardcoded Secrets**: No API keys, database passwords, or private tokens are committed or stored in this repository.
- **Environment Overrides**:
  - `CORS_ORIGINS`: Configure allowed frontend domains in `.env` (defaults to localhost ports).
  - `VITE_API_BASE_URL`: Configure backend URL in `frontend/.env` (defaults to `http://localhost:8000`).

---

## ðŸ”„ 14. Reproducibility & Environment Specifications

- **Python Runtime**: `Python 3.12.4` (Compatible with Python $\ge 3.10$)
- **Node.js Runtime**: `Node v22.18.0` / `npm v10.8.2`
- **Dependencies**: Locked and specified in [`requirements.txt`](file:///d:/Agrismart_AI/requirements.txt) and [`frontend/package.json`](file:///d:/Agrismart_AI/frontend/package.json).
- **Seed Consistency**: Training and split scripts use deterministic random seed `SEED = 42`.

---

## ðŸ‘¥ 15. Credits, Citations & Declarations

### Academic Datasets
- **PlantVillage**: Hughes, D. P., & SalathÃ©, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics*. arXiv:1511.08060.
- **PlantDoc**: Singh, D. et al. (2020). *PlantDoc: A Dataset for Visual Plant Disease Detection*. Proceedings of the 7th ACM IKDD CoDS and 25th COMAD.

### Core Open-Source Libraries
- **PyTorch & Torchvision**: BSD-3 License
- **PyTorch Image Models (`timm`)**: Ross Wightman, Apache 2.0 License
- **FastAPI & Uvicorn**: SebastiÃ¡n RamÃ­rez, MIT License
- **React & Vite**: MIT License
- **Tailwind CSS**: MIT License
- **Lucide Icons**: ISC License

### Originality & Challenge Declaration
All integration code, domain adaptation scripts, data leakage prevention pipelines, FastAPI REST backend implementation, React frontend web interface, and account-isolated storage modules were developed specifically for the **Smart India Hackathon (SIH) 2026 AgriSmart AI Challenge**.

---

## ðŸŽ¬ 16. Recommended Demo Flow for Evaluators

1. **Launch Services**: Start FastAPI backend (`uvicorn backend.main:app --port 8000`) and React frontend (`npm run dev`).
2. **Access Web App**: Open `http://localhost:5173` in a web browser.
3. **Register / Sign In**: Create an account with farm details (e.g., "Sunrise Farm", "Tomato & Potato").
4. **Perform Leaf Scan**: Navigate to `/scan`, upload a leaf image (or use sample tomato/potato leaves from `data/processed_model2/val`).
5. **Review Real-Time Diagnosis**: View predicted disease label, confidence percentage, confidence tier badge, and agronomic precautions.
6. **Inspect History & Dashboard**: Navigate to `/dashboard` and `/history` to observe real-time scan metrics.
7. **Verify Multi-Tenant Isolation**: Log out, log in as a second user, and observe that scan history starts at 0 without data leakage.

---

## ðŸ“‚ 17. Repository Directory Structure

```text
AgriSmart-AI/
â”œâ”€â”€ README.md                           â† Master project documentation
â”œâ”€â”€ requirements.txt                    â† Python runtime dependencies
â”œâ”€â”€ .env.example                        â† Backend environment configuration template
â”œâ”€â”€ experiments_model2.csv              â† Model 2 training history and validation logs
â”œâ”€â”€ AgriSmart_AI_Training_Colab.ipynb   â† Standalone GPU training notebook
â”‚
â”œâ”€â”€ backend/                            â† FastAPI REST Application
â”‚   â””â”€â”€ main.py                         â† Server entrypoint, CORS, /predict & /health
â”‚
â”œâ”€â”€ frontend/                           â† React 19 Web Application
â”‚   â”œâ”€â”€ .env.example                    â† Frontend environment configuration template
â”‚   â”œâ”€â”€ package.json                    â† Node.js dependencies and build scripts
â”‚   â”œâ”€â”€ vite.config.ts                  â† Vite build configuration
â”‚   â””â”€â”€ src/
â”‚       â”œâ”€â”€ components/                 â† Reusable UI & scan components
â”‚       â”œâ”€â”€ context/                    â† Auth and Toast contexts
â”‚       â”œâ”€â”€ data/                       â† Disease catalog & multi-crop metadata
â”‚       â”œâ”€â”€ i18n/                       â† English, Hindi, and Gujarati translations
â”‚       â”œâ”€â”€ pages/                      â† Dashboard, Scan, History, Result, Auth pages
â”‚       â”œâ”€â”€ services/                   â† API client, isolated auth & history services
â”‚       â””â”€â”€ types/                      â† TypeScript interfaces for predictions & auth
â”‚
â”œâ”€â”€ models/                             â† Trained Model Artifacts
â”‚   â”œâ”€â”€ README.md                       â† Model weights guide
â”‚   â”œâ”€â”€ agrismart_field_adapted_best.pthâ† Model 2 active checkpoint (93.6 MB)
â”‚   â”œâ”€â”€ agrismart_best.pth              â† Model 1 baseline checkpoint (93.6 MB)
â”‚   â”œâ”€â”€ classes.json                    â† 28-class JSON index mapping
â”‚   â””â”€â”€ verify_model.py                 â† Checkpoint loading and forward-pass test
â”‚
â”œâ”€â”€ data/                               â† Data Preparation & Leakage Guard Pipelines
â”‚   â”œâ”€â”€ class_mapping.csv               â† 38 -> 28 class taxonomy mapping
â”‚   â”œâ”€â”€ plantdoc_class_mapping.csv      â† PlantDoc class taxonomy mapping
â”‚   â”œâ”€â”€ download_dataset.py             â† PlantVillage dataset downloader
â”‚   â”œâ”€â”€ download_plantdoc.py            â† PlantDoc dataset downloader
â”‚   â”œâ”€â”€ split_dataset.py                â† Leaf-group isolated 80/10/10 split generator
â”‚   â””â”€â”€ prepare_plantdoc.py             â† PlantDoc field dataset organizer
â”‚
â”œâ”€â”€ training/                           â† Core Training Framework
â”‚   â”œâ”€â”€ config.py                       â† Hyperparameters, paths & augmentation settings
â”‚   â”œâ”€â”€ dataset.py                      â† PyTorch Dataset class
â”‚   â”œâ”€â”€ preprocessing.py                â† Image transform & augmentation pipelines
â”‚   â””â”€â”€ train.py                        â† Local training execution engine
â”‚
â”œâ”€â”€ inference/                          â† Inference Engine
â”‚   â””â”€â”€ predict.py                      â† Canonical prediction & precaution lookup module
â”‚
â”œâ”€â”€ evaluation/                         â† Evaluation & Benchmark Scripts
â”‚   â”œâ”€â”€ evaluate_model.py               â† Comprehensive validation evaluator
â”‚   â””â”€â”€ evaluate_plantdoc.py            â† PlantDoc field test-set evaluator
â”‚
â”œâ”€â”€ scripts/                            â† Colab & Utility Automation
â”‚   â””â”€â”€ run_model2_colab.py             â† Headless Colab GPU training script
â”‚
â””â”€â”€ tests/                              â† Automated Test Suite
    â””â”€â”€ test_download_dataset.py        â† Dataset and backend test cases
```
