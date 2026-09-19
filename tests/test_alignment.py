from voices.alignment import summarize_features_for_word
from voices.models import AcousticFeatures, WordTiming


def test_word_alignment_prefers_overlapping_frames():
    frames = [
        AcousticFeatures(0.0, 0.1, 100.0, 0.1, 800, 0.1, 0.8, 0.8),
        AcousticFeatures(0.1, 0.2, 200.0, 0.2, 1200, 0.2, 0.7, 0.5),
    ]
    result = summarize_features_for_word(
        WordTiming("x", 0.1, 0.2),
        frames,
    )
    assert abs(result.f0_hz - 200.0) < 1e-9
