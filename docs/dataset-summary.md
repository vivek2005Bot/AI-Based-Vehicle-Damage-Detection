# Dataset Summary (measured, 2026-10-15)

Source of truth: `dataset/` on disk. Validated with PIL + sha256 (`ml/data/inspect_dataset.py`
pattern; sample commands in §5).

## Layout

| Path | Files | Content |
|---|---|---|
| `dataset/damaged/` | **20,455** × `.jpg`, RGB, 0 corrupt in 1,500-sample | Vehicle-damage photos, mixed resolutions (dominant: 1280×1280, 1000×667, 1000×750; portrait variants exist) |
| `dataset/undamaged/bmw/` | UI **screenshots** (`.png`, e.g. `Screenshot 2023-09-14 …`) of car-listing pages | NOT usable as photographic negatives |

## Annotation status: NONE

- **No bounding boxes** (no YOLO/COCO/VOC/any annotation files anywhere under `dataset/`).
- **No segmentation masks or polygons.**
- **No per-image damage-class labels** — only the folder name (`damaged`).
- The 15 hand-annotated boxes in `ml/data/validation/annotations.json` are
  **class-agnostic** evaluation boxes, not training labels.

Consequence: only **image-level** damaged-vs-undamaged supervision exists in
principle — and even that is polluted because `undamaged/` holds screenshots,
so a classifier would learn *screenshot-vs-photo*, not *intact-vs-damaged*.

## Integrity findings

- 0 corrupt / 1,500 sampled (PIL `verify()` + decode).
- **2,816 exact-byte duplicates (13.8%)** → 17,639 unique files.
- Filenames carry shoot-date prefixes (`06012020…` ×1,027, `31012020…` ×820,
  …): bursts from the same shoots are near-certain, so random splits would
  leak near-identical images across train/val. **Any future training split
  MUST group by filename date/source prefix** (`ml/data/build_splits.py`
  pattern with prefix grouping).
- Mixed resolutions/aspect ratios require letterbox preprocessing (already the
  pipeline default).

## What this supports / blocks

- Supports: image-level EDA, honest negatives only after replacing
  `undamaged/` with real intact-car photos, annotation sampling frames.
- Blocks: **all localization training** (detector/segmenter) and per-class
  training until boxes/masks are human-annotated. Minimum viable labeling:
  ~1,500–2,000 images with YOLO/COCO boxes across the 7-class taxonomy
  (§6 of the project brief), sampled across date prefixes, double-reviewed.
  See `ml/train_detector.py` (refuses to run until labels exist) and
  `ml/data/annotation_workflow.py` (manifest + label validator).

## 5. Reproduce

```bash
.venv/bin/python - <<'EOF'
from PIL import Image
import os, hashlib, random
d = 'dataset/damaged'; files = sorted(os.listdir(d))
print(len(files), 'files')
random.seed(7)
bad = 0
for f in random.sample(files, 1500):
    try:
        with Image.open(os.path.join(d, f)) as im: im.verify()
    except Exception: bad += 1
print('corrupt in sample:', bad)
EOF
find dataset -type f -not -name '*.jpg' -not -name '*.png' -not -name '.DS_Store'
```
