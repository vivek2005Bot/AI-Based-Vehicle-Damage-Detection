# Model Evaluation & Training Visualizations Directory

This folder contains all evaluation plots, convergence curves, confusion matrices, precision-recall curves, and validation prediction samples for both the **Updated Background-Calibrated Model** and the **Baseline 25-Epoch Model**.

---

## Folder Organization

```
evaluation_and_training_graphs/
├── updated_model/                     <-- Primary Production Model (Background Calibrated)
│   ├── cardd_yolov8_best.pt          <-- Fine-tuned model checkpoint weights
│   ├── results.png                   <-- Training & validation loss / mAP convergence curves
│   ├── results.csv                   <-- Numerical epoch metrics log
│   ├── confusion_matrix.png          <-- Raw multi-class confusion matrix
│   ├── confusion_matrix_normalized.png<-- Normalized confusion matrix (percentages)
│   ├── BoxPR_curve.png               <-- Bounding Box Precision-Recall curve
│   ├── MaskPR_curve.png              <-- Segmentation Mask Precision-Recall curve
│   ├── BoxF1_curve.png               <-- Box F1 score vs confidence threshold
│   ├── MaskF1_curve.png              <-- Mask F1 score vs confidence threshold
│   ├── BoxP_curve.png & BoxR_curve.png<-- Box Precision and Recall curves
│   ├── MaskP_curve.png & MaskR_curve.png<-- Mask Precision and Recall curves
│   ├── val_batch*_pred.jpg           <-- Model predictions on validation batches
│   ├── val_batch*_labels.jpg         <-- Ground-truth annotations on validation batches
│   └── train_batch*.jpg              <-- Augmented training input batches
│
└── baseline_model/                    <-- Original 25-Epoch Training Run (CarDD only)
    ├── results.png                   <-- 25-epoch full convergence curve
    ├── results.csv                   <-- Full 25-epoch historical training log
    ├── confusion_matrix.png & *_normalized.png
    ├── BoxPR_curve.png & MaskPR_curve.png
    ├── BoxF1_curve.png & MaskF1_curve.png
    └── val_batch*_pred.jpg & labels.jpg
```

---

## Detailed File Guide for Your Research Paper

| Filename | Purpose in Research Paper / Report | Recommended Citation / Figure Title |
| :--- | :--- | :--- |
| **`results.png`** | Demonstrates training convergence, box loss, segmentation loss, classification loss, and mAP progression over epochs. | *Figure: Loss and mAP convergence curves across training and validation splits on Apple Silicon MPS.* |
| **`confusion_matrix_normalized.png`** | Proves per-class classification accuracy and inter-class confusion (e.g. `glass shatter` at 99%, `tire flat` at 95%). | *Figure: Normalized multi-class confusion matrix evaluating damage localization and background classification.* |
| **`BoxPR_curve.png`** | Evaluates spatial bounding box detection precision across recall ranges for all 6 damage categories. | *Figure: Precision-Recall curve for bounding box object detection across IoU thresholds.* |
| **`MaskPR_curve.png`** | Evaluates pixel-level instance segmentation polygon precision across recall ranges. | *Figure: Precision-Recall curve for instance polygon segmentation masks.* |
| **`BoxF1_curve.png` / `MaskF1_curve.png`** | Illustrates the optimal confidence threshold balancing precision and recall (peak F1 score). | *Figure: F1 score as a function of detection confidence threshold.* |
| **`val_batch0_pred.jpg`** | Visual qualitative evidence showing detected bounding boxes and segmentation masks overlaid on vehicle images. | *Figure: Qualitative validation set predictions showing accurate boundary delineations.* |
| **`val_batch0_labels.jpg`** | Visual ground truth annotations for side-by-side comparison with predictions. | *Figure: Ground-truth segmentation annotations from the validation split.* |
| **`results.csv`** | Raw numerical data of losses, precision, recall, and mAP values across each epoch for creating custom LaTeX/pgfplots tables. | *Table: Quantitative epoch-by-epoch training and validation metrics.* |

---

## Key Performance Metrics (Updated Calibrated Model)

- **Box mAP@50:** **64.1%** (Overall) / up to **99.1%** on critical safety classes
- **Mask mAP@50:** **65.5%** (Overall) / up to **99.1%** on critical safety classes
- **Undamaged Vehicle False Positive Rate:** **14.9%** (down from 100% on baseline CarDD)
- **Intact Car Accuracy:** **85.1%** clean `SAFE` / `NO_DAMAGE` verdicts
- **Inference Latency:** **2.7 ms / image** (~370 FPS) on Apple Silicon Metal GPU (MPS)
