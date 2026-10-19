# AI-Based Vehicle Damage Detection & Roadworthiness Assessment

[![Python Tests](https://img.shields.io/badge/Python%20Tests-116%20Passed-brightgreen)](tests/)
[![Flutter Analyzer](https://img.shields.io/badge/Flutter%20Analyzer-0%20Issues-brightgreen)](apps/ios/)
[![License](https://img.shields.io/badge/License-Non--Commercial%20Research-blue)](#legal-disclaimer)
[![YOLOv8 Segmentation](https://img.shields.io/badge/CarDD%20YOLOv8--Seg-mAP50%2070.6%25-orange)](checkpoints/)
[![Languages](https://img.shields.io/badge/Languages-English%20%2B%2022%20Indian%20Languages-blueviolet)](apps/ios/lib/l10n/)

An enterprise-grade, multi-modal automotive inspection platform combining **Deep Computer Vision (YOLOv8 Instance Segmentation & Classical Heuristics)**, **OBD-II Diagnostic Telemetry Analytics (SAE J2012 & Isolation Forest)**, **Deterministic Roadworthiness Safety Rules**, **Grounded Regulatory RAG**, and **Automotive Repair Cost Estimation**.

---

## 📖 Primary Project Documentation

> [!IMPORTANT]
> The authoritative, canonical technical documentation for this repository is located in:  
> **👉 [`PROJECT_MASTER_DOCUMENTATION.md`](PROJECT_MASTER_DOCUMENTATION.md)**  
> 
> This master document contains 24 in-depth sections covering the end-to-end system architecture, computer vision algorithms, telemetry parsing, deterministic safety rules, repair cost estimation, empirical training metrics, test results, and source material formatted for an **IEEE research paper**.

---

## 🚀 Key System Features

1. **Dual Computer Vision Engine:**
   - **Modern Deep Learning:** Native YOLOv8 instance segmentation (`checkpoints/cardd_yolov8_best.pt`) fine-tuned on the CarDD dataset across 25 epochs on Apple Silicon GPU (**Box $\text{mAP}_{50}: 70.6\%$**, **Mask $\text{mAP}_{50}: 69.1\%$**).
   - **Classical Heuristic Engine:** Zero-dependency OpenCV pipeline (`classical_cv_v1`) featuring vehicle-ROI background guards, directional top-hat scratch filters, shattered glass micro-fracture recognition, and specular reflection suppression.
2. **OBD-II Telemetry Diagnostics:**
   - Multi-dialect CSV parser normalizing German (Seat Leon) and English (UFPE) sensor headers.
   - Standardized SAE J2012 Diagnostic Trouble Code (DTC) extraction across Powertrain ($P$), Chassis ($C$), Body ($B$), and Network ($U$) families with plain-English functional explanations.
   - Unsupervised multivariate outlier detection using `IsolationForest` ($\nu = 0.05$).
3. **Deterministic Roadworthiness Governance:**
   - Strict non-probabilistic safety rules (`agents/rules.py`) prioritizing critical physical hazards (Airbag deployment DTCs, engine thermal overtemperature, structural bumper crush, windshield CVA cracks) over model confidence scores to assign `SAFE`, `CAUTION`, or `UNSAFE`.
4. **Itemized Repair Cost Estimation:**
   - Dual-scenario valuation evaluating **Scenario A (Component Repair)** versus **Scenario B (Component Replacement)**.
   - Grounded in genuine Indian replacement parts benchmarks (Maruti Suzuki, Hyundai, Tata, Mahindra, Honda), certified bodyshop labour rates, painting allowances, and statutory GST ($18\%$ labour, $28\%$ parts).
5. **Native 23-Language Multilingual Accessibility:**
   - Complete native localization across English and all 22 Eighth Schedule languages of India (Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia, Assamese, Urdu, Sanskrit, etc.), including Right-to-Left (RTL) support.
6. **Native Mobile App & Executive PDF Reporting:**
   - Native Flutter iOS mobile application featuring an interactive 2D `CustomPainter` overlay viewer for bounding boxes and sub-pixel polygon masks.
   - ReportLab Platypus executive PDF dossiers with TrueType Unicode font registration for non-Latin Indian scripts.

---

## ⚡ Quick Start

### 1. Prerequisites
- **macOS** (Apple Silicon M-series recommended) or **Linux (Ubuntu 22.04+)**
- **Python 3.11+** (Python 3.14 verified)
- **Flutter SDK 3.27+** with Xcode / iOS Simulator (for mobile app)

### 2. Backend API Setup
```bash
# 1. Clone and navigate to workspace
cd "/Users/vivekkumar/AI BASED VEHICLE DAMAGE DETECTION"

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Configure environment
cp .env.example .env

# 4. Start FastAPI server with live reloading
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger API Explorer: `http://127.0.0.1:8000/docs`
- API Health Status: `http://127.0.0.1:8000/health`

### 3. Native iOS Flutter Client Setup
```bash
# 1. Open iOS Simulator
open -a Simulator

# 2. Navigate to iOS client
cd apps/ios

# 3. Install dependencies & compile localization
/opt/homebrew/bin/flutter pub get
/opt/homebrew/bin/flutter gen-l10n

# 4. Launch app on iOS Simulator
/opt/homebrew/bin/flutter run
```

---

## 🧪 Testing and Verification

The repository maintains strict test baselines:

```bash
# Run complete Python Backend & ML test suite (117 tests)
pytest -v tests/

# Run Flutter mobile client static analysis
cd apps/ios && /opt/homebrew/bin/flutter analyze

# Run Flutter widget & unit test suite
cd apps/ios && /opt/homebrew/bin/flutter test
```

**Observed Verification Status:**
- `pytest`: **116 passed, 1 skipped** (opt-in smoke test) in 13.31s.
- `flutter analyze`: **0 errors, 0 warnings** (No issues found).
- `flutter test`: **100% tests passed**.

---

## 📂 Repository Layout

```
.
├── PROJECT_MASTER_DOCUMENTATION.md # Authoritative master technical specification
├── README.md                       # Repository entry point (this file)
├── .env.example                    # Sample configuration variables
├── agents/                         # Multi-agent supervisor, specialist agents, rules
├── apps/
│   └── ios/                        # Native Flutter iOS mobile application
├── backend/                        # FastAPI microservices, routers, ORM models
├── checkpoints/                    # Verified model weights (cardd_yolov8_best.pt)
├── configs/                        # Detection configs (configs/cardd/)
├── data/
│   ├── CarDD_COCO/                 # Official CarDD dataset (4,000 images, COCO format)
│   ├── CarDD_YOLO/                 # Converted CarDD dataset (YOLO-seg normalized polygons)
│   └── cache/                      # Online pricing disk cache
├── docs/                           # Focused technical guides & operational runbooks
│   ├── MARKDOWN_AUDIT_REPORT.md    # Documentation inventory, audit & cleanup log
│   ├── api-contract.md             # REST API endpoint contract
│   ├── runbook.md                  # Deployment & operations runbook
│   ├── privacy-and-security.md     # PII redaction & automotive compliance
│   └── yolo_cardd_training.md      # CarDD YOLOv8 training guide
├── ml/
│   ├── cost_estimation/            # Repair vs replacement economic engine
│   ├── obd/                        # Telemetry parser, DTC engine, Isolation Forest
│   ├── train/                      # Training scripts (train_cardd_yolo.py)
│   └── vision/                     # YOLOv8 adapter, classical engine, preprocessing
├── obdiidata/                      # 210 automotive telemetry CSV logs
├── reports/                        # ReportLab executive PDF dossier renderer
├── scripts/                        # Utility scripts (build_localization_resources.py)
└── tests/                          # 117 automated unit and integration tests
```

---

## ⚖️ Legal Disclaimer

Roadworthiness assessments (`SAFE`, `CAUTION`, `UNSAFE`) generated by this system are automated recommendations intended exclusively to support trained human examiners. This application does not issue a legally binding guarantee of structural integrity or roadworthiness. Critical vehicle safety systems (braking, airbag SRS, suspension geometry) must always be inspected physically by a certified mechanic.
