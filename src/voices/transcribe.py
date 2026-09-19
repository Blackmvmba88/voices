from __future__ import annotations

from pathlib import Path

from .models import WordTiming


def transcribe_with_faster_whisper(
    audio_path: str | Path,
    model_size: str = "small",
    language: str | None = None,
) -> list[WordTiming]:
    """Optional word-timestamp transcription adapter.

    Install with: pip install 'blackmamba-voices[whisper]'
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "faster-whisper is not installed; install the 'whisper' extra"
        ) from exc

    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, _ = model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
    )
    words: list[WordTiming] = []
    for segment in segments:
        for word in segment.words or []:
            token = word.word.strip()
            if token:
                words.append(
                    WordTiming(
                        token,
                        float(word.start),
                        float(word.end),
                    )
                )
    return words
