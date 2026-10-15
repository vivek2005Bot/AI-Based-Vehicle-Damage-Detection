# AI-Based Vehicle Damage Detection

An intelligent, multi-stage vehicle damage assessment framework that integrates computer vision, deep learning, OBD-II telemetry analysis, Retrieval-Augmented Generation (RAG), and agentic AI orchestration to provide comprehensive vehicle damage and drivability risk assessments.

## 🚗 Project Overview

Traditional vehicle damage inspection relies heavily on manual assessment, which can be time-consuming and subjective. This project proposes an AI-based solution that analyzes vehicle images and optional OBD-II diagnostic data to identify exterior damage, estimate severity, detect potential mechanical anomalies, and generate structured diagnostic reports.

The system combines visual evidence with vehicle telemetry and retrieved repair knowledge to support more objective, explainable, and efficient vehicle assessments.

## ✨ Key Features

- **Damage Classification:** Classifies vehicle images as damaged or intact and identifies damage categories.
- **Object Detection:** Localizes damage using bounding boxes.
- **Instance Segmentation:** Identifies damaged regions at pixel level for affected-area estimation.
- **Severity Assessment:** Estimates damage severity using segmented area and damage-category weights.
- **OBD-II Anomaly Detection:** Analyzes vehicle telemetry from CSV files to identify unusual readings and diagnostic trouble codes (DTCs).
- **Agentic AI Orchestration:** Uses a LangGraph supervisor to coordinate specialized vision, OBD analytics, knowledge retrieval, and risk assessment agents.
- **RAG-Based Repair Guidance:** Retrieves relevant diagnostic and repair information from a knowledge base.
- **Drivability Risk Assessment:** Produces a proposed risk classification: Safe, Caution, or Unsafe.
- **Structured Reports:** Designed to generate diagnostic reports in JSON or PDF format.

## 🧠 Proposed Technology Stack

- **Computer Vision:** EfficientNet, ResNet, ConvNeXt, Vision Transformer (ViT), YOLOv8, RT-DETR, Mask R-CNN, and SAM 2 as candidate models.
- **Telemetry Analytics:** Isolation Forest and XGBoost.
- **AI Orchestration:** LangGraph.
- **Knowledge Retrieval:** LlamaIndex, PostgreSQL, and pgvector.
- **Backend API:** FastAPI and NGINX.
- **Background Processing:** Redis.
- **Mobile Client:** Flutter for iOS.
- **Deployment:** Docker.

## 📊 Datasets

The proposed framework uses three datasets:

- **VehiDE:** Vehicle images and annotations for damage detection and segmentation.
- **CarDD:** Vehicle damage images and defect annotations for damage classification, detection, and segmentation.
- **OBD-II PID Dataset:** Tabular CSV telemetry for anomaly detection and diagnostic analysis.

Dataset labels, availability, and licensing must be verified before use.

## ⚙️ System Workflow

1. Upload vehicle images and optionally provide OBD-II telemetry in CSV format.
2. Preprocess and validate the input data.
3. Filter damaged and intact vehicles.
4. Classify damage types.
5. Detect and segment damaged regions.
6. Estimate damage severity.
7. Analyze OBD-II telemetry and diagnostic trouble codes, when provided.
8. Retrieve relevant repair and diagnostic knowledge.
9. Fuse the available evidence to assess drivability risk.
10. Generate a structured diagnostic report.

## 🎯 Project Goals

- Automate key stages of vehicle damage assessment.
- Quantify damage location, affected area, and severity.
- Combine exterior visual inspection with internal vehicle health indicators.
- Reduce unnecessary computation through early damage filtering.
- Provide explainable risk assessments supported by retrieved knowledge.

## 🔬 Evaluation

The planned evaluation includes classification accuracy, precision, recall, F1-score, detection mAP, segmentation IoU and Dice scores, anomaly detection metrics, risk assessment agreement, and end-to-end inference latency.

**Project status:** Proposed framework and implementation blueprint. Model training, end-to-end integration, and quantitative evaluation remain to be completed and validated.

## ⚠️ Disclaimer

This project is intended for research and decision-support purposes. Its outputs should not replace professional vehicle inspection, validated mechanical diagnostics, or qualified safety assessments. Risk classifications and repair recommendations require appropriate validation before real-world use.
