# AI-Based Vehicle Damage Detection — Antigravity Build Specification

> **Purpose:** This file is the primary build brief for Antigravity. Read it fully before making changes. Use it to implement the project end to end: iOS app, API/backend, model pipeline, LangGraph agents, RAG knowledge base, data processing, storage, Docker infrastructure, tests, and documentation.
>
> **Primary source:** `AI-Based_Vehicle_Damage_Detection_Final_Formatted_v2(1).docx`, “AI-Based Vehicle Damage Detection.”
>
> **Dataset layout supplied with the task:** `dataset/damaged/`, `dataset/undamaged/`, and `dataset/obdiidata/` (the third folder is spelled exactly this way in the supplied screenshot; do not assume it is a typo or rename it silently).

---

## 0. Instructions to Antigravity — Read First

### 0.1 Build the product, not just a plan

Create a working, maintainable repository. Do not stop after writing an architecture document or generating placeholder screens. Implement a vertical slice first, then expand it:

1. Inspect the existing repository and preserve useful existing files and the supplied dataset directory structure.
2. Create the repository structure described below, adapting to any valid files already present.
3. Implement the Flutter iOS client, FastAPI backend, asynchronous job processing, persisted inspection/report records, and Docker development environment.
4. Implement the vision and OBD interfaces as real, testable modules. If trained model weights or fully labelled data are not yet available, expose a clearly labelled `model_not_ready` / `demo` state rather than inventing predictions or metrics. A deterministic mock may be used only for UI development and automated tests, and must never be presented as a real model result.
5. Implement the LangGraph workflow with the four named specialist agents and explicit, typed state. Use replaceable model/tool adapters so a trained model can be added without rewriting the mobile app or API.
6. Implement RAG ingestion/retrieval and ensure report recommendations cite retrieved sources. If no approved repair manuals or source documents are available, return “No verified repair guidance available” rather than making up guidance.
7. Add tests, configuration examples, Docker health checks, API documentation, setup instructions, and a reproducible dataset/EDA/training workflow.
8. Run the tests and static checks available in the environment. Fix failures before claiming completion. Record any step that cannot be executed locally, with the exact reason and follow-up command.

### 0.2 Requirement labels

Use these labels in code comments, issue notes, and documentation where helpful:

- **[SOURCE REQUIREMENT]** — explicitly described in the supplied project document or dataset screenshot.
- **[IMPLEMENTATION DECISION]** — an engineering choice needed to make the application buildable, but not fixed by the source document.
- **[OPEN DECISION]** — must be decided after inspecting the real dataset, selecting/licensing sources, or running an experiment.
- **[EXPERIMENT REQUIRED]** — do not fill this with invented values. Generate it only from measured project runs.

When this specification adds implementation detail beyond the report, preserve the source requirements and clearly treat the added detail as a proposed implementation decision.

### 0.3 Non-negotiable truthfulness rules

- Do not fabricate model accuracy, F1, mAP, latency, severity calibration, risk-engine agreement, dataset volume, or number of training samples.
- Do not label published CarDD benchmark values as results from this application.
- Do not convert pixel area to cm² without a documented scale reference/calibration object and a validated calibration procedure.
- Do not claim the vehicle is definitely safe based only on an AI output. Display Safe / Caution / Unsafe as a decision-support classification with evidence, limitations, and a clear human/qualified-technician review disclaimer.
- Do not make an automatic repair-price guarantee. A cost estimate is permitted only when a validated, licensed source and method are added.
- Do not silently merge incompatible dataset labels or assume images and OBD logs belong to the same physical vehicles. The supplied report explicitly says the datasets are not paired.
- Do not enable live OBD Bluetooth/dongle access in the first implementation. The source scope is **offline OBD-II/PID CSV upload**. Live OBD support is future scope unless separately requested.
- Keep all secrets, keys, VINs, uploaded images, OBD logs, and report data out of source control and ordinary application logs.
- Keep the iOS app as the only required mobile target. Flutter may technically support other platforms, but iOS is the required release target in this brief.

---

## 1. Product Summary

Build an iOS application for AI-assisted vehicle damage inspection. The user captures or selects one or more still images from multiple vehicle angles, optionally supplies vehicle information, and optionally uploads an offline OBD-II/PID CSV file. The backend coordinates a multi-stage computer-vision pipeline and, where provided, OBD telemetry analysis. A LangGraph supervisor coordinates four specialist agents:

1. **Vision Agent** — damaged/intact filter, damage classification, object localization, instance segmentation, and severity feature calculation.
2. **OBD Analytics Agent** — PID data validation/cleaning, anomaly detection, and Diagnostic Trouble Code (DTC) extraction/mapping.
3. **RAG Knowledge Agent** — retrieval of relevant, approved repair/diagnostic knowledge and source references.
4. **Risk Engine Agent** — combines visual findings, OBD findings, and grounded knowledge into a transparent `Safe`, `Caution`, or `Unsafe` classification with reasons.

The application produces a structured diagnostic/damage report view and downloadable JSON/PDF report. Reports include images/findings, damage classes, bounding boxes, masks/affected areas where available, severity, optional OBD findings, risk classification, retrieved guidance and citations, model/run metadata, and known limitations.

### 1.1 Core user journey

1. Open the iOS app and start a new inspection.
2. Capture or select one or more JPEG/PNG vehicle images. Encourage multiple angles; images remain still images, not video.
3. Optionally enter make, model, year, mileage, and VIN. VIN must be optional and treated as personal/sensitive vehicle data.
4. Optionally select an OBD-II/PID CSV file. In the first version, this is an upload only, not a live connection to an OBD dongle.
5. Review input thumbnails, remove/replace images, and validate CSV/vehicle information.
6. Submit the inspection securely. The API validates the request and enqueues an asynchronous analysis job.
7. Show meaningful progress states while the backend runs the pipeline. Do not imply an exact remaining duration unless the service can estimate it.
8. Display the report with a clear summary, per-image findings, severity, evidence, OBD status if provided, risk classification, grounded repair/diagnostic guidance, and limitations.
9. Allow the user to export/share a PDF and JSON report and revisit past reports according to retention/privacy policy.

### 1.2 Goals

- Filter damaged vs. intact images with a binary classifier before expensive downstream processing.
- Classify damage into the proposed target classes after the damage filter passes.
- Detect/localize each damage instance with bounding boxes.
- Segment damage at pixel level and calculate pixel area and relative area-based severity.
- Optionally analyze offline OBD-II/PID telemetry and DTCs.
- Combine image and OBD evidence in a rule-transparent drivability risk classification.
- Generate RAG-grounded reports whose repair/diagnostic guidance cites sources.
- Evaluate every stage and the end-to-end system with defined metrics and leakage-free splits.
- Deliver a usable Flutter application targeted at iOS and a containerized, documented backend.

### 1.3 Non-goals for the first release

- Video-based inspection.
- Live OBD-II Bluetooth/Wi-Fi dongle connection or continuously streamed telemetry.
- Guaranteed repair pricing or automated insurance/legal claim adjudication.
- Vehicle-make-specific severity calibration beyond what supported data permits.
- On-device inference as a requirement. Initial ML inference is server-side; on-device inference is future work.
- Claim that unrelated public image and OBD datasets form paired examples for individual vehicles.

---

## 2. Source-Derived Requirements and Known Unknowns

### 2.1 Pipeline specified by the source report

The report's end-to-end flow is:

`Input → Preprocessing → Damage Classification → Damage Detection → Segmentation → Severity Analysis → optional OBD-II Analysis → Report`

Expanded operational stages:

| Stage | Required behavior | Output |
|---|---|---|
| M1 Input | Accept images, optional OBD-II CSV, and optional vehicle information | Validated request |
| M2 Preprocessing | Quality check, resize (1024×1024 is a reference value), normalize, optionally crop vehicle region; preserve annotation geometry | Model-ready tensors and image metadata |
| M3 Stage 1 filter | Binary Damaged/Intact prediction; reference threshold 0.85 is only a starting point and must be tuned on validation data | Damage flag and confidence |
| M4 Stage 2 classifier | Multi-class/multi-label damage-type classification | One or more labels and confidences |
| M5 Stage 3 detector | Localize damage instances | `[xmin, ymin, xmax, ymax]` boxes and instance count |
| M6 Stage 4 segmenter | Produce instance masks, using Mask R-CNN or SAM 2 prompted by detector boxes | Masks/polygons and pixel area |
| M7 Severity | Calculate mask/vehicle relative area and class-weighted score | Score and Low/Medium/High severity |
| M8 OBD-II, optional | Clean PIDs, detect anomalies, extract DTCs | Anomaly score/flags, PIDs, DTCs |
| M9 Knowledge | Retrieve manual/repair guidance with RAG | Grounded passages and citations |
| M10 Risk | Fuse vision and OBD evidence with retrieved context | Safe/Caution/Unsafe plus reason codes |
| M11 Report | Persist and return structured report | JSON and PDF |

### 2.2 Proposed damage taxonomy

The report proposes these classes, but exact mappings must be verified against downloaded annotation files:

- `scratch`
- `dent`
- `glass_crack`
- `bumper_smash`
- `flat_tire`
- `broken_light`

The document warns that `bumper_smash` may not exist as a native source label. Any merge, derivation, exclusion, or renaming must be explicit, documented, and tested. Preserve raw source label names alongside canonical application labels.

### 2.3 Dataset status and uncertainty

The document names three public dataset sources and gives volumes as unverified references:

- **VehiDE** — described as high-resolution images and annotations; stated volume in the report is 14,000+ images and 32,000+ annotations, to be re-verified. Intended for filter/detection/segmentation stages.
- **CarDD** — described as images and defect instances; stated volume is 4,000+ images and 9,000+ instances, to be re-verified. Damage category examples include scratch, dent, glass-related defects, lamp, and tire categories. Exact labels must be verified. Intended for classification/detection/segmentation and cross-dataset testing.
- **OBD-II PID dataset** — described as tabular CSV/PID time series; stated volume is 100k+ records, to be re-verified. Exact source, license, fields, and labels must be confirmed.

The user's local directory screenshot shows:

```text
dataset/
├── damaged/
├── undamaged/
└── obdiidata/
```

Treat this as an available local project-data layout, not proof of dataset contents, completeness, label quality, or licensing. Build a data-inspection script that inventories the actual files before training. Do not require the folder names to be changed. Use a configurable dataset root and configurable OBD directory path so `obdiidata` can continue to work even if the name is later standardized.

### 2.4 Values that must not be guessed

The project must explicitly record and later resolve:

- Exact dataset download URLs, revisions, licenses, and file manifests.
- Exact classes and annotation formats from VehiDE and CarDD.
- Class harmonization table and treatment of `bumper_smash`.
- Whether masks are supplied, derivable, or missing per dataset.
- OBD CSV column names, units, sampling rate, DTC representation, labels, and data provenance.
- Train/validation/test split assignments and grouping strategy.
- Best candidate model per stage and actual trained weights.
- Validation-calibrated filter confidence threshold (0.85 is a reference, not a final value).
- Class severity weights and thresholds mapping score to Low/Medium/High.
- Risk rules and any domain expert/technician validation.
- Approved manuals/repair corpus, rights to ingest it, and source metadata.
- Hardware used for latency measurements and whether the 15-second target is achieved.
- Whether and how to delete raw uploads/reports, and required retention period.

Keep an `OPEN_DECISIONS.md` or a similar section in the project docs and update it as decisions are made.

---

## 3. Required Technology Architecture

The supplied report specifies these technologies or candidate technology families. Implement the named components, but keep model choices configurable until experiments justify final selection.

| Layer | Source-specified technology | Responsibilities |
|---|---|---|
| iOS client | Flutter (iOS) | Image capture/selection, vehicle info, offline OBD CSV upload, progress, report display/export |
| API gateway | FastAPI + NGINX | JWT authentication, request validation, upload handling, rate limiting, async job queue |
| Agent orchestration | LangGraph supervisor | Agent routing, typed state, workflow control, error/fallback handling |
| Vision models | EfficientNet-B4/ResNet50; ConvNeXt/ViT; YOLOv8x/RT-DETR; Mask R-CNN/SAM 2 candidates | Filter, classify, detect, segment |
| OBD analytics | Isolation Forest/XGBoost candidates | Anomaly detection and/or labeled fault classification |
| Knowledge store | PostgreSQL + pgvector; LlamaIndex | Hybrid dense/sparse retrieval over approved manuals and repair guidance |
| Queue/cache | Redis | Async job queue state, cache/pub-sub where useful |
| Deployment | Docker | Reproducible services and persistent storage |

**Implementation decisions recommended for a runnable first version:** Python 3.11+ for the API/worker/ML backend, Pydantic schemas, SQL migrations, a Flutter stable channel version pinned in project docs, and a typed REST API under `/api/v1`. Pin exact versions in lockfiles or dependency manifests once selected. Do not use “latest” floating versions for production builds.

### 3.1 High-level architecture

```text
Flutter iOS app
   │ HTTPS, JWT
   ▼
NGINX reverse proxy / upload limits / rate limiting
   │
   ▼
FastAPI API ─────────── PostgreSQL (+ pgvector)
   │                         │
   ├── Redis queue            ├── users / inspections / reports / jobs
   │                          └── knowledge chunks / source metadata
   ▼
Background analysis worker / LangGraph Supervisor
   ├── Vision Agent
   │    ├── Stage 1 damage filter
   │    ├── Stage 2 type classifier
   │    ├── Stage 3 detector
   │    ├── Stage 4 segmenter
   │    └── severity calculation
   ├── OBD Analytics Agent (if CSV supplied)
   ├── RAG Knowledge Agent (LlamaIndex + hybrid retrieval)
   └── Risk Engine Agent
   │
   └── report JSON + PDF renderer + persisted results
```

The vision and OBD agents should be dispatched in parallel when both inputs exist. Their completed outputs feed the knowledge retrieval and risk/report steps. If OBD data is absent, record `obd_status: "not_provided"`; do not treat missing telemetry as healthy telemetry.

### 3.2 Service boundaries

- **iOS client:** presentation and user interaction; no model inference or database credentials. Use the API for all analysis.
- **API:** user auth, request validation, upload/session orchestration, inspection/report CRUD, and queue submission.
- **Worker:** long-running inspection processing. It must be independent from the API web process so API requests return promptly.
- **ML modules:** pure-ish reusable functions with typed inputs/outputs and model adapter interfaces. Model weights are loaded once per worker where possible.
- **Agent workflow:** manages execution order and typed evidence state; it must not hide model errors or generate unsupported findings.
- **RAG ingestion job:** imports approved documents, chunks them, stores source metadata/embeddings, and supports index refresh.
- **Database:** metadata and structured results. Store binaries in a file/object storage abstraction; in local development, use a private persistent Docker volume. A cloud object store can be added through configuration, not hard-coded.
- **NGINX:** reverse proxy, TLS termination in deployed environments, request/upload size limits, and coarse rate limiting. JWT authorization remains enforced by FastAPI.

---

## 4. Repository Layout to Create

Adapt this structure if an existing valid repository already exists, but keep clear separation between mobile, API, models, agents, data tools, infra, and tests.

```text
vehicle-damage-ai/
├── README.md
├── ANTIGRAVITY_PROJECT_SPEC.md
├── OPEN_DECISIONS.md
├── .gitignore
├── .dockerignore
├── .env.example
├── docker-compose.yml
├── Makefile
├── pyproject.toml                 # or backend-specific lock/manifests
├── docs/
│   ├── architecture.md
│   ├── api-contract.md
│   ├── data-dictionary.md
│   ├── model-card.md
│   ├── privacy-and-security.md
│   ├── evaluation-plan.md
│   └── runbook.md
├── apps/
│   └── ios/
│       ├── pubspec.yaml
│       ├── lib/
│       │   ├── main.dart
│       │   ├── app.dart
│       │   ├── core/
│       │   │   ├── config/
│       │   │   ├── networking/
│       │   │   ├── errors/
│       │   │   ├── theme/
│       │   │   ├── routing/
│       │   │   └── widgets/
│       │   ├── features/
│       │   │   ├── auth/
│       │   │   ├── home/
│       │   │   ├── inspection_creation/
│       │   │   ├── image_capture/
│       │   │   ├── vehicle_info/
│       │   │   ├── obd_upload/
│       │   │   ├── analysis_status/
│       │   │   ├── report/
│       │   │   ├── history/
│       │   │   └── settings_privacy/
│       │   └── shared/
│       ├── test/
│       └── ios/
├── backend/
│   ├── Dockerfile
│   ├── worker.Dockerfile            # may share base image with API
│   ├── migrations/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   ├── api/v1/
│   │   │   ├── router.py
│   │   │   └── endpoints/
│   │   ├── schemas/
│   │   ├── models_db/
│   │   ├── repositories/
│   │   ├── services/
│   │   │   ├── inspection_service.py
│   │   │   ├── report_service.py
│   │   │   ├── file_storage.py
│   │   │   └── job_service.py
│   │   ├── tasks/
│   │   └── db/
│   └── tests/
├── ml/
│   ├── README.md
│   ├── config/
│   │   ├── class_mapping.yaml
│   │   ├── severity.yaml
│   │   └── model_registry.yaml
│   ├── data/
│   │   ├── inspect_dataset.py
│   │   ├── validate_annotations.py
│   │   ├── harmonize_labels.py
│   │   ├── build_splits.py
│   │   └── generate_eda.py
│   ├── vision/
│   │   ├── preprocessing.py
│   │   ├── filter_model.py
│   │   ├── classifier.py
│   │   ├── detector.py
│   │   ├── segmenter.py
│   │   ├── severity.py
│   │   ├── schemas.py
│   │   └── pipeline.py
│   ├── obd/
│   │   ├── schemas.py
│   │   ├── csv_parser.py
│   │   ├── preprocessing.py
│   │   ├── features.py
│   │   ├── anomaly.py
│   │   ├── dtc.py
│   │   └── pipeline.py
│   ├── training/
│   │   ├── train_filter.py
│   │   ├── train_classifier.py
│   │   ├── train_detector.py
│   │   ├── train_segmenter.py
│   │   ├── train_obd.py
│   │   └── evaluate.py
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── cross_dataset.py
│   │   ├── latency.py
│   │   └── reports.py
│   ├── artifacts/                    # ignored by git by default
│   └── tests/
├── agents/
│   ├── state.py
│   ├── graph.py
│   ├── supervisor.py
│   ├── vision_agent.py
│   ├── obd_agent.py
│   ├── rag_agent.py
│   ├── risk_agent.py
│   ├── rules.py
│   └── tests/
├── rag/
│   ├── ingest.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── retrieval.py
│   ├── prompts.py
│   ├── source_registry.py
│   └── tests/
├── reports/
│   ├── json_schema.json
│   ├── pdf_renderer.py
│   └── templates/
├── scripts/
│   ├── dev_setup.sh
│   ├── check_env.py
│   ├── seed_dev_user.py
│   └── smoke_test.sh
├── infra/
│   └── nginx/
│       └── nginx.conf
├── data/                              # generated metadata only; keep raw data in dataset/
│   ├── manifests/
│   ├── splits/
│   └── processed/                     # ignored unless small, reproducible metadata
└── dataset/
    ├── damaged/                       # supplied local directory; inspect actual contents
    ├── undamaged/                     # supplied local directory; inspect actual contents
    └── obdiidata/                     # supplied spelling; configurable path
```

If Antigravity finds a different existing project root structure, do not move or duplicate large datasets unnecessarily. Record actual discovered paths in `docs/data-dictionary.md` and use configuration to point to them.

### 4.1 Git hygiene

Include `.gitignore` entries for at least:

- `.env`, secrets, certificates, tokens, and local config overrides.
- Python virtual environments, `__pycache__`, test/coverage caches.
- Flutter/Dart build output, `.dart_tool`, generated build files where appropriate.
- Model checkpoints/weights, large datasets, logs, temporary uploads, local databases, embeddings cache, and PDF exports.
- Local `dataset/` contents unless the user explicitly confirms the data is small, licensed for repository distribution, and intended to be committed. Keep dataset scripts and manifests tracked, not raw private/large data by default.

---

## 5. iOS Application Requirements (Flutter)

### 5.1 Design principles

- Build an iOS-first app with familiar navigation and responsive layouts for iPhone. Test safe areas, compact screens, dynamic text sizes, keyboard overlays, and both light/dark appearance.
- Keep the interface calm and readable. Severity/risk must use text labels and icons as well as color; never rely on color alone.
- Show where each result came from: image finding, OBD telemetry, retrieved guidance, or rule-based risk decision.
- Clearly distinguish “analysis pending,” “analysis completed,” “analysis incomplete,” and “model not available.”
- Provide accessible labels for buttons, camera controls, upload status, risk status, charts, and report sections.
- Never suggest that an image-only result is a complete vehicle safety assessment.

### 5.2 Required screens

#### A. Welcome / sign-in (if authentication is enabled)

- App name: **Vehicle Damage AI** or a configurable product name.
- Short plain-language explanation of AI-assisted visual damage assessment and optional OBD CSV analysis.
- JWT-backed authentication flow because the source architecture calls for JWT authentication.
- Store access tokens securely using iOS Keychain-backed secure storage, not plain preferences.
- Handle expired/invalid sessions and sign-out. Keep dev-only login/seed flows disabled in production.

If account creation is not part of the first deliverable, use a documented local development account flow but do not ship a hard-coded production credential.

#### B. Home / inspection dashboard

- Primary action: **New inspection**.
- Recent inspection cards with created date/time, thumbnail if permitted, analysis state, risk class, and a tap-through to report.
- Empty state with clear instructions when no inspections exist.
- A refresh action and reliable loading/error states.
- Do not show fabricated pre-existing reports in production. Seed/demo records must be explicitly marked demo.

#### C. New inspection — image capture and selection

- Capture via iOS camera or select from Photos.
- Accept JPEG and PNG.
- Support one or more still images and multiple vehicle angles.
- Show thumbnails, image count, file sizes, remove/replace/reorder controls, and a full-screen preview.
- Validate that at least one image exists before submission.
- Validate image readability, decodable format, size, and minimum resolution as configured by the backend. Client checks are convenience only; the backend must repeat validation.
- Do not silently crop away damage. If image cropping or compression is offered, preserve the original securely or clearly explain which version is submitted.
- Display useful capture hints (good lighting, include the damaged area and surrounding vehicle context, avoid motion blur, do not use video in this version).
- Ask for permission only when a capability is invoked. Include the needed iOS camera/photo-library usage descriptions.
- Show a helpful error if permission is denied, with a link to iOS Settings if supported by the chosen plugin.

#### D. Vehicle information (optional)

Fields from the report:

- Make (text or searchable selector if a list is available).
- Model.
- Year.
- Mileage/odometer value and unit.
- VIN (optional; sensitive; avoid placing it in analytics or ordinary logs).

Vehicle info improves retrieval/report context but must not block an image-only inspection. Validate year and mileage format without pretending to validate VIN ownership or legal identity.

#### E. OBD-II CSV upload (optional)

- Use the iOS Files/document picker to select CSV.
- Clearly say “Upload an existing OBD-II/PID CSV file”; do not imply a live dongle connection.
- Show filename, file size, remove/replace option, parse/validation status, and a summary of detected columns after server validation.
- Support optional timestamp and PID columns. A DTC field may be present. Exact schema is dataset-dependent and must be configurable/documented.
- If the CSV schema is unrecognized, provide a useful error listing missing/unsupported columns and a link/help screen explaining the expected format.
- Treat a missing CSV as “not provided,” not “normal telemetry.”
- The CSV may contain time series; the backend owns cleaning, imputation, outlier treatment, scaling, and windowing.

#### F. Review and submit

- Summarize selected image count, vehicle information, and whether OBD CSV is attached.
- Allow the user to go back and change inputs.
- Explain that results are AI-assisted and may require professional review.
- Disable submission while invalid or already in progress; avoid duplicate submission through retries/idempotency.
- Show a clear upload state and retry when network upload fails.

#### G. Analysis progress

Use server job state, not a fake local progress percentage. Show stages only when supported by backend progress events:

- Upload received / validating inputs.
- Vision analysis.
- OBD analysis (only if supplied).
- Retrieving repair/diagnostic knowledge.
- Calculating risk and generating report.
- Completed / completed with warnings / failed.

Poll a job-status endpoint at a conservative interval or use a documented push mechanism if actually implemented. Cancel/back navigation must not accidentally delete or corrupt a running job. On app relaunch, restore in-progress inspection status from the API.

#### H. Results / report screen

Required sections:

1. **Overall summary:** damage detected/not detected, key findings, model/status disclaimer.
2. **Risk classification:** Safe/Caution/Unsafe, with text explanation, evidence inputs used, and any mandatory escalation reason.
3. **Visual findings per image:** class label(s), confidence, bounding-box overlay, mask overlay when available, number of instances, and processing/model state.
4. **Severity:** score and Low/Medium/High level once calibrated. Include affected pixel area and relative area. Show cm² only when scale calibration is valid.
5. **OBD-II results:** “Not provided,” “Analysis completed,” “Anomaly detected,” “Input invalid,” or “Analysis unavailable,” as appropriate; flagged PIDs, anomaly score, active DTCs, and mapping/source status.
6. **Repair/diagnostic guidance:** retrieved passages, source/manual name, section/page where available, link/reference metadata, and limitations. If no relevant sources are retrieved, clearly say so.
7. **Report metadata:** inspection ID, timestamps, analysis version, model versions, threshold/config version, warnings, and incomplete stages.
8. **Export:** download/share JSON and PDF through the iOS share sheet. Export only user-authorized inspection information; respect deletion/retention settings.

Use an image viewer with overlays. Bounding-box and polygon coordinates must be scaled correctly from original/image tensor dimensions to the displayed image. Include a legend and let users hide/show overlays.

#### I. Inspection history

- List inspections owned by the authenticated user.
- Search/filter by date or risk status if the API supports it.
- Show a stable state for pending, completed, partial, failed, and deleted records.
- Detail screen loads the persisted report from backend, not only local memory.
- Handle expired/deleted reports gracefully.

#### J. Settings and privacy

- App version, privacy notice, data retention/deletion details, sign out, and support/diagnostic export without personal data.
- If delete-inspection is implemented, clearly explain whether raw files, stored reports, job records, and backups are deleted immediately or according to retention policy.
- Do not expose admin dataset-management screens to ordinary users.

### 5.3 Flutter architecture

Use a maintainable feature-first structure. Choose a state-management and routing solution that fits the existing project and pin dependencies. If starting fresh, use Riverpod or Bloc and a typed router; document the choice and avoid mixing multiple state-management systems.

- `core/config`: environment/base URL; dev/staging/prod configuration.
- `core/networking`: HTTP client, JWT injection, timeouts, upload progress, retries limited to safe/idempotent calls, error normalization.
- `core/errors`: user-friendly errors tied to API error codes.
- Feature modules: presentation, controllers/state, API/repository clients, domain models.
- Use generated/typed DTOs where practical. Keep API JSON keys and enums aligned with Pydantic schemas.
- Add widget tests for image selection state, CSV validation messaging, progress status, report rendering, error states, and overlay coordinate scaling.

### 5.4 iOS-specific setup

- Use a pinned Flutter SDK and compatible Xcode/iOS deployment target; document exact versions chosen.
- Configure camera/photo permissions and appropriate privacy usage descriptions in `ios/Runner/Info.plist` as required by selected plugins.
- Test on at least one simulator and, when available, a physical iPhone for camera, document picker, file upload, secure token storage, and share-sheet behavior.
- Use HTTPS in non-local environments. Do not hard-code a LAN IP or localhost URL into production. For simulator development, document how the API base URL differs from a physical device.
- Do not request unrelated permissions (contacts, location, microphone, Bluetooth) for the first version.
- Add app icon, launch screen, bundle identifier placeholders, app display name, and release build instructions. Do not invent a real App Store account/certificate.

---

## 6. Backend API — FastAPI

### 6.1 API conventions

- Base prefix: `/api/v1`.
- JSON uses `snake_case`; enums have documented stable values.
- Use Pydantic request/response schemas for all external payloads.
- Use consistent error responses, request IDs/correlation IDs, structured logs, and OpenAPI docs.
- All user resources must be scoped to the authenticated user. Do not trust user IDs supplied in a request body.
- Upload endpoints validate content types, extension, actual decoding, file size, count, and CSV row/column limits on the server.
- Protect against path traversal, malicious filenames, MIME spoofing, archive bombs, CSV formula exposure on export, and oversized payloads.
- Use short request timeouts for API operations; actual ML computation runs asynchronously in worker processes.
- Add idempotency handling or duplicate-job detection for inspection submission where appropriate.

### 6.2 Proposed API endpoints

The following are implementation contracts suggested to operationalize the source architecture. Keep them documented in `docs/api-contract.md` and align the iOS client exactly.

#### Health and configuration

- `GET /health/live` — process is alive.
- `GET /health/ready` — API can reach required database/queue services.
- `GET /api/v1/meta` — API version, schema version, enabled capabilities, and whether trained models are available. Never return secrets.

#### Authentication

- `POST /api/v1/auth/login` — exchange supported credentials for access token (and refresh token if implemented).
- `POST /api/v1/auth/refresh` — optional token refresh.
- `POST /api/v1/auth/logout` — invalidate refresh/session token if server-side sessions are used.
- `GET /api/v1/auth/me` — current user profile/minimal account state.

JWT authentication is required by the source architecture. Choose a secure login mechanism based on deployment needs and document password hashing, token expiry, refresh/revocation policy, and account creation policy. Do not add a hard-coded shared production password.

#### Inspections

- `POST /api/v1/inspections` — create a draft inspection and store optional vehicle information; return `inspection_id`.
- `POST /api/v1/inspections/{inspection_id}/images` — upload one image or a documented multipart collection; return file IDs and server validation status.
- `POST /api/v1/inspections/{inspection_id}/obd` — upload the optional CSV and return parse/validation summary.
- `POST /api/v1/inspections/{inspection_id}/analyze` — validate prerequisites, enqueue a job, return HTTP `202 Accepted` with `job_id` and current state.
- `GET /api/v1/jobs/{job_id}` — job status, current stage, progress only if reliable, warnings, retryable/fatal state.
- `GET /api/v1/inspections` — paginated history for current user.
- `GET /api/v1/inspections/{inspection_id}` — inspection metadata/status.
- `GET /api/v1/inspections/{inspection_id}/report` — structured JSON report.
- `GET /api/v1/inspections/{inspection_id}/report.pdf` — authenticated PDF response or short-lived download URL.
- `DELETE /api/v1/inspections/{inspection_id}` — optional user-initiated deletion, with explicit cascading/retention behavior.

Do not return a report until its state and completeness are clear. Use meaningful status codes: 400/422 for invalid inputs, 401/403 for auth/authorization, 404 for inaccessible/nonexistent objects without leaking ownership, 409 for invalid state/idempotency conflict, 413 for files too large, 429 for rate limits, and 5xx for unexpected failures.

### 6.3 Inspection lifecycle

Suggested states:

- `draft`
- `validating`
- `queued`
- `processing`
- `completed`
- `completed_with_warnings`
- `failed_retryable`
- `failed_terminal`
- `cancelled` (only if real cancellation is implemented)

Enforce valid state transitions in the service layer. A job retry must preserve auditability and make it clear which attempt generated the current report. Store job attempt count and failure category; do not expose stack traces to the client.

### 6.4 Request/input validation

**Images:**

- Accepted formats: JPEG/JPG and PNG.
- One or more images are required for an analysis.
- Check actual bytes/decode, dimensions, file size, allowed count, empty files, and duplicate image hash.
- Preserve original dimensions and record any resize/crop/letterbox transform so boxes/masks can be mapped back to the original image.
- The report references a 1024×1024 resize target; make it configurable and preserve aspect ratio unless a model's documented input needs another policy.

**OBD CSV:**

- Optional; no CSV is a valid inspection state.
- Validate parser encoding, delimiter, row/column count, timestamp parse, numeric feature values, duplicate rows, missing values, units where known, and DTC columns.
- Include a data-quality report in the OBD agent output.
- Do not assume all CSV files use identical PID names/units. Use adapters/mapping configuration.

**Vehicle info:**

- Optional make/model/year/mileage/VIN fields.
- Treat VIN as sensitive personal/vehicle data; mask it in logs, analytics, and user-visible diagnostics by default.

### 6.5 Example API response: job status

Use this as a schema guide, not as a hard-coded live response:

```json
{
  "job_id": "<uuid>",
  "inspection_id": "<uuid>",
  "status": "processing",
  "current_stage": "vision_analysis",
  "completed_stages": ["input_validation"],
  "warnings": [],
  "created_at": "<ISO-8601 timestamp>",
  "updated_at": "<ISO-8601 timestamp>"
}
```

### 6.6 Error format

Keep the error response predictable and safe:

```json
{
  "error": {
    "code": "CSV_SCHEMA_INVALID",
    "message": "The uploaded CSV does not contain the required timestamp/PID columns.",
    "details": {"missing_columns": ["<column-name>"]},
    "request_id": "<correlation-id>"
  }
}
```

Never leak SQL, stack traces, filesystem paths, environment variables, bearer tokens, or raw sensitive fields.

---

## 7. Database, Storage, and Persistence

Use PostgreSQL for structured records and pgvector for knowledge embeddings. Apply database migrations and enforce ownership/foreign-key constraints. If a simpler ORM is used, keep the schema explicit and migrations reproducible.

### 7.1 Suggested entities

These are implementation proposals because the source report names PostgreSQL/pgvector and stored reports but does not provide a complete relational schema.

- **users**: ID, auth identifier, password hash/identity provider reference as applicable, status, created/updated timestamps.
- **inspections**: ID, user ID, lifecycle status, optional vehicle fields, input metadata, creation/update timestamps, current report ID, retention/deletion state.
- **inspection_files**: ID, inspection ID, role (`vehicle_image` or `obd_csv`), private storage key, original filename sanitized, media type, byte size, hash, dimensions or CSV metadata, upload/validation state, creation time.
- **analysis_jobs**: ID, inspection ID, status, attempt, current stage, stage events, started/finished timestamps, error code/category, worker version.
- **reports**: ID, inspection ID, schema version, JSON payload, PDF storage key or generation metadata, risk label, completeness/warning state, generated timestamp.
- **model_runs**: report/job relation, filter/classifier/detector/segmenter/OBD model versions, thresholds/config version, timing metadata, inference mode (`real`, `mock_for_test`, `model_unavailable`).
- **knowledge_sources**: ID, title, publisher/manufacturer, document type, source URL or local reference, version/date, license/ingestion permission, checksum, ingestion status.
- **knowledge_chunks**: source ID, page/section, text chunk, metadata, embedding/vector, sparse index fields, chunking version.
- **audit_events**: minimal security/audit events; avoid storing full images, full VIN, full CSV rows, or tokens in event payloads.

Add appropriate timestamps, indexes, pagination indexes, uniqueness constraints, and deletion/retention strategy. Use UUIDs or another non-guessable public ID. Do not return internal storage keys to the mobile client.

### 7.2 Binary file storage

- Keep uploaded images/CSVs in private storage, not in a public web directory.
- Use generated storage names/IDs rather than user-provided filenames as paths.
- In Docker development, use a named persistent volume or a well-defined bind mount.
- Abstract storage behind `FileStorage` so local disk can later be replaced by S3-compatible/object storage without changing business logic.
- Restrict file access to authorized inspection owners. Downloads must be authenticated or use short-lived signed URLs.
- Implement cleanup jobs and retention configuration; never delete files unexpectedly as a side effect of a failed analysis retry.

---

## 8. Computer-Vision Pipeline

### 8.1 Stage order and gating

For each uploaded image:

1. Decode/validate image and run quality checks.
2. Apply preprocessing using configured target size (1024×1024 is the report's reference), normalization and vehicle crop policy. Record transforms.
3. Run Stage 1 damaged/intact filter.
4. If the image is below the calibrated threshold, mark it as predicted intact and skip classification/detection/segmentation. Preserve confidence and filter/model version.
5. If classified as potentially damaged, run Stage 2 damage classifier.
6. Run Stage 3 detector and return one box per detected instance, with canonical labels and confidence values.
7. Run Stage 4 instance segmenter. The report proposes Mask R-CNN or SAM 2 prompted by detection boxes. Make segmenter implementation replaceable.
8. Calculate mask pixels/area and severity features, then aggregate image-level and inspection-level findings.
9. If any stage is unavailable or fails, annotate that fact. Do not represent missing stages as negative findings.

The report's pseudocode filters when `p_damage < T_FILTER`. The reference threshold is 0.85 but must be tuned on held-out validation data to balance compute savings against dangerous false negatives. Record threshold choice and measured recall impact.

### 8.2 Model selection and registry

Candidate models in the source report:

| Stage | Candidates | Implementation note |
|---|---|---|
| 1 filter | EfficientNet-B4, ResNet50 | Compare accuracy, precision, recall, F1, latency, compute saved |
| 2 type classifier | ConvNeXt, ViT-Base | Compare macro-F1 and per-class F1; transformer is data-hungry per report |
| 3 detector | YOLOv8x, RT-DETR | Compare mAP@0.5, mAP@0.5:0.95, AP by class, latency |
| 4 segmenter | Mask R-CNN, SAM 2 | Compare Mean IoU, Dice, mask AP, runtime, boundary quality for thin scratches/cracks |
| OBD anomaly | Isolation Forest, XGBoost | Unsupervised baseline vs supervised model when valid labels exist |

Do not train all candidates blindly before data inventory. First establish data formats, label availability, baseline and resource budget. Record the winning choice only after evaluation; keep alternatives in the registry/configuration for reproducibility.

`model_registry.yaml` should define model name/version, artifact location, input size, canonical classes, preprocessing version, label mapping version, confidence thresholds, and availability. Model weight artifacts should be ignored by Git or tracked with a deliberate artifact system.

### 8.3 Shared output contract

Define Pydantic/domain schemas for all intermediate results. Suggested per-image structure:

```json
{
  "image_id": "<uuid>",
  "damage_detected": true,
  "damage_probability": null,
  "filter_threshold": null,
  "filter_model": "<model-name-or-unavailable>",
  "classifications": [
    {"label": "<canonical-class>", "confidence": null, "source_label": "<raw-source-label>"}
  ],
  "detections": [
    {
      "instance_id": "<id>",
      "label": "<canonical-class>",
      "confidence": null,
      "bbox_xyxy": [0, 0, 0, 0],
      "coordinate_space": "original_image_pixels",
      "mask": null,
      "mask_pixel_area": null,
      "relative_area": null
    }
  ],
  "severity": {
    "score": null,
    "level": "unavailable",
    "calibration_version": null
  },
  "stage_status": {
    "filter": "completed",
    "classification": "not_run",
    "detection": "not_run",
    "segmentation": "not_run",
    "severity": "not_run"
  },
  "warnings": []
}
```

The nulls are intentional schema placeholders, not model outputs. Replace them only with measured output values. Use clear enums for stage status such as `completed`, `not_run`, `skipped_intact`, `failed`, and `model_unavailable`.

### 8.4 Detection geometry

- Canonical box format: `[xmin, ymin, xmax, ymax]` (`xyxy`).
- Define all coordinate units and reference space; the public report schema should state whether coordinates refer to original image pixels or normalized 0–1 coordinates. Recommended public output is original-image pixel coordinates.
- Validate bounds and box ordering; clip to valid original image boundaries after inverse transforms.
- Masks can be serialized as polygons or compact encoded masks; document the representation and coordinate space.
- Preserve transforms for resize, padding, or crop. Overlay geometry in the iOS app must use the inverse transform and fit the displayed image correctly.

### 8.5 Severity calculation

The source proposes:

- `A_mask`: total pixels covered by damage segmentation masks.
- `A_veh`: pixels covered by the vehicle region.
- Relative damage ratio `r = A_mask / A_veh`.
- Severity score `S = Σ (w_c × r_c)`, where `w_c` is a class-dependent weight and `r_c` is relative area for that class/instance.
- Map score to `Low`, `Medium`, `High` using calibrated cutoffs.

Requirements:

- Calculate per-instance and aggregated values without double-counting overlapping masks; document the aggregation policy.
- Obtain/estimate the vehicle region robustly or report the denominator/method and its confidence. If `A_veh` is unavailable, return pixel area only and set relative severity to unavailable rather than dividing by an invalid area.
- Put weights and cutoffs in versioned config, not hard-coded magic numbers.
- Calibrate weights/cutoffs against labelled repair/severity data or expert-labelled results. Until that exists, return an explicitly provisional area-derived indicator and mark calibrated severity unavailable. Do not imply clinical/engineering certainty.
- Convert to cm² only when a documented scale reference exists and calibration is validated. Otherwise show pixel area and ratio only.

### 8.6 Preprocessing and image quality

- Fail gracefully on unreadable/corrupted files.
- Assess at least resolution, severe blur/underexposure if implemented, orientation metadata, and aspect ratio.
- Preserve aspect ratio (letterbox/pad when appropriate) rather than distorting damage geometry.
- Do not crop automatically without recording the crop transform.
- Training augmentations proposed in the report include flip, color jitter, and scale. Apply only augmentations that do not invalidate labels or change class semantics for the selected task.
- Deduplicate exact/perceptual duplicates and prevent cross-split leakage.

---

## 9. Dataset Ingestion, EDA, and Training

### 9.1 First action: inventory the actual files

Before training, create and run `ml/data/inspect_dataset.py`. It must:

- Detect the project root and accept `--dataset-root` (default `dataset/`).
- Inspect `damaged/`, `undamaged/`, and `obdiidata/` without requiring renaming.
- Report counts by folder, extensions, total size, unreadable/corrupt files, duplicate hashes, image width/height/aspect ratios, and CSV candidate files/columns/row counts.
- Detect whether the source images have only folder-level labels, bounding boxes, masks, or additional annotation files. Never infer that bounding boxes/masks exist merely because a dataset is intended for detection/segmentation.
- Write a timestamped machine-readable JSON manifest plus a human-readable Markdown report under `data/manifests/` or `reports/`.
- Avoid printing private paths beyond useful root-relative paths if report artifacts may be shared.
- Exit non-zero when a required directory is absent, but clearly distinguish “optional OBD folder missing” from invalid mandatory image folders.

If source datasets are downloaded separately, store their original unmodified copies separately and map them through configuration. Do not overwrite the supplied local folders.

### 9.2 Label mapping

Create `ml/config/class_mapping.yaml` with raw-to-canonical mappings for each dataset. Required canonical target labels:

```yaml
canonical_classes:
  - scratch
  - dent
  - glass_crack
  - bumper_smash
  - flat_tire
  - broken_light
```

This is an illustrative config shape, not a claim that these exact source labels already exist. Fill source mappings only after inspecting the annotation files. Support one of these explicitly documented treatments for an unavailable class: `exclude`, `merge_to:<canonical-label>`, or `derived_label` with an auditable rule. Store the raw label and mapping version in generated manifests.

### 9.3 Leakage-free train/validation/test splits

- Use deterministic, seeded splits and persist the split manifest.
- Split at the strongest available grouping level (vehicle identity, sequence, source group, or image family) to avoid near-duplicate leakage. If vehicle/group identity is unavailable, deduplicate before splitting and document the limitation.
- Use stratification where feasible and report any class absent from a split.
- Keep the test set untouched until model/config selection is complete.
- Cross-dataset evaluation must be explicit: train VehiDE/test CarDD and the reverse where label mapping and annotation coverage permit.
- The source notes image data and OBD logs are not paired. Do not claim paired multimodal training; evaluate fusion using declared scenario-based or synthetically combined test cases unless a properly paired dataset is obtained.

### 9.4 Image EDA deliverables

Implement `ml/data/generate_eda.py` and produce chart files, metric tables, and an explanation of each result. Generate these source-required charts:

| ID | Chart | Required purpose |
|---|---|---|
| E1 | Class distribution | Reveal class imbalance; plan weighting/resampling if justified |
| E2 | Damage-type distribution per dataset | Compare taxonomies/domain shifts and need for harmonization |
| E3 | Image dimension scatter | Inform resize/padding policy |
| E4 | Aspect-ratio histogram | Detect varied capture styles and distortion risks |
| E5 | Bounding-box area histogram | Characterize object scale; many small boxes may favour high resolution/multiscale detection |
| E6 | Bounding-box width/height ratio | Characterize object shape and anchor/augmentation needs |
| E7 | Instances per image | Understand object density/crowding |
| E8 | Annotation-type availability | Count images with image-level labels, boxes and masks; expose missing supervision |
| E9 | Train/val/test split summary | Verify stratification and leakage checks |
| E10 | Missing/duplicate audit | Count corrupt files, duplicate files and empty annotations; remove leakage-causing duplicates |
| E11 | Damaged vs intact balance | Check Stage 1 suitability; document any negative-class shortage |
| E12 | Sample-image grid with overlays | Qualitatively inspect lighting, angles, annotation quality and label alignment |

Charts E5/E6/E7/E8 should display “not available” or be skipped with a clear explanation if the dataset has no corresponding annotations; do not fabricate empty-looking conclusions.

### 9.5 OBD/tabular EDA deliverables

Create charts/reports for:

| ID | Chart | Required purpose |
|---|---|---|
| T1 | Missing-value heatmap/table | Locate missing PID values and consider drop/imputation policy |
| T2 | PID feature distributions | Identify scale, skew and outliers |
| T3 | PID correlation heatmap | Understand redundancy/relationships and possible feature reduction |
| T4 | Time-series trace per PID | Inspect drift, spikes and candidate anomalies |
| T5 | DTC frequency plot/table | Check code frequencies and rare codes |
| T6 | Normal vs anomalous feature box plots | Check whether features may discriminate labelled conditions |
| T7 | Duplicate-record audit | Find and report duplicate rows |

If there are no labels for anomalies or normal/anomalous conditions, say so and do not produce a misleading supervised comparison. Document feature units where known and do not combine incompatible units without conversion.

### 9.6 Imbalance and data-quality strategy

The source suggests class-weighted loss, oversampling rare classes, image augmentation (flip/color jitter/scale), stratified splits, and tuning Isolation Forest's contamination parameter with precision-recall evaluation. Adopt these only when EDA supports them. Do not oversample before train/validation/test splitting; never synthesize validation/test examples by leakage-prone duplication.

### 9.7 Training and artifact requirements

For every trained candidate, store:

- Dataset manifest and split-manifest IDs/checksums.
- Label mapping version.
- Preprocessing/augmentation configuration.
- Model architecture and software version.
- Random seeds, optimizer/loss/training settings, epochs, checkpoint-selection criterion.
- Class weights/sampling rules where applicable.
- Evaluation outputs, confusion matrices/PR curves and latency hardware.
- Final artifact path and SHA/checksum.
- Known limitations and class-wise errors.

Provide command-line training/evaluation entry points. A README must say exactly how to run them; do not make training automatically download unknown data or silently change model definitions.

---

## 10. OBD-II / PID Analytics

### 10.1 Input scope

Input is an optional CSV time series, possibly containing a timestamp, PID columns (examples mentioned in the source: engine load, coolant temperature, RPM, speed, throttle, fuel trims), and an optional DTC field. These examples are not a guaranteed dataset schema. Inspect the real columns and create a configurable schema/mapping.

### 10.2 Processing stages

1. Parse and validate CSV.
2. Normalize column aliases into canonical feature IDs while retaining original column names.
3. Parse timestamps and sort by time when available.
4. Check units/ranges and flag impossible or suspicious values using documented rules; do not silently erase anomalies that may be the phenomenon being detected.
5. Handle duplicates and missingness with a documented policy. Fit all learned scalers/imputers on training data only.
6. Create windows/features for time-series records if needed; maintain traceability to input rows/time ranges.
7. Run anomaly scoring using Isolation Forest as a candidate unsupervised model.
8. If valid labelled fault classes exist, train/evaluate XGBoost as a supervised candidate. Do not train a supervised model without valid labels.
9. Extract DTC strings if present and map them using an approved source/reference dataset. Unknown codes must remain unknown rather than receive an invented explanation.
10. Return anomaly score/flags, flagged PID features, any active DTCs, data-quality warnings, model version, and interpretation limitations.

### 10.3 Required OBD result fields

- `status`: `not_provided`, `completed`, `invalid_input`, `failed`, or `model_unavailable`.
- `anomaly_detected`: nullable Boolean when analysis was not possible.
- `anomaly_score`: nullable numeric, with documented score direction/range.
- `flagged_pids`: list with name, value/window, expected range if a trusted range is known, reason, and confidence/status.
- `dtcs`: code, source-mapped description only if verified, severity/urgency only when supported by the mapping source, source citation.
- `data_quality`: missing-value counts, duplicate counts, column-mapping results, dropped/imputed records, warnings.
- `model_metadata`: model name/version and threshold/config.

Do not interpret absent telemetry or absent DTC columns as proof that no mechanical issue exists.

---

## 11. LangGraph Agentic Orchestration

### 11.1 Agents and responsibilities

| Agent | Input | Required output |
|---|---|---|
| Supervisor (LangGraph) | Inspection state, input availability, agent results | Routes, validates state, handles failures/conflicts and completes workflow |
| Vision Agent | One or more images | Damage flag, classes, boxes, masks, areas/severity, evidence and warnings |
| OBD Analytics Agent | PID CSV if supplied | Anomaly scores/flags, DTC list, data-quality summary |
| RAG Knowledge Agent | Damage classes, visual findings, DTCs, vehicle information, risk context | Retrieved repair/diagnostic passages with source metadata/citations |
| Risk Engine Agent | Vision + OBD findings + retrieved evidence | Safe/Caution/Unsafe, reasons, evidence references, warnings |

### 11.2 Workflow behavior

Recommended graph:

```text
START
  → Validate/normalize inspection state
  → Run Vision Agent (required images)
  → Run OBD Agent only if CSV exists (parallel with Vision where practical)
  → Build query from completed evidence + optional vehicle info
  → RAG Knowledge Agent retrieval
  → Risk Engine (rule/config based, evidence linked)
  → Validate completeness and unsupported-claim policy
  → Store structured report and render PDF
  → Mark job completed / completed_with_warnings
END
```

More efficient implementations may execute Vision and OBD concurrently. Still ensure the Risk Engine and final report wait for whichever agents were requested and for RAG results/failure state to be resolved.

### 11.3 Typed workflow state

Define a typed `InspectionGraphState` that includes:

- `inspection_id`, `job_id`, request/user ownership context (avoid propagating secrets).
- Secure storage references to image/CSV inputs, not raw file bytes in graph logs.
- Sanitized vehicle info.
- `vision_result` with status and per-image structured findings.
- `obd_result` with explicit `not_provided` state where no CSV exists.
- `retrieval_result` with query metadata, source IDs, chunks, scores and retrieval status.
- `risk_result` with risk enum, reason codes and evidence references.
- `warnings`, `errors`, `completed_stages`, schema/config versions, timestamps.
- `report_payload`.

Each agent must have a stable input/output schema. Catch known transient errors and retry selectively. Do not retry invalid inputs indefinitely. If one optional agent fails, create a partial report with explicit warnings if the risk/report policy allows; never silently omit the failure.

### 11.4 Agent versus deterministic code

Use LangGraph for routing and shared state. Use deterministic, separately testable Python code for calculations and risk-rule evaluation. Use a language model only where it adds clear value (e.g. query reformulation or grounded wording); it must not invent model detections, DTC explanations, citations, measurements, or risk evidence. Do not let generated prose override risk rules.

---

## 12. RAG Knowledge Base

### 12.1 Responsibilities

RAG retrieves approved vehicle manuals, service documents, repair guidance, and trusted DTC reference content relevant to the observed damage and telemetry. It should improve traceability, not be treated as a source of truth for visual measurements.

### 12.2 Required implementation

- Use PostgreSQL with pgvector and LlamaIndex, as named in the source report.
- Support a hybrid dense + sparse retrieval strategy. Document which sparse index/query implementation is used (for example, PostgreSQL full-text search) and how hybrid scores are combined.
- Build an explicit document ingestion flow with source registry, parsing, chunking, metadata extraction, embedding/version, and index refresh.
- Store at least: source ID, title, publisher/manufacturer, document name, source URL or local citation, revision/date where available, license/permission metadata, page/section, chunk ID/checksum, embedding model/version, ingestion timestamp.
- Apply source-access and licensing checks before ingestion or redistribution. Do not scrape or bundle protected manuals without permission.
- Use metadata filters for vehicle make/model/year and DTC where valid and available. If vehicle information is not supplied, do not pretend to know the exact vehicle configuration.
- Return top-k retrieved passages with relevance scores, source links/IDs, and exact page/section references when available.
- Use a retrieval precision@k evaluation plan and report faithfulness of generated guidance to retrieved sources.

### 12.3 Grounding requirements

- Every repair/diagnostic recommendation shown to the user must map to one or more retrieved source chunks or a clearly marked deterministic rule.
- If no suitable passages are retrieved, say “No verified repair guidance was found in the configured knowledge base.”
- Do not generate a fabricated OEM procedure, torque specification, part number, repair price, maintenance interval, or DTC meaning.
- Keep quotes short and within source rights; prefer concise paraphrases with citations.
- Preserve uncertainty and applicability conditions. Retrieval from a manual for a different model/year must not be presented as vehicle-specific advice.

---

## 13. Risk Engine and Safety Presentation

### 13.1 Risk labels

The source uses `Safe`, `Caution`, and `Unsafe`. These labels must be accompanied by a rationale and evidence references. They are app decision-support categories, not certified roadworthiness determinations.

### 13.2 Source-defined rule

The source document specifically says that the Risk Engine escalates risk when OBD anomalies are present, regardless of visual severity. Implement this as a configurable, auditable rule. Do not make an OBD anomaly lower risk. Exact escalation mapping is not defined by the document and requires domain calibration.

### 13.3 Suggested rule-engine output contract

- `risk_class`: `safe`, `caution`, `unsafe`, or `unavailable` if required evidence/rules are insufficient.
- `reason_codes`: stable machine-readable rule IDs.
- `summary`: concise user-facing rationale derived only from recorded evidence.
- `evidence_refs`: links to visual finding IDs, OBD finding IDs, and retrieved source IDs.
- `triggered_rules`: rule ID, version, input facts, output effect.
- `limitations`: such as no OBD data, incomplete segmentation, low image quality, unavailable model, unpaired datasets, or missing vehicle-specific manual.
- `review_required`: Boolean plus reason.

### 13.4 Implementation rules

- Put thresholds and mappings in `agents/rules.py` and versioned configuration (e.g. YAML); create unit tests for each rule and boundary condition.
- Make risk logic deterministic and auditable. Any LLM may explain a decision but must not choose the class independently of the configured rules.
- If an OBD anomaly is detected, escalate according to the configured policy even if the visual severity is low; record exactly which anomaly triggered it.
- Missing OBD must not be interpreted as no anomaly.
- Unavailable or low-confidence upstream outputs should result in a warning, review flag, or unavailable risk rather than an unsupported Safe result.
- The false-safe rate is a required evaluation metric; treat false-safe outcomes as a critical error category.
- Do not present “Safe” as “guaranteed safe to drive.” Recommended UI wording: “No high-risk signals were detected by the configured checks. This is not a guarantee of roadworthiness; seek qualified inspection if concerned.”

### 13.5 Human review and fallback

When image quality is low, Stage 1 confidence is near threshold, a class is out of vocabulary, masks fail, OBD parsing is incomplete, RAG returns no relevant evidence, or agents disagree, expose a review warning and explain which analysis is incomplete. Do not pretend the system resolved ambiguity that it could not resolve.

---

## 14. Report Format (JSON + PDF)

### 14.1 Report sections

A report must contain:

- Report/inspection ID and timestamps.
- Input summary: image count, image IDs/hashes, vehicle data fields present, OBD presence and validation status.
- Overall damage/no-damage outcome with confidence and model state.
- Per-image classes, confidences, detection boxes, masks, pixel areas and relative ratios where calculated.
- Severity score/level and calibration status.
- OBD anomaly scores, flagged PIDs, DTC codes/descriptions only where verified, and data-quality warnings.
- Risk class, explanation, reason codes, evidence references, and limitations.
- RAG retrieved context/source citations and applicability metadata.
- Model versions, config/threshold versions, preprocessing and report schema versions.
- Processing durations by stage and total duration when measured.
- Warnings/failed/skipped stages.
- Safety notice that output is AI decision support, not a definitive mechanical inspection.

### 14.2 Suggested report JSON schema shape

The schema lives in `reports/json_schema.json`; implement validation and version it. This example shows structure only; it contains no real predictions:

```json
{
  "schema_version": "1.0.0",
  "inspection_id": "<uuid>",
  "report_id": "<uuid>",
  "generated_at": "<ISO-8601 timestamp>",
  "overall": {
    "damage_detected": null,
    "status": "model_unavailable",
    "summary": "",
    "limitations": []
  },
  "vehicle": {
    "make": null,
    "model": null,
    "year": null,
    "mileage": null,
    "vin_redacted": true
  },
  "images": [],
  "severity": {
    "score": null,
    "level": "unavailable",
    "method": "mask_area_ratio_weighted_by_class",
    "calibrated": false
  },
  "obd": {
    "status": "not_provided",
    "anomaly_detected": null,
    "anomaly_score": null,
    "flagged_pids": [],
    "dtcs": [],
    "data_quality": {"warnings": []}
  },
  "risk": {
    "class": "unavailable",
    "summary": "",
    "reason_codes": [],
    "evidence_refs": [],
    "review_required": true
  },
  "knowledge": {
    "status": "no_sources_available",
    "citations": [],
    "passages": []
  },
  "model_metadata": {},
  "processing": {"stage_durations_ms": {}, "total_duration_ms": null},
  "warnings": [],
  "disclaimer": "AI-assisted decision support only; not a guarantee of vehicle safety or a substitute for a qualified inspection."
}
```

Use precise enum values; avoid mixing JSON `null` with strings such as `"N/A"` in machine fields. User-facing text may display “Not available.”

### 14.3 PDF report design

Create a readable, printable report with:

- Title, report ID, date/time, and app/model version.
- Executive summary and conspicuous risk label with text explanation.
- Annotated input images and a legend for boxes/masks.
- Findings table with damage type, confidence, area/ratio, and severity status.
- Separate optional OBD section with input quality, flagged PIDs and verified DTC references.
- Retrieved repair/diagnostic guidance with citations and source metadata.
- Limitations, missing-data/stage warnings, and decision-support disclaimer.
- Page numbers and generated-at timestamp.

Do not make a polished PDF imply greater certainty than the underlying analysis supports. If report generation fails, preserve JSON results and mark the job `completed_with_warnings` or an appropriate terminal state.

---

## 15. Docker, Local Development, and Deployment

### 15.1 Docker services

Provide a Docker Compose setup for local development with these services or clearly documented equivalents:

- `api`: FastAPI web server.
- `worker`: background job processor and LangGraph workflow.
- `postgres`: PostgreSQL configured with pgvector extension.
- `redis`: queue/cache service.
- `nginx`: reverse proxy and request limits.
- Optional one-shot `rag-ingest` profile for knowledge ingestion and optional `training` profile for ML experiments.

Do not place the Flutter iOS app inside Docker as if Docker can replace Xcode/iOS signing. The mobile app is built on the host using Flutter/Xcode. Docker is for backend and supporting services.

### 15.2 Compose requirements

- Use named volumes for PostgreSQL and local private file storage.
- Include a health check for API readiness, PostgreSQL, and Redis.
- Ensure API/worker wait for service health rather than mere container start.
- Apply database migrations as a documented one-shot step or controlled startup process. Avoid unsafe concurrent migrations from multiple replicas.
- Keep credentials in `.env` for local development and secret injection in deployed environments. `.env.example` contains placeholders only.
- Use separate dev/prod settings; disable reload and verbose SQL logging in production.
- Limit CPU/memory assumptions in docs and avoid requiring a GPU for basic API tests. Real model inference may need different hardware; document it.
- Ensure the API container can be started in `model_unavailable` mode if large model weights have not been installed, so health checks and mobile integration tests still work honestly.
- Provide reproducible volume reset instructions and warn before destructive commands.

### 15.3 Environment variables

Create and document variables similar to these (exact names may evolve, but keep consistent across services):

```dotenv
APP_ENV=development
API_BASE_PATH=/api/v1
JWT_SECRET_KEY=replace-me-locally
JWT_ACCESS_TOKEN_MINUTES=30
DATABASE_URL=postgresql+<driver>://<user>:<password>@postgres:5432/<database>
REDIS_URL=redis://redis:6379/0
FILE_STORAGE_BACKEND=local
FILE_STORAGE_ROOT=/app/private_uploads
DATASET_ROOT=/app/dataset
OBD_DATASET_DIR=/app/dataset/obdiidata
MODEL_REGISTRY_PATH=/app/ml/config/model_registry.yaml
FILTER_THRESHOLD=0.85
RAG_ENABLED=false
RAG_TOP_K=5
LOG_LEVEL=INFO
MAX_IMAGE_UPLOAD_MB=<configured-limit>
MAX_OBD_UPLOAD_MB=<configured-limit>
```

These are illustrative names and values. The JWT secret must be replaced with a random local secret and supplied via secret management in production. The 0.85 threshold is a source reference only; set `FILTER_THRESHOLD` to the calibrated value after validation and record the selected calibration version. Do not make `RAG_ENABLED=true` until source ingestion/retrieval is actually configured.

### 15.4 NGINX and network safety

- Proxy only required API routes.
- Configure maximum request body size consistent with API validation.
- Add coarse per-IP rate limits for authentication and upload/analysis endpoints where practical.
- Set proxy timeouts appropriate for uploads but keep analysis itself asynchronous.
- In deployment, use TLS and standard security headers; do not treat local HTTP as production configuration.
- Do not expose PostgreSQL or Redis publicly.
- Never expose private uploads through NGINX static directory configuration.

### 15.5 Operational scripts

Provide documented commands such as:

- `make setup` — install backend dependencies and project tooling.
- `make up` / `make down` — start/stop local Docker services.
- `make migrate` — apply schema migrations.
- `make test` — run backend/agent/ML unit tests that do not require large weights.
- `make lint` — lint/format/static checks.
- `make inspect-data` — inventory dataset directories.
- `make eda` — generate EDA artifacts where data supports it.
- `make smoke-test` — run health and API flow checks.
- Document equivalent Flutter commands: `flutter pub get`, `flutter analyze`, `flutter test`, and iOS simulator run/build commands.

Commands must be real and working; do not add Makefile targets that call nonexistent scripts.

---

## 16. Security, Privacy, and Reliability

### 16.1 Privacy

- Vehicle images, VIN, mileage, and OBD logs may be sensitive. Collect only needed fields.
- Mask VIN and private identifiers in normal logs. Prefer IDs and hashes for traceability.
- Never log raw image bytes, entire CSV contents, access tokens, password fields, JWT secrets, or unredacted VINs.
- Define retention defaults and deletion behavior in `docs/privacy-and-security.md`; do not promise deletion from backups unless implemented.
- Use TLS between the app and deployed API. Encrypt storage/volumes according to deployment requirements.
- Restrict report/file access by inspection owner, not possession of an ID alone.
- Avoid sending sensitive vehicle/user data to external model/embedding providers unless that provider is explicitly configured, disclosed, and approved for the deployment.

### 16.2 Reliability

- Validate all input both client-side and server-side.
- Add request IDs and structured logs across API → queue → worker → agents.
- Track every job attempt and stage status.
- Use retry/backoff only for transient infrastructure/model-serving errors.
- Make report persistence idempotent or versioned to prevent duplicate/contradictory reports.
- Set worker timeouts and resource caps so a malformed image/CSV cannot stall all jobs.
- Make long-running processing resilient to app closure and network interruption.
- Preserve partial findings when permitted but clearly mark report completeness and limitations.
- Use fallback states rather than fabricated results when models, RAG documents, or optional data are unavailable.

### 16.3 Monitoring

Record aggregate operational metrics without sensitive payloads:

- Request counts, error rates, upload failures, queue depth, job duration, per-stage duration, model unavailable count, report generation failures, and RAG retrieval empty-result rate.
- Track compute saved from filter gating only when measured against a valid no-gating baseline.
- Avoid collecting more personal information in telemetry than necessary.

---

## 17. Test Plan and Acceptance Criteria

### 17.1 Backend/API tests

- Health/live and health/ready behavior.
- JWT missing/expired/invalid behavior and user ownership checks.
- Valid/invalid image uploads, corrupt files, bad extensions, oversized files, duplicate hashes, and dimension handling.
- Valid/invalid CSV, missing columns, nonnumeric data, malformed timestamps, empty file, duplicate rows, and optional DTC handling.
- Inspection lifecycle transitions and queue retries.
- Job status endpoint returns persisted state across worker restarts.
- JSON report conforms to versioned schema; PDF generation failure produces a documented fallback.
- File access and deletion are scoped to owning users.

### 17.2 ML/data tests

- Dataset inventory matches sampled manual inspection.
- Label mapping handles known labels and errors on unapproved/unmapped labels according to config.
- No group/hash leakage across splits.
- Image preprocessing preserves known test geometry and maps boxes/masks back to original dimensions correctly.
- Stage 1 gate skips later stages for intact predictions and calls them for above-threshold inputs.
- Metrics functions are checked against small hand-calculated fixtures.
- Severity ratio guards division by zero/missing vehicle mask and handles overlapping masks according to policy.
- OBD normalization/scaling avoids fit leakage and preserves traceability to flagged records.
- Unknown DTC codes remain unknown.

### 17.3 Agent/RAG/risk tests

- Graph routes Vision and OBD correctly based on input availability.
- Optional OBD missing state is not converted into a normal result.
- Agent failure is visible in final warnings/status and does not become a false negative.
- Risk rules are tested at boundaries and for OBD-triggered escalation.
- RAG citations resolve to actual ingested sources/chunks.
- Empty retrieval returns no-source language, not fabricated guidance.
- Generated report text cannot introduce an unsupported fact absent from evidence/rules.

### 17.4 Flutter tests

- Image picker/camera selection, thumbnail preview, removal/reorder, and submission validation.
- Vehicle details are optional; VIN stays out of user-visible logs/debug telemetry.
- CSV upload and server validation errors are displayed accurately.
- Upload/progress/error/retry states are stable and do not duplicate jobs.
- Report view handles no OBD, OBD error, unavailable models, partial report and full report states.
- Bounding-box/mask overlays map correctly across aspect ratios, rotation and contain/cover display modes.
- JSON/PDF export uses iOS share functionality.
- History loads from backend and handles deleted/inaccessible report IDs.
- Accessibility labels and dynamic text sizes.

### 17.5 End-to-end smoke test

At minimum, automate or document a reproducible flow:

1. Start Docker services and migrate database.
2. Log in with a development test identity.
3. Create inspection.
4. Upload a small valid test image fixture.
5. Optionally upload a small synthetic/test CSV fixture clearly labelled as test data.
6. Submit analysis and wait for completion.
7. Retrieve the report JSON and verify required schema fields.
8. Retrieve the PDF if PDF generation is enabled.
9. Verify that model-unavailable/test mode is explicitly identified and does not claim real accuracy.

Do not use private or copyrighted sample data in tests unless the license permits it; small synthetic fixtures are acceptable for testing parsers and orchestration, but cannot be used to claim model performance.

### 17.6 Definition of done

The implementation is not done until:

- The iOS app builds for an iOS simulator with documented setup.
- The API, worker, database, Redis, and NGINX start using Docker Compose.
- Health checks pass and migrations apply cleanly from an empty local database.
- A new inspection with images can be created, uploaded, queued, processed, and reported through the API.
- OBD CSV is optional and its absence is represented honestly.
- Four agent roles exist and are connected by a LangGraph supervisor with typed state.
- Report JSON is schema-valid and PDF export works or an explicit documented blocker remains.
- Input validation, ownership checks, and core failure states are tested.
- Dataset inspection scripts work against the actual local folder layout.
- No fabricated model results are shown; if weights are unavailable, the app labels that state.
- README covers installation, configuration, running tests, app launch, data setup, training/evaluation, privacy, and known limitations.
- Open decisions and unexecuted tests are documented precisely.

---

## 18. Evaluation Metrics and Required Experiments

### 18.1 Metrics required by the source report

| Task | Metrics |
|---|---|
| Filter/classification | Accuracy, precision, recall, F1 (macro and per class), confusion matrix |
| Detection | mAP@0.5, mAP@0.5:0.95, per-class AP |
| Segmentation | Mean IoU, Dice, mask AP |
| Severity | Agreement with expert-labelled severity, e.g. weighted kappa; severity labels are required |
| OBD anomaly | Precision, recall, F1, PR-AUC, ROC-AUC where labels permit |
| Risk engine | Agreement with expert ratings, false-safe rate |
| RAG | Retrieval precision@k; report faithfulness to retrieved sources |
| Efficiency | Per-stage and end-to-end inference time; compute saved by gating |

Metric choice must match the actual labels available. Do not report ROC-AUC/precision/recall as if a labelled ground truth exists when the OBD data is unlabeled.

### 18.2 Required experiments

- **X1:** Compare Stage 1 filter backbones (EfficientNet-B4 vs ResNet50; source also refers to filter comparisons under B1).
- **X2:** Compare ConvNeXt vs ViT for damage classification.
- **X3:** Compare YOLOv8x vs RT-DETR detection.
- **X4:** Compare Mask R-CNN vs SAM 2 segmentation.
- **X5:** Ablation with vs without Stage 1 filter, measuring latency and recall loss.
- **X6:** Ablation of image-only risk vs image + OBD-II risk, using declared test scenarios because public datasets are not paired.
- **X7:** Cross-dataset testing: train on VehiDE/test on CarDD and reverse where annotations and label mappings permit.
- **X8:** End-to-end latency on stated hardware compared with the report's under-15-second reference target.

The source report states all these results are experiment-required. No target value should be claimed as achieved until it is measured. Keep data split IDs, hardware, model versions and repeated-run variance (where feasible) alongside the results.

### 18.3 Research charts in the source report

The document includes literature/public-benchmark CarDD charts (Figures 5A–5E, report pages 15–17). They are context only, not project results. They must be cited and labelled as published/publicly reported comparison values if included in project documentation. Do not copy them into the app or imply the proposed app attained them.

Project experiment charts to generate after evaluation include filter accuracy/damaged-class recall/F1, Stage 2 macro/per-class F1, inference latency on stated hardware, and Isolation Forest versus XGBoost metrics on the chosen OBD dataset.

---

## 19. Implementation Roadmap (12 Sprints / 24 Weeks)

The source report proposes 12 sprints (24 weeks), organized into four phases. Treat sprint length as a planning reference; adapt to team capacity, but preserve dependencies and acceptance checks.

### Phase 1 — Data and backend foundation (Sprints 1–3)

**Sprint 1: Repository and environment**
- Inspect the existing repository and dataset folders.
- Establish project structure, Git hygiene, env config, Docker Compose, API skeleton, Flutter skeleton, CI/test commands.
- Write `OPEN_DECISIONS.md` and dataset inventory tooling.

**Sprint 2: API, persistence, uploads**
- Implement JWT-based auth, database schema/migrations, inspection CRUD, private file storage, image/CSV validation.
- Implement API/worker boundary and Redis queue.
- Add API tests and OpenAPI contract.

**Sprint 3: iOS vertical slice**
- Build Home, new inspection, camera/photo selection, vehicle info, CSV picker, review/submit, progress, and basic report shell.
- Connect the iOS app to the real API.
- Complete an integration flow with a model-unavailable result state.

### Phase 2 — Model development (Sprints 4–6)

**Sprint 4: Data audit and Stage 1**
- Inventory dataset contents/licensing/annotations.
- Generate initial EDA and split manifests.
- Implement preprocessing, baseline filter training/inference interface and filter metrics.

**Sprint 5: Classifier and detector**
- Complete label harmonization and annotation validation.
- Train/evaluate candidate classifier and detector where labels allow.
- Implement inference adapters and geometry tests.

**Sprint 6: Segmentation, severity, OBD**
- Implement segmentation adapter, mask area calculations, provisional/calibrated severity states.
- Implement OBD CSV normalization, DTC extraction and Isolation Forest baseline; train XGBoost only if proper labels exist.
- Generate training/evaluation model cards with actual results.

### Phase 3 — Agentic integration (Sprints 7–9)

**Sprint 7: LangGraph orchestration**
- Define typed graph state, supervisor, Vision Agent and OBD Analytics Agent.
- Add asynchronous execution, progress tracking, retries and partial-result behavior.

**Sprint 8: RAG knowledge agent**
- Approve source corpus, implement ingestion/chunking/pgvector hybrid retrieval and source citations.
- Add retrieval quality and no-source tests.

**Sprint 9: Risk/report integration**
- Implement configurable risk engine, OBD-triggered escalation, JSON report schema, PDF generator, persisted history.
- Test false-safe-sensitive rule cases and incomplete-agent scenarios.

### Phase 4 — Mobile, quality and deployment (Sprints 10–12)

**Sprint 10: Complete iOS results UX**
- Report visual overlays, severity, optional OBD section, grounded guidance/citations, history, PDF/JSON share, error and privacy states.

**Sprint 11: Evaluation and security hardening**
- Run X1–X8 where data/resources permit, generate EDA/Tables/plots, leakage audit, model cards, API/mobile regression tests, privacy/security review.

**Sprint 12: Release packaging and documentation**
- Validate Docker production settings, deployment runbook, database backups/migrations, observability, iOS release build settings, complete smoke tests, known limitations and handoff docs.

At every sprint, keep the end-to-end flow runnable. Do not block all app/backend work on final model weights; use explicit unavailable adapters and replace them when trained artifacts are ready.

---

## 20. Documentation Antigravity Must Maintain

### `README.md`

Must include:

- Project purpose and capability boundaries.
- Architecture diagram.
- Prerequisites and pinned versions.
- `.env` creation and safe local secrets.
- Docker build/start/stop/migration commands.
- Flutter setup, iOS simulator/device configuration, base URL notes, and build/run commands.
- Dataset layout exactly as discovered, data inventory/EDA commands, dataset license caveats.
- Model training/evaluation commands and expected artifacts.
- How to run tests and smoke tests.
- API docs location.
- Privacy, file retention, and known limitations.
- Clear difference between real trained inference, model-unavailable state, and test-only mocks.

### `docs/model-card.md`

For each model: purpose, architecture, intended use, excluded use cases, training data/source and license, preprocessing, target classes, split IDs, metrics, calibration, known errors/biases, artifact checksum/version, inference hardware/latency and limitations.

### `docs/evaluation-plan.md`

Map each source requirement X1–X8 and E1–E12/T1–T7 to a script, input manifest, output artifact and completion status. Mark unavailable experiments with the concrete blocker rather than leaving ambiguous placeholders.

### `docs/privacy-and-security.md`

Document collected data, purpose, auth, file storage, access control, logs, retention/deletion, third-party providers, deployment TLS/secrets, backup behavior and incident response basics.

### `docs/runbook.md`

Document health checks, migrations, backup/restore, stuck jobs, Redis/worker health, disk storage monitoring, model updates, RAG reindexing, safe restart and troubleshooting.

---

## 21. Final Instructions for Antigravity

Work in small, verifiable steps. Before changing anything, inspect the current repository, read its existing README/configs, and inventory `dataset/damaged/`, `dataset/undamaged/`, and `dataset/obdiidata/`. Do not move or rename user files without a clear reason and explicit confirmation when destructive.

Prioritize the runnable vertical slice: **Flutter iOS → FastAPI → database/Redis queue → worker/LangGraph → structured report → iOS report screen**. Then integrate actual trained models, OBD analytics, RAG sources, calibrated severity and risk rules progressively. Keep model, data, label mapping and threshold versions attached to results.

When finished, report:

1. What was built.
2. Exact commands to run Docker/backend and the iOS app.
3. Test/build commands executed and their outcomes.
4. Which model stages use real trained weights, which are unavailable, and which mocks are test-only.
5. Dataset findings based on actual inventory, not assumptions.
6. Remaining open decisions, blocked experiments, and any manual Xcode/signing steps.

**Success means a documented, testable, iOS-first application and backend that honestly exposes completed and unavailable capabilities — not a demo that invents AI results.**

---

## 22. Source-Report Traceability and Research Context

This section preserves the research framing from the supplied 27-page report in addition to the implementation instructions above. The numbers and model comparisons below are reference content reported in that document; they are not results from this implementation.

### 22.1 Objectives O1–O7

- **O1:** Build a binary damaged/intact filter.
- **O2:** Classify damage into the defined damage classes (subject to confirmed class mapping).
- **O3:** Detect and localize damage instances with bounding boxes.
- **O4:** Segment damage at pixel level and compute area-based severity.
- **O5:** Detect OBD-II anomalies and map active DTCs.
- **O6:** Fuse visual and OBD-II evidence into a risk class and a RAG-grounded report.
- **O7:** Evaluate each stage and the full pipeline using standard metrics.

### 22.2 Research gaps described by the report

- **G1 — Isolated tasks:** Much prior work solves classification, detection, or segmentation independently rather than as one coordinated pipeline.
- **G2 — Area-to-severity gap:** Pixel-level output is rarely translated into a severity index.
- **G3 — Separate modalities:** Image models and OBD-II analytics are normally studied separately.
- **G4 — Weakly grounded guidance:** Repair/diagnostic report text is not always grounded in retrieved service knowledge.
- **G5 — Compute inefficiency:** Heavy detection/segmentation models are often run without an early lightweight filter.

The proposed contribution is the integration and evaluation of these components. Do not claim that each algorithm is new. The report itself notes novelty is confirmed only if experiments show benefit over image-only and single-model baselines.

### 22.3 Existing approach families and their trade-offs

| Approach/model family | Task | Strength in the source report | Limitation in the source report |
|---|---|---|---|
| Transfer-learning CNNs (e.g. ResNet, EfficientNet) | Damage classification/filter | Reuse pretrained representations; appropriate baseline family | Classification alone does not provide localization or affected area |
| YOLO-family detectors | Object detection | Speed and mature tooling; single-stage detection | Boxes alone provide coarse area estimation; small-object sensitivity can be a concern |
| Mask R-CNN | Instance segmentation | Established two-stage mask prediction; supervised masks | Heavier/slower; expensive to run on every image |
| SAM 2 | Promptable segmentation | Zero/few-shot masks from box prompts | Class-agnostic; boundary quality on thin scratches is unverified and must be tested |
| Isolation Forest | Unsupervised OBD anomaly detection | Does not require fault labels | Sensitive to contamination parameter and feature/data setup |
| XGBoost | Supervised tabular fault classification | Strong tabular candidate and feature importance | Requires valid labels for supervised training |

Candidate-by-candidate reasons to test:

- **EfficientNet-B4 vs ResNet50:** compare filter quality and efficiency; EfficientNet is the proposed lightweight gate candidate, while ResNet50 is a stable baseline.
- **ConvNeXt vs ViT-Base:** compare modern CNN feature learning with transformer global-context modeling; ViT can be more data-hungry.
- **YOLOv8x vs RT-DETR:** compare speed/mature tooling against end-to-end detection design; RT-DETR has different training/tooling trade-offs.
- **Mask R-CNN vs SAM 2:** compare supervised instance masks with box-prompted segmentation and measure thin-damage boundary quality.
- **Isolation Forest vs XGBoost:** compare unsupervised scoring where labels are unavailable against supervised fault classification where reliable labels exist.

The source report says the final model selection is decided by experiments, not by the candidate list alone.

### 22.4 Published/public CarDD benchmark values shown in the source report

The report includes the following figures as literature/public-benchmark context. Preserve the label “literature/public benchmark,” name the method/dataset/source with the original figure citation where these are reused, and never present them as results from the new application.

**Figure 5A — CarDD detection benchmark, ResNet-50, Box AP50 (percent):**

| Method | Box AP50 (%) |
|---|---:|
| Mask R-CNN | 66.3 |
| CM-R-CNN | 64.7 |
| GCNet | 66.4 |
| HTC | 68.1 |
| DCN | 70.9 |
| DCN+ | 77.4 |

**Figure 5B — CarDD segmentation benchmark, ResNet-50, Mask AP (percent):**

| Method | Mask AP (%) |
|---|---:|
| Mask R-CNN | 48.4 |
| CM-R-CNN | 48.6 |
| GCNet | 48.7 |
| HTC | 50.5 |
| DCN | 51.3 |
| DCN+ | 55.6 |

**Figure 5C — DCN+ ResNet-101 Box AP50 by damage class on CarDD (percent):**

| Damage class as presented in the chart | Box AP50 (%) |
|---|---:|
| Dent | 42.2 |
| Scratch | 42.3 |
| Crack | 29.6 |
| Glass shatter | 90.1 |
| Lamp broken | 69.5 |
| Tire flat | 90.2 |

**Figure 5D — Supplementary CarDD binary damage-filter benchmark (macro F1, percent):**

| Model | Macro F1 (%) |
|---|---:|
| ResNet-18 | 95.7 |
| ViT-B/16 | 93.5 |
| Custom CNN | 75.0 |

The source report explicitly describes this as a public implementation on a held-out 92-image test split and says it should be used only as supplementary evidence, not as a peer-reviewed benchmark. Preserve that caveat.

**Figure 5E — Extended CarDD detection comparison (Box mAP50, percent):**

| Method | Box mAP50 (%) |
|---|---:|
| YOLOv8s-seg v2.0 | 75.8 |
| DCN+ ResNet-50 | 77.4 |
| DCN+ ResNet-101 | 78.8 |

The source report notes that these results come from different implementations and must be used as literature/context rather than a controlled comparison.

The report attributes the main detection/segmentation literature figures to Wang, Li & Wu, “CarDD: A New Dataset for Vision-based Car Damage Detection,” *IEEE Transactions on Intelligent Transportation Systems* (2023), Tables IV–V, while noting that bibliographic details should be verified. The values above were transcribed from the report's figures and need primary-source verification before formal publication. Do not use these as a selection shortcut; run the project's own controlled experiments.

### 22.5 Compute-saving claim

The report mentions a reference claim of approximately 80% compute saving from the early filter, but marks it as an unverified reference. Do not repeat “80% saved” as a project result or promise. Measure compute/latency with and without Stage 1 using the same evaluation inputs and hardware, and report the measured result plus the accuracy/recall trade-off.

### 22.6 Proposed contribution summary

The planned contribution is the integration of:

1. A multi-stage computer-vision cascade with early filtering.
2. Exterior image analysis fused with OBD-II telemetry.
3. Bounding-box localization plus pixel-level segmentation.
4. Mask-derived area severity and drivability risk.
5. LangGraph agent orchestration.
6. RAG-grounded repair/diagnostic knowledge.

These are proposed project contributions, not guaranteed scientific novelty. Evaluate against image-only and single-model baselines before making claims.

### 22.7 Source document's scope and limitations

The report scopes the system to exterior damage from still images, offline OBD-II PID CSV logs, report generation, and mobile/API deployment design. It excludes video-based inspection, automated pricing guarantees, legal claim adjudication, and vehicle-make-specific calibration beyond data support.

It explicitly identifies these current limitations:

- Public exterior image datasets and OBD-II logs are not paired to the same vehicles.
- Dataset label taxonomies differ and require explicit mapping.
- Actual accuracy and latency of the proposed system are not yet measured in the source document.
- Severity calibration requires labelled repair/severity data or expert labels.
- Datasets' exact volume, links, license and annotation fields need re-verification.

Potential future work named by the report includes video-based inspection, calibrated cost estimation, vehicle-specific severity calibration, and on-device inference. Keep these outside the first release unless scope changes.

### 22.8 Reference list carried forward from the source report

The source report says these references need verification for complete bibliographic details, URLs, venue, pages and DOI before formal submission. Preserve that status rather than silently inventing missing details.

1. “AI Based Vehicle Damage Detection – Technical Architecture & System Blueprint” (project reference PDF cited by the source report; verify exact file/bibliographic details if it is to be referenced externally).
2. VehiDE dataset — named as Kaggle in the source report; exact dataset page and license to be confirmed.
3. CarDD dataset — named as Hugging Face in the source report; associated paper: X. Wang, W. Li, Z. Wu, “CarDD: A New Dataset for Vision-based Car Damage Detection,” *IEEE Transactions on Intelligent Transportation Systems*, 2023; verify complete citation details.
4. OBD-II telemetry dataset — named as Kaggle in the source report; exact page and license to be confirmed.
5. M. Tan, Q. Le, “EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks,” ICML, 2019.
6. K. He et al., “Deep Residual Learning for Image Recognition,” CVPR, 2016; K. He et al., “Mask R-CNN,” ICCV, 2017.
7. Z. Liu et al., “A ConvNet for the 2020s” (ConvNeXt), CVPR, 2022.
8. A. Dosovitskiy et al., “An Image is Worth 16x16 Words” (ViT), ICLR, 2021.
9. Ultralytics YOLOv8 documentation/repository — URL to be confirmed.
10. Y. Zhao et al., “DETRs Beat YOLOs on Real-time Object Detection” (RT-DETR), CVPR, 2024.
11. N. Ravi et al., “SAM 2: Segment Anything in Images and Videos,” 2024.
12. F. T. Liu, K. M. Ting, Z.-H. Zhou, “Isolation Forest,” ICDM, 2008.
13. T. Chen, T. Guestrin, “XGBoost: A Scalable Tree Boosting System,” KDD, 2016.

Before publication, verify every paper/dataset reference against the primary source and include exact DOI/URL/version/license data in the appropriate dataset/model documentation.
