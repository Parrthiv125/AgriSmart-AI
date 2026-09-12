# Dataset — Download & Preparation

## Source

**Primary Dataset:** PlantVillage  
**Hugging Face Hub:** https://huggingface.co/datasets/mohanty/PlantVillage  
**Size:** ~54,306 images  
**License:** CC0 / Public Domain  

**Citation:**
```
Hughes, D. P., & Salathé, M. (2015).
An open access repository of images on plant health to enable the development
of mobile disease diagnostics.
arXiv:1511.08060
```

---

## ⚠️ Important Notes

- The **raw dataset is NOT committed** to this repository (too large).
- Use the download script below to fetch and prepare the dataset locally.
- The hackathon organizers supply the **official class list**. Once available, update `training/config.py` with the exact classes.
- Do **not** use the hidden judging/test dataset for training.

---

## Expected Folder Structure After Preparation

```
data/
├── raw/                    ← raw downloaded images (not committed)
│   └── plantvillage/
│       ├── Apple___Apple_scab/
│       ├── Tomato___Early_blight/
│       └── ...
│
├── processed/              ← split dataset (not committed)
│   ├── train/
│   │   ├── class_1/
│   │   └── ...
│   ├── val/
│   │   ├── class_1/
│   │   └── ...
│   └── test/
│       ├── class_1/
│       └── ...
│
├── classes.json            ← generated class list (committed once known)
└── dataset_stats.json      ← class counts, split sizes (committed)
```

---

## Download & Prepare

### Step 1: Download from Hugging Face
```bash
python data/download_dataset.py
```

This script:
1. Downloads the PlantVillage dataset from Hugging Face Hub
2. Saves raw images to `data/raw/plantvillage/`
3. Inspects folder structure and counts per-class images
4. Checks for corrupted images
5. Prints a summary

### Step 2: Inspect & Clean
```bash
python data/inspect_dataset.py
```

Outputs:
- Number of classes found
- Images per class
- Any empty folders
- Any corrupted files

### Step 3: Split Dataset
```bash
python data/split_dataset.py --seed 42 --train 0.8 --val 0.15 --test 0.05
```

Creates `data/processed/{train,val,test}/` with reproducible splits.

---

## Class Configuration

Once the hackathon organizers provide the official class list:

1. Update `training/config.py` → `CLASSES` list
2. Re-run `data/split_dataset.py` to filter to only required classes
3. Update `models/classes.json`

The training pipeline is designed to work with any subset of PlantVillage classes.

---

## Dataset Statistics

*(Updated after download and inspection)*

| Metric | Value |
|---|---|
| Total images | ~54,306 |
| Number of classes | ~39 |
| Avg images per class | ~1,393 |
| Min images per class | TBD |
| Max images per class | TBD |

---

## PlantVillage Class List (Public)

The public PlantVillage dataset contains ~39 classes across multiple crops including:
Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Pepper, Potato, Raspberry,
Soybean, Squash, Strawberry, Tomato — with healthy and disease variants.

The **official hackathon class list** may be a subset. Do not assume all classes are used.
