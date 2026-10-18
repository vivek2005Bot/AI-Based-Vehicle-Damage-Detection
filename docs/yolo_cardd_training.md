# CarDD YOLOv8 / YOLOv11 Instance Segmentation Training & Inference Guide

This guide details how to train and deploy modern YOLOv8/YOLOv11 instance segmentation on the CarDD dataset.

---

## Why YOLOv8/v11 Segmentation over Legacy Mask R-CNN?

| Metric / Feature | Legacy Mask R-CNN (MMDetection 2.x) | Modern YOLOv8/v11-Seg (Ultralytics) |
|---|---|---|
| **macOS Native Support** | ❌ Broken (`mmcv-full` C++ CUDA ops fail to compile) | ✅ Native Apple Silicon Metal GPU (`device='mps'`) |
| **Python Version** | ❌ Locked to Python 3.8 (deprecated) | ✅ Fully supported on Python 3.10 - 3.14 |
| **Inference Latency** | ~280ms - 450ms | **~15ms - 35ms** |
| **Polygon Masks** | RLE / Binary Masks | **Sub-pixel Smooth Polygon Contours** |
| **Training Ease** | Multi-file config hierarchies | **One CLI command** |

---

## 1. Dataset Status

The CarDD dataset (4,000 images, 8,740 segmentation masks) has been converted to normalized YOLO segmentation format in `data/CarDD_YOLO/`:

```
data/CarDD_YOLO/
├── cardd_yolo.yaml
├── images/
│   ├── train/  (2,816 images)
│   ├── val/    (810 images)
│   └── test/   (374 images)
└── labels/
    ├── train/  (2,816 polygon text files, 6,211 instances)
    ├── val/    (810 polygon text files, 1,744 instances)
    └── test/   (374 polygon text files, 785 instances)
```

Target classes:
- `0: dent`
- `1: scratch`
- `2: crack`
- `3: glass shatter` (maps to canonical `glass_shatter`)
- `4: lamp broken` (maps to canonical `broken_light`)
- `5: tire flat` (maps to canonical `flat_tire`)

---

## 2. Option A: Train Locally on Mac (Apple Silicon GPU)

The training script automatically utilizes your Mac's Metal Performance Shaders (MPS):

```bash
# Run training with base pretrained weights (yolov8n-seg.pt)
./.venv/bin/python ml/train/train_cardd_yolo.py \
  --model yolov8n-seg.pt \
  --epochs 25 \
  --batch 8 \
  --device mps \
  --name cardd_seg_v1
```

- **Output Directory**: `work_dirs/cardd_yolo/cardd_seg_v1/`
- **Best Weights Checkpoint**: `work_dirs/cardd_yolo/cardd_seg_v1/weights/best.pt`

---

## 3. Option B: Train on Free Google Colab GPU (Fastest: ~12-15 Mins)

If you prefer cloud training with an NVIDIA T4 GPU:

1. Open [Google Colab](https://colab.research.google.com/) and select **Runtime > Change runtime type > T4 GPU**.
2. Run the following cells:

```python
# Cell 1: Install Ultralytics
!pip install -q ultralytics

# Cell 2: Download or upload data/CarDD_YOLO and train
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8n-seg.pt')

# Train on CarDD
results = model.train(
    data='cardd_yolo.yaml',
    epochs=30,
    imgsz=640,
    batch=16,
    device=0, # GPU
    name='cardd_seg_colab'
)

# Download best.pt
from google.colab import files
files.download('runs/segment/cardd_seg_colab/weights/best.pt')
```

---

## 4. Enabling the Model in the Application

Once `best.pt` is generated, place it in `checkpoints/cardd_yolov8_best.pt` or leave it in `work_dirs/cardd_yolo/cardd_seg_v1/weights/best.pt`.

Edit `.env`:

```ini
CARDD_MODEL_BACKEND=yolo
CARDD_YOLO_ENABLED=true
CARDD_YOLO_MODEL_PATH=work_dirs/cardd_yolo/cardd_seg_v1/weights/best.pt
CARDD_YOLO_DEVICE=mps
CARDD_YOLO_SCORE_THRESHOLD=0.35
```

Restart the FastAPI backend:
```bash
./.venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 5. Verification & Testing

Verify that the backend recognizes the YOLO detector:
```bash
curl -s http://localhost:8000/api/v1/meta | jq .models.cardd_detector
```

Run test suite:
```bash
./.venv/bin/pytest tests/test_yolo_detector.py
```
