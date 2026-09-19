from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class VoiceActivitySegmenter:
    """Tiny energy VAD for the live MVP."""

    sample_rate: int = 16000
    speech_rms: float = 0.012
    min_speech_ms: int = 220
    end_silence_ms: int = 520
    max_utterance_s: float = 20.0
    _chunks: list[np.ndarray] = field(default_factory=list, init=False)
    _speech_samples: int = field(default=0, init=False)
    _silence_samples: int = field(default=0, init=False)
    _active: bool = field(default=False, init=False)

    def push(self, samples: np.ndarray) -> np.ndarray | None:
        chunk = np.asarray(samples, dtype=np.float32).reshape(-1)
        if chunk.size == 0:
            return None
        rms = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))
        voiced = rms >= self.speech_rms

        if voiced:
            self._active = True
            self._speech_samples += chunk.size
            self._silence_samples = 0
            self._chunks.append(chunk.copy())
        elif self._active:
            self._silence_samples += chunk.size
            self._chunks.append(chunk.copy())

        max_samples = int(self.max_utterance_s * self.sample_rate)
        silence_needed = int(self.end_silence_ms / 1000.0 * self.sample_rate)
        min_speech = int(self.min_speech_ms / 1000.0 * self.sample_rate)
        buffered = sum(part.size for part in self._chunks)

        should_flush = (
            self._active
            and self._speech_samples >= min_speech
            and self._silence_samples >= silence_needed
        ) or buffered >= max_samples

        if should_flush:
            return self.flush()
        return None

    def flush(self) -> np.ndarray | None:
        if not self._chunks:
            self.reset()
            return None
        utterance = np.concatenate(self._chunks)
        enough_speech = self._speech_samples >= int(
            self.min_speech_ms / 1000.0 * self.sample_rate
        )
        self.reset()
        return utterance if enough_speech else None

    def reset(self) -> None:
        self._chunks.clear()
        self._speech_samples = 0
        self._silence_samples = 0
        self._active = False
