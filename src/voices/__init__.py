"""BlackMamba VOICES acoustic color engine."""

from .analyzer import AcousticAnalyzer
from .color import ColorEngine
from .models import AcousticFeatures, ColoredWord, VoiceProfile, WordTiming
from .profile import build_voice_profile

__all__ = [
    "AcousticAnalyzer",
    "AcousticFeatures",
    "ColorEngine",
    "ColoredWord",
    "VoiceProfile",
    "WordTiming",
    "build_voice_profile",
]

__version__ = "0.1.0"
