# Portable CarDD Mask R-CNN config (project-specific, MMDetection 2.x generation).
#
# Starting point: official CarDD `mask_rcnn_cfg.py`
# (https://github.com/CarDD-USTC/CarDD-USTC.github.io/blob/main/code/CarDD_detection/configs/car_damage/mask_rcnn_cfg.py)
# which inherits `mask_rcnn_r50_fpn_2x_coco.py` and fine-tunes 6 CarDD classes.
#
# This file is PORTABLE: no `/root/autodl-*` absolute paths remain. All
# machine-specific paths are placeholders overridden via env vars or CLI when
# training inside a compatible Linux/NVIDIA MMDetection 2.x environment.
# See docs/cardd_training.md for the exact train/test commands.
#
# IMPORTANT: the local `.pth` in the repo root
# (`mask_rcnn_r50_fpn_2x_coco_... .pth`) is a COCO-pretrained initialization
# checkpoint, NOT a CarDD-fine-tuned damage model. `load_from` below points at
# it only as fine-tuning initialization. Do not use it for production
# predictions until a `work_dirs/.../epoch_*.pth` fine-tuned checkpoint exists.

_base_ = '../mask_rcnn/mask_rcnn_r50_fpn_2x_coco.py'

# CarDD classes — ORDER MATTERS (must match annotations + category-ID mapping).
classes = ('dent', 'scratch', 'crack', 'glass shatter', 'lamp broken', 'tire flat')

model = dict(
    roi_head=dict(
        bbox_head=dict(num_classes=6),
        mask_head=dict(num_classes=6),
    )
)

# ---------------------------------------------------------------------------
# Paths: override these for your machine / container. Relative defaults assume
# training runs from a cloned MMDetection 2.x + CarDD_detection checkout with:
#   data/CarDD_COCO/{train2017,val2017,test2017,annotations/*.json}
# ---------------------------------------------------------------------------
dataset_type = 'COCODataset'
data = dict(
    samples_per_gpu=8,
    workers_per_gpu=2,
    train=dict(
        img_prefix='data/CarDD_COCO/train2017/',
        classes=classes,
        ann_file='data/CarDD_COCO/annotations/instances_train2017.json',
    ),
    val=dict(
        img_prefix='data/CarDD_COCO/val2017/',
        classes=classes,
        ann_file='data/CarDD_COCO/annotations/instances_val2017.json',
    ),
    test=dict(
        img_prefix='data/CarDD_COCO/test2017/',
        classes=classes,
        ann_file='data/CarDD_COCO/annotations/instances_test2017.json',
    ),
)

optimizer = dict(lr=0.01)
lr_config = dict(step=[16, 22])
runner = dict(type='EpochBasedRunner', max_epochs=24)
checkpoint_config = dict(create_symlink=False)
evaluation = dict(metric=['bbox', 'segm'], interval=4)

# COCO initialization checkpoint (fine-tuning start point — NOT CarDD-trained).
# Point at your actual local file, e.g. checkpoints/mask_rcnn_r50_fpn_2x_coco_*.pth
load_from = 'checkpoints/mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth'

work_dir = 'work_dirs/cardd_mask_rcnn_r50_fpn_2x'
