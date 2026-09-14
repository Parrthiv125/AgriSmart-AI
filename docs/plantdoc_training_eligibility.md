# PlantDoc Training Eligibility Report

## 1. Data Provenance and Source Verification
We performed a final pre-training audit of the `PlantVillage-Dataset/development_dataset/plantdoc/` directory to verify its contents, origin, and independence from existing training sets.
- **Exact Source**: The directory contains exactly 2,572 images.
- **Dataset Identification**: The filenames strongly indicate that these images originate from the public **PlantDoc** dataset (Singh et al., 2020), which was sourced from the internet. Filenames such as `test_apple scab leaf.jpg` and `train_apple-scab-disease-tree-fungus-906x391.jpg` directly map to the PlantDoc dataset's web-scraped naming conventions and its original train/test partitioning.
- **Dataset Version**: This directory acts as a combined pool of PlantDoc's original training and testing sets, curated to match our 28 development classes.

## 2. Complete PlantDoc Class Table
The 2,572 images have been mapped into the 28 development classes. Evidence supports high mapping confidence based on directory alignment.

| Class | Image Count | Source/Provenance Evidence | Mapping Confidence / Notes |
|---|---|---|---|
| Apple___Apple_scab | 93 | Public PlantDoc Web-Scraped | High confidence |
| Apple___Cedar_apple_rust | 88 | Public PlantDoc Web-Scraped | High confidence |
| Apple___healthy | 91 | Public PlantDoc Web-Scraped | High confidence |
| Blueberry___healthy | 115 | Public PlantDoc Web-Scraped | High confidence |
| Cherry_(including_sour)___healthy | 57 | Public PlantDoc Web-Scraped | High confidence |
| Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot | 68 | Public PlantDoc Web-Scraped | High confidence |
| Corn_(maize)___Common_rust_ | 116 | Public PlantDoc Web-Scraped | High confidence |
| Corn_(maize)___Northern_Leaf_Blight | 191 | Public PlantDoc Web-Scraped | High confidence |
| Grape___Black_rot | 64 | Public PlantDoc Web-Scraped | High confidence |
| Grape___healthy | 69 | Public PlantDoc Web-Scraped | High confidence |
| Peach___healthy | 111 | Public PlantDoc Web-Scraped | High confidence |
| Pepper,_bell___Bacterial_spot | 71 | Public PlantDoc Web-Scraped | High confidence |
| Pepper,_bell___healthy | 61 | Public PlantDoc Web-Scraped | High confidence |
| Potato___Early_blight | 116 | Public PlantDoc Web-Scraped | High confidence |
| Potato___Late_blight | 105 | Public PlantDoc Web-Scraped | High confidence |
| Raspberry___healthy | 119 | Public PlantDoc Web-Scraped | High confidence |
| Soybean___healthy | 65 | Public PlantDoc Web-Scraped | High confidence |
| Squash___Powdery_mildew | 130 | Public PlantDoc Web-Scraped | High confidence |
| Strawberry___healthy | 96 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Bacterial_spot | 110 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Early_blight | 88 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Late_blight | 111 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Leaf_Mold | 91 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Septoria_leaf_spot | 151 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Spider_mites Two-spotted_spider_mite | 2 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Tomato_Yellow_Leaf_Curl_Virus | 76 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___Tomato_mosaic_virus | 54 | Public PlantDoc Web-Scraped | High confidence |
| Tomato___healthy | 63 | Public PlantDoc Web-Scraped | High confidence |

**Total images**: 2,572
**Intra-dataset duplicates (exact SHA-256)**: 12

*Note: The complete set of 2,572 filenames has been programmatically reviewed to ensure they all conform to standard PlantDoc web-scraped naming patterns, without any hidden non-image metadata files.*

## 3. Leakage Audit and Overlap Verification
We executed a strict cryptographic overlap check across the entire proposed training universe:
- **Cross-Dataset SHA-256 Intersection**: PlantVillage ∩ PlantDoc = **0 files**. No exact byte-identical duplicates were detected between the audited local PlantVillage and PlantDoc image sets. **This does not prove independence from the organizer's hidden set.**
- **Filename/Path Collisions**: PlantVillage ∩ PlantDoc = **0 files**.
- **Existing Manifest Integrity**: The existing frozen PlantVillage train/validation manifests have been verified and remain entirely unchanged.

## 4. Organizer-Provided Data Independence
- **Physical Presence**: There are **no** organizer-provided held-out test images physically present in this local project repository.
- **Hidden Test Set Limitation**: Because the hackathon organizer's held-out test set is unseen and unavailable locally, **independence from the hidden test set cannot be cryptographically proven from local data**. We can only attest that our added PlantDoc dataset is a recognized public dataset and does not intersect with our existing PlantVillage distribution.

## 5. Evaluation Policy
Because PlantDoc images will now partially enter the training set in Experiment B:
- **The previous PlantDoc external evaluation (Macro-F1 0.2662 from 2,572 images) is officially archived as a historical external evaluation for Experiment A.**
- This historical 2,572-image evaluation **can no longer be reported** as an independent, unbiased test metric for Experiment B, to strictly prevent data leakage.

## Conclusion on Eligibility
The public PlantDoc dataset is eligible for inclusion in the training set under the hackathon's "public data allowed if cited" rule. It introduces zero physical leakage into our PlantVillage splits, provided we strictly partition the PlantDoc images themselves into new separate train and validation subsets.
