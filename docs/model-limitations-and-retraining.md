# Model Limitations & Retraining Plan

## Current Active Backend

As of pipeline version **1.2.0** the four vision stages run a **local OpenCV
engine** (`ml/vision/classical_engine.py`, registry id `classical_cv_v1`) — no
neural checkpoints, no network access. Behavior:

- **Stage 1 (filter)**: measured anomaly mass → saturating damage probability.
  `assessment = "damaged"` requires `p ≥ 0.85`; below that the pipeline returns
  a *valid negative* (`no_damage`) from completed inference — not an abstention.
- **Stage 2 (classifier)**: labels assigned from measured region geometry
  (elongation, brightness, area, frame position) against the 6-class taxonomy.
- **Stage 3 (detector)**: hysteresis thresholding of four response channels
  (scratch top-hat, texture-gated DoG, local-std chaos, morphological gradient)
  with border-spanning and area guards; outputs real bounding boxes + pixel
  contours mapped to original image coordinates.
- **Stage 4 (segmenter)**: polygon areas computed from the *real* contours
  Stage 3 extracted; `mask_pixel_area`/`relative_area` are measured, never
  synthesized from boxes.

### Honest limitations of the classical engine

- Class labels are geometric heuristics: a chaotic bright region may be labeled
  `broken_light` when it is actually a shattered mirror or headlamp; heavy
  front-end damage is labeled `bumper_smash` by position/size heuristics.
  Taxonomy precision is lower than a trained detector.
- `flat_tire` is not detectable (wheel/tire region is not segmented).
- Severity uses `calibrated = false` with spec-fixed class weights; score is a
  relative-area heuristic, not an expert-calibrated grade.
- No vehicle-part segmentation: severity denominator is the full frame when no
  vehicle mask exists.
- Scene guardrails (border-spanning rejection, fine-texture gating, local
  contrast normalization) suppress background texture but adversarial scenes
  (reflections, murals, heavy graffiti) can still confuse response channels.

### Major-collision fix (1.2.0) — what changed and why

Root causes found by tracing the severe white-car frontal image
(`insp_e7736baa/.../19f6218212434986b8822ef7608e2fce.jpg`) from raw response
maps to the rendered overlay:
1. **Severe damage was gated away, trivia kept.** Crushed-grille / exposed-
   internal / headlight fragments fire the chaos/crack channels with
   edge_share 0.70–0.84, and the single global edge gate (0.40/0.65) rejected
   every one of them — while a smooth sky/tree highlight (edge 0.21) passed
   and rendered as `dent 79%` on trees. Fix: channel-aware edge caps
   (`CHAOS_EDGE_MAX 0.88`, `CRACK_EDGE_MAX 0.92`), deep-shadow hue skip
   (`DARK_HUE_SKIP_GRAY 60`), sky-band background rejection, and a
   conservative vehicle-ROI guard (small boxes <25% inside the estimated
   vehicle box are dropped; large boxes never are).
2. **Fragmented bumpers missed the size bar.** A crushed bumper shatters into
   adjacent pieces (area 0.02–0.04), each below the old 0.05/0.06
   `bumper_smash` minimums, so the main damage rendered as plain `dent`.
   Fix: fragment-tolerant minimums (`BUMPER_SMASH_MIN_AREA_CHAOS 0.030`,
   `..._DENT 0.035`, zone `y > 0.60`) plus adjacent-tiny-fragment
   suppression in `_dedupe` so shatter shards don't multiply boxes.
3. **No notion of primary damage.** Boxes were ordered by
   confidence×√area, so a confident minor scratch could outrank the crushed
   bumper. Fix: `ml/vision/prioritization.py` ranks by class weight × extent
   × confidence × localization quality, stamps `priority` (`primary` first,
   rest `secondary`), `component` (positional estimate, rear-view aware via
   red-taillight sampling), and `priority_score`. Overlay chips, box tags,
   classifications, and the PDF all consume the same ordered list.
4. **Shattered lamps unlabeled.** Added a measured bright+edge-dense+mid-
   height rule emitting `broken_light` on chaos/crack channels.

Verified on the reference images: frontal white car → primary
`bumper_smash`/`front_bumper` first, buckled hood localized, tree FP gone
(11→8 boxes, all in vehicle zone); rear white car → primary
`bumper_smash`/`rear_bumper` with `taillight` identified. Regression tests:
`tests/test_major_damage.py` (7 tests). Full suite: 39 passed in `.venv`.

Remaining gaps (still require neural retraining, NOT completed):
- Dent-vs-scratch and exact part boundaries remain heuristic; components are
  positional estimates, not trained part segmentation.
- `flat_tire` effectively undetectable; severity weights uncalibrated.
- See Retraining Plan below for the CarDD/YOLO-seg path with acceptance gate.

## Abstention semantics (unchanged)

- When a stage genuinely fails (engine init failure, corrupt bytes, degenerate
  image), the pipeline returns `assessment = "inconclusive"` with
  `severity.level = "unavailable"`, `score = null`.
- Inconclusive assessments are propagated end-to-end: risk engine
  (`RiskClass.UNAVAILABLE`, `review_required = true`, rule
  `RULE_V0_VISION_INCONCLUSIVE`), report payload (`overall.assessment`,
  `images[].assessment`), PDF renderer, and the Flutter UI.
- The application will **never** fabricate `NO DAMAGE`, `SAFE`, or a numeric
  severity score from a failed inference. A `NO DAMAGE` verdict requires a
  completed Stage 1 inference below the calibrated threshold; a `DAMAGED`
  verdict requires Stage 1 above threshold plus surviving localizations.
- Inconclusive reason strings are de-duplicated at aggregation
  (`process_inspection`) and report compilation (`_compile_report`); raw
  filenames/stack traces stay in server logs, not user-facing messages.
- Duplicate image content (repeat selection/upload) is analyzed once; the skip
  is reported as a single report warning.

## Retraining Plan (remaining work)

1. **Dataset**: Train on CarDD (Car Damage Detection) with its four tasks (damage region
   detection, damage part segmentation, part-level detection, severity grading). Do not label
   published benchmark metrics as results of this application.
2. **Stage 1 (binary filter)**: Fine-tune EfficientNet-B4 on damaged-vs-intact; calibrate the
   decision threshold (`ml/config/vision.yaml: stage1_filter.threshold`) on a held-out
   validation split for target recall ≥ 0.99 on damaged vehicles (false negatives are the
   safety-critical error direction).
3. **Stage 2 (classification)**: Fine-tune ConvNeXt-Tiny on the 16-class taxonomy; report
   macro F1 and per-class recall; document any label remapping rather than silently merging.
4. **Stage 3/4 (detection + segmentation)**: YOLOv8x / Mask R-CNN on damage instances with
   polygon masks; validate mask IoU on a human-reviewed subset.
5. **Severity calibration**: Calibrate `ml/config/severity.yaml` weights and cutoffs against
   expert-graded severity on validation images; keep `calibrated = false` until a documented
   calibration procedure exists. Never convert pixel area to cm² without a scale reference.
6. **Acceptance gate before flipping defaults**: Offline evaluation suite covering all four
   tasks plus the abstention cases (blank/corrupt/low-light images), regression tests in
   `tests/test_vision.py` / `tests/test_vision_inference.py` updated to run against mounted
   weights, and an explicit re-audit of every `damage_detected` consumer in `agents/`,
   `reports/`, and `apps/ios/`. When mounting neural weights, keep the classical engine as
   the abstention fallback so `MODEL_UNAVAILABLE` remains an honest state.

