# 🌿 AgriSmart AI

AgriSmart AI is an end-to-end crop disease diagnostic system. It allows farmers and agronomists to photograph or upload a leaf image to receive real-time disease identification, confidence scores, and actionable precautionary advice.

---

## Key Features

- **28 Crop Disease Classes**: Covers 12 crops (Tomato, Potato, Corn, Apple, Grape, Pepper, Strawberry, Cherry, Peach, Blueberry, Raspberry, Squash).
- **Field-Adapted Model 2**: Trained on both lab and real-world field images to bridge the laboratory-to-field domain gap.
- **Actionable Guidance**: Delivers immediate cultural and organic treatment advice for every identified disease.
- **Confidence Scoring**: Outputs softmax confidence and categorizes predictions into High, Medium, or Low confidence.
- **Account-Isolated Local Storage**: Supports multiple user accounts on the same device with private scan history and profile data in browser storage.
- **Multilingual Support**: UI available in English, Hindi, and Gujarati.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | FastAPI, Uvicorn, Pydantic, Python-Multipart |
| **Machine Learning** | PyTorch, torchvision, timm (EfficientNet-B2), Pillow |
| **Data & Evaluation** | NumPy, scikit-learn, Hugging Face Datasets |

---

## System Architecture

```text
Browser (React 19 + Vite)
    │  POST /predict (multipart/form-data)
    ▼
FastAPI REST API (Port 8000)
    │  Normalized 260x260 image tensor
    ▼
EfficientNet-B2 Model 2 (PyTorch)
    │  JSON prediction + precautions
    ▼
Browser Display & Account-Isolated localStorage
```

1. The frontend captures an image via device camera or file upload.
2. The image is sent to FastAPI (`POST /predict`), which runs inference through the preloaded EfficientNet-B2 model.
3. The response returns the diagnosed class, confidence score, and treatment advice, which the frontend displays and stores in the user's isolated local history.

---

## ML Model & Evaluation

### Model Details
- **Architecture**: `EfficientNet-B2` (pretrained on ImageNet via `timm`, 9.1M parameters).
- **Input Resolution**: `260 x 260` RGB pixels with standard ImageNet normalization.
- **Training Strategy**: Two-stage transfer learning using Cosine Annealing learning rate schedule and AdamW optimizer.
- **Data Leakage Guard**: Multi-view images of the same physical leaf are strictly grouped together during dataset splitting (`leaf_id` grouping).

### Results

| Model Checkpoint | Training Data | PlantDoc Test Macro-F1 (Field) | PlantDoc Test Accuracy (Field) | Internal Val Macro-F1 | Internal Val Accuracy |
|---|---|---|---|---|---|
| **Model 1 (Baseline)** | Lab (PlantVillage) | 0.2311 | 27.47% | 0.9979 | 99.79% |
| **Model 2 (Field-Adapted)** | Lab + Field Mixed | **0.5904** | **63.09%** | **0.9555** | **96.86%** |

Model 2 delivers a **+155.5% relative boost** in Macro-F1 on real-world field images over the lab-only baseline, significantly reducing the laboratory-to-field performance drop.

---

## Getting Started

### Prerequisites
- Python 3.10+ (tested on 3.12)
- Node.js 18+ and npm

### 1. Clone & Python Environment
```bash
git clone https://github.com/Parrthiv125/AgriSmart-AI.git
cd AgriSmart-AI

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1   # On Linux/macOS: source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Verify model checkpoint
python models/verify_model.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## Running the Application

Start the backend and frontend in separate terminals:

### Terminal 1: Backend
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API is available at `http://127.0.0.1:8000`
- Interactive Swagger docs at `http://127.0.0.1:8000/docs`
- Health check at `http://127.0.0.1:8000/health`

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
- Web UI is available at `http://localhost:5173`

---

## API & CLI Usage

### FastAPI `POST /predict`
Upload a leaf image via HTTP multipart request:
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -F "file=@path/to/leaf.jpg"
```

Example response:
```json
{
  "class_label": "Tomato — Early Blight",
  "confidence": 0.9642,
  "disease": "Tomato — Early Blight",
  "confidence_pct": "96.4%",
  "confidence_level": "High",
  "precaution": "Remove and destroy affected leaves. Apply copper-based fungicide or mancozeb. Avoid overhead irrigation. Rotate crops; do not plant tomatoes in the same soil for >=2 years.",
  "low_confidence_warning": null,
  "top_predictions": [
    { "class": "Tomato — Early Blight", "confidence": 0.9642 },
    { "class": "Tomato — Septoria Leaf Spot", "confidence": 0.0215 },
    { "class": "Tomato — Target Spot", "confidence": 0.0084 }
  ]
}
```

### CLI Inference
Run predictions directly from the terminal:
```bash
python inference/predict.py --image path/to/leaf.jpg
```

---

## Project Structure

```text
AgriSmart-AI/
├── backend/               # FastAPI application (main.py)
├── frontend/              # React 19 web application (Vite, Tailwind)
│   ├── src/components/    # UI components (camera, scan, cards)
│   ├── src/pages/         # Dashboard, Scan, History, Auth pages
│   └── src/services/      # API client, isolated auth & history services
├── models/                # Checkpoints and class mapping
│   ├── agrismart_field_adapted_best.pth  # Model 2 checkpoint (93.6 MB)
│   ├── classes.json       # 28 class index mapping
│   └── verify_model.py    # Checkpoint integrity test
├── data/                  # Dataset preparation and split scripts
├── training/              # Training configuration, transforms, and pipeline
├── inference/             # predict.py inference module
└── tests/                 # Unit tests
```

---

## Limitations

- **Closed-Set Classification**: The model classifies inputs strictly into one of the 28 supported classes; non-leaf images will still receive a classification.
- **Field Variations**: Heavy occlusion, extreme shadows, or severe blur can reduce diagnostic accuracy.
- **Advisory Only**: Predictions are statistical recommendations to assist farmers, not guaranteed laboratory diagnoses.
- **Client-Side Storage**: Profile and scan histories are saved in the browser's `localStorage` and are not synchronized across devices or clouds.