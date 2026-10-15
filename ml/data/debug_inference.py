"""Debug helper: run vision pipeline on an image and dump coordinate trace.

Usage:
  .venv/bin/python ml/data/debug_inference.py <image_path> [--out /tmp/dbg.png]

Prints original dims, letterbox scale/pad, final boxes, mask stats.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, ".")

from ml.vision.pipeline import VisionPipeline


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    p = VisionPipeline()
    # EXIF-orient to match pipeline decoding (preprocessing.decode_image_bytes)
    img = ImageOps.exif_transpose(Image.open(args.image)).convert("RGB")
    print(f"original: {img.size} mode={img.mode}")
    finding = p.process_image(str(args.image), filename=Path(args.image).name)
    t = finding.transforms
    print(f"letterbox: target=({t.target_width},{t.target_height}) scale={t.scale_factor} pad=({t.pad_left},{t.pad_top})")
    print(f"damage={finding.damage_detected} prob={finding.damage_probability} sev={finding.severity.score}")
    for d in finding.detections:
        print(f" - {d.label} conf={d.confidence} box={d.bbox_xyxy} mask_pts={len(d.mask) if d.mask else 0}")
    if args.out:
        ov = img.copy()
        dr = ImageDraw.Draw(ov)
        for d in finding.detections:
            dr.rectangle(d.bbox_xyxy, outline=(0, 200, 255), width=4)
            if d.mask:
                dr.polygon([tuple(pt) for pt in d.mask], outline=(0, 200, 255))
            dr.text((d.bbox_xyxy[0], max(0, d.bbox_xyxy[1] - 14)), f"{d.label} {int(d.confidence*100)}%")
        ov.save(args.out)
        print(f"overlay saved: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
