# Vehicle Damage Detection & Roadworthiness Assessment — System Architecture

## 1. System Overview

This system is an end-to-end, multi-modal vehicle damage inspection platform adhering strictly to **`ANTIGRAVITY_PROJECT_SPEC.md`**. It combines:
1. **Flutter Native iOS Mobile Application** for vehicle photographers and claims adjusters.
2. **FastAPI Microservices Backend** offering secure RESTful endpoints, background task dispatching, and PDF reporting.
3. **Four-Stage Cascading Computer Vision Pipeline** for damaged vehicle gating, taxonomy classification, bounding-box detection, and polygon segmentation.
4. **OBD-II Diagnostic Engine** parsing multi-dialect telemetry files, SAE J2012 DTC extraction, and unsupervised Isolation Forest anomaly detection.
5. **Deterministic Safety Rules Engine** ensuring roadworthiness escalations (Safe, Caution, Unsafe) independently of model predictions.
6. **RAG Knowledge Retrieval System** grounding inspection observations in regulatory standards (NHTSA, AGRSS/ANSI, USTMA, SAE J2012).
7. **LangGraph Multi-Agent Orchestration Layer** coordinating vision, telemetry, knowledge retrieval, and risk assessment into unified inspection dossiers.

```
                           +-------------------------------+
                           |      Flutter iOS Client       |
                           |   (Clean Architecture / BLoC) |
                           +---------------+---------------+
                                           | HTTPS / Multipart
                                           v
+-----------------------------------------------------------------------------------------+
|                                    Nginx Reverse Proxy                                  |
|                            (Rate Limiting, SSL, 50MB Uploads)                           |
+------------------------------------------+----------------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------------+
|                                   FastAPI Application                                   |
|               (/auth, /inspections, /analyze, /status, /report, /health)                 |
+--------------------+-----------------------------------------------------+--------------+
                     |                                                     |
                     v                                                     v
+------------------------------------+             +--------------------------------------+
|        PostgreSQL + pgvector       |             |             Redis 7 Cache            |
|  (Inspections, Findings, Reports)  |             |      (Job Status, Lock Management)   |
+------------------------------------+             +--------------------------------------+
                     ^
                     | Async Background Job Dispatch
                     v
+-----------------------------------------------------------------------------------------+
|                         LangGraph Supervisor Orchestrator                               |
+-----------+--------------------+-------------------------+------------------------------+
            |                    |                         |                              |
            v                    v                         v                              v
   +-----------------+  +------------------+     +-------------------+          +------------------+
   |  Vision Agent   |  |    OBD Agent     |     |     RAG Agent     |          |    Risk Agent    |
   | (4-Stage CV)    |  | (DTC & Isolation |     | (NHTSA/AGRSS/SAE) |          | (Deterministic   |
   | - Filter        |  |  Forest Anomaly) |     | - Source Registry |          |  Rules Escalator)|
   | - Classifier    |  +------------------+     | - Grounded Passages          +------------------+
   | - Detector      |                           +-------------------+
   | - Segmenter     |
   | - Severity Calc |
   +-----------------+
```

---

## 2. Four-Stage Computer Vision Pipeline

| Stage | Model Paradigm | Input Shape | Purpose | Early Exit Criteria |
|---|---|---|---|---|
| **Stage 1: Filter** | Binary Classifier (ConvNeXt-V2 / EfficientNet) | $1024 \times 1024 \times 3$ | Gating damaged vs. undamaged vehicle | If $P(\text{damaged}) < 0.85$, exit early as `INTACT`. Downstream detection skipped to save compute. |
| **Stage 2: Taxonomy** | Multi-class Classifier | $1024 \times 1024 \times 3$ | Damage categorization (dent, scratch, smash, crack, flat tire) | Establishes high-level vehicle damage category prior to spatial localisation. |
| **Stage 3: Localisation** | Bounding Box Detector (YOLOv8x / RT-DETR) | $1024 \times 1024 \times 3$ | Component bounding boxes ($x_{\min}, y_{\min}, x_{\max}, y_{\max}$) | Predicts localized region of interest with calibrated confidence thresholds. |
| **Stage 4: Segmentation** | Instance Segmenter (Mask R-CNN / SAM 2) | BBox ROI Crops | Precise damage polygon boundary | Computes pixel area ratio $r_c = A_{\text{mask}} / A_{\text{veh}}$ and severity index $S$. |

### Coordinate Transformations
Aspect-ratio preserving letterbox preprocessing scales the maximum dimension to 1024 pixels, centering on a neutral $(114, 114, 114)$ canvas. Bidirectional mapping transforms coordinates between model tensor space, original image pixels, and iOS screen viewports without spatial distortion.

---

## 3. OBD-II Diagnostics Pipeline

The OBD pipeline handles real-world automotive telemetry:
1. **Multi-Dialect Parser:** Automatically matches both European (Seat Leon driving events with German labels like `Stau`, `Glatteis`) and standard OBD PIDs (`ENGINE_RPM`, `VEHICLE_SPEED`, `ENGINE_COOLANT_TEMP`, `INTAKE_AIR_TEMP`, `THROTTLE_POS`).
2. **SAE J2012 DTC Extraction:** Regular expression extraction for Powertrain (`P`), Chassis (`C`), Body (`B`), and Network (`U`) trouble codes, cross-referenced with a verified automotive fault database.
3. **Isolation Forest Anomaly Detection:** Multivariate unsupervised anomaly scoring detecting abnormal mechanical operating envelopes (e.g., severe overheating, erratic engine load, abnormal vacuum pressure).

---

## 4. Deterministic Risk Escalation Engine

To prevent catastrophic hallucinations, roadworthiness classification is governed by hard deterministic safety rules (`agents/rules.py`):

1. **Unsafe Mandatory Triggers:**
   - Any active Stage 1 Airbag / SRS deployment DTC (`B0001`, `B0002`).
   - Severe engine thermal event (`P0217` or Coolant $> 118^\circ\text{C}$).
   - Structural bumper/front-end crush (`bumper_smash` with severity score $\ge 0.50$).
   - Multiple severe misfires (`P0300`, `P0301`, `P0302`, `P0303`, `P0304`).
2. **Caution Mandatory Triggers:**
   - Wheel speed sensor malfunction (`C0035`).
   - Severe flat tire or sidewall compromise.
   - Windshield crack in the Critical Viewing Area (CVA).
   - Any moderate anomaly count ($> 5$) or visual severity score $\ge 0.25$.
3. **Safe Assessment:**
   - No structural damage, zero active DTCs, normal operating telemetry, severity score $< 0.10$.

---

## 5. Decision-Support Legal Boundary

This application is strictly an **AI Decision-Support System**. All reports and UI screens include explicit regulatory disclaimers:
> *"Roadworthiness assessments (Safe, Caution, Unsafe) generated by this system are automated recommendations intended exclusively to support trained human examiners. This application does not issue a legally binding guarantee of structural integrity or roadworthiness. Critical vehicle safety systems must always be inspected physically by a certified mechanic."*
