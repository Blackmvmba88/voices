from voices.pitch import hz_to_note, hz_to_midi, midi_to_hz, semitone_delta


def test_a4_reference():
    assert hz_to_midi(440.0) == 69.0
    assert midi_to_hz(69.0) == 440.0
    note, _, cents = hz_to_note(440.0)
    assert note == "A4"
    assert abs(cents) < 1e-9


def test_octave_is_twelve_semitones():
    assert abs(semitone_delta(220.0, 110.0) - 12.0) < 1e-9
