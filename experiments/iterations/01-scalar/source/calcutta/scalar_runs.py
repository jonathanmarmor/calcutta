"""A single line traverses each Calcutta chord up and down twice."""
import argparse
import json
import math
from pathlib import Path

import mido

from calcutta import Calcutta
from render import read_notes, synthesize


def distinct_pitches(harmony):
    """Remove unisons and floating point noise, retaining near-unison pitches."""
    result = []
    for pitch in sorted(harmony):
        if not result or pitch - result[-1] > 1e-9:
            result.append(pitch)
    return result


def up_down_twice(scale):
    # One initial low note, then two complete excursions; endpoints occur once
    # at each turning point. Each excursion returns to the lowest pitch.
    excursion = scale[1:] + scale[-2::-1]
    return scale[:1] + excursion * 2


def export(path, note_seconds):
    piece = Calcutta()
    midi = mido.MidiFile(ticks_per_beat=480)
    track = mido.MidiTrack()
    midi.tracks.append(track)
    track.append(mido.MetaMessage('track_name', name='Calcutta: up and down twice'))
    track.append(mido.MetaMessage('set_tempo', tempo=500000))
    for control, value in [(101, 0), (100, 0), (6, 2), (38, 0), (101, 127), (100, 127)]:
        track.append(mido.Message('control_change', control=control, value=value))
    track.append(mido.Message('program_change', program=89))
    ticks = max(1, round(note_seconds * 960))
    gate = max(1, round(ticks * .9))
    pending = 0
    time_ticks = 0
    expected = []
    chords = []
    for i, harmony in enumerate(piece.harmonies):
        scale = distinct_pitches(harmony)
        line = up_down_twice(scale)
        a, b, ratio = piece.ratios[i]
        track.append(mido.MetaMessage('marker', text=f'Chord {i+1}: {b}/{a}', time=pending))
        pending = 0
        chords.append({'chord': i+1, 'ratio': f'{b}/{a}', 'start_seconds': time_ticks/960,
                       'scale_midi_pitches': scale, 'note_count': len(line)})
        for pitch in line:
            note = round(pitch)
            bend = round((pitch-note) / 2 * 8192)
            track.append(mido.Message('pitchwheel', pitch=bend, time=pending))
            track.append(mido.Message('note_on', note=note, velocity=80))
            track.append(mido.Message('note_off', note=note, time=gate))
            pending = ticks-gate
            expected.append((time_ticks/960, gate/960, pitch))
            time_ticks += ticks
    track.append(mido.MetaMessage('end_of_track', time=pending))
    midi.save(path)
    return expected, {'note_seconds': ticks/960, 'repetitions': 2, 'chords': chords}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--note-seconds', type=float, default=.125,
                        help='Time between successive notes; default: sixteenths at 120 BPM')
    parser.add_argument('--output', type=Path, default=Path('output/scalar_runs'))
    args = parser.parse_args()
    if not math.isfinite(args.note_seconds) or args.note_seconds <= 0:
        parser.error('--note-seconds must be positive and finite')
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / 'calcutta_scalar_runs.mid'
    expected, data = export(path, args.note_seconds)
    actual = read_notes(path)
    assert len(actual) == len(expected)
    for (start, duration, pitch), (want_start, want_duration, want_pitch) in zip(actual, expected):
        assert abs(start-want_start) < 1e-7
        assert abs(duration-want_duration) < 1e-7
        assert abs(pitch-want_pitch) <= 1/8192
    assert all(start+duration <= next_start+1e-7
               for (start,duration,_),(next_start,_,_) in zip(actual, actual[1:]))
    data['duration_seconds'] = synthesize(actual, args.output / 'calcutta_scalar_runs.wav')
    (args.output / 'calcutta_scalar_runs.json').write_text(json.dumps(data, indent=2)+'\n')
    print(f'{len(data["chords"])} chords; {len(actual)} notes; {data["duration_seconds"]:.1f} seconds')


if __name__ == '__main__':
    main()
