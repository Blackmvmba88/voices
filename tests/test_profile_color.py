from voices.color import ColorEngine
from voices.models import AcousticFeatures, WordTiming
from voices.profile import build_voice_profile


def frame(
    f0: float,
    centroid: float,
    low: float,
    harmonicity: float = 0.8,
):
    return AcousticFeatures(
        0.0,
        0.1,
        f0,
        0.1,
        centroid,
        0.08,
        harmonicity,
        low,
    )


def test_profiles_keep_family_but_pitch_modulates_color():
    frames = [
        frame(110.0, 850.0, 0.82),
        frame(115.0, 900.0, 0.78),
    ]
    profile = build_voice_profile(frames)
    engine = ColorEngine()
    word = WordTiming("hola", 0.0, 0.2)
    low = engine.color_word(word, frame(95.0, 850.0, 0.8), profile)
    high = engine.color_word(word, frame(150.0, 850.0, 0.8), profile)
    assert low.color != high.color
    assert abs(((high.hue - profile.base_hue + 180) % 360) - 180) <= 18.1
    assert abs(((low.hue - profile.base_hue + 180) % 360) - 180) <= 18.1


def test_deeper_profile_is_not_same_as_brighter_profile():
    deep = build_voice_profile([frame(85.0, 600.0, 0.9)])
    bright = build_voice_profile([frame(270.0, 3000.0, 0.2)])
    assert deep.base_hue != bright.base_hue
    assert deep.depth > bright.depth
