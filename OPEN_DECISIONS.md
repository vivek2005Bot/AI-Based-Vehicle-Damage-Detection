# Open Decisions & Technical Log — AI-Based Vehicle Damage Detection

> **Specification Reference:** `ANTIGRAVITY_PROJECT_SPEC.md` Section 2.4

---

## 1. Resolved Decisions

### Decision 1: Monorepo Organization
- **Status:** Resolved
- **Choice:** Unified monorepo with `apps/ios/` for the Flutter iOS app, `backend/` for FastAPI & Celery/Redis worker, `ml/` for vision and OBD models/data pipelines, `agents/` for LangGraph agent workflow, `rag/` for document ingestion and retrieval, `reports/` for JSON/PDF report rendering, and `infra/` for Docker/NGINX.
- **Rationale:** Aligns with Spec Section 4 and allows unified contract sharing, testing, and continuous deployment.

### Decision 2: Dataset Directory Resolution
- **Status:** Resolved
- **Finding:** The local workspace contains `dataset/damaged`, `dataset/undamaged`, and `obdiidata` at root.
- **Decision:** Configurable paths via `DATASET_ROOT` (default `./dataset`) and `OBD_DATASET_DIR` (resolves `./obdiidata` or `./dataset/obdiidata`). Preserves all existing files without moving or modifying raw user data.

### Decision 3: Annotation Availability & Model Strategy
- **Status:** Resolved
- **Finding:** Inspection of `dataset/` reveals 20,455 `.jpg` damaged images and 154 `.png` undamaged images, with zero bounding box or segmentation annotation files.
- **Decision:**
  - Stage 1 (Damaged vs Undamaged filter): Trainable directly using the folder-classified images with stratified leakage-free splits.
  - Stage 2 (Taxonomy Classification), Stage 3 (Detection), and Stage 4 (Segmentation): Implement modular inference adapters supporting YOLOv8 / RT-DETR / Mask R-CNN / SAM 2 architectures. When model weights are not loaded or missing, return an explicit `model_not_ready` / `demo` capability status, strictly adhering to the truthfulness rules of Spec §0.3.

### Decision 4: OBD-II Telemetry Formats
- **Status:** Resolved
- **Finding:** Discovered 210 CSV files. Two primary formats:
  1. Seat Leon log format with header including `Time`, `Engine Coolant Temperature [°C]`, `Engine RPM [RPM]`, `Vehicle Speed Sensor [km/h]`, `Air Flow Rate...`, and driving conditions in filename (`Normal`, `Stau`, `Vollbremsung`, `Glatteis`).
  2. UFPE/Drive/Idle format with header `ENGINE_RPM ()`, `VEHICLE_SPEED ()`, `THROTTLE ()`, `ENGINE_LOAD ()`, `COOLANT_TEMPERATURE ()`, etc.
- **Decision:** Implement multi-dialect CSV parser with automatic column alias normalization, PID range validation, and Isolation Forest anomaly detection.

---

## 2. Open Technical Decisions

| ID | Topic | Current Recommendation | Pending Verification |
|---|---|---|---|
| OD-1 | Filter Threshold `T_FILTER` | Default 0.85 (starting reference from spec). | Tune on validation ROC curve to optimize recall on damaged vehicles. |
| OD-2 | Stage 4 Segmenter Choice | Box-prompted SAM 2 adapter with Mask R-CNN fallback. | Evaluate scratch and thin crack boundary accuracy on real images. |
| OD-3 | Severity Weights $w_c$ | Default heuristic: Bumper Smash: 0.35, Glass Crack: 0.25, Dent: 0.20, Broken Light: 0.15, Scratch: 0.10, Flat Tire: 0.20. | Calibrate against certified automotive body shop repair cost matrices. |
| OD-4 | Vehicle Mask Area ($A_{veh}$) Denominator | Use YOLO/segmentation vehicle bounding box / mask when available; fallback to image area with disclaimer. | Test vehicle segmentation models on varying camera angles. |
| OD-5 | RAG Approved Manual Corpus | Curate open-access NHTSA, EPA, and open diagnostic technical service bulletins (TSBs). | Verify public redistribution license for included knowledge chunks. |
