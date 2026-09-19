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
            formants_hz=self._estimate_formants(frame),
            mfcc=self._estimate_mfcc(power, freqs),
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

    def _estimate_formants(self, frame: np.ndarray) -> tuple[float, ...]:
        """Estimate F1-F3 with a small LPC model using only NumPy."""
        if frame.size < 64 or float(np.sqrt(np.mean(frame * frame))) < 1e-4:
            return ()
        x = np.array(frame, dtype=np.float64, copy=True)
        x[1:] = x[1:] - 0.97 * x[:-1]
        order = min(16, max(8, int(self.sample_rate / 1000) + 2))
        corr = np.correlate(x, x, mode="full")[len(x) - 1 : len(x) + order]
        if corr.size < order + 1 or corr[0] <= 1e-10:
            return ()
        toeplitz = np.empty((order, order), dtype=np.float64)
        for i in range(order):
            for j in range(order):
                toeplitz[i, j] = corr[abs(i - j)]
        try:
            coeffs = np.linalg.solve(
                toeplitz + np.eye(order) * 1e-8,
                corr[1 : order + 1],
            )
        except np.linalg.LinAlgError:
            return ()
        roots = np.roots(np.concatenate(([1.0], -coeffs)))
        roots = roots[np.imag(roots) >= 0]
        angles = np.angle(roots)
        freqs_hz = angles * self.sample_rate / (2.0 * np.pi)
        bandwidths = (
            -0.5
            * self.sample_rate
            / np.pi
            * np.log(np.maximum(np.abs(roots), 1e-9))
        )
        candidates = sorted(
            float(freq)
            for freq, bw in zip(freqs_hz, bandwidths)
            if 90.0 <= freq <= min(5000.0, self.sample_rate / 2 - 50)
            and 0.0 < bw < 700.0
        )
        return tuple(candidates[:3])

    def _estimate_mfcc(
        self,
        power: np.ndarray,
        freqs: np.ndarray,
        count: int = 13,
    ) -> tuple[float, ...]:
        """Small MFCC implementation for timbre signatures without SciPy/librosa."""
        filters = 26
        low_hz = 80.0
        high_hz = min(7600.0, self.sample_rate / 2 - 1.0)
        if high_hz <= low_hz:
            return ()

        def hz_to_mel(hz: float) -> float:
            return 2595.0 * np.log10(1.0 + hz / 700.0)

        def mel_to_hz(mel: np.ndarray) -> np.ndarray:
            return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

        mel_points = np.linspace(
            hz_to_mel(low_hz),
            hz_to_mel(high_hz),
            filters + 2,
        )
        hz_points = mel_to_hz(mel_points)
        energies = np.zeros(filters, dtype=np.float64)
        for m in range(1, filters + 1):
            left, center, right = hz_points[m - 1 : m + 2]
            up = np.clip(
                (freqs - left) / max(center - left, 1e-9),
                0.0,
                1.0,
            )
            down = np.clip(
                (right - freqs) / max(right - center, 1e-9),
                0.0,
                1.0,
            )
            triangle = np.minimum(up, down)
            energies[m - 1] = np.sum(power * triangle)

        log_energy = np.log(np.maximum(energies, 1e-12))
        n = np.arange(filters, dtype=np.float64)
        coeffs = []
        for k in range(count):
            basis = np.cos(np.pi * k * (n + 0.5) / filters)
            coeffs.append(float(np.sum(log_energy * basis)))
        return tuple(coeffs)
