"""Fine-tune CarDD YOLO segmentation model with undamaged vehicle background images.

This trains the YOLO network to penalize false-positive activations on intact car bodies,
clean wheels/spokes, headlight reflectors, and panel seams.
"""

from pathlib import Path
import torch
from ultralytics import YOLO
import shutil

ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = ROOT / "data/CarDD_YOLO/cardd_yolo.yaml"
CHECKPOINT_ORIG = ROOT / "checkpoints/cardd_yolov8_best_orig.pt"
TARGET_CHECKPOINT = ROOT / "checkpoints/cardd_yolov8_best.pt"


def finetune():
    dev = "mps" if (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()) else "cpu"
    print("=" * 60)
    print(f"Fine-tuning YOLO on CarDD with Undamaged Negative Backgrounds")
    print(f"Base weights: {CHECKPOINT_ORIG}")
    print(f"Device: {dev}")
    print("=" * 60)

    model = YOLO(str(CHECKPOINT_ORIG))

    results = model.train(
        data=str(DATA_YAML),
        epochs=3,
        imgsz=640,
        batch=16,
        device=dev,
        project=str(ROOT / "work_dirs/cardd_yolo"),
        name="cardd_seg_bg_v1",
        save=True,
        plots=True,
        workers=4,
        lr0=0.0005,  # gentle learning rate for fine-tuning
        lrf=0.0001,
        exist_ok=True,
    )

    best_pt = ROOT / "work_dirs/cardd_yolo/cardd_seg_bg_v1/weights/best.pt"
    if best_pt.exists():
        print(f"Updating production checkpoint: {TARGET_CHECKPOINT}")
        shutil.copy2(best_pt, TARGET_CHECKPOINT)
        print("Production checkpoint updated successfully!")
    else:
        print("Warning: best.pt not found, keeping previous weights.")

    return results


if __name__ == "__main__":
    finetune()
