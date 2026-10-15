"""Image preprocessing and coordinate transformation utilities.

Complies with ANTIGRAVITY_PROJECT_SPEC.md Section 8.4 and Section 8.6.
Preserves aspect ratio using letterbox padding and maintains bidirectional
coordinate transformations between model tensor space, original image pixels,
and display screens.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageOps

from ml.vision.schemas import BoundingBox, PreprocessingTransformMetadata


def decode_image_bytes(image_bytes: bytes) -> Image.Image:
    """Safely decode image bytes into RGB PIL Image.

    EXIF orientation is baked into the pixels here: Flutter's image decoder
    applies the EXIF orientation flag when rendering, so boxes must be
    computed in the same upright space the user actually sees (otherwise
    overlays land in a rotated coordinate frame on oriented camera photos).
    Images with orientation=1 (already upright) are unaffected.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        # Re-open after verify()
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img
    except Exception as e:
        raise ValueError(f"Corrupt or unsupported image bytes: {e}") from e


def load_image_from_file(file_path: Union[str, Path]) -> Image.Image:
    """Load and verify an image from a filesystem path."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found at {p}")
    with open(p, "rb") as f:
        return decode_image_bytes(f.read())


def letterbox_resize(
    image: Image.Image,
    target_size: Tuple[int, int] = (1024, 1024),
    fill_color: Tuple[int, int, int] = (114, 114, 114),
) -> Tuple[Image.Image, PreprocessingTransformMetadata]:
    """Resize image preserving aspect ratio with padding (letterbox).

    Returns the resized PIL Image and transformation metadata.
    """
    orig_w, orig_h = image.size
    target_w, target_h = target_size

    # Calculate scale factor
    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    # Resize with antialiasing
    resized_img = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Create padded background
    letterboxed = Image.new("RGB", target_size, fill_color)
    pad_left = (target_w - new_w) // 2
    pad_top = (target_h - new_h) // 2
    letterboxed.paste(resized_img, (pad_left, pad_top))

    meta = PreprocessingTransformMetadata(
        original_width=orig_w,
        original_height=orig_h,
        target_width=target_w,
        target_height=target_h,
        scale_factor=scale,
        pad_left=pad_left,
        pad_top=pad_top,
    )
    return letterboxed, meta


def model_to_original_box(
    box: List[float],
    transforms: PreprocessingTransformMetadata,
) -> List[float]:
    """Map bounding box [xmin, ymin, xmax, ymax] from model letterbox space back to original image pixels."""
    xmin, ymin, xmax, ymax = box
    scale = transforms.scale_factor
    pad_x = transforms.pad_left
    pad_y = transforms.pad_top

    orig_xmin = (xmin - pad_x) / scale
    orig_ymin = (ymin - pad_y) / scale
    orig_xmax = (xmax - pad_x) / scale
    orig_ymax = (ymax - pad_y) / scale

    # Clip to original image boundaries
    orig_xmin = max(0.0, min(float(transforms.original_width), orig_xmin))
    orig_ymin = max(0.0, min(float(transforms.original_height), orig_ymin))
    orig_xmax = max(0.0, min(float(transforms.original_width), orig_xmax))
    orig_ymax = max(0.0, min(float(transforms.original_height), orig_ymax))

    return [round(orig_xmin, 2), round(orig_ymin, 2), round(orig_xmax, 2), round(orig_ymax, 2)]


def model_to_original_polygon(
    polygon: List[List[float]],
    transforms: PreprocessingTransformMetadata,
) -> List[List[float]]:
    """Map polygon coordinates from letterbox space back to original image pixel coordinates."""
    scale = transforms.scale_factor
    pad_x = transforms.pad_left
    pad_y = transforms.pad_top
    max_w = float(transforms.original_width)
    max_h = float(transforms.original_height)

    out = []
    for pt in polygon:
        x, y = pt[0], pt[1]
        ox = max(0.0, min(max_w, (x - pad_x) / scale))
        oy = max(0.0, min(max_h, (y - pad_y) / scale))
        out.append([round(ox, 2), round(oy, 2)])
    return out


def normalize_box(box: List[float], img_width: int, img_height: int) -> List[float]:
    """Convert absolute pixel coordinates to normalized 0.0 - 1.0 coordinates."""
    xmin, ymin, xmax, ymax = box
    return [
        max(0.0, min(1.0, xmin / max(1, img_width))),
        max(0.0, min(1.0, ymin / max(1, img_height))),
        max(0.0, min(1.0, xmax / max(1, img_width))),
        max(0.0, min(1.0, ymax / max(1, img_height))),
    ]
