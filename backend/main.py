"""
AgriSmart AI — FastAPI Backend
================================
Endpoints:
  GET  /health     — Service health check
  POST /predict    — Disease prediction from uploaded image
  POST /explain    — Grad-CAM heatmap generation (optional)

Run with:
    uvicorn backend.main:app --reload --port 8000
    or from project root:
    uvicorn main:app --reload  (from inside backend/)
"""

import io
import os
import sys
import base64
import traceback
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from inference.predict import predict, load_model
from training.config import BEST_MODEL_PATH

# ── App Initialisation ────────────────────────────────────────────────────────

app = FastAPI(
    title="AgriSmart AI",
    description="Crop disease detection API — Upload a leaf image, get a disease prediction.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS: allow frontend development origins or environment override
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
env_origins = os.environ.get("CORS_ORIGINS")
allowed_origins = [o.strip() for o in env_origins.split(",") if o.strip()] if env_origins else DEFAULT_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload model at startup for fast inference
_model_ready = False

@app.on_event("startup")
async def startup_event():
    global _model_ready
    try:
        load_model(BEST_MODEL_PATH)
        _model_ready = True
        print("[OK] AgriSmart AI model loaded successfully.")
    except FileNotFoundError:
        print("[WARN] Model weights not found. Train the model first: python training/train.py")
        _model_ready = False


# ── Schemas ───────────────────────────────────────────────────────────────────

class PredictionResult(BaseModel):
    class_label: str = Field(..., description="Predicted crop disease class label")
    confidence: float = Field(..., description="Model confidence score between 0.0 and 1.0")
    disease: Optional[str] = Field(None, description="Disease name alias matching class_label")
    confidence_pct: Optional[str] = Field(None, description="Formatted confidence percentage string")
    confidence_level: Optional[str] = Field(None, description="Categorical confidence level (High, Medium, Low)")
    precaution: Optional[str] = Field(None, description="Agronomic precaution advice")
    low_confidence_warning: Optional[str] = Field(None, description="Warning if confidence is below threshold")
    top_predictions: Optional[list] = Field(None, description="Top-k alternative prediction candidates")


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    status: str
    model_loaded: bool
    message: str


# ── Utility ───────────────────────────────────────────────────────────────────

MAX_FILE_SIZE_MB = 10

async def read_image_from_upload(file: UploadFile) -> Image.Image:
    """Read and validate an uploaded image file."""
    # Check content type if specified
    valid_content_types = (
        "image/jpeg", "image/png", "image/webp", "image/bmp", "image/jpg", "application/octet-stream"
    )
    if file.content_type and file.content_type not in valid_content_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type: {file.content_type}. Use JPEG or PNG."
        )

    # Read bytes
    contents = await file.read()

    # Check file size
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB."
        )

    # Try to open image with PIL
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not decode image. Please upload a valid image file."
        )

    return img


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Returns service health and model status."""
    if _model_ready:
        return HealthResponse(
            status="ok",
            model_loaded=True,
            message="AgriSmart AI is ready to predict crop diseases.",
        )
    else:
        return HealthResponse(
            status="degraded",
            model_loaded=False,
            message="Model weights not loaded. Train the model first.",
        )


@app.post("/predict", response_model=PredictionResult, tags=["Disease Detection"])
@app.post("/api/v1/predict", response_model=PredictionResult, tags=["Disease Detection"])
async def predict_disease(
    file: Optional[UploadFile] = File(None, description="Leaf/crop image (JPEG or PNG)"),
    image: Optional[UploadFile] = File(None, description="Leaf/crop image alias"),
):
    """
    Upload a leaf image and receive:
    - Predicted disease class (class_label)
    - Confidence score
    - Confidence level (High / Medium / Low)
    - Precautionary guidance
    - Top-3 alternative predictions
    """
    if not _model_ready:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please contact the administrator or train the model first."
        )

    upload = file or image
    if upload is None:
        raise HTTPException(
            status_code=400,
            detail="No image file provided. Upload using key 'file' or 'image'."
        )

    img = await read_image_from_upload(upload)

    try:
        result = predict(img, top_k=3)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    return PredictionResult(
        class_label=result["class"],
        confidence=result["confidence"],
        disease=result["class"],
        confidence_pct=f"{result['confidence']*100:.1f}%",
        confidence_level=result["confidence_level"],
        precaution=result["precaution"],
        low_confidence_warning=result["low_confidence_warning"],
        top_predictions=result["top_k"],
    )


@app.post("/explain", tags=["Explainability"])
async def explain_prediction(file: UploadFile = File(..., description="Leaf/crop image for Grad-CAM")):
    """
    Generate a Grad-CAM heatmap for model explainability.
    Returns the prediction result + base64-encoded heatmap image.
    """
    if not _model_ready:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    img = await read_image_from_upload(file)

    try:
        from backend.explainability import generate_gradcam
        result = predict(img, top_k=1)
        heatmap_b64 = generate_gradcam(img)

        return JSONResponse({
            "disease": result["class"],
            "confidence": result["confidence"],
            "confidence_level": result["confidence_level"],
            "heatmap_base64": heatmap_b64,
        })

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Grad-CAM not yet available. Complete core training first."
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Explainability failed: {str(e)}")


# ── Error Handlers ────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# ── Dev Run ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
