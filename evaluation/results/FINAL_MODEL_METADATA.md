# Final Model Metadata
## Experiment C — Champion Model

### Identification
| Field | Value |
| :--- | :--- |
| **Final model path** | `models/agrismart_final.pth` |
| **Source checkpoint** | `models/experiment_C_best.pth` |
| **SHA-256** | `79188ba84c95cc6d...` (verified byte-for-byte copy) |
| **Architecture** | EfficientNet-B2 (`timm`) |
| **Input size** | 260×260 |
| **Classes** | 28 |
| **Checkpoint key** | `model_state_dict` (not `state_dict`) |
| **Class list key** | `class_names` (embedded, authoritative) |

### Training Configuration
| Field | Value |
| :--- | :--- |
| **Base model** | `models/agrismart_best.pth` (Experiment A, PV-trained) |
| **Fine-tuning strategy** | Partial — final stage (`blocks.6`) + classifier |
| **Frozen layers** | `blocks.0–5`, `conv_stem`, `bn1` |
| **Trainable layers** | `blocks.6`, `conv_head`, `bn2`, `classifier` |
| **Classifier LR** | 1e-4 |
| **Backbone LR** | 1e-5 |
| **Epochs trained** | 5 (best at Epoch 4) |
| **Optimizer** | AdamW |
| **Scheduler** | CosineAnnealingLR |
| **AMP** | Yes (CUDA mixed precision) |
| **Loss** | Weighted CrossEntropyLoss |

### Training Data
| Dataset | Split | Count |
| :--- | :--- | :--- |
| PlantVillage | Train | 30,858 |
| PlantDoc | Train | 2,046 |
| **Combined** | **Train** | **32,904** |

### Validation Performance (Final Audit)
| Validation Set | N | Macro F1 | Macro Precision | Macro Recall |
| :--- | :--- | :--- | :--- | :--- |
| **PlantDoc (field-domain)** | 514 | **0.3650** | 0.4468 | 0.3933 |
| PlantVillage (source-domain) | 7,684 | 0.9986 | — | — |

### A → B → C Progression
| Experiment | PlantDoc F1 | PlantVillage F1 | Strategy |
| :--- | :--- | :--- | :--- |
| A (baseline) | 0.1882 | 0.9993 | PV-only, full model |
| B (head-only) | 0.2762 | 0.9980 | + PlantDoc, frozen backbone |
| **C (final)** | **0.3650** | **0.9986** | + PlantDoc, last stage unfrozen |

### Per-Class Performance Summary (PlantDoc Val)
| Class | Support | Precision | Recall | F1 | Notes |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Squash — Powdery Mildew | 26 | 0.7857 | 0.8462 | 0.8148 | |
| Strawberry — Healthy | 19 | 0.6957 | 0.8421 | 0.7619 | |
| Corn — Northern Leaf Blight | 38 | 0.6000 | 0.6316 | 0.6154 | |
| Grape — Healthy | 14 | 0.4615 | 0.8571 | 0.6000 | |
| Apple — Healthy | 18 | 0.8000 | 0.4444 | 0.5714 | |
| Corn — Cercospora Leaf Spot | 14 | 0.4545 | 0.7143 | 0.5556 | |
| Raspberry — Healthy | 24 | 0.4043 | 0.7917 | 0.5352 | |
| Apple — Cedar Apple Rust | 18 | 0.4444 | 0.6667 | 0.5333 | |
| Tomato — Septoria Leaf Spot | 30 | 0.4643 | 0.4333 | 0.4483 | |
| Corn — Common Rust | 23 | 0.6154 | 0.3478 | 0.4444 | |
| Peach — Healthy | 22 | 0.3000 | 0.8182 | 0.4390 | |
| Blueberry — Healthy | 23 | 0.7000 | 0.3043 | 0.4242 | |
| Tomato — Late Blight | 22 | 0.5385 | 0.3182 | 0.4000 | |
| Apple — Apple Scab | 19 | 0.6250 | 0.2632 | 0.3704 | |
| Potato — Late Blight | 20 | 0.3889 | 0.3500 | 0.3684 | |
| Tomato — Early Blight | 18 | 0.2857 | 0.4444 | 0.3478 | |
| Grape — Black Rot | 13 | 0.3333 | 0.3077 | 0.3200 | |
| Potato — Early Blight | 23 | 0.2692 | 0.3043 | 0.2857 | |
| Tomato — Leaf Mold | 18 | 0.7500 | 0.1667 | 0.2727 | |
| Bell Pepper — Healthy | 12 | 0.6667 | 0.1667 | 0.2667 | |
| Cherry — Healthy | 11 | 0.1724 | 0.4545 | 0.2500 | |
| Bell Pepper — Bacterial Spot | 14 | 0.2857 | 0.1429 | 0.1905 | |
| Tomato — Tomato Mosaic Virus | 11 | 0.1364 | 0.2727 | 0.1818 | |
| Soybean — Healthy | 13 | 1.0000 | 0.0769 | 0.1429 | Weak recall |
| Tomato — Bacterial Spot | 22 | 0.3333 | 0.0455 | 0.0800 | Weak |
| **Tomato — Healthy** | 13 | 0.0000 | 0.0000 | **0.0000** | ZERO F1 |
| **Tomato — YLCV** | 15 | 0.0000 | 0.0000 | **0.0000** | ZERO F1, never predicted |
| **Tomato — Spider Mites** | **1** | 0.0000 | 0.0000 | **0.0000** | 1 val sample only |

### Key Confusion Patterns
| Count | True Class | Predicted As |
| ---: | :--- | :--- |
| 9 | Corn — Common Rust | Corn — Northern Leaf Blight |
| 7 | Tomato — YLCV | Tomato — Tomato Mosaic Virus |
| 7 | Tomato — Healthy | Raspberry — Healthy |
| 7 | Corn — Northern Leaf Blight | Corn — Cercospora |
| 6 | Tomato — Bacterial Spot | Tomato — Early Blight |
| 6 | Apple — Healthy | Peach — Healthy |
| 5 | Tomato — Late Blight | Potato — Late Blight |

### Output Files
| File | Description |
| :--- | :--- |
| `evaluation/results/experiment_c/per_class_pd_val_final.csv` | Per-class P/R/F1 |
| `evaluation/results/experiment_c/cm_pd_val_final.csv` | 28×28 confusion matrix |
| `evaluation/results/experiment_c/final_audit_summary.json` | Machine-readable summary |

### Production Inference Service
| Field | Value |
| :--- | :--- |
| **Module path** | `backend/services/disease_service.py` |
| **Entry function** | `predict_disease(image_input, model_path=None, top_k=3)` |
| **Startup function** | `warm_up()` — call once at FastAPI startup |
| **Model loading** | Once per process, cached at module level |
| **Device** | CUDA if available, else CPU |
| **Missing image** | Raises `FileNotFoundError` (no silent fallback) |
| **Corrupt image** | Raises `UnidentifiedImageError` |
| **Class authority** | `checkpoint["class_names"]` — never `classes.json` |

### Pre-FastAPI Issues
None blocking. The following are known model limitations (not bugs):
- **3 classes with F1=0**: Tomato Healthy, Tomato YLCV, Tomato Spider Mites — expected given PlantDoc field conditions and 1-sample support
- **YLCV consistently confused with Mosaic Virus**: Visually similar viral symptoms
- **Corn rust/blight cross-confusion**: Known agronomic challenge in field images
- **Peach Healthy over-predicted (60 predictions, 22 support)**: Serving as a confusion catch-all for other healthy crops
