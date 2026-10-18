# CarDD Mask R-CNN training & inference (isolated MMDetection 2.x env)
#
# The main repo venv is Python 3.14 with NO torch/mmdet/mmcv. The official
# CarDD code is the MMDetection 2.x / MMCV 1.x generation (Python 3.8,
# PyTorch 1.7.0, CUDA 11.0 era) and its inference script hardcodes cuda:0/1.
# DO NOT pip-install that legacy stack into the main venv. Use ONE of:
#
#  Option 1 — isolated conda env on a Linux/NVIDIA machine (recommended):
#    conda create -n cardd-mmdet2 python=3.8 -y
#    conda activate cardd-mmdet2
#    pip install torch==1.7.0+cu110 torchvision==0.8.1+cu110 -f https://download.pytorch.org/whl/torch_stable.html
#    pip install mmcv-full==1.7.2 -f https://download.openmmlab.com/mmcv/dist/cu110/torch1.7/index.html
#    git clone https://github.com/open-mmlab/mmdetection.git && cd mmdetection && git checkout v2.28.2
#    pip install -r requirements/build.txt && pip install -v -e .
#    # overlay official CarDD_detection code + this portable config:
#    #   configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py  (repo file)
#
#  Option 2 — Docker training service (same stack, one command on GPU host):
#    docker build -f infra/cardd/Dockerfile.cardd -t cardd-train .
#    docker run --gpus all -v $PWD/data/CarDD_COCO:/mmdetection/data/CarDD_COCO:ro \
#      -v $PWD/work_dirs:/mmdetection/work_dirs cardd-train train
#    # then: ... cardd-train eval work_dirs/cardd_mask_rcnn_r50_fpn_2x/<actual>.pth
#    # Preflight (runs on THIS Mac, stdlib only): ml/data/prepare_cardd_host.py
#    # The built image can also serve Route C (small HTTP API) later.
#
#  Option 3 — MacBook dev (this machine): implement + test the adapter with
#  mocks (done in tests/test_cardd_detector.py). Live inference stays BLOCKED
#  until Option 1/2 produces a fine-tuned checkpoint.

# --- 0. Dataset license (read before downloading anything) -----------------
# CarDD is non-commercial research/educational use (underlying Flickr /
# Shutterstock image licenses apply). Source: https://cardd-ustc.github.io/
# Do NOT package the dataset into app assets or Docker images. Keep
# CarDD_COCO/ and *.pth out of git (see .gitignore). Verify the current
# terms before any commercial deployment.


# --- 1. Prepare data (inside the isolated env) -----------------------------
# Official config expects COCO instance-seg layout (bboxes + masks):
#   data/CarDD_COCO/{train2017,val2017,test2017,annotations/instances_*.json}
# The repo's dataset/ folder is binary damaged/undamaged ONLY (no COCO JSON,
# no masks) -> NOT trainable as-is. Download/convert CarDD_COCO first and
# verify what the guide calls "dataset readiness" before training.
#   ls data/CarDD_COCO/train2017 | head
#   python -c "import json; d=json.load(open('data/CarDD_COCO/annotations/instances_train2017.json')); print(d.keys()); print(len(d['images']), len(d['annotations']))"
#
# Mac shortcut (runs on THIS MacBook, stdlib only, no GPU/torch needed):
#   ./.venv/bin/python ml/data/check_cardd_readiness.py [--root data/CarDD_COCO]
# Expected right now: exit 2 / NOT READY (no CarDD_COCO folder exists).

# --- 2. Stage the COCO init checkpoint (init weights, NOT a damage model) --
#   mkdir -p checkpoints
#   cp /path/to/mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth \
#      checkpoints/
# `load_from` in configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py already points
# there. Keep *.pth OUT of git (see .gitignore).

# --- 3. Fine-tune (from the MMDetection root in the isolated env) ----------
#   python tools/train.py configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py \
#     --work-dir work_dirs/cardd_mask_rcnn_r50_fpn_2x
# Expect ~24 epochs. Record the actual best/last checkpoint filename from the
# work dir listing — do NOT assume epoch_24.pth without checking.

# --- 4. Evaluate on the HELD-OUT test split --------------------------------
#   python tools/test.py configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py \
#     work_dirs/cardd_mask_rcnn_r50_fpn_2x/<actual-checkpoint>.pth \
#     --eval bbox segm
# Save bbox mAP, mask mAP, per-class AP/precision/recall. Never report COCO
# zoo AP (0.392/0.354) as CarDD performance. Tune the score threshold on VAL,
# never on test.

# --- 5. Enable the adapter (main app env, after a verified checkpoint) -----
#   export CARDD_MODEL_ENABLED=true
#   export CARDD_MODEL_CONFIG=./configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py
#   export CARDD_MODEL_CHECKPOINT=/abs/path/to/work_dirs/cardd_mask_rcnn_r50_fpn_2x/<actual>.pth
#   export CARDD_MODEL_DEVICE=cpu   # or cuda:0 inside the isolated service
#   export CARDD_MODEL_SCORE_THRESHOLD=0.50  # validated value from step 4
# Current state: only COCO init weights exist -> adapter stays
# disabled/unavailable by design; classical engine remains active.
