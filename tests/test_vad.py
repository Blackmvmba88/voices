import numpy as np

from voices.vad import VoiceActivitySegmenter


def test_vad_flushes_after_speech_then_silence():
    sr = 16000
    vad = VoiceActivitySegmenter(
        sample_rate=sr,
        min_speech_ms=100,
        end_silence_ms=100,
    )
    speech = np.full(int(sr * 0.12), 0.05, dtype=np.float32)
    silence = np.zeros(int(sr * 0.12), dtype=np.float32)
    assert vad.push(speech) is None
    result = vad.push(silence)
    assert result is not None
    assert result.size == speech.size + silence.size
