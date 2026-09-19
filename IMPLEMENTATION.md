# Implementation map

## Implemented in v0.1

- Pure NumPy frame analysis: F0, RMS, spectral centroid, spectral flatness, harmonicity proxy and low-frequency energy.
- Stable acoustic voice profile separated from instantaneous pitch.
- Acoustic profile -> base color family.
- Pitch contour -> bounded hue/lightness modulation inside that family.
- Texture channels: opacity, font weight, glow and roughness.
- Pitch -> note + cents metadata.
- Word timestamp -> acoustic-frame alignment.
- PCM WAV reader.
- Optional faster-whisper word-timestamp transcription.
- HTML renderer for colored transcripts.
- CLI entry point.
- Unit tests and GitHub Actions CI.

## Deliberately not inferred

VOICES does not infer sex, gender, identity or emotion to choose a color. The color family is generated from measured acoustic features. A designer may choose the palette, but the measurement-to-palette mapping must remain explicit and testable.

## Next engineering slices

1. Live microphone ring buffer + Voice Activity Detection.
2. Streaming STT adapter with partial/final word replacement.
3. Persistent speaker profile and optional speaker diarization.
4. Formant extraction (F1/F2/F3) and calibrated timbre model.
5. Syllable/phoneme granularity.
6. WebSocket live renderer.
7. Session export containing audio hash, transcript, acoustic frames and rendered styles.
