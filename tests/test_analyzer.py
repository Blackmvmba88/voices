import numpy as np

from voices.analyzer import AcousticAnalyzer


def test_detects_sine_pitch():
    sr = 16000
    duration = 0.7
    t = np.arange(int(sr * duration)) / sr
    samples = 0.5 * np.sin(2 * np.pi * 220.0 * t)
    frames = AcousticAnalyzer(sample_rate=sr).analyze(samples)
    voiced = [f.f0_hz for f in frames if f.f0_hz]
    assert voiced
    assert abs(float(np.median(voiced)) - 220.0) < 5.0
