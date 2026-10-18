#!/bin/bash
# CarDD train/eval entrypoint (Linux/NVIDIA only). Usage: train | eval [CKPT]
set -euo pipefail

CONFIG="${CARDD_CONFIG:-configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py}"
WORK_DIR="${CARDD_WORK_DIR:-work_dirs/cardd_mask_rcnn_r50_fpn_2x}"
# COCO init weights (fine-tuning start, NOT a damage model).
LOAD_FROM="${CARDD_LOAD_FROM:-checkpoints/mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth}"

MODE="${1:-train}"
echo "== CarDD $MODE =="
echo "config:   $CONFIG"
echo "work-dir: $WORK_DIR"
nvidia-smi --query-gpu=name,driver_version --format=csv || true

if [ ! -f "$CONFIG" ]; then echo "ERROR: config $CONFIG not found."; exit 2; fi
if [ ! -f "data/CarDD_COCO/annotations/instances_train2017.json" ]; then
  echo "ERROR: data/CarDD_COCO not mounted or not in COCO layout."
  echo "Run ml/data/check_cardd_readiness.py first."
  exit 2
fi
if [ ! -f "$LOAD_FROM" ]; then
  echo "ERROR: COCO init checkpoint $LOAD_FROM not mounted."
  echo "Copy the repo-root mask_rcnn_r50_fpn_2x_coco_*.pth to checkpoints/ on the host."
  exit 2
fi

if [ "$MODE" = "train" ]; then
  echo "load_from (COCO init, NOT CarDD-trained): $LOAD_FROM"
  python tools/train.py "$CONFIG" --work-dir "$WORK_DIR"
  echo "--- work dir contents (record the ACTUAL checkpoint filename) ---"
  ls -lh "$WORK_DIR"
elif [ "$MODE" = "eval" ]; then
  CKPT="${2:-${CARDD_CHECKPOINT:-}}"
  if [ -z "$CKPT" ]; then
    echo "Usage: eval <work_dirs/.../epoch_N.pth>"
    echo "Available checkpoints:"; ls -lh "$WORK_DIR" 2>/dev/null || true
    exit 2
  fi
  python tools/test.py "$CONFIG" "$CKPT" --eval bbox segm
  echo "Save: bbox mAP, mask mAP, per-class AP/precision/recall."
  echo "Do NOT report COCO zoo AP (0.392/0.354) as CarDD performance."
else
  echo "Usage: train | eval <checkpoint>"; exit 2
fi
