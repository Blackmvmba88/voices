from __future__ import annotations

import numpy as np

from .alignment import summarize_features_for_word
from .analyzer import AcousticAnalyzer
from .color import ColorEngine
from .models import ColoredWord, VoiceProfile, WordTiming
from .profile import build_voice_profile


def colorize_transcript(
    samples: np.ndarray,
    words: list[WordTiming],
    sample_rate: int = 16000,
) -> tuple[VoiceProfile, list[ColoredWord]]:
    analyzer = AcousticAnalyzer(sample_rate=sample_rate)
    frames = analyzer.analyze(samples)
    profile = build_voice_profile(frames)
    engine = ColorEngine()
    colored = [
        engine.color_word(
            word,
            summarize_features_for_word(word, frames),
            profile,
        )
        for word in words
    ]
    return profile, colored
