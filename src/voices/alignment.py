from __future__ import annotations

from dataclasses import replace

import numpy as np

from .models import AcousticFeatures, WordTiming


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def summarize_features_for_word(
    word: WordTiming,
    features: list[AcousticFeatures],
) -> AcousticFeatures:
    candidates = [
        f
        for f in features
        if _overlap(word.start, word.end, f.start, f.end) > 0
    ]
    if not candidates:
        if not features:
            raise ValueError("no acoustic frames available")
        center = (word.start + word.end) / 2.0
        candidates = [
            min(
                features,
                key=lambda f: abs(((f.start + f.end) / 2.0) - center),
            )
        ]

    weights = np.asarray(
        [_overlap(word.start, word.end, f.start, f.end) for f in candidates],
        dtype=float,
    )
    if float(weights.sum()) <= 0:
        weights = np.ones(len(candidates), dtype=float)
    weights /= weights.sum()

    def avg(name: str) -> float:
        return float(
            np.sum([getattr(f, name) * w for f, w in zip(candidates, weights)])
        )

    f0_pairs = [
        (f.f0_hz, w)
        for f, w in zip(candidates, weights)
        if f.f0_hz is not None
    ]
    f0 = None
    if f0_pairs:
        values = np.asarray([x for x, _ in f0_pairs], dtype=float)
        f0_weights = np.asarray([w for _, w in f0_pairs], dtype=float)
        f0 = float(np.sum(values * f0_weights) / np.sum(f0_weights))

    strongest = max(candidates, key=lambda f: f.rms)
    first = candidates[0]
    return replace(
        first,
        start=word.start,
        end=word.end,
        f0_hz=f0,
        rms=avg("rms"),
        spectral_centroid_hz=avg("spectral_centroid_hz"),
        spectral_flatness=avg("spectral_flatness"),
        harmonicity=avg("harmonicity"),
        low_frequency_energy=avg("low_frequency_energy"),
        formants_hz=strongest.formants_hz,
        mfcc=strongest.mfcc,
    )
