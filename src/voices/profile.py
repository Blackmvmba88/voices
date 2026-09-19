from __future__ import annotations

import numpy as np

from .models import AcousticFeatures, VoiceProfile


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _interp_palette(score: float) -> float:
    """Deep/acoustically dark -> green; bright/light -> magenta.

    Intermediate voices pass through cyan and violet rather than jumping between
    unrelated colors. This is an intentionally designed visual mapping, not a
    classifier for sex, gender or identity.
    """
    anchors = ((0.0, 120.0), (0.35, 185.0), (0.68, 255.0), (1.0, 325.0))
    x = _clip01(score)
    for (x0, h0), (x1, h1) in zip(anchors, anchors[1:]):
        if x <= x1:
            t = (x - x0) / (x1 - x0)
            return h0 + t * (h1 - h0)
    return anchors[-1][1]


def build_voice_profile(features: list[AcousticFeatures]) -> VoiceProfile:
    voiced = [f for f in features if f.f0_hz is not None and f.harmonicity >= 0.15]
    source = voiced or features
    if not source:
        raise ValueError("at least one acoustic frame is required")

    f0s = np.asarray([f.f0_hz for f in voiced], dtype=float) if voiced else np.asarray([140.0])
    centroids = np.asarray([f.spectral_centroid_hz for f in source], dtype=float)
    harmonics = np.asarray([f.harmonicity for f in source], dtype=float)
    lows = np.asarray([f.low_frequency_energy for f in source], dtype=float)

    median_f0 = float(np.median(f0s))
    low_f0 = float(np.percentile(f0s, 10))
    high_f0 = float(np.percentile(f0s, 90))

    register = _clip01(
        (np.log2(median_f0) - np.log2(70.0))
        / (np.log2(350.0) - np.log2(70.0))
    )
    brightness = _clip01(float(np.median(centroids)) / 3500.0)
    harmonicity = _clip01(float(np.median(harmonics)))
    depth = _clip01(0.65 * float(np.median(lows)) + 0.35 * (1.0 - register))

    character = _clip01(0.52 * register + 0.30 * brightness + 0.18 * (1.0 - depth))
    base_hue = _interp_palette(character)
    base_saturation = 48.0 + 42.0 * harmonicity
    base_lightness = 40.0 + 20.0 * (1.0 - depth) + 6.0 * brightness

    return VoiceProfile(
        median_f0_hz=median_f0,
        pitch_low_hz=low_f0,
        pitch_high_hz=high_f0,
        brightness=brightness,
        harmonicity=harmonicity,
        depth=depth,
        base_hue=base_hue,
        base_saturation=float(np.clip(base_saturation, 30.0, 95.0)),
        base_lightness=float(np.clip(base_lightness, 28.0, 72.0)),
    )
