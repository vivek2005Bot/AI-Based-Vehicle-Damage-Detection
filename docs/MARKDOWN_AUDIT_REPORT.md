# Markdown Documentation Audit & Consolidation Report

**Date of Audit:** October 19, 2026  
**Auditor:** Antigravity AI Engineering Assistant  
**Project:** AI-Based Vehicle Damage Detection & Roadworthiness Assessment  
**Canonical Master Reference:** [`PROJECT_MASTER_DOCUMENTATION.md`](../PROJECT_MASTER_DOCUMENTATION.md)

---

## 1. Executive Summary

An audit of all project-owned `.md` files was performed across the repository. Previously, documentation was fragmented across redundant root-level task specifications, outdated status files, legacy integration notes, and decentralized `docs/` guides. 

All unique technical details, optical algorithms, empirical training metrics, telemetry definitions, deterministic safety rules, economic formulas, and IEEE research citations have been synthesized into **`PROJECT_MASTER_DOCUMENTATION.md`**.

Obsolete root duplicate files have been safely removed. Retained documents in `docs/` have been audited to ensure no broken references exist across the codebase.

---

## 2. Documentation Classification & Action Matrix

| File Path | Initial Category | Final Status | Justification & Verification Notes |
| :--- | :--- | :---: | :--- |
| **`PROJECT_MASTER_DOCUMENTATION.md`** | Canonical Master Document | **Created (Active Canonical)** | Authoritative master technical specification containing all 24 verified sections. |
| **`README.md`** (root) | Essential Project Overview | **Created / Updated** | High-level repository entry point directing developers and researchers to the master document. |
| **`ANTIGRAVITY_PROJECT_SPEC.md`** | Historical Project Specification | **Retained** | Contains the original 1,669-line project brief. Retained because 30+ Python docstrings in `agents/`, `backend/`, `ml/`, and `reports/` explicitly cite its section numbers. |
| **`PROJECT_DOCUMENTATION.md`** | Redundant Architecture Doc | **Merged & Safely Removed** | Subsumed 100% by `PROJECT_MASTER_DOCUMENTATION.md`. Zero code or test dependencies. |
| **`IMPLEMENTATION_STATUS.md`** | Outdated Status Checklist | **Merged & Safely Removed** | Stale status from Oct 14 (referenced only 12 tests). Subsumed into Master Doc Sections 20 & 21 (now 117 tests). |
| **`OPEN_DECISIONS.md`** | Outdated Technical Decision Log | **Merged & Safely Removed** | Outdated decisions log from Oct 14. All decisions and unresolved questions synthesized into Master Doc Sections 4, 8, 20, and 22. |
| **`CarDD_Mask_RCNN_Integration_Guide.md`**| Legacy Agent Task Guide | **Merged & Safely Removed** | Temporary guide for legacy MMDetection 2.x Mask R-CNN. Completely subsumed into Master Doc Sections 6, 17, 18, and `docs/yolo_cardd_training.md`. |
| **`docs/yolo_cardd_training.md`** | Operational Training Runbook | **Retained** | Practical, command-level guide for training YOLOv8 on Apple Silicon MPS and Colab GPU. |
| **`docs/api-contract.md`** | Operational API Contract | **Retained** | Discrete REST API specification detailing request and response JSON payloads for frontend integration. |
| **`docs/runbook.md`** | Operational Deployment Guide | **Retained** | Focused operations and Docker runbook for DevOps and deployment engineers. |
| **`docs/privacy-and-security.md`** | Compliance & Security Policy | **Retained** | Standalone privacy policy detailing PII redaction (license plates, faces, VINs) for legal audits. |
| **`docs/model-limitations-and-retraining.md`** | Limitations & Collision Fix | **Retained** | Explicitly referenced by `ml/vision/prioritization.py:21`. Retained to maintain docstring integrity. |
| **`docs/cardd_training.md`** | Legacy Conda/Docker Guide | **Retained** | Explicitly referenced by `ml/vision/cardd_detector.py:233`. Retained to maintain docstring integrity. |
| **`docs/architecture.md`** | Modular Architecture Overview | **Retained** | Concise 100-line modular architecture reference in `docs/`. |
| **`docs/dataset-summary.md`** | Raw Dataset Summary | **Retained** | Measured inventory of initial raw unannotated `dataset/` directory. |
| **`docs/evaluation-plan.md`** | Evaluation Protocol | **Retained** | Concise 50-line evaluation protocol in `docs/`. |
| **`docs/model-card.md`** | Model Card | **Retained** | Concise model summary in `docs/`. |
| **`data/manifests/DATASET_INSPECTION_REPORT.md`**| Dataset Audit Artifact | **Retained** | Machine-generated inventory of raw data files inside `data/manifests/`. |
| **`apps/ios/README.md`** | Mobile Client Readme | **Updated** | Replaced default Flutter boilerplate with an actual guide for running and configuring the iOS client. |
| **`apps/ios/.../LaunchImage.imageset/README.md`**| Xcode Framework Asset | **Retained** | Framework-owned asset guideline for Xcode asset catalog. |

---

## 3. Preservation of Unique Technical Information

During consolidation, all unique technical information was verified against the codebase and preserved in `PROJECT_MASTER_DOCUMENTATION.md`:
1. **Physical Optical Heuristics:** Preserved exact mathematical and optical thresholds for `estimate_vehicle_roi()`, directional top-hat scratch filters, Difference-of-Gaussians, compact fracture recognition for glass, and specular reflection suppression ([Section 6.3](../PROJECT_MASTER_DOCUMENTATION.md#63-classical-vision-engine-physical-optical-methods)).
2. **Defect Prioritization & Area Formulas:** Preserved the priority scoring formula and Gauss's Shoelace formula for polygon area calculation ([Section 6.6 & 6.7](../PROJECT_MASTER_DOCUMENTATION.md#66-component-identification-and-spatial-prioritization)).
3. **Empirical Training Data:** Preserved exact per-epoch loss, precision, recall, and mAP metrics from `work_dirs/cardd_yolo/cardd_seg_v1/results.csv` ([Section 19.1](../PROJECT_MASTER_DOCUMENTATION.md#191-measured-empirical-training-results-yolov8n-seg-on-cardd)).
4. **Deterministic Safety Rules:** Preserved exact precedence logic and rule IDs (V0–V3, O1–O3) from `agents/rules.py` ([Section 8.2 & 8.3](../PROJECT_MASTER_DOCUMENTATION.md#82-safety-rule-hierarchy-and-escalation-precedence)).
5. **Economic Estimation Taxonomy:** Preserved Indian automotive pricing benchmarks, OEM part numbers, bodyshop labour schedules, and GST taxation rates ([Section 10](../PROJECT_MASTER_DOCUMENTATION.md#10-automotive-repair-cost-estimation-engine)).
6. **Statutory Standards & Citations:** Preserved citations for NHTSA FMVSS 214, AGRSS/ANSI 002-2014, USTMA, and SAE J2012 ([Section 24](../PROJECT_MASTER_DOCUMENTATION.md#24-references--source-traceability)).

---

## 4. Unresolved Discrepancies & Research Caveats

1. **Unpaired Datasets in Automotive Literature:** Visual crash images (`CarDD_COCO`, `dataset/damaged`) and electronic OBD-II sensor logs (`obdiidata/`) represent independent vehicles. Causal diagnosis linking a specific dent to a specific engine sensor spike is a multi-modal heuristic inference, not a physical causal certainty.
2. **Physical Area Scaling:** True physical area ($cm^2$) cannot be measured accurately without a camera-calibrated fiducial marker (e.g., standard license plate dimensions). The system strictly reports non-dimensional relative area ratios ($r = A_{\text{mask}} / A_{\text{vehicle}}$).
3. **Legacy Mask R-CNN Incompatibility:** The official CarDD MMDetection 2.x codebase is tied to Python 3.8 and legacy CUDA ops, making it incompatible with modern Python 3.11–3.14 on macOS Apple Silicon. This is solved by the active YOLOv8 instance segmentation adapter.
