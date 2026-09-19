# Implementation map

## Implemented in v0.1

- Pure NumPy frame analysis: F0, RMS, spectral centroid, spectral flatness, harmonicity proxy, low-frequency energy, LPC formants and 13-coefficient MFCC signatures.
- Stable acoustic voice profile separated from instantaneous pitch.
- Acoustic profile -> base color family.
- Pitch contour -> bounded hue/lightness modulation inside that family.
- Texture channels: opacity, font weight, glow and roughness.
- Pitch -> note + cents metadata.
- Word timestamp -> acoustic-frame alignment.
- PCM WAV reader.
- Reusable faster-whisper word-timestamp transcription.
- HTML renderer for colored transcripts.
- CLI entry point for WAV processing.
- Browser microphone capture at 16 kHz PCM16.
- WebSocket live transport.
- Energy-based Voice Activity Detection for phrase segmentation.
- Live F0/note/color meter.
- Live phrase transcription and acoustic colorization.
- Unit tests and GitHub Actions CI.

## Deliberately not inferred

VOICES does not infer sex, gender, identity or emotion to choose a color. The color family is generated from measured acoustic features. A designer may choose the palette, but the measurement-to-palette mapping remains explicit and testable.

## Validation

Local deterministic core validation: 9 tests passed.

The live server and faster-whisper adapter use optional dependencies, so CI validates the deterministic acoustic core independently of model downloads and microphone hardware.

## Next engineering slices

1. Replace energy VAD with an optional neural VAD adapter for noisy rooms.
2. Calibrate the existing LPC formants against reference speech corpora.
3. Add speaker diarization for multi-person sessions.
4. Add syllable/phoneme-level alignment and continuous glyph gradients.
5. Add session export containing audio hash, transcript, acoustic frames and rendered styles.
6. Replace ScriptProcessorNode with AudioWorklet for production browser capture.
