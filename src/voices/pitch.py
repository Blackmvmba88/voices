from __future__ import annotations

import math

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def hz_to_midi(f0_hz: float) -> float:
    if f0_hz <= 0:
        raise ValueError("frequency must be positive")
    return 69.0 + 12.0 * math.log2(f0_hz / 440.0)


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((midi - 69.0) / 12.0))


def hz_to_note(f0_hz: float) -> tuple[str, float, float]:
    """Return nearest note name, MIDI value and cents offset."""
    midi = hz_to_midi(f0_hz)
    nearest = round(midi)
    note = f"{NOTE_NAMES[nearest % 12]}{nearest // 12 - 1}"
    cents = (midi - nearest) * 100.0
    return note, midi, cents


def semitone_delta(f0_hz: float, reference_hz: float) -> float:
    if f0_hz <= 0 or reference_hz <= 0:
        return 0.0
    return 12.0 * math.log2(f0_hz / reference_hz)
