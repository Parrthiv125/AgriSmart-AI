# AgriSmart AI — Backend API Contract
## Version 2.0.0

> [!IMPORTANT]
> The server/model determines **all** prediction values (crop, disease, confidence, class_index).
> The client supplies only the image file.

---

## Base URL

| Environment | URL |
| :--- | :--- |
| Local development | `http://localhost:8000` |
| API docs | `http://localhost:8000/docs` |
| OpenAPI spec | `http://localhost:8000/openapi.json` |

---

## Start the backend

```bash
# From the project root (c:\SIH 2\AgriSmart-AI-main)
uvicorn backend.main:app --reload --port 8000
```

The server loads `models/agrismart_final.pth` at startup. No model parameters change during prediction.

---

## Endpoints

### `GET /health`

Returns service health and model load status.

**Response `200 OK`:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_path": "models/agrismart_final.pth",
  "num_classes": 28,
  "version": "2.0.0"
}
```

| Field | Type | Notes |
| :--- | :--- | :--- |
| `status` | `"ok"` or `"degraded"` | `"degraded"` if model not loaded |
| `model_loaded` | boolean | true after successful startup |

---

### `POST /predict`

Upload a leaf image and receive a disease prediction.

#### Request

```
Content-Type: multipart/form-data
```

| Field | Type | Required | Notes |
| :--- | :--- | :--- | :--- |
| `file` | binary | Yes | Leaf image (JPEG, PNG, WebP, BMP, TIFF) |

**Maximum file size**: 10 MB

#### Example curl

```bash
curl -X POST http://localhost:8000/predict \
     -F "file=@leaf.jpg"
```

#### Example fetch (JavaScript)

```javascript
const formData = new FormData();
formData.append("file", imageFile);  // imageFile is a File object from <input type="file">

const response = await fetch("http://localhost:8000/predict", {
  method: "POST",
  body: formData,
});

const result = await response.json();
console.log(result.crop, result.disease, result.confidence);
```

#### Success Response `200 OK`

```json
{
  "success": true,
  "crop": "Corn",
  "disease": "Northern Leaf Blight",
  "display_name": "Corn — Northern Leaf Blight",
  "confidence": 0.9869,
  "class_index": 9,
  "disease_id": "corn_northern_leaf_blight",
  "top_k": [
    {
      "display_name": "Corn — Northern Leaf Blight",
      "crop": "Corn",
      "disease": "Northern Leaf Blight",
      "confidence": 0.9869,
      "class_index": 9
    },
    {
      "display_name": "Corn — Common Rust",
      "crop": "Corn",
      "disease": "Common Rust",
      "confidence": 0.0081,
      "class_index": 8
    },
    {
      "display_name": "Corn — Cercospora Leaf Spot / Gray Leaf Spot",
      "crop": "Corn",
      "disease": "Cercospora Leaf Spot / Gray Leaf Spot",
      "confidence": 0.0034,
      "class_index": 7
    }
  ]
}
```

| Field | Type | Description |
| :--- | :--- | :--- |
| `success` | boolean | Always `true` for 200 responses |
| `crop` | string | Detected crop name |
| `disease` | string | Detected disease name |
| `display_name` | string | Full `"Crop — Disease"` label |
| `confidence` | float [0–1] | Model's top-1 probability |
| `class_index` | int [0–27] | Integer class index in the 28-class model |
| `disease_id` | string | URL-safe snake_case identifier |
| `top_k` | array | Top-3 predictions (same fields, descending confidence) |

#### Error Responses

| Status | When |
| :--- | :--- |
| `400 Bad Request` | No file, empty file, corrupt/unreadable image |
| `413 Request Entity Too Large` | File exceeds 10 MB |
| `422 Unprocessable Entity` | Form field missing entirely |
| `503 Service Unavailable` | Model not loaded (check server logs) |
| `500 Internal Server Error` | Unexpected prediction failure |

**Error response body:**
```json
{
  "success": false,
  "error": "Cannot identify image file. Upload a valid JPEG, PNG, WebP, or BMP image.",
  "detail": null
}
```

---

## 28-Class Model Output

The model maps predictions to exactly these 28 display names (ordered by class index):

| Index | Display Name |
| :--- | :--- |
| 0 | Apple — Apple Scab |
| 1 | Apple — Cedar Apple Rust |
| 2 | Apple — Healthy |
| 3 | Bell Pepper — Bacterial Spot |
| 4 | Bell Pepper — Healthy |
| 5 | Blueberry — Healthy |
| 6 | Cherry — Healthy |
| 7 | Corn — Cercospora Leaf Spot / Gray Leaf Spot |
| 8 | Corn — Common Rust |
| 9 | Corn — Northern Leaf Blight |
| 10 | Grape — Black Rot |
| 11 | Grape — Healthy |
| 12 | Peach — Healthy |
| 13 | Potato — Early Blight |
| 14 | Potato — Late Blight |
| 15 | Raspberry — Healthy |
| 16 | Soybean — Healthy |
| 17 | Squash — Powdery Mildew |
| 18 | Strawberry — Healthy |
| 19 | Tomato — Bacterial Spot |
| 20 | Tomato — Early Blight |
| 21 | Tomato — Healthy |
| 22 | Tomato — Late Blight |
| 23 | Tomato — Leaf Mold |
| 24 | Tomato — Septoria Leaf Spot |
| 25 | Tomato — Spider Mites / Two-Spotted Spider Mite |
| 26 | Tomato — Tomato Mosaic Virus |
| 27 | Tomato — Tomato Yellow Leaf Curl Virus |

> [!NOTE]
> The authoritative class ordering is embedded in `models/agrismart_final.pth` under `checkpoint["class_names"]`.
> The backend reads this directly. Do NOT rely on a separate `classes.json` file.

---

## CORS

The backend allows requests from these local origins by default:
- `http://localhost:3000` (React/Next.js)
- `http://localhost:5173` (Vite)
- `http://localhost:8080` (generic)

To add production frontend origins, edit `ALLOWED_ORIGINS` in `backend/main.py`.

---

## Architecture

```
Frontend (any origin in ALLOWED_ORIGINS)
    |
    | POST /predict  multipart/form-data  { file: <image> }
    v
FastAPI  backend/main.py
    |   - validate file size, type
    |   - decode PIL Image
    |   - write to secure temp file
    |   - call predict_disease()
    |   - delete temp file
    v
backend/services/disease_service.py
    |   - model loaded once at startup (warm_up())
    |   - exact production preprocessing (Resize 292 -> CenterCrop 260)
    |   - ImageNet normalisation
    v
models/agrismart_final.pth
    EfficientNet-B2, 28 classes
    PlantDoc field-domain Macro F1: 0.3650
    PlantVillage Macro F1:          0.9986
```
