# Dataset Inspection & Validation Report

**Generated at:** 2026-10-14T17:42:38.957105+00:00  
**Dataset Root:** `/Users/vivekkumar/AI BASED VEHICLE DAMAGE DETECTION/dataset`  
**OBD Root:** `/Users/vivekkumar/AI BASED VEHICLE DAMAGE DETECTION/obdiidata`  

---

## 1. Executive Summary

| Category | Count | Status | Notes |
|---|---|---|---|
| **Damaged Images** | 20,455 | Available | {'.jpg': 20455} |
| **Undamaged Images** | 154 | Available | {'.png': 154} |
| **Class Imbalance** | 132.8:1 | Extreme | Heavy skew toward damaged images; requires class-weighting & stratified sampling |
| **OBD-II CSV Logs** | 210 | Available | Multi-format telemetry (Seat Leon driving events + UFPE logs) |
| **Annotation Files** | 0 | Missing in raw folder | No native bounding box or mask files found |

---

## 2. Image Inspection Findings

### Damaged Images (`dataset/damaged`)
- **Total Files:** 20,455
- **Formats:** {'.jpg': 20455}
- **Average Size:** 410.9 KB
- **Corrupt Files Detected:** 0

### Undamaged Images (`dataset/undamaged`)
- **Total Files:** 154
- **Formats:** {'.png': 154}
- **Average Size:** 456.9 KB
- **Corrupt Files Detected:** 0

---

## 3. Annotation & Supervision Availability

- **Stage 1 (Damaged vs. Undamaged Filter):** **SUPPORTED**. Binary supervision is available from directory separation.
- **Stage 2 (Damage Classification):** **REQUIRES PRETRAINED WEIGHTS / ADAPTER**. Instance-level classes (scratch, dent, glass_crack, etc.) are not labelled in the raw images.
- **Stage 3 (Damage Detection):** **REQUIRES PRETRAINED WEIGHTS / ADAPTER**. No bounding box coordinates exist in raw data.
- **Stage 4 (Damage Segmentation):** **REQUIRES PRETRAINED WEIGHTS / ADAPTER**. No segmentation masks or polygons exist in raw data.

> [!IMPORTANT]
> In accordance with `ANTIGRAVITY_PROJECT_SPEC.md` §0.3 and Master Prompt Step 2, our CV pipeline implements modular adapters. When external trained weights are not mounted, the system exposes transparent `model_not_ready` / `demo` capability flags rather than fabricating fake predictions or metrics.

---

## 4. OBD-II Telemetry Inspection

- **Total CSV Files:** 210
- **Distinct Schema Signatures:** 3
- **Sample Files:**
  - `2018-03-01_Seat_Leon_RT_S_Normal.csv`: 2029.5 KB, 32097 rows, 11 columns
  - `ufpe18.csv`: 665.7 KB, 2272 rows, 27 columns
  - `2017-07-11_Seat_Leon_S_RT_Frei.csv`: 1764.0 KB, 28114 rows, 11 columns
  - `2017-07-14_Seat_Leon_KA_KA_Frei.csv`: 435.3 KB, 6829 rows, 11 columns
  - `2017-08-07_Seat_Leon_KA_RT_Frei.csv`: 1736.0 KB, 27371 rows, 11 columns

---

## 5. Architectural Recommendations

1. **Stage 1 Binary Filter:** Train an EfficientNet-B4 / ResNet-50 binary classifier on a balanced, stratified subset of damaged vs. undamaged images.
2. **Stage 2/3/4 Adapters:** Use pre-trained YOLOv8 / Mask R-CNN / SAM 2 adapters with fallback states when weights are absent.
3. **OBD-II Multi-dialect Parser:** Support both Seat Leon headers (`Engine Coolant Temperature [°C]`, etc.) and UFPE headers (`ENGINE_RPM ()`, `VEHICLE_SPEED ()`, etc.).
4. **Data Isolation:** Never modify or move original datasets; store manifests in `data/manifests/` and derived splits in `data/splits/`.
