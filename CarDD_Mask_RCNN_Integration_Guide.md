# Agent Task Guide: Integrate CarDD Mask R-CNN into the Existing Vehicle Damage Inspection Project

> **Audience:** Antigravity / Cline coding agent working inside the existing repository.  
> **Primary goal:** Integrate a CarDD-trained damage detection/instance-segmentation model into the existing FastAPI + Flutter inspection application without breaking current behaviour.  
> **Important:** The downloaded `.pth` checkpoint described below is **COCO-pretrained Mask R-CNN**, not a CarDD-fine-tuned car-damage model. It is an initialization checkpoint for training/fine-tuning, not a reliable six-class car-damage detector by itself.

---

## 0. Non-negotiable instructions for the coding agent

1. **Inspect before editing.** Read the actual repository files and tests. This guide and the project documentation are architectural context, not a substitute for inspecting the current source.
2. **Protect existing work.** Run `git status --short` first. Do not discard, overwrite, reset, or reformat unrelated user changes. Create a working branch only if appropriate for the user's workflow.
3. **Do not make false claims.** Do not call COCO-only weights a trained CarDD model. Do not enable the detector for production predictions until a CarDD-fine-tuned checkpoint is available and verified.
4. **Preserve the current application contract.** Keep the existing FastAPI inspection endpoint, response schema, Flutter overlays, severity calculation, rules engine, and PDF report working unless a change is required and covered by tests.
5. **Keep a fallback.** Preserve the current classical vision engine. The new detector must be feature-flagged and failure-safe so the app can still operate when the optional model is disabled or its checkpoint/dependencies are unavailable.
6. **Do not modify safety rules based on model confidence.** A visual model is not proof that a vehicle is roadworthy. Do not let a no-detection result override OBD-II faults or deterministic safety rules.
7. **Do not add large model weights or dataset files to Git.** Keep `.pth`, datasets, generated predictions, and training artifacts out of commits. Add appropriate `.gitignore` entries if missing.
8. **Avoid dependency breakage.** This repository's CarDD implementation is from the MMDetection 2.x / MMCV 1.x generation. Do not install incompatible legacy dependencies into the main project's current virtual environment without checking its Python/PyTorch versions and tests first. If isolation is necessary, use a separate optional environment or inference service.
9. **Do not invent annotation conversions.** Inspect the dataset and annotation format before writing converters. The official config expects COCO-format bounding boxes and instance masks.
10. **After changes, run tests** relevant to the backend and ML pipeline; report any tests that could not be run and why.

## 1. Known project architecture

The project documentation describes the following existing parts (verify the paths exist before editing):

- Mobile app: `apps/ios/` (Flutter/Dart)
- Backend/API: `backend/app/main.py`, `backend/app/api/endpoints/inspections.py`
- Vision pipeline: `ml/vision/pipeline.py`
- Existing classical detector/feature logic: `ml/vision/classical_engine.py`
- Preprocessing: `ml/vision/preprocessing.py`
- Detector/filter modules: `ml/vision/detector.py`, `ml/vision/filter.py`
- Schemas: `ml/vision/schemas.py` and/or `backend/app/schemas/`
- Severity calculations: `ml/vision/severity.py`
- Orchestration: `agents/supervisor.py`
- Deterministic safety rules: `agents/rules.py`
- PDF generation: `reports/pdf_renderer.py`

The current end-to-end flow is documented as:

`Flutter image upload -> FastAPI inspection endpoint -> SupervisorAgent -> VisionPipeline -> findings/severity -> rules engine -> JSON inspection response -> Flutter overlays/PDF report`

The project already presents bounding boxes, polygons/masks, damage labels, confidence, priority, component, and severity in inspection results. Adapt model outputs to the existing result contract rather than adding a parallel API response format.

## 2. Model and dataset facts

### Checkpoint downloaded by the user

The checkpoint link previously selected is the standard MMDetection Mask R-CNN R-50-FPN 2x checkpoint trained on COCO:

`mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth`

Direct source URL:

<https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_fpn_2x_coco/mask_rcnn_r50_fpn_2x_coco_bbox_mAP-0.392__segm_mAP-0.354_20200505_003907-3e542a40.pth>

Save it somewhere local such as `checkpoints/` or `models/pretrained/`, keeping the actual filename. If it is already downloaded elsewhere, locate it; do not download a duplicate unnecessarily.

**This checkpoint knows COCO classes, not the six CarDD damage categories.** Fine-tuning is required before calling it a CarDD damage detector.

### CarDD classes expected by the official configuration

The official CarDD detection configuration lists these six class names, in this order:

1. `dent`
2. `scratch`
3. `crack`
4. `glass shatter`
5. `lamp broken`
6. `tire flat`

The order matters when interpreting model outputs. Do not reorder them without updating the model config, annotations, and category-ID mapping together.

### Official source files

- Repository and main usage instructions: <https://github.com/CarDD-USTC/CarDD-USTC.github.io>
- CarDD detector README: <https://github.com/CarDD-USTC/CarDD-USTC.github.io/blob/main/README.md>
- CarDD Mask R-CNN config: <https://github.com/CarDD-USTC/CarDD-USTC.github.io/blob/main/code/CarDD_detection/configs/car_damage/mask_rcnn_cfg.py>
- CarDD DCN + Mask R-CNN config: <https://github.com/CarDD-USTC/CarDD-USTC.github.io/blob/main/code/CarDD_detection/configs/car_damage/DCN_plus_cfg.py>
- Official legacy inference script: <https://github.com/CarDD-USTC/CarDD-USTC.github.io/blob/main/code/CarDD_detection/tools/inference.py>
- MMDetection v2.28.2 Mask R-CNN model zoo: <https://github.com/open-mmlab/mmdetection/blob/v2.28.2/configs/mask_rcnn/README.md>

The CarDD repository documents training a model on CarDD, then using a resulting work-directory checkpoint such as `epoch_24.pth` for testing/inference. During repository inspection, a committed, directly downloadable CarDD-fine-tuned detector checkpoint was not verified. Assume training is required unless a real CarDD-fine-tuned checkpoint is discovered and its provenance is verified.

## 3. Phase 1 — Preflight investigation (do this before coding)

1. Identify the repository root and inspect:
   - `git status --short`
   - `find ml/vision backend/app agents -maxdepth 4 -type f` (or platform-appropriate equivalent)
   - Python version and active environment
   - dependency manifests (`pyproject.toml`, `requirements*.txt`, lock files)
   - current detector-loading path and vision response schemas
   - tests for `VisionPipeline`, detector, schemas, severity, API inspections, and rules
2. Read at least these source files if present:
   - `ml/vision/pipeline.py`
   - `ml/vision/detector.py`
   - `ml/vision/filter.py`
   - `ml/vision/classical_engine.py`
   - `ml/vision/preprocessing.py`
   - `ml/vision/schemas.py`
   - the inspection endpoint and `agents/supervisor.py`
   - tests covering the above
3. Locate the `.pth` file and record its size and path. Do not print personal credentials or unrelated environment variables.
4. Check the actual environment:

   ```bash
   python --version
   python -c "import torch; print('torch', torch.__version__); print('mps', hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False); print('cuda', torch.cuda.is_available())"
   python -c "import importlib.util as u; print('mmdet', u.find_spec('mmdet')); print('mmcv', u.find_spec('mmcv'))"
   ```

   If the project has a virtual environment, use its Python executable and do not accidentally use the system Python.
5. Determine whether CarDD image files and COCO annotations exist locally. The official config assumes a COCO-format layout with `train2017`, `val2017`, `test2017`, and JSON files such as `instances_train2017.json`. Do not assume the Hugging Face/FiftyOne download automatically has this exact structure.
6. Before making dependency changes, present a short implementation plan to the user if the agent's environment reveals a major incompatibility or missing dataset/checkpoint. Continue with safe, code-only integration where possible.

## 4. Phase 2 — Decide the execution strategy

The official CarDD code is legacy tooling. Its README specifies Python 3.8, PyTorch 1.7.0, CUDA 11.0, MMDetection, and MMCV 1.x-era dependencies. The config files also contain author-machine absolute paths such as `/root/autodl-nas/...` and `/root/autodl-fs/...`; these must be made portable before use.

Choose the least disruptive route based on the actual project environment:

### Route A — Compatible Linux/NVIDIA environment is available

Use the official MMDetection 2.x implementation and the downloaded COCO checkpoint to fine-tune on CarDD. Pin dependencies in an **isolated optional environment/container** if they conflict with the main backend. Prefer this route for reproducing the original config.

### Route B — Development happens on a MacBook

Do not assume the official inference script runs as written: it hardcodes `cuda:0` / `cuda:1`, and legacy MMCV custom operators may not work with the installed Mac/PyTorch build. A CPU test may work only if the compatible dependencies and operators are available. Apple Silicon/MPS compatibility must be proven, not assumed.

- Do not blindly install an old CUDA/MMCV stack into the project's `.venv`.
- The agent may implement a clean optional detector adapter and feature flag in the existing codebase while documenting that model inference is unavailable until a compatible environment/checkpoint is prepared.
- If model inference must run locally and the legacy stack cannot be made compatible, propose an isolated Linux/cloud inference service or a deliberate model-porting effort. Do not try to load this `.pth` through an unrelated framework (for example, Ultralytics) and claim compatibility.

### Route C — Main project dependencies conflict with MMDetection 2.x

Keep MMDetection in a separate environment or service with a small request/response interface. The existing FastAPI app can call that service or a controlled subprocess. Avoid changing the main project's pinned Torch/OpenCV dependencies just to support one model.

The coding agent should make a reasoned choice, record it in the final summary, and never silently change the project's core Python stack.

## 5. Phase 3 — Prepare the CarDD training config

Use the official `mask_rcnn_cfg.py` as the starting point because it matches the downloaded **R-50-FPN 2x COCO** checkpoint. Do not start with the DCN configuration unless the agent intentionally chooses and verifies the matching DCN checkpoint/config.

Create a project-specific portable config, for example:

`configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py`

or place it within the cloned legacy repository and ensure the path is documented. Requirements:

- Set `_base_` to the relative config path for the matching Mask R-CNN R-50-FPN 2x COCO config. Remove the original absolute author-machine path.
- Define the six class names in the exact order listed above.
- Set both the box head and mask head to `num_classes=6`.
- Point `load_from` to the user's actual local COCO `.pth` file, using a relative path or a clearly configurable environment-specific path. Remove `/root/autodl-nas/...`.
- Set training, validation, and test image directories and COCO annotation JSON paths to actual paths on this machine/runtime. Remove `/root/autodl-fs/...`.
- Keep a held-out test split separate from training and model/threshold selection.
- Make work directory configurable, and preserve the original config untouched where practical.
- Ensure evaluation includes bounding-box and segmentation metrics (`bbox`, `segm`) and class-wise results if supported by the installed MMDetection version.
- Confirm the checkpoint architecture is exactly compatible with the chosen config. If the class-head shapes differ, use the standard MMDetection fine-tuning mechanism and resolve any mismatched keys explicitly; do not suppress load errors silently.

**Dataset condition:** If image files and annotations are not present in the correct format, stop short of launching training. Report precisely what is missing. Inspect annotation fields and official dataset instructions before generating a conversion script. Instance-segmentation training requires mask annotations, not only class labels or bounding boxes.

## 6. Phase 4 — Fine-tune on CarDD

Run commands from the appropriate isolated MMDetection 2.x checkout/environment. These are templates; use the actual paths and interpreter discovered during preflight.

```bash
# From the compatible CarDD/MMDetection code root
python tools/train.py configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py \
  --work-dir work_dirs/cardd_mask_rcnn_r50_fpn_2x
```

After training:

1. Inspect the work directory and identify the best/last actual checkpoint and training logs. Do not assume the exact epoch filename without checking.
2. Save the path of the verified CarDD-fine-tuned checkpoint in the project configuration/environment, not in source code.
3. Keep the original COCO checkpoint as an initialization asset; it is not the production damage model.
4. Do not commit either checkpoint to Git.

### Evaluate the fine-tuned checkpoint

For the legacy MMDetection 2.x scripts, the documented pattern is:

```bash
python tools/test.py \
  configs/cardd/mask_rcnn_r50_fpn_2x_cardd.py \
  work_dirs/cardd_mask_rcnn_r50_fpn_2x/<actual-checkpoint>.pth \
  --eval bbox segm
```

Use the exact arguments accepted by the installed version. Save per-class precision/recall or AP, bbox mAP, mask mAP, and the confusion/error analysis if supported. Do not report COCO model-zoo AP as CarDD performance.

Visualize predictions on held-out images and manually inspect each class, especially thin scratches/cracks and small damage regions. Record the confidence threshold chosen on validation data; do not tune thresholds on the final test set.

## 7. Phase 5 — Integrate through a dedicated adapter

Prefer a new module such as `ml/vision/carddd_detector.py` (adjust naming to match project conventions). The agent must first inspect how `ml/vision/detector.py` and the current pipeline are structured; reuse existing abstractions when possible and avoid duplicate model-loading logic.

### Required adapter behaviour

- Load the model once at application startup or lazily once, not once per image/request.
- Read configuration from environment/settings; suggested variables:

  ```text
  CARDD_MODEL_ENABLED=false
  CARDD_MODEL_CONFIG=<path-to-carddd-model-config>
  CARDD_MODEL_CHECKPOINT=<path-to-carddd-finetuned-checkpoint>
  CARDD_MODEL_DEVICE=cpu
  CARDD_MODEL_SCORE_THRESHOLD=0.50
  CARDD_MODEL_BACKEND=mmdet2
  ```

  Put safe defaults/placeholders in `.env.example`, not private paths or secrets. Start disabled until the CarDD-fine-tuned checkpoint has been verified. `cpu` is only a safe requested device default; actual compatibility must be tested.

- Validate at startup that config and checkpoint paths exist, labels are configured, and checkpoint provenance indicates CarDD fine-tuning. Emit actionable logs without logging image bytes or sensitive paths unnecessarily.
- Return a typed result that includes, per detection:
  - class label and/or stable class ID
  - confidence score
  - bounding box in pixel `xyxy` coordinates in the **original image coordinate system**
  - instance-mask/polygon data when available
  - source model name/version and optional inference timing
- Reject invalid/non-image inputs gracefully and avoid API crashes on model exceptions.
- Add a clear status path/log so it is obvious whether the deep model is enabled, disabled, or unavailable.
- Preserve a configurable fallback to the current `ClassicalDamageEngine` when appropriate. Do not silently treat a failed deep-model call as a successful no-damage prediction.
- Add a model-loading lock if needed to avoid races under concurrent FastAPI startup/requests. Avoid CPU/GPU oversubscription; batch only if it matches the existing worker model.

### Example API for legacy MMDetection 2.x (illustration only)

The old MMDetection API uses `init_detector` and `inference_detector`. The original CarDD `tools/inference.py` hardcodes CUDA, so do not copy it without correcting the device selection and integrating its raw output parsing.

```python
from mmdet.apis import init_detector, inference_detector

model = init_detector(config_path, checkpoint_path, device=device)
raw_result = inference_detector(model, image_path)
# Parse raw_result according to the installed MMDetection 2.x API and model type.
# Convert it into your project's typed findings here.
```

The result structure of Mask R-CNN in MMDetection 2.x normally separates per-class detections from per-instance segmentation masks. Validate the exact structure with a small real inference before writing the conversion logic. Add tests for empty results and no-mask cases.

## 8. Phase 6 — Map predictions into the existing application's finding schema

Inspect existing Pydantic/dataclass/enum definitions first. The existing project documentation mentions internal labels such as `glass_crack`, `broken_light`, `bumper_smash`, `broken_mirror`, `dent`, and `scratch`, while CarDD uses `dent`, `scratch`, `crack`, `glass shatter`, `lamp broken`, and `tire flat`.

Do not assume these names mean exactly the same thing. Implement an explicit, documented category-mapping layer and preserve the original CarDD class as `source_class` where the schema permits. If an existing enum cannot safely represent a CarDD class, extend the schema carefully with backward-compatible tests rather than mapping a crack to a bumper smash or inventing detections for classes the model does not contain.

Suggested semantic mapping candidates (must verify against the actual schema before committing):

| CarDD label | Candidate internal handling |
|---|---|
| `dent` | Existing `dent` class, if the schema definition matches |
| `scratch` | Existing `scratch` class, if the schema definition matches |
| `crack` | Preserve as `crack` unless the affected component is reliably known; do not infer windshield location from this label alone |
| `glass shatter` | Preserve as `glass_shatter` or another explicit glass-damage label; do not equate it automatically with every `glass_crack` category |
| `lamp broken` | Can map to `broken_light` only if the schema semantics support it; component may be unknown from the damage label alone |
| `tire flat` | Map to an explicit `flat_tire` label if supported; it may require adding a schema value |

Important conversion checks:

- Clamp boxes to image width/height, ensure `x2 > x1` and `y2 > y1`, and preserve the documented `xyxy` convention.
- Convert mask coordinates/polygons to the existing schema's coordinate convention, whether normalized `[0,1]` or pixel coordinates. Never guess: inspect `preprocessing.py`, `schemas.py`, and Flutter's overlay renderer.
- Test images with EXIF orientation and resized/letterboxed images to ensure overlays align with the original uploaded photo.
- If the UI requires polygon vertices, convert the model's mask to contours/polygons in a tested manner. Keep box-only output possible if mask extraction fails.
- Do not calculate damage area as box area when a valid mask is available. If masks are missing, label the estimate as approximate.
- Apply confidence thresholds to suppress low-confidence predictions, but select thresholds on validation data per class where useful.
- Deduplicate overlapping predictions only with a tested rule. Avoid deleting nearby but distinct damage instances.

## 9. Phase 7 — Wire into the existing vision pipeline

Integrate the adapter at the narrowest sensible point in `VisionPipeline`/detector flow.

Recommended selection logic:

1. If `CARDD_MODEL_ENABLED` is false, retain existing behaviour exactly.
2. If enabled and a **verified CarDD-fine-tuned** model is available, run the deep detector on the original image and convert its outputs into the existing findings schema.
3. Preserve pre-existing safety/telemetry processing regardless of the visual model's outputs.
4. Decide whether to run the classical engine alongside the deep detector or only as fallback based on the current project design and a measured benchmark. Avoid simply combining every prediction from both systems, which may double-count defects.
5. If the model cannot load or inference errors, log a clear message and use the approved fallback policy. Never return `NO_DAMAGE` merely because model loading failed.
6. Pass structured findings through existing severity, rules, supervisor, JSON, Flutter overlay, and PDF flows with backwards compatibility.

Do not hard-wire new severity thresholds to a model confidence score. Keep severity calculation based on explicit calibrated/validated measurements and known safety rules. Confidence communicates model certainty, not roadworthiness.

## 10. Phase 8 — Tests required before enabling by default

Add focused tests compatible with the existing test framework. Mock inference where possible so the normal test suite does not need a large model checkpoint.

Minimum tests:

1. Disabled feature flag preserves current classical-engine behaviour.
2. Missing config/checkpoint disables the optional model safely and returns a visible warning/status rather than crashing app startup unexpectedly.
3. Model output class IDs map to the correct ordered CarDD labels.
4. Box parsing handles empty output, one detection, multiple classes, invalid boxes, and coordinates outside image boundaries.
5. Mask parsing handles empty masks, multiple masks, and expected polygon/normalized coordinates.
6. The adapter preserves original image coordinates after preprocessing/resizing.
7. Model failure does not become a false `NO_DAMAGE` result.
8. API response schema remains valid and the existing Flutter overlay/PDF fields remain present.
9. Existing `pytest` suite passes; run relevant backend tests and any Flutter static analysis/tests if shared schemas/UI change.
10. Add an opt-in smoke test (not run by default) that loads a real fine-tuned checkpoint and runs on a sample image.

Use synthetic/mock model outputs in unit tests. Avoid requiring the full CarDD dataset or checkpoint to run the standard test suite.

## 11. Phase 9 — Benchmark and document improvements

Compare the current classical pipeline against the CarDD model on the same held-out samples. Record:

- bbox mAP and mask mAP on CarDD test data
- precision and recall per class
- per-class false positives/false negatives
- inference latency per image and peak memory
- results for small damage regions (especially scratches/cracks)
- overlay alignment and mask-area errors
- fallback behaviour when model weights are unavailable

Possible later experiments (only after a reproducible baseline exists):

- higher-resolution/multi-scale training to improve small-damage recall
- validation-set confidence thresholds per class
- augmentations for brightness, glare, blur, scale, and viewpoints that resemble target photos
- compare R-50-FPN against R-101-FPN, DCN, or Cascade Mask R-CNN
- consider a lighter deployment/export path after accuracy is validated

Do not claim an improvement until metrics on the same test set demonstrate it. Use the same splits and avoid tuning on the held-out test set.

## 12. Dataset, copyright, and usage limitations

The CarDD dataset page notes restrictions related to underlying Flickr/Shutterstock image licenses and states that the dataset is intended for non-commercial research and educational purposes. The coding agent must preserve dataset/license notices and must not package the full dataset into the application's distributable assets. Verify the specific terms before any non-academic or commercial deployment.

Dataset details and access: <https://cardd-ustc.github.io/>  
Official repository: <https://github.com/CarDD-USTC/CarDD-USTC.github.io>

## 13. Suggested Git hygiene

Add or retain ignore rules similar to the following (adapt to existing conventions; do not duplicate rules unnecessarily):

```gitignore
# Large ML assets and private datasets
checkpoints/
models/pretrained/*.pth
*.pth
*.pth.tar
# Dataset folders (use the actual project dataset path)
CarDD_COCO/
data/CarDD/
work_dirs/
outputs/cardd_test/
```

Do not use ignore rules that hide source config files or small, intentional test fixtures. If the `.pth` is currently tracked, do not rewrite Git history without explicit permission; report the situation and propose a safe fix.

## 14. Definition of done

The task is done only when the agent can report all applicable items below accurately:

- [x] Existing code and Git changes were inspected before editing.
- [x] A portable CarDD Mask R-CNN config exists and no author-machine absolute paths remain in that active config.
- [x] The downloaded COCO checkpoint is referenced correctly as an initialization checkpoint, not misrepresented as CarDD-trained.
- [x] Dataset/annotation readiness was verified; missing data or format conversion is documented.
- [x] Training instructions are reproducible in a compatible environment; if training was executed, the actual fine-tuned checkpoint path is recorded.
- [x] A dedicated model adapter exists and is integrated behind a feature flag, or the agent documents the concrete blocker and leaves the current app unchanged.
- [x] The new adapter emits the current application's structured finding schema with well-tested labels, boxes, and masks.
- [x] Existing classical vision, telemetry analysis, rules engine, API schema, reports, and Flutter presentation remain functional.
- [x] Relevant tests and lint/static-analysis commands were run, with results recorded.
- [x] `.pth` and dataset assets are not accidentally committed.
- [x] Final response lists files created/modified, install/train/run commands, tests passed/failed, actual limitations, and the next action required from the user.

## 15. Final report format for the coding agent

At the end of the task, report:

1. **What changed:** files created/modified and the role of each.
2. **Model status:** state clearly whether there is only COCO initialization weights or a verified CarDD-fine-tuned checkpoint.
3. **How to run:** exact commands for the user's environment.
4. **Tests:** commands run and their outcomes; never say tests passed if they were not run.
5. **Known limitations:** platform/package incompatibility, missing dataset annotations, model artifact path, or unverified accuracy.
6. **Recommended next step:** one concrete action to reach a working end-to-end CarDD detector.

---

## Key implementation principle

**Integrate the detector as an optional, independently testable component; fine-tune it on the six CarDD classes; translate its predictions into the current finding schema; and keep the existing safety and reporting pipeline intact.**
