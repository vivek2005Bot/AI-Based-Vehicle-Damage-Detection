"""Validation harness for the classical damage-detection gates.

Runs the full VisionPipeline over the hand-annotated subset in
ml/data/validation/annotations.json and reports:

  * image-level confusion  (damage_detected vs folder-as-label)
  * damage_probability     distributions for positives vs negatives
  * box-level recall       (GT hit if IoU >= 0.20 or det-center inside GT)
  * detection precision    (every emitted box must hit some GT box; any
                            box on a negative image is a false positive)

Usage:
  .venv/bin/python -m ml.data.validate_gates [--limit N] [--overlays DIR]
                   [--filter-threshold T] [--det-threshold T]

The harness is deliberately tolerant (class-agnostic matching): the
classical engine cannot reliably separate dent vs scratch, so gate tuning
optimizes *where* and *whether* damage is reported, not the exact class.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import cv2

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from ml.vision.pipeline import VisionPipeline  # noqa: E402

ANNOTATIONS = REPO_ROOT / "ml" / "data" / "validation" / "annotations.json"


def _iou(a, b) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    if inter <= 0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def _matches(det_box, gt_box) -> bool:
    if _iou(det_box, gt_box) >= 0.20:
        return True
    cx = (det_box[0] + det_box[2]) / 2.0
    cy = (det_box[1] + det_box[3]) / 2.0
    return gt_box[0] <= cx <= gt_box[2] and gt_box[1] <= cy <= gt_box[3]


def _draw_overlay(image_path: Path, finding, gt_boxes, out_path: Path) -> None:
    img = cv2.imread(str(image_path))
    if img is None:
        return
    for gb in gt_boxes:
        cv2.rectangle(img, (int(gb[0]), int(gb[1])), (int(gb[2]), int(gb[3])), (0, 220, 0), 3)
    for det in finding.detections:
        x1, y1, x2, y2 = [int(v) for v in det.bbox_xyxy]
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 60, 60), 2)
        cv2.putText(img, f"{det.label} {det.confidence:.2f}", (x1, max(14, y1 - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 60, 60), 2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), img)


def main() -> int:
    ap = argparse.ArgumentParser(description="validation harness for gates")
    ap.add_argument("--limit", type=int, default=0, help="cap number of negative images")
    ap.add_argument("--overlays", type=str, default="", help="write annotated result images here")
    ap.add_argument("--filter-threshold", type=float, default=None)
    ap.add_argument("--det-threshold", type=float, default=None)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    spec = json.loads(ANNOTATIONS.read_text())
    pipeline = VisionPipeline()
    if args.filter_threshold is not None:
        pipeline.stage1_filter.threshold = args.filter_threshold
    if args.det_threshold is not None:
        pipeline.stage3_detector.confidence_threshold = args.det_threshold

    negatives: list[Path] = []
    for pattern in spec.get("negative_globs", []):
        negatives.extend(sorted(REPO_ROOT.glob(pattern)))
    random.seed(args.seed)
    random.shuffle(negatives)
    cap = spec.get("max_negatives", 0)
    if cap:
        negatives = negatives[:cap]
    if args.limit:
        negatives = negatives[:args.limit]

    jobs = [(Path(REPO_ROOT / e["path"]), e["boxes"], True) for e in spec["positives"]]
    jobs += [(p, [], False) for p in negatives]

    n_pos = n_neg = 0
    img_tp = img_fn = img_fp = img_tn = 0
    gt_total = gt_hit = 0
    det_total = det_matched = 0
    fp_detections: list[tuple[str, str, float, list]] = []
    probs_pos: list[float] = []
    probs_neg: list[float] = []
    failures: list[str] = []
    overlays_dir = Path(args.overlays) if args.overlays else None

    for path, gt_boxes, is_positive in jobs:
        finding = pipeline.process_image(path, filename=path.name)
        dets = [(d.label, float(d.confidence), [float(v) for v in d.bbox_xyxy])
                for d in finding.detections]
        detected = bool(finding.damage_detected)

        if is_positive:
            n_pos += 1
            probs_pos.append(finding.damage_probability)
            for gb in gt_boxes:
                gt_total += 1
                gt_hit += int(any(_matches(db, gb) for _, _, db in dets))
            for label, conf, db in dets:
                det_total += 1
                ok = any(_matches(db, gb) for gb in gt_boxes)
                det_matched += int(ok)
                if not ok:
                    fp_detections.append((path.name, label, conf, db))
            if detected:
                img_tp += 1
            else:
                img_fn += 1
                failures.append(
                    f"MISS    {path.name}: damage=True but damage_detected=False "
                    f"(prob={finding.damage_probability:.3f}, boxes={len(dets)})")
        else:
            n_neg += 1
            probs_neg.append(finding.damage_probability)
            for label, conf, db in dets:
                det_total += 1
                fp_detections.append((path.name, label, conf, db))
            if detected:
                img_fp += 1
                failures.append(
                    f"FP-IMG  {path.name}: undamaged image flagged "
                    f"(prob={finding.damage_probability:.3f}, boxes={len(dets)})")
            else:
                img_tn += 1

        if overlays_dir is not None:
            _draw_overlay(path, finding, gt_boxes,
                          overlays_dir / (path.stem + "_res.jpg"))


    print("=" * 78)
    print(f"images: {n_pos} positive, {n_neg} negative")
    print("-" * 78)
    print("[image-level damage_detected]")
    recall_img = img_tp / n_pos if n_pos else 0.0
    spec_img = img_tn / n_neg if n_neg else 0.0
    print(f"  positive recall : {img_tp}/{n_pos} = {recall_img:.3f}   (misses: {img_fn})")
    print(f"  negative specif.: {img_tn}/{n_neg} = {spec_img:.3f}   (false alarms: {img_fp})")
    if probs_pos and probs_neg:
        print("[damage_probability]")
        print(f"  positives: min={min(probs_pos):.3f} "
              f"mean={sum(probs_pos)/len(probs_pos):.3f} max={max(probs_pos):.3f}")
        print(f"  negatives: min={min(probs_neg):.3f} "
              f"mean={sum(probs_neg)/len(probs_neg):.3f} max={max(probs_neg):.3f}")
    print("-" * 78)
    print("[box-level] (class-agnostic, IoU>=0.20 or center-in-GT)")
    box_recall = gt_hit / gt_total if gt_total else 0.0
    box_prec = det_matched / det_total if det_total else 1.0
    print(f"  GT recall     : {gt_hit}/{gt_total} = {box_recall:.3f}")
    print(f"  box precision : {det_matched}/{det_total} = {box_prec:.3f}  "
          f"({len(fp_detections)} spurious boxes)")
    print("-" * 78)
    if failures:
        print("[image-level failures]")
        for f in failures:
            print("  " + f)
    if fp_detections:
        print("[spurious boxes]")
        for name, label, conf, db in fp_detections:
            box = ",".join(f"{v:.0f}" for v in db)
            print(f"  {name[:44]:44s} {label:11s} {conf:.2f} [{box}]")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

