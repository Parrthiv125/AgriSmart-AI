# 🌿 AgriSmart AI

> **AI-powered crop disease detection and farm intelligence system**  
> Built for the AI/ML Hackathon · September 2026

---

## 🎯 Problem Statement

Crop diseases cause billions of dollars in agricultural losses annually. Smallholder farmers often lack timely access to expert diagnosis. AgriSmart AI provides instant, accurate crop disease detection from a single leaf photograph — turning visual diagnosis into actionable farm decisions.

---

## 🏆 Project Objective

Build a reliable, reproducible AI system that:
1. **Identifies crop diseases** from leaf/crop images with high Macro-F1
2. **Generalises** from clean lab images (PlantVillage) to real-world field photographs
3. **Provides actionable guidance** — confidence score + precautionary advice
4. **Integrates** into a usable web interface for farmers

---

## ✅ Core Features (Mandatory)

| Feature | Status |
|---|---|
| Disease classification from leaf image | 🔄 In Progress |
| Confidence score (High / Medium / Low) | 🔄 In Progress |
| Precautionary guidance | 🔄 In Progress |
| FastAPI backend (`POST /predict`) | 🔄 In Progress |
| Responsive web frontend | 🔄 In Progress |
| Macro-F1 evaluation | 🔄 In Progress |
| Confusion matrix + per-class metrics | 🔄 In Progress |
| Robustness testing | 🔄 In Progress |
| Grad-CAM explainability | 🔄 In Progress |
| Reproducible inference (`predict.py`) | 🔄 In Progress |

## 🌟 Bonus Features (Optional — after core is complete)

| Module | Status |
|---|---|
| Smart Irrigation | ⬜ Planned |
| Weather Intelligence | ⬜ Planned |
| Farmer Assistant (LLM) | ⬜ Planned |
| Sustainability Score | ⬜ Planned |
| Crop Recommendation | ⬜ Planned |
| Simulated IoT | ⬜ Planned |
| Agentic Advisor | ⬜ Planned |

---

## 🏗️ Architecture

```
Leaf Image
    ↓
Preprocessing (resize, normalize)
    ↓
EfficientNet-B2 (Transfer Learning)
    ↓
Disease Class + Confidence
    ↓
Grad-CAM Heatmap (optional)
    ↓
Precautionary Guidance
    ↓
FastAPI Backend
    ↓
Web Frontend
```

---

## 📂 Repository Structure

```
AgriSmart-AI/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── README.md               ← Dataset download + prep instructions
│
├── training/
│   ├── config.py               ← All hyperparameters & paths
│   ├── dataset.py              ← Dataset loading, splitting
│   ├── preprocessing.py        ← Transforms & augmentation
│   └── train.py                ← Training loop
│
├── evaluation/
│   ├── evaluate.py             ← Full evaluation pipeline
│   ├── metrics.py              ← Macro-F1, confusion matrix, etc.
│   ├── robustness.py           ← Robustness testing
│   └── results/                ← Saved plots & CSVs (git-tracked if small)
│
├── inference/
│   └── predict.py              ← CLI + importable predict() function
│
├── models/
│   └── README.md               ← How to obtain trained weights
│
├── backend/
│   ├── main.py                 ← FastAPI app
│   ├── routes/
│   └── schemas.py
│
├── frontend/
│   └── ...                     ← React / plain HTML web app
│
├── modules/
│   ├── weather/
│   ├── irrigation/
│   ├── crop_recommendation/
│   ├── sustainability/
│   ├── assistant/
│   └── agent/
│
├── tests/
│
└── docs/
    ├── architecture.md
    ├── dataset.md
    ├── model.md
    └── evaluation.md
```

---

## 📊 Dataset

**Primary Dataset:** [PlantVillage on Hugging Face](https://huggingface.co/datasets/mohanty/PlantVillage)  
**Size:** ~54,306 images  
**License:** CC0 / Public Domain

> ⚠️ The dataset is **NOT** committed to this repository. See [`data/README.md`](data/README.md) for download and preparation instructions.

The model is trained on PlantVillage (clean/lab images) and evaluated for generalisation to real-world field conditions (PlantDoc-style imagery).

---

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_ORG/AgriSmart-AI.git
cd AgriSmart-AI
```

### 2. Create Python environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Prepare the dataset
```bash
# See data/README.md for full instructions
python data/download_dataset.py
```

---

## 🧠 Training

```bash
cd training
python train.py --config config.py
```

Key hyperparameters are in [`training/config.py`](training/config.py).  
All experiment runs are logged to `experiments.csv`.

---

## 📈 Evaluation

```bash
cd evaluation
python evaluate.py --model_path models/agrismart_best.pth
```

Outputs:
- Macro-F1 score
- Confusion matrix (saved to `evaluation/results/`)
- Per-class precision, recall, F1
- Robustness table

### Results

> *(Updated after training is complete)*

| Metric | Value |
|---|---|
| Validation Accuracy | TBD |
| Validation Macro-F1 | TBD |
| Robustness (Blur) Macro-F1 | TBD |
| Robustness (Brightness) Macro-F1 | TBD |

---

## 🔍 Inference

### Python API
```python
from inference.predict import predict

result = predict("path/to/leaf.jpg")
print(result)
# {
#   "class": "Tomato Early Blight",
#   "confidence": 0.914,
#   "confidence_level": "High",
#   "precaution": "..."
# }
```

### Command Line
```bash
python inference/predict.py --image path/to/leaf.jpg
```

---

## 🚀 Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Endpoints:**
- `GET /health` — Health check
- `POST /predict` — Upload image, get disease prediction
- `POST /explain` — Get Grad-CAM heatmap

API documentation: `http://localhost:8000/docs`

---

## 🌐 Frontend

```bash
cd frontend
# (see frontend/README.md for framework-specific instructions)
```

---

## 🏅 Model

**Architecture:** EfficientNet-B2 (pretrained on ImageNet, fine-tuned on PlantVillage)  
**Input size:** 260×260  
**Classes:** *(Official class list from hackathon organizers — see `models/classes.json`)*

Model weights are available at: *(link to be added after training)*

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## ⚠️ Limitations

- Trained primarily on lab-condition PlantVillage images; field generalisation is a known challenge addressed via robustness experiments
- Not a substitute for agronomist professional advice
- Confidence thresholds should be used; low-confidence predictions require clearer images

---

## 📚 Documentation

See the [`docs/`](docs/) folder for detailed documentation:
- [`docs/architecture.md`](docs/architecture.md) — System architecture
- [`docs/dataset.md`](docs/dataset.md) — Dataset details
- [`docs/model.md`](docs/model.md) — Model architecture & training
- [`docs/evaluation.md`](docs/evaluation.md) — Evaluation methodology

---

## 👥 Team

AgriSmart AI Hackathon Team — 2026

---

## 📜 License

MIT License — See `LICENSE` file.

---

*"AgriSmart AI turns crop-image diagnosis into an actionable agricultural decision."*
