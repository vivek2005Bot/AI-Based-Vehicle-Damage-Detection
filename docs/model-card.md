# Model Card — Multi-Stage Computer Vision & Telemetry Engine

## 1. Model Summary & Architectural Topology

| Sub-system | Model Base Architecture | Intended Task | Primary Inputs | Output Artifacts |
|---|---|---|---|---|
| **Stage 1: Filter** | ConvNeXt-V2 / EfficientNet-B4 | Binary classification (Damaged vs. Undamaged) | $1024 \times 1024 \times 3$ RGB | $P(\text{damaged}) \in [0, 1]$, binary decision gate ($T=0.85$) |
| **Stage 2: Classifier** | Vision Transformer / ConvNeXt | Multi-class damage taxonomy | $1024 \times 1024 \times 3$ RGB | Class distribution over 5 canonical classes |
| **Stage 3: Detector** | YOLOv8x / RT-DETR | Spatial localisation | $1024 \times 1024 \times 3$ RGB | Normalized $[x_1, y_1, x_2, y_2]$ bounding boxes |
| **Stage 4: Segmenter** | Mask R-CNN / SAM 2 | Pixel-level polygon segmentation | ROI Bounding Box Crops | Polygon coordinates, pixel area ratio $r_c = A_{\text{mask}} / A_{\text{veh}}$ |
| **OBD Anomaly Engine**| Isolation Forest ($n=100$) | Multivariate unsupervised anomaly detection | Core PIDs (RPM, Speed, Temp, Load) | Anomaly scores $\in [-1, 1]$, outlier flags |

---

## 2. Quantitative Ground Truth & Performance Transparency (Spec §0.3)

### Dataset Realities
- **Image Dataset:** 20,455 damaged vehicle JPEGs and 154 undamaged PNGs.
- **Annotation Truth:** The raw dataset provided does **not** contain native bounding-box or segmentation mask annotations.
- **Truthfulness Commitment:** In compliance with Project Spec Section 0.3, this project **does not fabricate** artificial mAP, F1, or IoU scores.
- **Capability Adapters:** When pre-trained model checkpoint weights are unmounted or undergoing active training, the system uses transparent capability adapters that flag model availability in metadata and provide deterministic heuristic overlays to facilitate testing and validation.

---

## 3. Physical Area Conversion Boundary

- **Pixel Ratios Only:** The segmentation engine strictly reports the non-dimensional damage ratio $r = A_{\text{mask}} / A_{\text{vehicle}}$.
- **No Direct $cm^2$ or $in^2$ Conversion:** Without a known physical calibration fiducial (e.g., standard license plate dimensions or ArUco reference markers in the camera frame), converting pixel areas to physical metric units ($cm^2$) introduces unquantified perspective distortion errors and is prohibited.

---

## 4. Telemetry Anomaly Boundaries

- **Normal Operating Bands:**
  - Coolant Temperature: $75^\circ\text{C} - 105^\circ\text{C}$ (Caution $\ge 108^\circ\text{C}$, Critical $\ge 118^\circ\text{C}$)
  - Engine RPM: $600 - 6,500$ RPM
  - Vehicle Speed: $0 - 200$ km/h
  - Throttle Position: $0\% - 100\%$
- **Unsupervised Contamination:** Isolation Forest contamination factor is bounded at $\nu = 0.05$ to suppress false positives caused by transient sensor spikes or gear shifts.

---

## 5. Known Limitations & Failure Modes

1. **Severe Occlusion & Extreme Night Shots:** Images taken with low lux ($< 15$ mean luminance) or extreme glare can cause false negatives in Stage 1 gating.
2. **Surface Dirt vs. Scratches:** Dried mud or dirt spatter may trigger high false-positive scratch classifications without physical tactile verification.
3. **Unpaired Telemetry:** Visual images and OBD logs are unpaired in current dataset versions; telemetry anomaly signals reinforce roadworthiness classification but are evaluated concurrently via multi-agent state.
