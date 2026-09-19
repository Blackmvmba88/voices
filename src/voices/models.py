from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AcousticFeatures:
    start: float
    end: float
    f0_hz: float | None
    rms: float
    spectral_centroid_hz: float
    spectral_flatness: float
    harmonicity: float
    low_frequency_energy: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class VoiceProfile:
    median_f0_hz: float
    pitch_low_hz: float
    pitch_high_hz: float
    brightness: float
    harmonicity: float
    depth: float
    base_hue: float
    base_saturation: float
    base_lightness: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WordTiming:
    text: str
    start: float
    end: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ColoredWord:
    text: str
    start: float
    end: float
    color: str
    hue: float
    saturation: float
    lightness: float
    opacity: float
    font_weight: int
    glow_px: float
    roughness: float
    note: str | None = None
    cents: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
