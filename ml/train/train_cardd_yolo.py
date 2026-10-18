"""Train YOLOv8 / YOLOv11 Instance Segmentation on CarDD dataset.

Runs natively on macOS using Apple Silicon GPU acceleration (device='mps')
or on CUDA / CPU.

Usage:
  ./.venv/bin/python ml/train/train_cardd_yolo.py --epochs 30 --batch 8 --model yolov8n-seg.pt
"""

import argparse
from pathlib import Path
import torch
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
DATA_YAML = ROOT / "data/CarDD_YOLO/cardd_yolo.yaml"


def get_optimal_device() -> str:
    """Select the best compute device available on this host."""
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def train_yolo(
    model_name: str = "yolov8n-seg.pt",
    epochs: int = 30,
    imgsz: int = 640,
    batch: int = 8,
    device: str = None,
    project: str = "work_dirs/cardd_yolo",
    name: str = "train_run",
):
    dev = device or get_optimal_device()
    print("=" * 60)
    print(f"Starting CarDD YOLO Segmentation Training")
    print(f"Model: {model_name}")
    print(f"Dataset config: {DATA_YAML}")
    print(f"Device: {dev} ({'Apple Silicon Metal GPU' if dev == 'mps' else dev})")
    print(f"Epochs: {epochs}, Batch size: {batch}, Image size: {imgsz}")
    print("=" * 60)

    model = YOLO(model_name)

    results = model.train(
        data=str(DATA_YAML),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=dev,
        project=str(ROOT / project),
        name=name,
        save=True,
        plots=True,
        patience=10,
        workers=4,
    )

    best_checkpoint = ROOT / project / name / "weights" / "best.pt"
    print("\n" + "=" * 60)
    print(f"Training Complete!")
    print(f"Best model saved to: {best_checkpoint}")
    print("=" * 60)
    return results, best_checkpoint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO on CarDD")
    parser.add_argument("--model", default="yolov8n-seg.pt", help="Pretrained base model (e.g., yolov8n-seg.pt, yolov8s-seg.pt)")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    parser.add_argument("--device", default=None, help="Device ('mps', 'cuda', 'cpu')")
    parser.add_argument("--name", default="cardd_seg_v1", help="Experiment name")
    args = parser.parse_args()

    train_yolo(
        model_name=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        name=args.name,
    )
