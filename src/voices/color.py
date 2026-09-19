from __future__ import annotations

import colorsys

import numpy as np

from .models import AcousticFeatures, ColoredWord, VoiceProfile, WordTiming
from .pitch import hz_to_note, semitone_delta


def _clamp(value: float, low: float, high: float) -> float:
    return float(np.clip(value, low, high))


def hsl_to_hex(h: float, s: float, l: float) -> str:
    r, g, b = colorsys.hls_to_rgb(
        (h % 360.0) / 360.0,
        l / 100.0,
        s / 100.0,
    )
    return "#{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


class ColorEngine:
    """Map a stable voice profile + local acoustics to visual text style."""

    def color_word(
        self,
        word: WordTiming,
        local: AcousticFeatures,
        profile: VoiceProfile,
    ) -> ColoredWord:
        f0 = local.f0_hz or profile.median_f0_hz
        delta = semitone_delta(f0, profile.median_f0_hz)

        hue = (profile.base_hue + _clamp(delta * 2.8, -18.0, 18.0)) % 360.0
        saturation = _clamp(
            profile.base_saturation
            + 16.0 * (local.harmonicity - profile.harmonicity)
            - 10.0 * local.spectral_flatness,
            28.0,
            96.0,
        )

        energy = _clamp(local.rms / 0.22, 0.0, 1.0)
        pitch_lift = _clamp(delta / 12.0, -1.0, 1.0)
        lightness = _clamp(
            profile.base_lightness + 8.0 * pitch_lift + 8.0 * (energy - 0.5),
            24.0,
            78.0,
        )

        breathiness = _clamp(local.spectral_flatness * 1.6, 0.0, 1.0)
        opacity = _clamp(1.0 - 0.30 * breathiness, 0.58, 1.0)
        font_weight = int(
            round(_clamp(430 + 280 * profile.depth + 130 * energy, 350, 850) / 50) * 50
        )
        glow_px = _clamp(1.0 + 8.0 * local.harmonicity, 0.0, 9.0)
        roughness = _clamp(
            (1.0 - local.harmonicity) * 0.55 + local.spectral_flatness * 0.45,
            0.0,
            1.0,
        )

        note, _, cents = hz_to_note(f0)
        return ColoredWord(
            text=word.text,
            start=word.start,
            end=word.end,
            color=hsl_to_hex(hue, saturation, lightness),
            hue=hue,
            saturation=saturation,
            lightness=lightness,
            opacity=opacity,
            font_weight=font_weight,
            glow_px=glow_px,
            roughness=roughness,
            note=note,
            cents=cents,
        )
