from __future__ import annotations

from pathlib import Path

from .models import WordTiming


class FasterWhisperTranscriber:
    """Lazy, reusable faster-whisper adapter with word timestamps."""

    def __init__(self, model_size: str = "small") -> None:
        self.model_size = model_size
        self._model = None

    def _load(self):
        if self._model is not None:
            return self._model
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed; install the 'whisper' extra"
            ) from exc
        self._model = WhisperModel(self.model_size, device="auto", compute_type="int8")
        return self._model

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> list[WordTiming]:
        model = self._load()
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


def transcribe_with_faster_whisper(
    audio_path: str | Path,
    model_size: str = "small",
    language: str | None = None,
) -> list[WordTiming]:
    return FasterWhisperTranscriber(model_size=model_size).transcribe(
        audio_path,
        language,
    )
