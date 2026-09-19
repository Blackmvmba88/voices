from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .models import AcousticFeatures


@dataclass
class AcousticAnalyzer:
    sample_rate: int = 16000
    frame_ms: float = 40.0
    hop_ms: float = 20.0
    f0_min_hz: float = 60.0
    f0_max_hz: float = 500.0

    def analyze(self, samples: np.ndarray) -> list[AcousticFeatures]:
        signal = np.asarray(samples, dtype=np.float64)
        if signal.ndim != 1:
            raise ValueError("samples must be mono")
        if signal.size == 0:
            return []

        peak = float(np.max(np.abs(signal)))
        if peak > 1.0:
            signal = signal / peak

        frame_size = max(32, int(self.sample_rate * self.frame_ms / 1000.0))
        hop_size = max(1, int(self.sample_rate * self.hop_ms / 1000.0))
        window = np.hanning(frame_size)
        features: list[AcousticFeatures] = []

        for start_idx in range(0, max(1, signal.size - frame_size + 1), hop_size):
            frame = signal[start_idx : start_idx + frame_size]
            if frame.size < frame_size:
                frame = np.pad(frame, (0, frame_size - frame.size))
            features.append(self._analyze_frame(frame * window, start_idx / self.sample_rate))
        return features

    def _analyze_frame(self, frame: np.ndarray, start: float) -> AcousticFeatures:
        eps = 1e-12
        duration = frame.size / self.sample_rate
        rms = float(np.sqrt(np.mean(frame * frame) + eps))

        spectrum = np.abs(np.fft.rfft(frame)) + eps
        freqs = np.fft.rfftfreq(frame.size, 1.0 / self.sample_rate)
        power = spectrum * spectrum
        power_sum = float(np.sum(power)) + eps
        centroid = float(np.sum(freqs * power) / power_sum)
        flatness = float(np.exp(np.mean(np.log(spectrum))) / np.mean(spectrum))
        low_mask = freqs <= 500.0
        low_energy = float(np.sum(power[low_mask]) / power_sum)

        f0, harmonicity = self._estimate_f0(frame, rms)
        return AcousticFeatures(
            start=start,
            end=start + duration,
            f0_hz=f0,
            rms=rms,
            spectral_centroid_hz=centroid,
            spectral_flatness=float(np.clip(flatness, 0.0, 1.0)),
            harmonicity=harmonicity,
            low_frequency_energy=float(np.clip(low_energy, 0.0, 1.0)),
        )

    def _estimate_f0(self, frame: np.ndarray, rms: float) -> tuple[float | None, float]:
        if rms < 1e-4:
            return None, 0.0

        centered = frame - float(np.mean(frame))
        autocorr = np.correlate(centered, centered, mode="full")[len(centered) - 1 :]
        zero = float(autocorr[0])
        if zero <= 1e-12:
            return None, 0.0

        min_lag = max(1, int(self.sample_rate / self.f0_max_hz))
        max_lag = min(len(autocorr) - 1, int(self.sample_rate / self.f0_min_hz))
        if max_lag <= min_lag:
            return None, 0.0

        region = autocorr[min_lag : max_lag + 1]
        rel_idx = int(np.argmax(region))
        lag = min_lag + rel_idx
        strength = float(np.clip(autocorr[lag] / zero, 0.0, 1.0))
        if strength < 0.15:
            return None, strength
        return float(self.sample_rate / lag), strength
