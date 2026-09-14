"""
AgriSmart AI — Backend Test Suite
===================================
Minimal tests covering:
  1. /health returns 200
  2. /predict with a valid image → 200 + full schema
  3. /predict with no file → 422
  4. /predict with non-image file → 400
  5. Model is not reloaded per request (cache check)
  6. /docs endpoint is accessible
  7. /openapi.json schema is valid

Run:
    pytest tests/test_backend.py -v
    (from project root, using the CUDA venv)

ROOT CAUSE FIX (2026-09-14):
    TestClient(app) at module level does NOT trigger FastAPI's
    @app.on_event("startup") handler, so _model_ready stays False and every
    /predict call returns 503.  The fix is a session-scoped fixture that uses
    TestClient as a context manager: "with TestClient(app) as c: yield c".
    The "with" block calls __enter__ which runs the ASGI lifespan, firing
    startup_event() and populating disease_service._cache before any test runs.
"""
import io
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Import the app
from backend.main import app


def make_jpeg_bytes() -> bytes:
    """Create a minimal synthetic JPEG for tests that need a valid image."""
    buf = io.BytesIO()
    img = Image.new("RGB", (260, 260), color=(120, 180, 80))
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ── Session-scoped client: triggers startup/shutdown events exactly once ─────────────
# TestClient MUST be used as a context manager for FastAPI's
# @app.on_event("startup") / lifespan handlers to fire.  A bare
# TestClient(app) at module level does NOT call startup_event(), so
# _model_ready stays False and every /predict returns 503.
@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# ── Test 1: /health ─────────────────────────────────────────────────────────────────
def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "version" in data
    assert data["num_classes"] == 28


# ── Test 2: /predict with a valid image ───────────────────────────────────────────────
def test_predict_real_image_returns_full_schema(client):
    """
    Use a synthetic 260x260 green JPEG as a portable stand-in for a leaf
    image.  The model will produce a (possibly low-confidence) prediction,
    but the response schema must be fully populated regardless.
    """
    img_bytes = make_jpeg_bytes()
    fname = "test_leaf.jpg"

    resp = client.post(
        "/predict",
        files={"file": (fname, img_bytes, "image/jpeg")},
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data["success"] is True
    assert isinstance(data["crop"], str) and len(data["crop"]) > 0
    assert isinstance(data["disease"], str) and len(data["disease"]) > 0
    # Parentheses around the disjunction prevent operator-precedence bugs
    assert isinstance(data["display_name"], str) and (
        " — " in data["display_name"] or len(data["display_name"]) > 0
    )
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["class_index"], int)
    assert 0 <= data["class_index"] < 28
    assert isinstance(data["disease_id"], str) and len(data["disease_id"]) > 0
    assert isinstance(data["top_k"], list) and len(data["top_k"]) == 3

    # top_k structure
    for pred in data["top_k"]:
        assert "display_name" in pred
        assert "crop" in pred
        assert "disease" in pred
        assert "confidence" in pred
        assert "class_index" in pred


# ── Test 3: /predict with no file → 422 ────────────────────────────────────────────
def test_predict_missing_file_returns_error(client):
    resp = client.post("/predict")
    # FastAPI returns 422 Unprocessable Entity when a required field is absent
    assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"


# ── Test 4: /predict with a non-image file → 400 ─────────────────────────────────
def test_predict_non_image_returns_400(client):
    fake_data = b"This is definitely not an image file. It is plain text."
    resp = client.post(
        "/predict",
        files={"file": ("notes.txt", fake_data, "text/plain")},
    )
    # We expect either 400 (our image validation) or 415 (content-type rejection)
    assert resp.status_code in (400, 415), (
        f"Expected 400 or 415 for non-image, got {resp.status_code}: {resp.text}"
    )


# ── Test 5: model is not reloaded for every request ───────────────────────────────
def test_model_not_reloaded_per_request(client):
    """
    Verify the module-level cache works deterministically: the model object
    returned by two consecutive _load_model() calls must be the exact same
    Python object (same id()), proving no reload occurred.
    """
    from backend.services import disease_service

    # After startup, cache must be populated
    assert len(disease_service._cache) > 0, (
        "Model cache is empty — model is not being cached at module level"
    )

    # Retrieve the cached entry and call _load_model again — must return the
    # exact same model object (identity check, not equality).
    key = next(iter(disease_service._cache))
    model_first, _, _ = disease_service._cache[key]

    model_second, _, _ = disease_service._load_model(
        disease_service.DEFAULT_MODEL_PATH
    )

    assert model_first is model_second, (
        "Different model objects returned on consecutive calls — "
        "cache is not working correctly"
    )


# ── Test 6: /docs endpoint is accessible ───────────────────────────────────────────────
def test_docs_accessible(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


# ── Test 7: /openapi.json schema is valid ──────────────────────────────────────────────
def test_openapi_json(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "paths" in schema
    assert "/predict" in schema["paths"]
    assert "/health" in schema["paths"]
