import numpy as np

from voices.analyzer import AcousticAnalyzer


def test_mfcc_signature_is_produced_for_tone():
    sr = 16000
    t = np.arange(int(sr * 0.25)) / sr
    samples = 0.45 * np.sin(2 * np.pi * 180.0 * t)
    frames = AcousticAnalyzer(sample_rate=sr).analyze(samples)
    assert frames
    assert len(frames[0].mfcc) == 13


def test_formant_field_is_always_tuple():
    sr = 16000
    t = np.arange(int(sr * 0.25)) / sr
    samples = 0.4 * np.sin(2 * np.pi * 130.0 * t)
    frame = AcousticAnalyzer(sample_rate=sr).analyze(samples)[0]
    assert isinstance(frame.formants_hz, tuple)
    assert len(frame.formants_hz) <= 3
