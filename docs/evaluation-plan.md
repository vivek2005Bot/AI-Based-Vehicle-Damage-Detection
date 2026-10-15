# Model Evaluation & Validation Plan

## 1. Objective

This document defines the formal validation protocol for the Computer Vision and Telemetry pipelines in accordance with `ANTIGRAVITY_PROJECT_SPEC.md` Section 3 and Section 4.

---

## 2. Dataset Splitting Protocol

Splits are strictly deterministic and stratified using random seed `42` (`data/splits/split_manifest.json`):
- **Train Set (70%):** Model parameter optimization and feature extraction.
- **Validation Set (15%):** Hyperparameter tuning, early stopping, and gating threshold selection ($T_{\text{FILTER}}$).
- **Test Set (15%):** Unseen final benchmark reporting.

---

## 3. Evaluation Metrics by Stage

### Stage 1: Binary Filter
- **Target:** Gating damaged vs undamaged vehicles.
- **Primary Metric:** Recall on Damaged Class ($\ge 0.98$). False negatives (missing a damaged car) are treated as severe errors.
- **Secondary Metric:** False Positive Rate on Undamaged Class ($\le 0.10$).
- **Gating Threshold Sweep:** Operating characteristic curve evaluated across $T \in [0.50, 0.95]$ with default $T_{\text{FILTER}} = 0.85$.

### Stage 2: Damage Classifier
- **Target:** Multi-class damage taxonomy (`dent`, `scratch`, `smash`, `crack`, `flat_tire`).
- **Primary Metrics:** Macro-averaged Precision, Recall, and F1-Score across all 5 classes.
- **Confusion Matrix:** Explicit tracking of inter-class confusion (e.g., small dent vs scratch).

### Stage 3: Bounding-Box Detector
- **Target:** Spatial localisation of damaged panels.
- **Primary Metric:** $\text{mAP}_{50}$ and $\text{mAP}_{50-95}$ across all annotated classes.
- **Intersection over Union (IoU):** Standard threshold $\text{IoU} \ge 0.50$.

### Stage 4: Polygon Segmentation
- **Target:** Exact boundary and pixel area ratio $r_c = A_{\text{mask}} / A_{\text{veh}}$.
- **Primary Metrics:** Mask $\text{mAP}$, Mean Dice Coefficient, and Mean IoU (mIoU).
- **Shoelace Polygon Consistency:** Verifies Shoelace formula area matches polygon raster mask pixel count.

### OBD-II Anomaly Detection
- **Target:** Outlier detection on core engine signals.
- **Primary Metric:** Precision / Recall against synthetic injected anomalies (e.g., $125^\circ\text{C}$ coolant temp, 7,500 RPM overrev).
- **DTC Precision:** 100% exact match against verified SAE J2012 fault table.

---

## 4. End-to-End Decision Support Risk Evaluation

The risk engine's Safe / Caution / Unsafe classifications are evaluated against a golden safety test suite (`tests/test_risk_rules.py`):
1. **Zero Hallucination Tolerance:** Any inspection with an active Airbag DTC (`B0001`) or Coolant Overheat (`P0217`) must classify as `UNSAFE` 100% of the time, regardless of visual model output.
2. **Glass Safety Tolerance:** Any windshield crack in the Critical Viewing Area (CVA) must escalate to at least `CAUTION`.
