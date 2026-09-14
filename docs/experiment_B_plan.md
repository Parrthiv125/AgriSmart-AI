# Experiment B Plan: Integrating Public Field Data

## Task 2: Training Split Design
To integrate PlantDoc data without causing leakage, we will create a reproducible manifest generator script that outputs separate CSVs (`exp_b_train.csv`, `exp_b_val.csv`) and does **not** modify the existing PlantVillage manifests or original data.
- **Split Strategy**: PlantDoc images will be split into an 80% Train / 20% Validation distribution, stratified by the 28 classes.
- **Strict Separation Policy**: The training and validation sets will be strictly separated and finalized into static CSV manifests *before* any model fitting or dataloader initialization begins.
- **Grouping/Exclusions**:
  - 12 exact SHA-256 duplicate images found within PlantDoc will be removed.
  - Images with identical base filenames (after stripping `train_`/`test_` prefixes and numeric IDs) will be forced into the same split to prevent near-duplicate leakage.
  - **No pHash candidates** or visual-similarity heuristics will be used to merge groups, preserving natural field variance while avoiding accidental over-pruning.

## Task 3 & 4: Protocol & Leakage Prevention
**Protocol**:
- **Control (Exp A)**: PlantVillage Train -> Model -> PlantVillage Val.
- **Experiment B**: (PlantVillage Train + PlantDoc Train) -> Model -> PlantDoc field-domain validation set.
**Leakage Prevention**: Since PlantDoc images are now entering the training set, the prior **0.2662** PlantDoc evaluation result is officially archived as a **historical external evaluation for Experiment A**. It will **never** be compared against Experiment B, as it is no longer an unbiased metric. Experiment B will only be evaluated against the strict, unseen 20% PlantDoc field-domain validation set.

## Task 5: Validation Strategy Recommendation
**Recommendation: Separate PlantVillage + PlantDoc validation sets**
- **What they measure**: PlantVillage Val measures retention of lab-condition visual features. PlantDoc field-domain validation set measures zero-shot generalization to heterogeneous field conditions.
- **Primary metric**: PlantDoc field-domain validation set Macro-F1. Our goal is field generalization.
- **Organizer Test Set**: The organizer's held-out test set remains strictly unseen and untouched, serving as the ultimate blind evaluation.

## Task 6: Training Size, Distribution, and Cost Reduction
- **Exact Training Size**: 32,904 images (PlantVillage Train: 30,858 + PlantDoc Train: 2,046).
- **Exact Validation Size**: Evaluated separately: PlantVillage Val: 7,684 images; PlantDoc field-domain validation set: 514 images.
- **Class Distribution**: Highly imbalanced on the PlantDoc side (ranging from 2 images for Spider Mites to 191 for Northern Leaf Blight). PlantVillage side remains evenly distributed as established in Exp A.

**Cost Reduction Strategy**:
Running a full 10-epoch training from scratch on CPU would exceed 130 hours.
1. **Transfer Learning**: Initialize with the Experiment A best checkpoint.
2. **Frozen Backbone Pilot**: Freeze the EfficientNet-B2 feature extractor. Unfreeze only the classification head.
This reduces gradient computation drastically, dropping epoch time to approximately 6-7 hours.

---

## Task 7: Exact Experiment B Configuration

1. **Hypothesis**: Fine-tuning the Experiment A baseline with eligible public PlantDoc images will adapt the classification head/decision boundary to the PlantDoc field domain, yielding a significantly higher Macro-F1 on the PlantDoc field-domain validation set without catastrophic forgetting of PlantVillage baseline features.
2. **Why public PlantDoc training data is relevant**: It explicitly bridges the domain gap between uniform lab backgrounds and the complex field environments expected in the organizer's hidden test set.
3. **Exact Training Data**: Original frozen PlantVillage Train manifest (30,858 images) + PlantDoc Train manifest (80% deduplicated grouped split, 2,046 images).
4. **Exact Validation Data**: Original frozen PlantVillage Val manifest (7,684 images, evaluated independently) and PlantDoc field-domain validation set (20% grouped split, 514 images, evaluated independently).
5. **Exact Classes**: The 28 shared development classes.
6. **Model Initialization**: EfficientNet-B2, initialized from the best `experiment_A_best.pth` weights.
7. **Frozen/Unfrozen Layers**: The entire EfficientNet-B2 backbone is **frozen**. Only the final dense classification head (classifier block) is **unfrozen**.
8. **Epochs**: 3 epochs max (pilot run).
9. **Learning Rate**: 1e-4 (conservative rate for head-only fine-tuning) with a Cosine Annealing scheduler.
10. **Batch Size**: 32.
11. **Augmentation**: Moderate (Random Horizontal Flip, slight Color Jitter, Random Rotation ±15°). No heavy geometric transformations to save CPU cycles.
12. **Loss**: Cross-Entropy Loss with inverse class frequency weighting applied to counteract PlantDoc imbalance.
13. **Primary Metric**: PlantDoc field-domain validation set Macro-F1.
14. **Success Threshold**: Macro-F1 on the PlantDoc field-domain validation set exceeds the Exp A baseline performance on that exact same split, while PlantVillage Val F1 drops by no more than 0.05.
15. **Failure Threshold**: PlantDoc field-domain validation set Macro-F1 stagnates/degrades, or training loss diverges.
16. **Estimated CPU Runtime**: ~18–21 hours total (approx. 6–7 hours per epoch).

## Task 8: Reproducibility and Action
The split generation script must be committed and generate deterministic CSV manifests using seed 42 without overwriting Exp A files. If the experiment succeeds, we adopt this split design for the final submission.
