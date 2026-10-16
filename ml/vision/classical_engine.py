"""Classical-CV damage inference engine (OpenCV).

Active inference backend for the 4-stage vision pipeline when no neural
checkpoint is mounted. Every output is derived from real pixel measurements
on the input image — nothing is fabricated or hard-coded:

  - scratch channel: multi-orientation morphological black top-hat
    (thin bright ridges = scratches / paint damage)
  - dent channel: illumination band-pass residual, Difference-of-Gaussians
    (broad shading deformation = dents / crushed panels)
  - chaos channel: local standard-deviation anomaly
    (shattered / exposed internals = broken components, bumper smash)
  - crack channel: small morphological gradient ridges
    (thin dark branching lines = glass cracks)

All response maps are locally contrast-normalized (response minus a heavily
blurred version of itself) so *diffuse* background texture — trees, asphalt —
cancels out, while *spatially localized* anomalies (damage) survive
thresholding. Region confidence is a monotone function of measured anomaly
strength; the stage-1 probability is a saturating function of total anomaly
mass — both deterministic functions of measured image statistics.
"""

from __future__ import annotations

import hashlib
import math
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

# Canonical damage taxonomy (shared with ml.vision.classifier).
# broken_mirror (id 6) covers torn/destroyed side-mirror assemblies: dark
# cavity + jagged internals + mirror-zone position. Added because destroyed
# mirrors were systematically mislabeled "dent" with no supported alternative;
# the dataset has no per-class labels to learn this from, so the rule is
# evidence-based (dark-core fraction, torn texture, cross-channel
# corroboration) and validated by regression tests on real mirror images.
CANONICAL_CLASSES = (
    "scratch",
    "dent",
    "glass_crack",
    "bumper_smash",
    "flat_tire",
    "broken_light",
    "broken_mirror",
)


WORK_MAX_SIDE = 768          # analysis resolution cap; boxes are mapped back
MIN_IMAGE_SIDE = 48          # below this, inference is meaningless -> FAILED
HP_SIGMA_FRAC = 1.0 / 14.0   # local-contrast normalization sigma (of long side)
ANOMALY_FLOOR = 0.055        # absolute floor on normalized anomaly map
ANOMALY_PERCENTILE = 99.0    # adaptive threshold percentile of positive values
MIN_REGION_AREA_FRAC = 2.5e-4
MAX_REGION_AREA_FRAC = 0.35
REGION_CONF_FLOOR = 0.30     # stage-3 gate is 0.35; engine stays slightly lower
PROB_GAIN = 11.0             # saturating mass->probability gain (stage 1)

# --- Local-distinctness gates (validated on ml/data/validation) ---------------
# A response blob is only "damage" if it looks like a *localized material
# defect*, not an object boundary, window frame, wheel arch, foliage clump,
# taillight or letterbox seam. Each threshold below rejects a measured FP
# signature that was confirmed against annotated false positives while true
# damage (creases, scratches, cracks, crumpled areas) stays below them.
EDGE_SHARE_MAX_BASE = 0.40   # Base threshold for edge_share gate
                             # (windows/taillights/trees/seams) measure 0.5-0.8;
                             # true dents/scratches measure 0.05-0.25
# Adaptive edge share: if global image edge density is high, relax the threshold
# to avoid rejecting valid damage on high-edge images (complex body lines, etc.)
EDGE_SHARE_MAX_HIGH_EDGE = 0.65  # Threshold when global edge density > HIGH_EDGE_FRAC
HIGH_EDGE_FRAC = 0.30            # Global Sobel>60 fraction above which image is "high-edge"
HUE_STD_MAX_DEG = 45.0       # circular std of saturated hues inside the region:
                             # foliage/tint blends measure 60-120 deg; paint
                             # fields measure <25 deg; unsaturated panels skip
SAT_DIFF_MAX = 60            # |S(region) - S(context ring)|: window glass vs
                             # frame/paint measures 55-183; same-paint damage <25
HUE_SAT_MIN = 50             # S below this carries no hue signal (gray paint)
HUE_MIN_VOTES = 8            # saturated pixels required before hue gates apply
RING_MIN_VOTES = 30          # ring saturated pixels required for context stats
VARIATION_MIN_STD = 5.0      # gray std below this = uniform fill (no physical
                             # signal: flat color fields, pad bars, black bars)
# glass_crack label gate: the crack channel must only produce glass_crack in a
# dark, low-saturation glass context (tinted glass + seal). Bright/saturated
# contexts are body panels, where a "crack" response is a crease edge instead.
# Thresholds are CONSERVATIVE (strict) to avoid mislabeling dark paint as glass:
# dark paint (black/dark gray) can satisfy lenient gates, so require very dark
# + very low saturation + darker-than-surroundings (tint effect).
GLASS_GRAY_MAX = 110.0       # region mean luminance (0-255): glass is very dark
GLASS_RING_GRAY_MAX = 140.0  # context ring mean luminance: surroundings also dark (seal/frame)
GLASS_SAT_MAX = 60           # region median saturation: glass has minimal color
GLASS_DARKER_THAN_RING = 10.0  # region must be at least this much darker than ring (tint)

# --- Major-collision + background handling (severe front-end regression) ----
# Severe collision damage (crushed bumper, exposed internals, shattered lamps)
# is *structurally* edge-dense: torn metal and exposed components produce dense
# Sobel responses. A single global edge gate therefore suppresses the most
# important damage while letting smooth background highlights (sky/tree gaps)
# through. Thresholds below are channel-aware and position-aware, validated
# against the severe white-car front-collision regression image:
CHAOS_EDGE_MAX = 0.88        # chaos channel EXPECTS edges (shattered/torn);
                             # only reject near-solid edge blocks
CRACK_EDGE_MAX = 0.92        # crack channel fires on ridges by design
DARK_HUE_SKIP_GRAY = 60.0    # hue is unreliable in deep shadow/gaps (exposed
                             # dark internals); skip busy_texture gate there
SKY_BAND_Y_MAX = 0.12        # normalized y-center below this = sky/vegetation band
SKY_MAX_AREA_FRAC = 0.008    # background bits are tiny; never reject large regions here
SKY_BRIGHT_GRAY = 170.0      # bright smooth highlight in sky band = sky/tree gap
# Bumper thresholds lowered for fragmented structural damage: a crushed bumper
# shatters into adjacent fragments, each below the old 0.05/0.06 minimums.
BUMPER_SMASH_MIN_AREA_CHAOS = 0.030  # was 0.05
BUMPER_SMASH_MIN_AREA_DENT = 0.025    # was 0.035 (severe front bumper crush is ~0.033)
# Lower vehicle zone. NOTE: 0.60 was tried but stole mid-door mirror cavities
# (y~0.60) into bumper_smash; 0.62 keeps mirror/door damage separate while all
# validated fragmented bumpers (y~0.75+) still qualify.
BUMPER_SMASH_MIN_Y = 0.62
# Shattered-lamp rule: bright, mid-height, edge-dense fragments are broken
# headlights/taillights even when small (validated on front-collision image).
LAMP_MIN_GRAY = 150.0
LAMP_MIN_EDGE = 0.55
LAMP_MAX_SAT = 80.0
LAMP_MIN_AREA_FRAC = 0.003
LAMP_MAX_AREA_FRAC = 0.12
LAMP_Y_MIN = 0.30
LAMP_Y_MAX = 0.70
# Vehicle-ROI guard: detections mostly outside the estimated vehicle box are
# background (trees/sky/asphalt) unless large (ROI estimation can err).
ROI_MIN_OVERLAP = 0.25
ROI_LARGE_AREA_FRAC = 0.02

# --- Broken-mirror rule (torn/destroyed side-mirror assemblies) --------------
# A destroyed mirror = dark torn cavity + jagged texture in the mirror zone
# (mid-height, not bottom strip, not wide low-center intake). Cross-channel
# corroboration (chaos/crack firing on the same pixels) is required for
# moderate-dark regions; extreme-dark torn regions qualify on contrast alone.
MIRROR_Y_MIN = 0.15
MIRROR_Y_MAX = 0.85
MIRROR_MIN_AREA = 0.004
MIRROR_MAX_AREA = 0.09
MIRROR_DARK_GRAY = 70.0        # cavity/shadow pixel threshold
MIRROR_DARK_MOD = 0.25         # dark fraction needing corroboration
MIRROR_DARK_EXT = 0.50         # dark fraction qualifying on contrast alone
MIRROR_MIN_STD = 12.0          # torn (not flat black paint)
MIRROR_MIN_CONTRAST = 40.0     # cavity darker than its surround (vs black paint)
MIRROR_MIN_XCORR = 0.15        # cross-channel overlap fraction
MIRROR_DARK_SUB_MIN_PX = 32    # min dark-subcore pixels for cavity rescue
MIRROR_DARK_SUB_FRAC = 0.08    # min subcore share of parent mask
# --- Shattered-lamp rule (v2: torn lenses are dark, not just bright) ---------
# Headlight/taillight lenses shatter into mixed bright-shard + dark-gap
# fragments. Brightness alone misses torn dark lenses, so small edge-dense
# mid-height fragments with cross-channel corroboration also qualify.
LAMP_Y_MIN_V2 = 0.35
LAMP_Y_MAX_V2 = 0.68
LAMP_MIN_AREA_V2 = 0.0008
LAMP_MAX_AREA_V2 = 0.030
LAMP_MIN_XCORR_V2 = 0.10
# --- Trim-seam guard (long intact panel gaps labeled "scratch") ---------------
# True scratches sit on uniform paint (homogeneous ring); seam slivers split
# two different surfaces (heterogeneous ring). Applies to very elongated
# scratch labels only.
SEAM_MIN_ELONGATION = 3.0
SEAM_MAX_RING_STD = 42.0
# --- Wheel-arch / ground-shadow guard -----------------------------------------
# Dark dent/scratch boxes glued to the bottom frame corners are wheel arches,
# tires, or ground shadows — except genuine tire damage (tire-shaped exempt).
ARCH_DARK_GRAY = 100.0
ARCH_BOTTOM_FRAC = 0.97
# --- Strong-core box tightening ------------------------------------------------
# Weak-level (0.40) boxes sprawl over intact paint around the defect.
# Re-localize to the strong-core (>=0.78) bbox + margin when it covers a
# meaningful share of the weak box. Measured, never invented.
CORE_MIN_PX = 12
CORE_MIN_FRAC = 0.15
CORE_MARGIN_FRAC = 0.06

_VALID_LABELS = set(CANONICAL_CLASSES)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _box_overlap_frac(box: Tuple[float, float, float, float],
                      roi: List[float]) -> float:
    """Fraction of `box` area lying inside `roi` (0..1)."""
    ax1, ay1, ax2, ay2 = box
    bx1, by1, bx2, by2 = roi
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
    area = max(1e-9, (ax2 - ax1) * (ay2 - ay1))
    return inter / area


def estimate_vehicle_roi(gray_u8: np.ndarray, hsv: np.ndarray) -> List[float]:
    """Estimate the vehicle bounding box in work-space pixels (classical only).

    Method (no learned weights): Canny edges -> dilate -> largest external
    contour below the sky band. The vehicle is the dominant structured object;
    sky is smooth (few edges) and foliage is fragmented (many small contours).
    Falls back to the full frame when nothing dominant is found, so this guard
    can only suppress small background bits, never large damage.
    """
    hh, ww = gray_u8.shape[:2]
    try:
        edges = cv2.Canny(gray_u8, 60, 150)
        # Ignore the sky band: zero out top rows so tree/sky edges can't win.
        sky_rows = max(1, int(hh * SKY_BAND_Y_MAX))
        edges[:sky_rows, :] = 0
        dil = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        contours, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return [0.0, 0.0, float(ww), float(hh)]
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        # Pad modestly; clamp to frame. Never smaller than half the frame:
        # an absurdly small ROI means estimation failed -> fall back to full.
        pad = int(0.03 * max(ww, hh))
        x1, y1 = max(0, x - pad), max(0, y - pad)
        x2, y2 = min(ww, x + w + pad), min(hh, y + h + pad)
        if (x2 - x1) * (y2 - y1) < 0.25 * ww * hh:
            return [0.0, 0.0, float(ww), float(hh)]
        return [float(x1), float(y1), float(x2), float(y2)]
    except Exception:
        return [0.0, 0.0, float(ww), float(hh)]


@dataclass
class DamageRegion:
    """One localized damage candidate in *work-space* coordinates."""

    label: str
    confidence: float
    bbox_xyxy: Tuple[float, float, float, float]
    polygon: List[List[float]]  # [[x, y], ...] work-space pixels
    strength: float
    area_frac: float
    channel: str
    gray_mean: float = 0.0  # mean luminance (nested dark-core preference)
    gray_std: float = 0.0   # std luminance (torn vs smooth test)


@dataclass
class DamageAnalysis:
    """Full engine output for one image."""

    probability: float
    regions: List[DamageRegion] = field(default_factory=list)
    work_width: int = 0
    work_height: int = 0
    global_edge_share: float = 0.0  # Fraction of pixels with Sobel>60 globally
    vehicle_roi: Optional[List[float]] = None  # [x1,y1,x2,y2] work-space vehicle box estimate


@dataclass
class RegionEvidence:
    """Measured local-distinctness statistics of one candidate region.

    Compares the region against its context ring (dilated surroundings) so
    gating decisions are functions of real pixels, not heuristics on labels.
    """

    edge_share: float            # strong-Sobel fraction inside the mask
    gray_mean: float             # mean luminance inside the mask (0-255)
    gray_std: float              # std luminance inside the mask (0-255)
    ring_gray_mean: float        # mean luminance of the context ring
    ring_gray_std: float         # std luminance of the context ring (seam test)
    reg_s_med: float             # median saturation inside (0-255)
    ring_s_med: float            # median saturation of the ring (0-255)
    d_sat: float                 # reg_s_med - ring_s_med
    reg_hue_rad: Optional[float]     # circular mean hue of saturated pixels
    reg_hue_std_deg: Optional[float]  # circular std of those hues (degrees)
    ring_hue_rad: Optional[float]
    ring_hue_std_deg: Optional[float]
    ring_n_sat: int              # saturated pixels in the ring
    reg_n_sat: int               # saturated pixels inside the region
    red_frac: float = 0.0        # fraction of saturated red pixels (taillight check)


class ClassicalDamageEngine:
    """Deterministic OpenCV damage detector with a tiny per-instance cache
    so the 4 pipeline stages do not re-analyze the same letterboxed image.
    """

    def __init__(
        self,
        prob_gain: float = PROB_GAIN,
        anomaly_floor: float = ANOMALY_FLOOR,
        anomaly_percentile: float = ANOMALY_PERCENTILE,
    ):
        self.prob_gain = prob_gain
        self.anomaly_floor = anomaly_floor
        self.anomaly_percentile = anomaly_percentile
        self._cache: "OrderedDict[bytes, DamageAnalysis]" = OrderedDict()
        self._cache_max = 4

    def analyze(self, image: Image.Image) -> DamageAnalysis:
        """Run full analysis on a PIL RGB image. Raises on degenerate input."""
        if image is None or image.width < MIN_IMAGE_SIDE or image.height < MIN_IMAGE_SIDE:
            raise ValueError(
                "Image too small for inference: "
                f"{getattr(image, 'width', 0)}x{getattr(image, 'height', 0)}"
            )

        arr = np.asarray(image.convert("RGB"), dtype=np.uint8)
        key = hashlib.blake2b(arr.tobytes(), digest_size=8).digest()
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached

        result = self._analyze_array(arr)
        self._cache[key] = result
        if len(self._cache) > self._cache_max:
            self._cache.popitem(last=False)
        return result

    def _analyze_array(self, arr: np.ndarray) -> DamageAnalysis:
        h0, w0 = arr.shape[:2]
        scale = min(1.0, WORK_MAX_SIDE / float(max(h0, w0)))
        if scale < 1.0:
            work = cv2.resize(
                arr,
                (max(1, int(round(w0 * scale))), max(1, int(round(h0 * scale)))),
                interpolation=cv2.INTER_AREA,
            )
        else:
            work = arr
        wh, ww = work.shape[:2]

        gray_u8 = cv2.cvtColor(work, cv2.COLOR_RGB2GRAY)
        gray_f = gray_u8.astype(np.float32) / 255.0
        blur_u8 = cv2.GaussianBlur(gray_u8, (5, 5), 0)
        blur_f = blur_u8.astype(np.float32) / 255.0
        hp_sigma = max(4.0, HP_SIGMA_FRAC * max(ww, wh))

        # Compute global edge density for adaptive thresholding
        gx = cv2.Sobel(gray_u8.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_u8.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(gx, gy)
        global_edge_share = float((mag > 60.0).mean())

        channels = {
            "scratch": self._scratch_response(blur_u8, hp_sigma),
            "dent": self._dent_response(blur_f, hp_sigma),
            "chaos": self._chaos_response(blur_u8, hp_sigma),
            "crack": self._crack_response(blur_u8, hp_sigma),
        }
        hsv = cv2.cvtColor(work, cv2.COLOR_RGB2HSV)

        # Phase 1: per-channel candidate discovery (geometry only). Weak masks
        # are retained so Phase 2 can measure CROSS-channel corroboration
        # (e.g. a dent candidate overlapping chaos response = torn structure).
        chan_maps: dict[str, dict] = {}
        raw_cands: list[tuple] = []  # (channel, mask, x, y, w, h, area_frac)
        for channel_name, resp in channels.items():
            weak, amap, cands = self._channel_candidates(resp, wh, ww)
            chan_maps[channel_name] = {"weak": weak, "a": amap}
            raw_cands.extend([(channel_name,) + c for c in cands])

        # Check if the vehicle itself is predominantly red (prevents red paint from being mistaken for taillights)
        h_deg = hsv[..., 0].astype(np.int32)
        s_chan = hsv[..., 1].astype(np.int32)
        v_chan = hsv[..., 2].astype(np.int32)
        red_pix = ((h_deg <= 8) | (h_deg >= 172)) & (s_chan >= 70) & (v_chan >= 50)
        is_red_vehicle = float(red_pix.mean()) > 0.12

        regions: List[DamageRegion] = []
        for channel_name, mask, x, y, w, h, area_frac in raw_cands:
            region = self._build_region(
                channel_name, mask, (x, y, w, h), area_frac,
                gray_u8, hsv, wh, ww, global_edge_share, chan_maps,
                is_red_vehicle=is_red_vehicle,
            )
            if region is not None:
                regions.append(region)

        regions = self._dedupe(regions, wh, ww)
        # Vehicle-ROI guard: suppress background bits (trees/sky/asphalt)
        # lying outside or mostly outside the estimated vehicle box.
        vehicle_roi = estimate_vehicle_roi(gray_u8, hsv)
        kept_roi: List[DamageRegion] = []
        for r in regions:
            overlap = _box_overlap_frac(r.bbox_xyxy, vehicle_roi)
            x1, y1, x2, y2 = r.bbox_xyxy
            cy = (y1 + y2) / 2.0
            if cy < vehicle_roi[1] or cy > vehicle_roi[3] or overlap < 0.35:
                continue  # background region outside vehicle
            kept_roi.append(r)
        regions = kept_roi
        total_mass = sum(r.confidence * math.sqrt(max(r.area_frac, 0.0)) for r in regions)
        probability = 1.0 - math.exp(-self.prob_gain * total_mass)

        regions.sort(
            key=lambda r: r.confidence * math.sqrt(max(r.area_frac, 0.0)), reverse=True
        )
        return DamageAnalysis(
            probability=round(float(min(1.0, probability)), 4),
            regions=regions,
            work_width=ww,
            work_height=wh,
            global_edge_share=global_edge_share,
            vehicle_roi=vehicle_roi,
        )

    # Response channels ---------------------------------------------------

    def _local_anomaly(self, resp: np.ndarray, hp_sigma: float) -> np.ndarray:
        """High-pass the response: keep localized anomalies, kill diffuse texture."""
        hp = resp - cv2.GaussianBlur(resp, (0, 0), hp_sigma)
        np.clip(hp, 0.0, None, out=hp)
        m = float(hp.max())
        if m > 1e-6:
            hp /= m
        return hp

    def _scratch_response(self, blur_u8: np.ndarray, hp_sigma: float) -> np.ndarray:
        """Thin bright ridges via black top-hat across multiple orientations."""
        hh, ww = blur_u8.shape[:2]
        length = max(9, int(min(hh, ww) * 0.022))
        length = length + 1 if length % 2 == 0 else length
        best = np.zeros((hh, ww), dtype=np.float32)
        for angle in (0.0, 45.0, 90.0, 135.0):
            k = self._line_kernel(length, 3, angle)
            bh = cv2.morphologyEx(blur_u8, cv2.MORPH_BLACKHAT, k).astype(np.float32) / 255.0
            np.maximum(best, bh, out=best)
        return self._local_anomaly(best, hp_sigma)

    @staticmethod
    def _line_kernel(length: int, thickness: int, angle_deg: float) -> np.ndarray:
        size = length + 2
        k = np.zeros((size, size), dtype=np.uint8)
        cx = cy = size // 2
        rad = math.radians(angle_deg)
        dx, dy = math.cos(rad) * length / 2.0, math.sin(rad) * length / 2.0
        cv2.line(
            k,
            (int(round(cx - dx)), int(round(cy - dy))),
            (int(round(cx + dx)), int(round(cy + dy))),
            1,
            thickness,
        )
        return k

    def _dent_response(self, gray_f: np.ndarray, hp_sigma: float) -> np.ndarray:
        """Broad shading deformation via texture-gated Difference-of-Gaussians.

        The band-pass (DoG) isolates mid-scale shading variation = dents.
        Foliage/asphalt also vary at that scale, but they are *fine-textured*;
        a real dent is a smooth surface with a shading gradient. So the DoG
        amplitude is suppressed wherever fine-scale Sobel texture is high.
        """
        s = max(3.0, hp_sigma * 0.35)
        dog = np.abs(
            cv2.GaussianBlur(gray_f, (0, 0), s) - cv2.GaussianBlur(gray_f, (0, 0), s * 3.0)
        )
        # Fine texture gate: strong fine gradients => not a smooth panel.
        gx = cv2.Sobel(gray_f, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_f, cv2.CV_32F, 0, 1, ksize=3)
        fine = cv2.GaussianBlur(np.sqrt(gx * gx + gy * gy), (0, 0), 3.0)
        f90 = float(np.percentile(fine, 90.0))
        if f90 > 1e-6:
            gate = 1.0 - np.clip(fine / (2.0 * f90), 0.0, 1.0)
        else:
            gate = np.ones_like(fine)
        return dog * gate


    def _chaos_response(self, blur_u8: np.ndarray, hp_sigma: float) -> np.ndarray:
        """Local standard-deviation anomaly: shattered / exposed internals."""
        g = blur_u8.astype(np.float32) / 255.0
        mean = cv2.blur(g, (9, 9))
        mean2 = cv2.blur(g * g, (9, 9))
        std = np.sqrt(np.clip(mean2 - mean * mean, 0.0, None))
        return self._local_anomaly(std, hp_sigma)

    def _crack_response(self, blur_u8: np.ndarray, hp_sigma: float) -> np.ndarray:
        """Thin dark ridges: small morphological gradient."""
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        grad = cv2.morphologyEx(blur_u8, cv2.MORPH_GRADIENT, k).astype(np.float32) / 255.0
        return self._local_anomaly(grad, hp_sigma)

    # Region extraction ---------------------------------------------------

    def _channel_candidates(
        self, anomaly: np.ndarray, wh: int, ww: int,
    ) -> tuple:
        """Phase 1: geometry-only candidate discovery for one channel.

        Returns (weak_mask, normalized_response_a, candidates) where each
        candidate is (mask, x, y, w, h, area_frac). No gating or labeling here
        so Phase 2 can use every channel's raw response for corroboration.
        """
        positive = anomaly[anomaly > 0]
        if positive.size < 64:
            return np.zeros((wh, ww), dtype=np.uint8), np.zeros((wh, ww), dtype=np.float32), []
        # Robust peak normalization: threshold relative to the strongest
        # sustained response, not a brittle absolute scale.
        peak = float(np.percentile(positive, 99.5))
        if peak <= 1e-6:
            return np.zeros((wh, ww), dtype=np.uint8), np.zeros((wh, ww), dtype=np.float32), []
        a = np.clip(anomaly / peak, 0.0, 1.0)

        # Hysteresis: strong seeds select components; weak support defines extent.
        strong = (a >= 0.78).astype(np.uint8)
        weak = (a >= 0.40).astype(np.uint8)
        if int(weak.sum()) == 0 or int(strong.sum()) == 0:
            return np.zeros((wh, ww), dtype=np.uint8), a.astype(np.float32), []

        # Merge fragments into coherent regions.
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        weak = cv2.morphologyEx(weak, cv2.MORPH_CLOSE, k)
        weak = cv2.morphologyEx(weak, cv2.MORPH_OPEN,
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))

        n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(weak, connectivity=8)
        seed_labels = set(int(v) for v in np.unique(labels[strong.astype(bool)])) - {0}

        frame_area = float(wh * ww)
        cands: list[tuple] = []
        for idx in seed_labels:
            area = float(stats[idx, cv2.CC_STAT_AREA])
            area_frac = area / frame_area
            if area_frac < MIN_REGION_AREA_FRAC or area_frac > MAX_REGION_AREA_FRAC:
                continue
            x = float(stats[idx, cv2.CC_STAT_LEFT])
            y = float(stats[idx, cv2.CC_STAT_TOP])
            w = float(stats[idx, cv2.CC_STAT_WIDTH])
            h = float(stats[idx, cv2.CC_STAT_HEIGHT])
            if w < 3 or h < 3:
                continue
            # Border-spanning guard: global patterns (illumination gradients,
            # horizons, quantization banding) span the frame; damage does not.
            if w > 0.9 * ww or h > 0.9 * wh:
                continue
            cands.append(((labels == idx).astype(np.uint8), x, y, w, h, area_frac))
        return weak, a.astype(np.float32), cands

    # Backwards-compatible alias (older debug scripts call _extract_regions).
    def _extract_regions(self, anomaly, gray_u8, hsv, channel, wh, ww,
                         global_edge_share=0.0) -> List[DamageRegion]:
        weak, amap, cands = self._channel_candidates(anomaly, wh, ww)
        chan_maps = {channel: {"weak": weak, "a": amap}}
        out: List[DamageRegion] = []
        for mask, x, y, w, h, area_frac in cands:
            r = self._build_region(channel, mask, (x, y, w, h), area_frac,
                                   gray_u8, hsv, wh, ww, global_edge_share, chan_maps)
            if r is not None:
                out.append(r)
        return out

    @staticmethod
    def _shape_stats(mask: np.ndarray, bbox) -> tuple:
        """Elongation + thinness of a region (shared by gates and classifier)."""
        x, y, w, h = bbox
        hh, ww = mask.shape[:2]
        ys, xs = np.nonzero(mask)
        if xs.size < 8:
            return 1.0, False
        cov = np.cov(np.stack([xs.astype(np.float64), ys.astype(np.float64)]))
        eig = np.clip(np.linalg.eigvalsh(cov), 1e-6, None)
        elongation = float(math.sqrt(eig[1] / eig[0]))
        thin = min(w, h) <= max(8.0, 0.10 * max(ww, hh))
        return elongation, thin

    @staticmethod
    def _tighten_to_core(mask: np.ndarray, a: np.ndarray, bbox, wh: int, ww: int):
        """Re-localize a weak-level box onto its strong response core.

        Weak (0.40) boxes sprawl over intact paint around the defect. The
        strong (>=0.78) core + margin, clipped to the weak box, surrounds the
        actual defect more closely. Returns (mask, bbox) — originals when the
        core is too small to trust. All coordinates measured, never invented.
        """
        x, y, w, h = bbox
        core = (mask.astype(bool) & (a >= 0.78))
        if int(core.sum()) < CORE_MIN_PX:
            return mask, bbox
        ys, xs = np.nonzero(core)
        cx1, cy1 = float(xs.min()), float(ys.min())
        cx2, cy2 = float(xs.max()) + 1.0, float(ys.max()) + 1.0
        mx, my = CORE_MARGIN_FRAC * w, CORE_MARGIN_FRAC * h
        nx1, ny1 = max(x, cx1 - mx), max(y, cy1 - my)
        nx2, ny2 = min(x + w, cx2 + mx), min(y + h, cy2 + my)
        if (nx2 - nx1) * (ny2 - ny1) < CORE_MIN_FRAC * w * h:
            return mask, bbox
        ix1, iy1, ix2, iy2 = int(nx1), int(ny1), int(nx2), int(ny2)
        if ix2 - ix1 < 3 or iy2 - iy1 < 3:
            return mask, bbox
        tight = np.zeros_like(mask)
        tight[iy1:iy2, ix1:ix2] = mask[iy1:iy2, ix1:ix2]
        if int(tight.sum()) < 8:
            return mask, bbox
        return tight, (float(ix1), float(iy1), float(ix2 - ix1), float(iy2 - iy1))

    @staticmethod
    def _dark_subcore(mask: np.ndarray, gray_u8: np.ndarray):
        """Largest dark connected component inside a gated mask (cavity rescue).

        Torn cavities (mirror guts, shattered lens voids) merged with bright
        surroundings (windows, reflectors) inherit foreign statistics and die
        in texture gates. The dark torn core itself is measurable damage.
        Returns (submask, bbox) or None.
        """
        dark = ((mask.astype(bool)) & (gray_u8 < MIRROR_DARK_GRAY)).astype(np.uint8)
        if int(dark.sum()) < MIRROR_DARK_SUB_MIN_PX:
            return None
        n, lab, stats, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
        if n < 2:
            return None
        best = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        area = float(stats[best, cv2.CC_STAT_AREA])
        parent = float(max(1, int(mask.sum())))
        if area < MIRROR_DARK_SUB_MIN_PX or area < MIRROR_DARK_SUB_FRAC * parent:
            return None
        sub = (lab == best).astype(np.uint8)
        x = float(stats[best, cv2.CC_STAT_LEFT])
        y = float(stats[best, cv2.CC_STAT_TOP])
        w = float(stats[best, cv2.CC_STAT_WIDTH])
        h = float(stats[best, cv2.CC_STAT_HEIGHT])
        return sub, (x, y, w, h)

    @staticmethod
    def _cross_overlap(mask: np.ndarray, chan_maps: dict, own: str) -> float:
        """Max fraction of `mask` covered by OTHER channels' weak responses."""
        m = mask.astype(bool)
        denom = float(max(1, int(m.sum())))
        best = 0.0
        for name, maps in chan_maps.items():
            if name == own:
                continue
            other = maps["weak"].astype(bool)
            inter = float(np.logical_and(m, other).sum())
            best = max(best, inter / denom)
        return best

    def _build_region(self, channel, mask, bbox, area_frac, gray_u8, hsv,
                      wh, ww, global_edge_share, chan_maps,
                      is_red_vehicle: bool = False) -> Optional[DamageRegion]:
        """Phase 2: tighten -> evidence -> gate (+cavity rescue) -> classify."""
        x, y, w, h = bbox
        frame_area = float(wh * ww)
        amap = chan_maps[channel]["a"]

        tight_mask, tight_box = self._tighten_to_core(mask, amap, bbox, wh, ww)
        tx, ty, tw, th = tight_box
        tight_frac = float(tight_mask.sum()) / frame_area
        if tight_frac < MIN_REGION_AREA_FRAC:
            return None
        strength = float(amap[tight_mask.astype(bool)].mean()) if int(tight_mask.sum()) else 0.0
        if strength <= 0:
            return None

        elongation, thin = self._shape_stats(tight_mask, tight_box)
        evidence = self._region_evidence(hsv, gray_u8, tight_mask, wh, ww)
        y_center_rel = (ty + th / 2.0) / max(1.0, wh)
        y_top_rel = ty / max(1.0, wh)
        x_center_rel = (tx + tw / 2.0) / max(1.0, ww)
        geo = (tx, ty, tx + tw, ty + th, ww, wh, elongation)
        gate_reason = self._gate_region(
            evidence, channel, global_edge_share,
            pos=(y_center_rel, y_top_rel, tight_frac), geo=geo,
        )
        work_mask, work_box, work_frac = tight_mask, tight_box, tight_frac
        if gate_reason is not None:
            # Cavity rescue: torn dark cores merged with foreign surroundings
            # (windows/reflectors) die in texture gates; the core is measurable.
            if gate_reason == "busy_texture" and channel in ("chaos", "crack"):
                rescued = self._dark_subcore(mask, gray_u8)
                if rescued is not None:
                    submask, (sx, sy, sw, sh) = rescued
                    sub_frac = float(submask.sum()) / frame_area
                    if sub_frac >= MIN_REGION_AREA_FRAC:
                        work_mask, work_box, work_frac = submask, (sx, sy, sw, sh), sub_frac
                        elongation, thin = self._shape_stats(work_mask, work_box)
                        evidence = self._region_evidence(hsv, gray_u8, work_mask, wh, ww)
                        y_center_rel = (sy + sh / 2.0) / max(1.0, wh)
                        y_top_rel = sy / max(1.0, wh)
                        x_center_rel = (sx + sw / 2.0) / max(1.0, ww)
                        geo = (sx, sy, sx + sw, sy + sh, ww, wh, elongation)
                        gate_reason = self._gate_region(
                            evidence, channel, global_edge_share,
                            pos=(y_center_rel, y_top_rel, work_frac), geo=geo,
                        )
            if gate_reason is not None:
                return None

        cross = self._cross_overlap(work_mask, chan_maps, channel)
        label = self._classify_region(
            channel=channel,
            gray_u8=gray_u8,
            mask=work_mask,
            bbox=work_box,
            area_frac=work_frac,
            evidence=evidence,
            cross_overlap=cross,
            elongation=elongation,
            thin=thin,
            x_center_rel=x_center_rel,
            y_center_rel=y_center_rel,
            is_red_vehicle=is_red_vehicle,
        )
        if label is None:
            return None
        wx, wy, ww_, wh_ = work_box
        if self._postgate_region(
            label, evidence, elongation, thin, gray_u8, (wx, wy, wx + ww_, wy + wh_), wh, ww,
        ) is not None:
            return None

        strength = float(amap[work_mask.astype(bool)].mean())
        conf = REGION_CONF_FLOOR + (0.95 - REGION_CONF_FLOOR) * _sigmoid(
            6.0 * (strength - 0.55)
        )
        conf = round(float(min(0.97, max(REGION_CONF_FLOOR, conf))), 4)

        return DamageRegion(
            label=label,
            confidence=conf,
            bbox_xyxy=(wx, wy, wx + ww_, wy + wh_),
            polygon=self._region_polygon(work_mask, work_box),
            strength=round(strength, 5),
            area_frac=round(work_frac, 5),
            channel=channel,
            gray_mean=round(evidence.gray_mean, 1),
            gray_std=round(evidence.gray_std, 1),
        )

    @staticmethod
    def _postgate_region(label: str, ev, elongation: float, thin: bool,
                         gray_u8=None, box=None, wh: int = 0, ww: int = 0) -> Optional[str]:
        """Post-label guards (measured, label-specific).

        * trim_seam: long slivers splitting two surfaces (windshield seals,
          hood gaps) labeled scratch/glass_crack. True scratches/cracks sit
          on uniform material (homogeneous ring); seam slivers have a
          heterogeneous ring. Compact damage is never affected.
        * wheel_arch_shadow: dark dent/scratch boxes glued to the bottom
          frame corners (arches, tires, ground shadow). Tire-shaped genuine
          damage is classified flat_tire/bumper before this point, so only
          dent/scratch labels are affected.
        """
        if (
            label in ("scratch", "glass_crack")
            and elongation >= SEAM_MIN_ELONGATION
            and ev.ring_gray_std > SEAM_MAX_RING_STD
        ):
            return "trim_seam"
        if label == "dent" and ev is not None:
            # Specular reflection on intact glossy panels/hoods: smooth gradient
            # with low contrast against surrounding paint and low edge content.
            if abs(ev.gray_mean - ev.ring_gray_mean) < 14.0 and ev.gray_std < 15.0 and ev.edge_share < 0.18:
                return "specular_reflection"
        if label == "scratch" and elongation >= 2.2 and box is not None and wh > 0:
            y_center = ((box[1] + box[3]) / 2.0) / float(wh)
            if y_center > 0.65 and ev.ring_gray_std > 20.0 and abs(ev.d_sat) > 15.0:
                return "trim_seam"
        if label in ("dent", "scratch") and gray_u8 is not None and box is not None and wh > 0:
            x1, y1, x2, y2 = box
            if y2 >= ARCH_BOTTOM_FRAC * wh and (x1 <= 0.05 * ww or x2 >= 0.95 * ww):
                patch = gray_u8[max(0, int(y1)):int(y2), max(0, int(x1)):int(x2)]
                if patch.size and float(patch.mean()) < ARCH_DARK_GRAY:
                    return "wheel_arch_shadow"
        return None

    @staticmethod
    def _region_polygon(mask: np.ndarray, bbox) -> List[List[float]]:
        """Real pixel contour of the region (approximated), work-space coords."""
        x, y, w, h = bbox
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return []
        cnt = max(contours, key=cv2.contourArea)
        eps = max(2.0, 0.015 * cv2.arcLength(cnt, True))
        approx = cv2.approxPolyDP(cnt, eps, True)
        pts = [[float(p[0][0]), float(p[0][1])] for p in approx]
        if len(pts) < 3:  # fall back to the bounding rectangle corners
            pts = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
        return pts

    # Region evidence & gating -------------------------------------------

    def _region_evidence(
        self,
        hsv: np.ndarray,
        gray_u8: np.ndarray,
        mask: np.ndarray,
        wh: int,
        ww: int,
    ) -> RegionEvidence:
        """Measure how a region differs from its immediate surroundings."""
        m = mask.astype(bool)
        if not m.any():
            return RegionEvidence(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                  None, None, None, None, 0, 0)

        # Edge structure: object borders (window/taillight/frame/seam) are
        # edge-dominated; material defects are texture/shading fields with
        # only internal ridge structure.
        gx = cv2.Sobel(gray_u8, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_u8, cv2.CV_32F, 0, 1, ksize=3)
        mag = cv2.magnitude(gx, gy)
        edge_share = float((mag[m] > 60.0).mean())

        gray = gray_u8.astype(np.float32)
        gray_mean = float(gray[m].mean())
        gray_std = float(gray[m].std())

        # Context ring = dilated surroundings excluding the region itself.
        rad = max(3, int(0.04 * max(wh, ww)))
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (2 * rad + 1, 2 * rad + 1)
        )
        ring = cv2.dilate(mask, kernel).astype(bool) & ~m
        ring_gray_mean = float(gray[ring].mean()) if ring.any() else gray_mean
        ring_gray_std = float(gray[ring].std()) if ring.any() else 0.0

        s = hsv[..., 1].astype(np.float32)
        hue = hsv[..., 0].astype(np.float32) * (math.pi / 90.0)  # 0..179 -> 0..2pi

        reg_s = float(np.median(s[m]))
        ring_s = float(np.median(s[ring])) if ring.any() else reg_s

        def circ_stats(sel: np.ndarray):
            sv = s[sel]
            n = int((sv >= HUE_SAT_MIN).sum())
            if n < HUE_MIN_VOTES:
                return None, None, n
            ang = hue[sel][sv >= HUE_SAT_MIN]
            mc = float(np.mean(np.cos(ang)))
            ms = float(np.mean(np.sin(ang)))
            mean_r = math.atan2(ms, mc)
            r = max(1e-9, math.hypot(mc, ms))
            std_r = math.sqrt(max(0.0, -2.0 * math.log(r)))
            return mean_r, math.degrees(std_r), n

        reg_hue, reg_hue_std, reg_n_sat = circ_stats(m)
        ring_hue, ring_hue_std, ring_n_sat = circ_stats(ring) if ring.any() else (None, None, 0)

        # Saturated red pixels (taillight check)
        h_deg = hsv[..., 0].astype(np.int32)
        v = hsv[..., 2].astype(np.int32)
        red_pix = ((h_deg <= 8) | (h_deg >= 172)) & (s >= 70.0) & (v >= 50)
        red_frac = float(red_pix[m].mean()) if m.any() else 0.0

        return RegionEvidence(
            edge_share=edge_share,
            gray_mean=gray_mean,
            gray_std=gray_std,
            ring_gray_mean=ring_gray_mean,
            ring_gray_std=ring_gray_std,
            reg_s_med=reg_s,
            ring_s_med=ring_s,
            d_sat=reg_s - ring_s,
            reg_hue_rad=reg_hue,
            reg_hue_std_deg=reg_hue_std,
            ring_hue_rad=ring_hue,
            ring_hue_std_deg=ring_hue_std,
            ring_n_sat=ring_n_sat,
            reg_n_sat=reg_n_sat,
            red_frac=red_frac,
        )

    @staticmethod
    def _gate_region(
        ev: RegionEvidence,
        channel: str,
        global_edge_share: float = 0.0,
        pos: Optional[tuple] = None,
        geo: Optional[tuple] = None,
    ) -> Optional[str]:
        """Return a rejection reason if this blob is not a material defect.

        Each branch corresponds to a measured false-positive signature
        (annotated in ml/data/validation/annotations.json):
          * uniform_fill      - flat color fields / black bars / pad fills
          * edge_dominated    - window frames, taillights, wheel arches,
                                foliage branches, letterbox seams. Channel-aware:
                                chaos/crack channels EXPECT edges (shattered /
                                torn / ridged damage), so they use higher caps;
                                otherwise severe collision damage is suppressed.
          * busy_texture      - foliage/tint blends: saturated hues spread
                                60-120 deg vs <25 deg for same-paint damage.
                                Skipped in deep shadow (hue unreliable there).
          * context_saturation_mismatch - window glass vs surrounding paint/
                                chrome frames (|dS| 55-183 vs <25 on panels)
          * background_sky_vegetation - tiny bright bits in the top sky band
                                (tree gaps / sky highlights, not vehicle damage)
          * wheel_arch_shadow - dark boxes glued to the bottom frame corners
                                (arches, tires, ground shadow). Tire-shaped
                                regions are exempt (genuine flat_tire path).
        None = region survives (counts toward stage-1 mass and stage-3 boxes).
        pos = (y_center_rel, y_top_rel, area_frac) when known.
        geo = (x1, y1, x2, y2, frame_w, frame_h, elongation) when known.
        """
        # uniform_fill: reject only border artifacts and tiny flat regions.
        # Large uniform regions in the middle of the image can be genuine
        # smooth dents/scratches on uniform paint.
        # uniform_fill: reject only border artifacts and tiny flat regions.
        # Large uniform regions in the middle of the image can be genuine
        # smooth dents/scratches on uniform paint.
        if ev.gray_std < VARIATION_MIN_STD:
            # Check if this looks like a letterbox/pad artifact: at border AND
            # matching pad color (gray 114), or tiny region at border.
            is_border = False
            if geo is not None:
                gx1, gy1, gx2, gy2, fw, fh, _ = geo
                if gx1 <= 4 or gy1 <= 4 or gx2 >= fw - 4 or gy2 >= fh - 4:
                    is_border = True
            area_frac = pos[2] if pos else 0.0
            is_tiny = area_frac < 0.002
            is_pad_color = abs(ev.gray_mean - 114.0) < 3.0
            if (is_border and is_pad_color) or (is_border and is_tiny):
                return "uniform_fill"
        if geo is not None:
            gx1, gy1, gx2, gy2, fw, fh, elong = geo
            touches_bottom = gy2 >= ARCH_BOTTOM_FRAC * fh
            at_side = gx1 <= 0.05 * fw or gx2 >= 0.95 * fw
            tire_shaped = (
                0.7 <= elong <= 1.3
                and (pos is not None and pos[2] > 0.01)
                and (pos is not None and pos[0] > 0.75)
            )
            if (
                touches_bottom and at_side
                and ev.gray_mean < ARCH_DARK_GRAY
                and not tire_shaped
            ):
                return "wheel_arch_shadow"
        # Sky/vegetation band: background bits at the very top (tree gaps, sky highlights,
        # sky gradients touching the top of the frame).
        if pos is not None:
            y_center_rel, y_top_rel, area_frac = pos
            if y_center_rel < SKY_BAND_Y_MAX:
                if y_top_rel <= 0.02:
                    return "background_sky_vegetation"
                if area_frac < SKY_MAX_AREA_FRAC and ev.gray_mean >= SKY_BRIGHT_GRAY:
                    return "background_sky_vegetation"
        # Channel-aware edge caps: severe structural damage is edge-dense.
        # Compact fracture exception: shattered glass / spiderweb fractures produce
        # thousands of micro-fractures (edge_share 0.50-0.90) in a compact zone
        # (elongation <= 2.2), not a single long object border/seam.
        is_compact_fracture = (
            geo is not None
            and geo[6] <= 2.2
            and pos is not None
            and 0.15 <= pos[0] <= 0.70
            and ev.edge_share >= 0.50
        )
        if channel == "chaos":
            edge_thresh = CHAOS_EDGE_MAX
        elif channel == "crack" or is_compact_fracture:
            edge_thresh = CRACK_EDGE_MAX
        elif global_edge_share > HIGH_EDGE_FRAC:
            edge_thresh = EDGE_SHARE_MAX_HIGH_EDGE
        else:
            edge_thresh = EDGE_SHARE_MAX_BASE
        if ev.edge_share > edge_thresh:
            return "edge_dominated"
        if abs(ev.d_sat) > SAT_DIFF_MAX:
            return "context_saturation_mismatch"
        # Smooth pitch-black window / cabin interior shadow in dent channel is not sheet metal deformation
        if channel == "dent" and ev.gray_mean < 25.0 and ev.gray_std < 12.0 and ev.edge_share < 0.22:
            return "uniform_fill"
        # Hue is meaningless in deep shadow; dark exposed internals would be
        # wrongly rejected as "busy" because of noisy colorful reflections.
        if ev.gray_mean < DARK_HUE_SKIP_GRAY:
            return None
        if (
            ev.reg_n_sat >= HUE_MIN_VOTES
            and ev.reg_hue_std_deg is not None
            and ev.reg_hue_std_deg > HUE_STD_MAX_DEG
        ):
            return "busy_texture"
        return None

    def _mirror_evidence(
        self,
        gray_u8: np.ndarray,
        mask: np.ndarray,
        evidence: Optional[RegionEvidence],
        area_frac: float,
        x_center_rel: float,
        y_center_rel: float,
        w_frac: float,
        cross_overlap: float,
    ) -> bool:
        """Torn side-mirror assembly? Dark cavity + torn texture in mirror zone.

        Destroyed mirrors have no trained class in the folder-labeled dataset,
        so this evidence rule (validated on real mirror images) maps them to
        `broken_mirror` instead of the systematic `dent` mislabel. Zone gates
        exclude bottom strips (wheels), wide low-center intakes (grilles), and
        large panels; corroboration (other channels firing here) or extreme
        torn-dark contrast is required — never position alone.
        """
        if not (MIRROR_Y_MIN <= y_center_rel <= MIRROR_Y_MAX):
            return False
        if not (MIRROR_MIN_AREA <= area_frac <= MIRROR_MAX_AREA):
            return False
        # Side mirrors are never tall, thin vertical pillar or window-seam slivers
        ys, xs = np.nonzero(mask)
        if xs.size > 0:
            bw = float(xs.max() - xs.min() + 1)
            bh = float(ys.max() - ys.min() + 1)
            if bh / max(1.0, bw) > 2.5 and bw <= 0.12 * gray_u8.shape[1]:
                return False
        # Saturated red reflector is a taillight, never a side mirror
        if evidence is not None and evidence.red_frac >= 0.06:
            return False
        # Center of vehicle (hood / grille / fascia / windshield) is never a side mirror
        if 0.28 <= x_center_rel <= 0.72 and y_center_rel >= 0.35 and w_frac > 0.18:
            return False
        if 0.28 <= x_center_rel <= 0.72 and area_frac < 0.012:
            return False
        if 0.25 <= x_center_rel <= 0.75 and w_frac > 0.32:
            return False
        # Wide low-center boxes are grilles/intakes, not mirrors.
        if y_center_rel > 0.65 and 0.30 <= x_center_rel <= 0.70 and w_frac > 0.30:
            return False
        m = mask.astype(bool)
        if not m.any():
            return False
        gray = gray_u8.astype(np.float32)
        dark_frac = float((gray[m] < MIRROR_DARK_GRAY).mean())
        if dark_frac < MIRROR_DARK_MOD:
            return False
        std = float(gray[m].std())
        if std < MIRROR_MIN_STD:
            return False
        contrast = (evidence.ring_gray_mean - evidence.gray_mean) if evidence else 0.0
        if dark_frac >= MIRROR_DARK_EXT and contrast >= MIRROR_MIN_CONTRAST:
            return True
        return cross_overlap >= MIRROR_MIN_XCORR

    @staticmethod
    def _bright_frac(gray_u8: np.ndarray, mask: np.ndarray, thresh: float = 170.0) -> float:
        """Fraction of region pixels at/above `thresh` (shard detector).

        Shattered lamps mix bright shards with dark voids, so the region MEAN
        can sit below brightness cutoffs while shards are clearly present.
        """
        m = mask.astype(bool)
        if not m.any():
            return 0.0
        return float((gray_u8[m].astype(np.float32) >= thresh).mean())

    def _lamp_evidence(
        self,
        gray_u8: np.ndarray,
        mask: np.ndarray,
        mean_brightness: float,
        edge_share: float,
        reg_s_med: float,
        gray_std: float,
        area_frac: float,
        y_center_rel: float,
        cross_overlap: float,
        evidence=None,
        is_red_vehicle: bool = False,
        x_center_rel: Optional[float] = None,
    ) -> bool:
        """Shattered lamp (headlight/taillight): shards, torn lenses, voids.

        Lamps are mounted on the front or rear fascia / corners; they are NEVER
        located on the vehicle roof panel.
        """
        # Red reflector -> taillight lamp check.
        # Saturated red is taillight evidence on non-red vehicles (on red cars,
        # red is normal body paintwork, not a lamp reflector).
        if evidence is not None and evidence.red_frac >= 0.06:
            if not is_red_vehicle:
                # Exclude upper central roof area on non-red cars
                if not (y_center_rel < 0.30 and 0.25 <= (x_center_rel or 0.5) <= 0.75):
                    return True

        # Roof zone prevention: vehicle lamps never sit on the central roof panel
        if y_center_rel < 0.36 and (x_center_rel is None or 0.15 <= x_center_rel <= 0.85):
            return False
        if not (LAMP_Y_MIN_V2 <= y_center_rel <= LAMP_Y_MAX_V2):
            return False
        if not (LAMP_MIN_AREA_V2 <= area_frac <= LAMP_MAX_AREA_V2):
            return False

        # Shattered lens void / socket of a lamp assembly (moderate edge density inside cavity)
        if (
            mean_brightness < 60.0
            and edge_share >= 0.20
            and gray_std >= 14.0
            and reg_s_med <= LAMP_MAX_SAT
        ):
            return True
        if edge_share < LAMP_MIN_EDGE or reg_s_med > LAMP_MAX_SAT:
            return False
        if mean_brightness >= LAMP_MIN_GRAY:
            return True
        if self._bright_frac(gray_u8, mask) >= 0.25:
            return True
        if (
            mean_brightness < 60.0
            and gray_std >= 20.0
            and edge_share >= 0.30
            and evidence is not None
            and evidence.reg_n_sat >= 100
            and (evidence.reg_hue_std_deg or 0.0) >= 70.0
        ):
            return True
        return gray_std >= 30.0 and cross_overlap >= LAMP_MIN_XCORR_V2

    def _classify_region(
        self,
        channel: str,
        gray_u8: np.ndarray,
        mask: np.ndarray,
        bbox,
        area_frac: float,
        evidence: Optional[RegionEvidence] = None,
        cross_overlap: float = 0.0,
        elongation: Optional[float] = None,
        thin: Optional[bool] = None,
        x_center_rel: Optional[float] = None,
        y_center_rel: Optional[float] = None,
        is_red_vehicle: bool = False,
    ) -> Optional[str]:
        """Map a measured region to a canonical damage class (geometry + evidence-based)."""
        x, y, w, h = bbox
        hh, ww = mask.shape[:2]

        ys, xs = np.nonzero(mask)
        if xs.size < 8:
            return None
        if elongation is None or thin is None or x_center_rel is None or y_center_rel is None:
            cov = np.cov(np.stack([xs.astype(np.float64), ys.astype(np.float64)]))
            eig = np.clip(np.linalg.eigvalsh(cov), 1e-6, None)
            elongation = float(math.sqrt(eig[1] / eig[0]))
            thin = min(w, h) <= max(8.0, 0.10 * max(ww, hh))
            y_center_rel = (y + h / 2.0) / max(1.0, hh)
            x_center_rel = (x + w / 2.0) / max(1.0, ww)
        w_frac = w / max(1.0, ww)
        mean_brightness = float(gray_u8[mask.astype(bool)].mean())

        # Extract evidence features if available
        edge_share = evidence.edge_share if evidence else 0.0
        gray_std = evidence.gray_std if evidence else 0.0
        d_sat = evidence.d_sat if evidence else 0.0
        reg_s_med = evidence.reg_s_med if evidence else 0.0
        reg_hue_std = evidence.reg_hue_std_deg if evidence else None
        ring_gray_mean = evidence.ring_gray_mean if evidence else mean_brightness

        # Shattered glass spiderweb / fracture network:
        # Dense micro-cracks in a compact region in the upper/mid vehicle zone
        # (windshield / glass area). Dark shattered lamp voids (gray_mean < 80)
        # and red taillights are broken_light, not glass_crack.
        is_lamp_void = (
            self._lamp_evidence(
                gray_u8, mask, mean_brightness, edge_share, reg_s_med, gray_std,
                area_frac, y_center_rel, cross_overlap, evidence,
                is_red_vehicle=is_red_vehicle, x_center_rel=x_center_rel,
            )
            and (mean_brightness < 80.0 or (evidence is not None and not is_red_vehicle and evidence.red_frac >= 0.06))
        )
        is_glass_fracture = (
            not is_lamp_void
            and 0.15 <= y_center_rel <= 0.60
            and elongation <= 2.2
            and edge_share >= 0.50
            and gray_std >= 20.0
            and (evidence is None or (evidence.reg_s_med <= 45.0 and (is_red_vehicle or evidence.red_frac < 0.15)))
        )
        is_corner_lamp = (x_center_rel <= 0.25 or x_center_rel >= 0.75) and y_center_rel >= 0.45

        # --- SCRATCH channel: thin bright ridges (scratches, paint lines) ---
        if channel == "scratch":
            if is_glass_fracture and not is_corner_lamp:
                return "glass_crack"
            # Strong elongation or thinness -> scratch
            if elongation >= 2.2 or thin:
                return "scratch"
            # Small compact region on panel -> could be dent or stone chip
            if area_frac < 0.02:
                return "dent"
            return "dent" if area_frac < 0.10 else "bumper_smash"

        # --- DENT channel: broad shading deformation (dents, creases) ---
        if channel == "dent":
            if is_glass_fracture and not is_corner_lamp:
                return "glass_crack"
            # Structural lower-zone deformation -> bumper_smash.
            # Bumper requires lower fascia (y > 0.65) and structural texture (not smooth interior shadow).
            if (
                area_frac >= BUMPER_SMASH_MIN_AREA_DENT
                and y_center_rel > 0.65
                and (mean_brightness >= 25.0 or gray_std >= 14.0)
            ):
                return "bumper_smash"
            # Shattered-lamp fragments also surface in the dent channel (lens
            # voids read as shading deformation). Lamp before mirror.
            if self._lamp_evidence(
                gray_u8, mask, mean_brightness, edge_share, reg_s_med, gray_std,
                area_frac, y_center_rel, cross_overlap, evidence,
                is_red_vehicle=is_red_vehicle, x_center_rel=x_center_rel,
            ):
                return "broken_light"
            # Torn mirror assembly (dark cavity + torn texture + corroboration).
            if self._mirror_evidence(
                gray_u8, mask, evidence, area_frac,
                x_center_rel, y_center_rel, w_frac, cross_overlap,
            ):
                return "broken_mirror"
            # Elongated horizontal region on lower half -> possible bumper scrape
            if elongation >= 1.8 and y_center_rel > 0.55 and thin:
                return "scratch"
            # Compact region with moderate elongation -> dent
            if 1.3 <= elongation < 2.2:
                return "dent"
            # Very compact region -> dent
            return "dent"

        # --- CHAOS channel: local std-dev anomaly (shattered, broken components) ---
        if channel == "chaos":
            if is_glass_fracture and not is_corner_lamp:
                return "glass_crack"
            # Structural lower-zone chaos -> bumper_smash (fragment-tolerant).
            if (
                area_frac >= BUMPER_SMASH_MIN_AREA_CHAOS
                and y_center_rel > 0.65
                and (mean_brightness >= 25.0 or gray_std >= 14.0)
            ):
                return "bumper_smash"

            # Small very bright region -> broken_light (headlight/taillight)
            if mean_brightness >= 170.0 and area_frac < 0.08 and not is_red_vehicle:
                return "broken_light"
            # Shattered-lamp rule: bright, edge-dense, mid-height fragments are
            # broken headlights even when small (front-collision regression).
            if (
                LAMP_MIN_AREA_FRAC <= area_frac <= LAMP_MAX_AREA_FRAC
                and LAMP_Y_MIN <= y_center_rel <= LAMP_Y_MAX
                and mean_brightness >= LAMP_MIN_GRAY
                and edge_share >= LAMP_MIN_EDGE
                and reg_s_med <= LAMP_MAX_SAT
            ):
                return "broken_light"
            # Torn-lens rule (v2): bright shards, dark voids with shard chroma,
            # or corroborated torn fragments are shattered lamps, not dents.
            # Lamp precedence over mirror: lamp-band fragments are evaluated
            # here first so headlight voids never become "mirror".
            if self._lamp_evidence(
                gray_u8, mask, mean_brightness, edge_share, reg_s_med, gray_std,
                area_frac, y_center_rel, cross_overlap, evidence,
                is_red_vehicle=is_red_vehicle, x_center_rel=x_center_rel,
            ):
                return "broken_light"
            # Torn mirror assembly in the chaos channel.
            if self._mirror_evidence(
                gray_u8, mask, evidence, area_frac,
                x_center_rel, y_center_rel, w_frac, cross_overlap,
            ):
                return "broken_mirror"
            # Elongated non-thin region -> diffuse specular reflection across panel
            if elongation >= 2.5 and not thin:
                return None
            # Elongated thin region -> scratch
            if elongation >= 2.5 and thin:
                return "scratch"
            # Circular/oval region at bottom -> flat_tire (tire sidewall damage)
            if 0.7 <= elongation <= 1.3 and y_center_rel > 0.75 and area_frac > 0.01:
                return "flat_tire"
            # High edge share + low saturation in compact zone -> broken component
            if edge_share > 0.5 and reg_s_med < 50 and elongation <= 2.2 and not thin and not is_red_vehicle:
                return "broken_light"
            return "dent"

        # --- CRACK channel: thin dark ridges (glass cracks, panel creases) ---
        if channel == "crack":
            if is_glass_fracture and not is_corner_lamp:
                return "glass_crack"
            # Dark, low-saturation glass context -> glass_crack (windshield/side glass).
            # Requires: very dark region + very low saturation + region darker than
            # surroundings (tinted glass effect). Dark paint fails the tint check
            # (paint is uniform, glass is darker than its frame/seal surroundings).
            # When in doubt, label as scratch (panel crease) — never guess glass.
            if (
                evidence is not None
                and evidence.gray_mean <= GLASS_GRAY_MAX
                and evidence.ring_gray_mean <= GLASS_RING_GRAY_MAX
                and evidence.reg_s_med <= GLASS_SAT_MAX
                and (evidence.ring_gray_mean - evidence.gray_mean) >= GLASS_DARKER_THAN_RING
            ):
                return "glass_crack"
            # Shattered-lamp fragments also fire the crack channel (bright ridges
            # around broken lamp assemblies) -> broken_light before panel fallback.
            if (
                evidence is not None
                and LAMP_MIN_AREA_FRAC <= area_frac <= LAMP_MAX_AREA_FRAC
                and LAMP_Y_MIN <= y_center_rel <= LAMP_Y_MAX
                and mean_brightness >= LAMP_MIN_GRAY
                and edge_share >= LAMP_MIN_EDGE
                and reg_s_med <= LAMP_MAX_SAT
            ):
                return "broken_light"
            if self._lamp_evidence(
                gray_u8, mask, mean_brightness, edge_share, reg_s_med, gray_std,
                area_frac, y_center_rel, cross_overlap, evidence,
                is_red_vehicle=is_red_vehicle, x_center_rel=x_center_rel,
            ):
                return "broken_light"
            # Torn mirror splinters in the crack channel.
            if self._mirror_evidence(
                gray_u8, mask, evidence, area_frac,
                x_center_rel, y_center_rel, w_frac, cross_overlap,
            ):
                return "broken_mirror"
            # Elongated thin region -> scratch (panel crease)
            if elongation >= 2.2 or thin:
                return "scratch"
            # Compact region -> dent
            return "dent"

        return None

    @staticmethod
    def _dedupe(regions: List[DamageRegion], wh: int = 768, ww: int = 768) -> List[DamageRegion]:
        """Single suppression stage for all channels (the pipeline must not
        run a second NMS on top of this).

        Rules, applied strongest-first, class-agnostic so one physical defect
        never shows up as overlapping "dent + scratch + glass_crack" boxes:
          * IoU > 0.30 with an kept region  -> duplicate response of same blob
          * IoM (inter/min-area) > 0.40      -> nested duplicate: a smaller
            fragment fully inside a kept region (IoU can be < 0.30 there)
          * Adjacent-fragment suppression: a TINY region (area_frac < 0.006)
            within a few pixels of a kept LARGER structural box of related
            class is the same shattered component (torn bumper / lamp shards),
            not a separate validated instance.
          * Same-label shatter merge: two TINY boxes (area_frac < 0.008 each)
            of the SAME label within 3% of frame side are shards of one defect
            (e.g. triple boxes on a single headlight); keep the stronger one.
          * Nested dark-core preference: a smaller nested box that is MUCH
            darker and more torn than the bright smooth box containing it is
            the actual defect (torn cavity inside a broad shading response on
            intact paint); it replaces the outer box instead of dying as a
            "duplicate". Measured on both sides, never positional.
          * Boundary artifact rejection: thin strips at image edges
            (window frames, A-pillars, door seals, seams) are not damage.
        """

        def iou(a, b) -> float:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            ix1, iy1 = max(ax1, bx1), max(ay1, by1)
            ix2, iy2 = min(ax2, bx2), min(ay2, by2)
            inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            if inter <= 0:
                return 0.0
            union = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
            return inter / union if union > 0 else 0.0

        def iom(a, b) -> float:
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            ix1, iy1 = max(ax1, bx1), max(ay1, by1)
            ix2, iy2 = min(ax2, bx2), min(ay2, by2)
            inter = max(0.0, ix2 - ix1) * max(0.0, iy2 - iy1)
            if inter <= 0:
                return 0.0
            aa = (ax2 - ax1) * (ay2 - ay1)
            bb = (bx2 - bx1) * (by2 - by1)
            small = min(aa, bb)
            return inter / small if small > 0 else 0.0

        def is_boundary_artifact(box, work_w, work_h) -> bool:
            """Check if a region is a likely boundary artifact at image edges."""
            x1, y1, x2, y2 = box
            w = x2 - x1
            h = y2 - y1
            # Very thin vertical line at left/right edge
            if w <= 10 and (x1 <= 10 or x2 >= work_w - 10):
                return True
            # Very thin horizontal line at top/bottom edge
            if h <= 10 and (y1 <= 10 or y2 >= work_h - 10):
                return True
            # Tall thin strip hugging the left/right frame (window frames,
            # A-pillars, door seals, seams): genuine damage is never a sliver
            # glued to the image border.
            if (
                w <= 0.07 * work_w
                and (x1 <= 6 or x2 >= work_w - 6)
                and h > 0
                and (h / max(1.0, w)) > 3.0
            ):
                return True
            # Any narrow strip flush against the left/right frame (door edge
            # seals, handle recesses) is trim, not damage.
            if w <= 0.10 * work_w and (x1 <= 4 or x2 >= work_w - 4):
                return True
            return False

        STRUCTURAL = {"dent", "scratch", "bumper_smash", "broken_light", "broken_mirror", "glass_crack"}

        def gap(a, b) -> float:
            """Edge-to-edge gap between boxes (0 when touching/overlapping)."""
            ax1, ay1, ax2, ay2 = a
            bx1, by1, bx2, by2 = b
            dx = max(0.0, max(bx1 - ax2, ax1 - bx2))
            dy = max(0.0, max(by1 - ay2, ay1 - by2))
            return math.hypot(dx, dy)

        # Reject boundary artifacts upfront so border strips never seed consolidation
        regions = [r for r in regions if not is_boundary_artifact(r.bbox_xyxy, ww, wh)]

        # Consolidate mirror assembly casing: if a broken mirror cavity is
        # identified, adjacent housing dents/scratches on that mirror are part of
        # the broken mirror assembly, not separate panel dents on the hood/fender.
        has_mirror = any(r.label == "broken_mirror" for r in regions)
        if has_mirror:
            mirror_boxes = [r.bbox_xyxy for r in regions if r.label == "broken_mirror"]
            for r in regions:
                if r.label in ("dent", "scratch"):
                    if any(gap(r.bbox_xyxy, mbox) <= 0.16 * max(ww, wh) for mbox in mirror_boxes):
                        r.label = "broken_mirror"

        # Consolidate shattered glass fracture: if a primary glass crack is identified,
        # adjacent small shards/scratches on that windshield are part of the shattered
        # glass network, not separate panel defects.
        has_glass = any(r.label == "glass_crack" and r.confidence >= 0.70 for r in regions)
        if has_glass:
            glass_boxes = [r.bbox_xyxy for r in regions if r.label == "glass_crack" and r.confidence >= 0.70]
            for r in regions:
                if r.label in ("dent", "scratch", "broken_light") and r.area_frac < 0.015:
                    if any(gap(r.bbox_xyxy, gbox) <= 0.16 * max(ww, wh) for gbox in glass_boxes):
                        r.label = "glass_crack"

        # Consolidate broken light fragments: if a confirmed broken light is identified,
        # adjacent tiny shards/creases on the lens/housing are part of the
        # broken lamp assembly.
        has_lamp = any(r.label == "broken_light" and r.confidence >= 0.70 for r in regions)
        if has_lamp:
            lamp_boxes = [r.bbox_xyxy for r in regions if r.label == "broken_light" and r.confidence >= 0.70]
            for r in regions:
                if r.label in ("dent", "scratch", "glass_crack") and r.area_frac < 0.005:
                    if any(gap(r.bbox_xyxy, lbox) <= 0.16 * max(ww, wh) for lbox in lamp_boxes):
                        r.label = "broken_light"

        # Structural severity ordering: major defects take precedence over minor cosmetic dents
        CLASS_SEVERITY_ORDER = {
            "bumper_smash": 6,
            "glass_crack": 6,
            "broken_light": 5,
            "broken_mirror": 5,
            "flat_tire": 3,
            "dent": 2,
            "scratch": 1,
        }

        kept: List[DamageRegion] = []
        for r in sorted(
            regions,
            key=lambda z: (
                CLASS_SEVERITY_ORDER.get(z.label, 0),
                z.confidence * math.sqrt(max(z.area_frac, 0.0)),
            ),
            reverse=True,
        ):
            # Reject boundary artifacts
            if is_boundary_artifact(r.bbox_xyxy, ww, wh):
                continue
            dup = False
            for oi, o in enumerate(kept):
                if iou(r.bbox_xyxy, o.bbox_xyxy) > 0.30 or iom(r.bbox_xyxy, o.bbox_xyxy) > 0.35:
                    # Nested dark-core preference BEFORE declaring a duplicate:
                    # a much darker, more torn nested box is the defect itself
                    # (cavity), while the bright smooth outer box is broad
                    # shading response over intact paint around it.
                    if (
                        r.label in STRUCTURAL
                        and o.label in STRUCTURAL
                        and iom(r.bbox_xyxy, o.bbox_xyxy) > 0.40
                        and o.gray_mean - r.gray_mean >= 60.0
                        and r.gray_std > o.gray_std
                        and o.gray_mean >= 150.0
                    ):
                        kept[oi] = r
                    dup = True
                    break
                # Adjacent tiny fragment near an existing structural defect
                # (e.g. tiny shard or crack near broken light / bumper / mirror).
                if (
                    r.area_frac < 0.012
                    and gap(r.bbox_xyxy, o.bbox_xyxy) <= 0.08 * max(ww, wh)
                ):
                    if o.label in ("broken_light", "broken_mirror", "bumper_smash"):
                        dup = True
                        break
                # Same-label shatter merge: two small shards side by side are one
                # defect (e.g. multiple shards on a single headlight or mirror).
                if (
                    r.label == o.label
                    and r.area_frac < 0.018
                    and o.area_frac < 0.018
                    and gap(r.bbox_xyxy, o.bbox_xyxy) <= 0.12 * max(ww, wh)
                ):
                    dup = True
                    break
            if dup:
                continue
            kept.append(r)
            if len(kept) >= 12:  # hard cap: a panel never shows dozens of separate marks
                break
        return kept



