"""
AgriSmart AI — FastAPI Backend
================================
Entry point for the production backend.

Start the server:
    uvicorn backend.main:app --reload --port 8000
    (from the project root: c:\\SIH 2\\AgriSmart-AI-main)

Or run directly:
    python backend/main.py

Architecture:
    POST /predict
        -> image validation (this file)
        -> disease_service.predict_disease()
        -> agrismart_final.pth (EfficientNet-B2, 28 classes)
        -> structured JSON response

Model loading lives exclusively in backend/services/disease_service.py.
No inference code belongs in this file.
"""

from __future__ import annotations

import io
import sys
import logging
import tempfile
import traceback
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from PIL import Image, UnidentifiedImageError

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from backend.services.disease_service import predict_disease, warm_up

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agrismart")

# ── CORS origins ───────────────────────────────────────────────────────────────
# Configure for local dev + any known deployed frontend origins.
# Do NOT use ["*"] in production — add your deployed frontend URL here.
ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React / Next.js dev server
    "http://localhost:5173",    # Vite dev server
    "http://localhost:8080",    # Generic local frontend
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

# ── Constraints ────────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 10
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgriSmart AI",
    description=(
        "Crop disease detection API. Upload a leaf image to receive a disease "
        "prediction from a 28-class EfficientNet-B2 model trained on PlantVillage "
        "and PlantDoc field imagery.\n\n"
        "**Model**: `models/agrismart_final.pth`\n"
        "**PlantDoc Field-Domain Macro F1**: 0.3650\n"
        "**PlantVillage Macro F1**: 0.9986"
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Startup / Shutdown ─────────────────────────────────────────────────────────
_model_ready = False

@app.on_event("startup")
async def startup_event():
    global _model_ready
    try:
        warm_up()
        _model_ready = True
        log.info("AgriSmart AI model loaded successfully.")
    except FileNotFoundError as e:
        log.error(f"Model file not found: {e}")
        _model_ready = False
    except Exception as e:
        log.error(f"Unexpected error loading model: {e}")
        _model_ready = False


# ── Response models ────────────────────────────────────────────────────────────

class TopKPrediction(BaseModel):
    display_name: str = Field(..., example="Tomato — Early Blight")
    crop: str         = Field(..., example="Tomato")
    disease: str      = Field(..., example="Early Blight")
    confidence: float = Field(..., ge=0.0, le=1.0, example=0.9123)
    class_index: int  = Field(..., ge=0, lt=28, example=20)


class PredictionResponse(BaseModel):
    success: bool       = Field(True, example=True)
    crop: str           = Field(..., example="Tomato")
    disease: str        = Field(..., example="Early Blight")
    display_name: str   = Field(..., example="Tomato — Early Blight")
    confidence: float   = Field(..., ge=0.0, le=1.0, example=0.9123)
    class_index: int    = Field(..., ge=0, lt=28, example=20)
    disease_id: str     = Field(..., example="tomato_early_blight")
    top_k: list[TopKPrediction]


class HealthResponse(BaseModel):
    status: str        = Field(..., example="ok")
    model_loaded: bool = Field(..., example=True)
    model_path: str    = Field(..., example="models/agrismart_final.pth")
    num_classes: int   = Field(28, example=28)
    version: str       = Field("2.0.0", example="2.0.0")


class ErrorResponse(BaseModel):
    success: bool = Field(False, example=False)
    error: str    = Field(..., example="Could not decode image")
    detail: Optional[str] = None


# ── Image validation helper ────────────────────────────────────────────────────

async def validate_and_open_image(file: UploadFile) -> tuple[Image.Image, bytes]:
    """
    Read upload, enforce size and type limits, decode image.
    Raises HTTPException on any failure — never substitutes a fake image.
    """
    # Empty file guard
    if file.filename == "" or file.filename is None:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    # Content-type guard (best-effort; not a security boundary)
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported content type: '{file.content_type}'. "
                f"Accepted: JPEG, PNG, WebP, BMP, TIFF."
            ),
        )

    raw = await file.read()

    if len(raw) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(raw) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(raw) // 1024 // 1024} MB). Maximum: {MAX_FILE_SIZE_MB} MB.",
        )

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        # Force decode to catch lazy-load failures
        img.load()
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="Cannot identify image file. Upload a valid JPEG, PNG, WebP, or BMP image.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to decode image: {e}",
        )

    return img, raw


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
)
async def health_check():
    """Returns service health and model load status."""
    return HealthResponse(
        status="ok" if _model_ready else "degraded",
        model_loaded=_model_ready,
        model_path="models/agrismart_final.pth",
        num_classes=28,
        version="2.0.0",
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or corrupt image"},
        413: {"model": ErrorResponse, "description": "File too large"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
        500: {"model": ErrorResponse, "description": "Unexpected server error"},
    },
    tags=["Disease Detection"],
    summary="Predict crop disease from a leaf image",
)
async def predict_endpoint(
    file: UploadFile = File(..., description="Leaf / crop image (JPEG or PNG recommended)"),
):
    """
    Upload a leaf image and receive a disease prediction.

    **Request**: `multipart/form-data`, field name `file`.

    **Response**:
    - `crop` — detected crop (e.g. "Tomato")
    - `disease` — detected disease (e.g. "Early Blight")
    - `display_name` — full display name (e.g. "Tomato — Early Blight")
    - `confidence` — model confidence in [0, 1]
    - `class_index` — integer class index [0–27]
    - `disease_id` — URL-safe disease identifier
    - `top_k` — top-3 predictions with per-class confidence

    The server/model determines all prediction values. The client supplies only the image.
    """
    if not _model_ready:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Check server startup logs.",
        )

    # Validate and decode image in memory
    img, raw_bytes = await validate_and_open_image(file)

    # Write to a secure temp file for disease_service (which accepts file paths)
    try:
        suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(raw_bytes)
            tmp_path = Path(tmp.name)

        result = predict_disease(tmp_path, top_k=3)

    except (FileNotFoundError, UnidentifiedImageError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        log.error(f"Prediction failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
    finally:
        # Always clean up temp file
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    return PredictionResponse(
        success=True,
        crop=result["crop"],
        disease=result["disease"],
        display_name=result["display_name"],
        confidence=result["confidence"],
        class_index=result["class_index"],
        disease_id=result["disease_id"],
        top_k=[TopKPrediction(**t) for t in result["top_k"]],
    )


# ── Global error handler ───────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error", "detail": str(exc)},
    )


# ── Dev run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
