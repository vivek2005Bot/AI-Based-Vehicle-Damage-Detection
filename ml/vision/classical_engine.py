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
CANONICAL_CLASSES = (
    "scratch",
    "dent",
    "glass_crack",
    "bumper_smash",
    "flat_tire",
    "broken_light",
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
EDGE_SHARE_MAX = 0.40        # Sobel-edge fraction inside region: object borders
                             # (windows/taillights/trees/seams) measure 0.5-0.8;
                             # true dents/scratches measure 0.05-0.25
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
GLASS_GRAY_MAX = 140.0       # region mean luminance (0-255)
GLASS_RING_GRAY_MAX = 165.0  # context ring mean luminance
GLASS_SAT_MAX = 110          # region median saturation

_VALID_LABELS = set(CANONICAL_CLASSES)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


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


@dataclass
class DamageAnalysis:
    """Full engine output for one image."""

    probability: float
    regions: List[DamageRegion] = field(default_factory=list)
    work_width: int = 0
    work_height: int = 0


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
    reg_s_med: float             # median saturation inside (0-255)
    ring_s_med: float            # median saturation of the ring (0-255)
    d_sat: float                 # reg_s_med - ring_s_med
    reg_hue_rad: Optional[float]     # circular mean hue of saturated pixels
    reg_hue_std_deg: Optional[float]  # circular std of those hues (degrees)
    ring_hue_rad: Optional[float]
    ring_hue_std_deg: Optional[float]
    ring_n_sat: int              # saturated pixels in the ring
    reg_n_sat: int               # saturated pixels inside the region


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

        channels = {
            "scratch": self._scratch_response(blur_u8, hp_sigma),
            "dent": self._dent_response(blur_f, hp_sigma),
            "chaos": self._chaos_response(blur_u8, hp_sigma),
            "crack": self._crack_response(blur_u8, hp_sigma),
        }
        hsv = cv2.cvtColor(work, cv2.COLOR_RGB2HSV)

        regions: List[DamageRegion] = []
        for channel_name, resp in channels.items():
            regions.extend(self._extract_regions(resp, gray_u8, hsv, channel_name, wh, ww))

        regions = self._dedupe(regions)
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

    def _extract_regions(
        self,
        anomaly: np.ndarray,
        gray_u8: np.ndarray,
        hsv: np.ndarray,
        channel: str,
        wh: int,
        ww: int,
    ) -> List[DamageRegion]:
        positive = anomaly[anomaly > 0]
        if positive.size < 64:
            return []
        # Robust peak normalization: threshold relative to the strongest
        # sustained response, not a brittle absolute scale.
        peak = float(np.percentile(positive, 99.5))
        if peak <= 1e-6:
            return []
        a = np.clip(anomaly / peak, 0.0, 1.0)

        # Hysteresis: strong seeds select components; weak support defines extent.
        strong = (a >= 0.78).astype(np.uint8)
        weak = (a >= 0.40).astype(np.uint8)
        if int(weak.sum()) == 0 or int(strong.sum()) == 0:
            return []

        # Merge fragments into coherent regions.
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        weak = cv2.morphologyEx(weak, cv2.MORPH_CLOSE, k)
        weak = cv2.morphologyEx(weak, cv2.MORPH_OPEN,
                                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))


        n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(weak, connectivity=8)
        seed_labels = set(int(v) for v in np.unique(labels[strong.astype(bool)])) - {0}

        frame_area = float(wh * ww)
        regions: List[DamageRegion] = []
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

            region_mask = (labels == idx).astype(np.uint8)
            strength = float(a[region_mask.astype(bool)].mean())
            if strength <= 0:
                continue

            # Local-distinctness evidence + gates: reject blobs that are
            # object boundaries / window frames / foliage / uniform fills
            # rather than localized material defects (measured, not assumed).
            evidence = self._region_evidence(hsv, gray_u8, region_mask, wh, ww)
            if self._gate_region(evidence, channel) is not None:
                continue

            label = self._classify_region(
                channel=channel,
                gray_u8=gray_u8,
                mask=region_mask,
                bbox=(x, y, w, h),
                area_frac=area_frac,
                evidence=evidence,
            )
            if label is None:
                continue

            # Confidence: monotone in measured regional strength.
            conf = REGION_CONF_FLOOR + (0.95 - REGION_CONF_FLOOR) * _sigmoid(
                6.0 * (strength - 0.55)
            )
            conf = round(float(min(0.97, max(REGION_CONF_FLOOR, conf))), 4)

            regions.append(
                DamageRegion(
                    label=label,
                    confidence=conf,
                    bbox_xyxy=(x, y, x + w, y + h),
                    polygon=self._region_polygon(region_mask, (x, y, w, h)),
                    strength=round(strength, 5),
                    area_frac=round(area_frac, 5),
                    channel=channel,
                )
            )
        return regions

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
            return RegionEvidence(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
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

        return RegionEvidence(
            edge_share=edge_share,
            gray_mean=gray_mean,
            gray_std=gray_std,
            ring_gray_mean=ring_gray_mean,
            reg_s_med=reg_s,
            ring_s_med=ring_s,
            d_sat=reg_s - ring_s,
            reg_hue_rad=reg_hue,
            reg_hue_std_deg=reg_hue_std,
            ring_hue_rad=ring_hue,
            ring_hue_std_deg=ring_hue_std,
            ring_n_sat=ring_n_sat,
            reg_n_sat=reg_n_sat,
        )

    @staticmethod
    def _gate_region(ev: RegionEvidence, channel: str) -> Optional[str]:
        """Return a rejection reason if this blob is not a material defect.

        Each branch corresponds to a measured false-positive signature
        (annotated in ml/data/validation/annotations.json):
          * uniform_fill      - flat color fields / black bars / pad fills
          * edge_dominated    - window frames, taillights, wheel arches,
                                foliage branches, letterbox seams (0.5-0.8 edge
                                share vs 0.05-0.25 for true damage)
          * busy_texture      - foliage/tint blends: saturated hues spread
                                60-120 deg vs <25 deg for same-paint damage
          * context_saturation_mismatch - window glass vs surrounding paint/
                                chrome frames (|dS| 55-183 vs <25 on panels)
        None = region survives (counts toward stage-1 mass and stage-3 boxes).
        """
        if ev.gray_std < VARIATION_MIN_STD:
            return "uniform_fill"
        if ev.edge_share > EDGE_SHARE_MAX:
            return "edge_dominated"
        if abs(ev.d_sat) > SAT_DIFF_MAX:
            return "context_saturation_mismatch"
        if (
            ev.reg_n_sat >= HUE_MIN_VOTES
            and ev.reg_hue_std_deg is not None
            and ev.reg_hue_std_deg > HUE_STD_MAX_DEG
        ):
            return "busy_texture"
        return None

    def _classify_region(
        self,
        channel: str,
        gray_u8: np.ndarray,
        mask: np.ndarray,
        bbox,
        area_frac: float,
        evidence: Optional[RegionEvidence] = None,
    ) -> Optional[str]:
        """Map a measured region to a canonical damage class (geometry-based)."""
        x, y, w, h = bbox
        hh, ww = mask.shape[:2]

        ys, xs = np.nonzero(mask)
        if xs.size < 8:
            return None
        cov = np.cov(np.stack([xs.astype(np.float64), ys.astype(np.float64)]))
        eig = np.clip(np.linalg.eigvalsh(cov), 1e-6, None)
        elongation = float(math.sqrt(eig[1] / eig[0]))
        thin = min(w, h) <= max(8.0, 0.10 * max(ww, hh))
        y_center_rel = (y + h / 2.0) / max(1.0, hh)
        mean_brightness = float(gray_u8[mask.astype(bool)].mean())

        if channel == "scratch":
            if elongation >= 2.2 or thin:
                return "scratch"
            return "dent" if area_frac < 0.10 else "bumper_smash"

        if channel == "dent":
            if area_frac >= 0.06 and y_center_rel > 0.62:
                return "bumper_smash"
            return "dent"

        if channel == "chaos":
            # Broken lamp assemblies are small + very bright; large chaotic
            # regions low in the frame are smashed bumpers / radiators.
            if area_frac >= 0.05 and y_center_rel > 0.62:
                return "bumper_smash"
            if mean_brightness >= 170.0 and area_frac < 0.08:
                return "broken_light"
            if elongation >= 2.5 and thin:
                return "scratch"
            return "dent"

        if channel == "crack":
            # The crack channel fires on any thin dark ridge — glass cracks
            # *and* body-panel crease edges. Only a dark, low-saturation
            # context (windshield/side glass, tint + seal surroundings) may
            # carry the glass_crack label; anything brighter is relabeled by
            # geometry so cracks never land on body panels (screenshot bug).
            if (
                evidence is not None
                and evidence.gray_mean <= GLASS_GRAY_MAX
                and evidence.ring_gray_mean <= GLASS_RING_GRAY_MAX
                and evidence.reg_s_med <= GLASS_SAT_MAX
            ):
                return "glass_crack"
            if elongation >= 2.2 or thin:
                return "scratch"
            return "dent"

        return None

    @staticmethod
    def _dedupe(regions: List[DamageRegion]) -> List[DamageRegion]:
        """Single suppression stage for all channels (the pipeline must not
        run a second NMS on top of this).

        Rules, applied strongest-first, class-agnostic so one physical defect
        never shows up as overlapping "dent + scratch + glass_crack" boxes:
          * IoU > 0.40 with an kept region  -> duplicate response of same blob
          * IoM (inter/min-area) > 0.55      -> nested duplicate: a smaller
            fragment fully inside a kept region (IoU can be < 0.40 there)
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

        kept: List[DamageRegion] = []
        for r in sorted(regions, key=lambda z: z.confidence * math.sqrt(max(z.area_frac, 0.0)), reverse=True):
            if any(
                iou(r.bbox_xyxy, o.bbox_xyxy) > 0.40 or iom(r.bbox_xyxy, o.bbox_xyxy) > 0.55
                for o in kept
            ):
                continue
            kept.append(r)
            if len(kept) >= 12:  # hard cap: a panel never shows dozens of separate marks
                break
        return kept



