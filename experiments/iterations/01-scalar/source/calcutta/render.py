"""Export the original harmonies as microtonal MIDI and synthesize that MIDI."""
import argparse
import json
import math
from pathlib import Path
import wave

import mido
import numpy as np
from calcutta import Calcutta

CHANNELS = [c for c in range(16) if c != 9]


def export_midi(piece, path, seconds):
    midi = mido.MidiFile(ticks_per_beat=480)
    conductor = mido.MidiTrack()
    midi.tracks.append(conductor)
    conductor.append(mido.MetaMessage('set_tempo', tempo=500000))
    for i, (a, b, _) in enumerate(piece.ratios):
        conductor.append(mido.MetaMessage('marker', text=f'Chord {i+1}: {b}/{a}',
                                         time=0 if i == 0 else round(seconds * 960)))
    for voice in range(32):
        track = mido.MidiTrack()
        midi.tracks.append(track)
        channel = CHANNELS[voice % 15]
        track.append(mido.MetaMessage('track_name', name=f'Voice {voice+1}'))
        track.append(mido.MetaMessage('midi_port', port=voice // 15))
        # Separate port/channel per voice; +/- 2-semitone bend range.
        for control, value in [(101, 0), (100, 0), (6, 2), (38, 0), (101, 127), (100, 127)]:
            track.append(mido.Message('control_change', channel=channel, control=control, value=value))
        track.append(mido.Message('program_change', channel=channel, program=89))
        for harmony in piece.harmonies:
            pitch = harmony[voice]
            note = round(pitch)
            bend = round((pitch-note) / 2 * 8192)
            track.append(mido.Message('pitchwheel', channel=channel, pitch=bend))
            track.append(mido.Message('note_on', channel=channel, note=note, velocity=64))
            track.append(mido.Message('note_off', channel=channel, note=note, velocity=0,
                                      time=round(seconds * 960)))
    midi.save(path)


def read_notes(path):
    notes = []
    for track in mido.MidiFile(path).tracks:
        time = 0.0
        bend = 0
        active = {}
        for msg in track:
            time += msg.time / 960.0  # Export uses fixed 120 BPM, 480 PPQ.
            if msg.type == 'pitchwheel':
                bend = msg.pitch
            elif msg.type == 'note_on' and msg.velocity:
                active[msg.note] = (time, msg.note + 2 * bend / 8192)
            elif msg.type == 'note_off' or (msg.type == 'note_on' and not msg.velocity):
                start, pitch = active.pop(msg.note)
                notes.append((start, time-start, pitch))
        assert not active, 'Unterminated MIDI notes'
    return notes


def synthesize(notes, path, rate=44100):
    # Fixed harmonic spectrum, no detuning or effects: beating comes from tuning.
    release = 0.2
    end = max(start+duration for start, duration, _ in notes) + release
    audio = np.zeros((math.ceil(end*rate), 2), dtype=np.float64)
    for start, duration, pitch in notes:
        count = round((duration+release)*rate)
        t = np.arange(count) / rate
        frequency = 440 * 2 ** ((pitch-69)/12)
        signal = np.zeros(count)
        for harmonic, amplitude in [(1, 1), (2, .28), (3, .12), (4, .06)]:
            if frequency*harmonic < rate/2:
                signal += amplitude*np.sin(2*np.pi*frequency*harmonic*t)
        envelope = np.minimum(t/.08, 1) * np.clip((duration+release-t)/release, 0, 1)
        offset = round(start*rate)
        # Center all pitches equally, keeping chord balance independent of voicing.
        audio[offset:offset+count] += (signal*envelope)[:, None]
    audio *= .85 / np.max(np.abs(audio))
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes((audio*32767).astype('<i2').tobytes())
    return end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds-per-chord', type=float, default=4)
    parser.add_argument('--output', type=Path, default=Path('output'))
    args = parser.parse_args()
    if not math.isfinite(args.seconds_per_chord) or args.seconds_per_chord <= 0:
        parser.error('--seconds-per-chord must be positive and finite')
    args.output.mkdir(parents=True, exist_ok=True)
    piece = Calcutta()
    midi_path = args.output / 'calcutta.mid'
    export_midi(piece, midi_path, args.seconds_per_chord)
    notes = read_notes(midi_path)
    assert len(notes) == 32 * len(piece.harmonies)
    expected = [pitch for chord in piece.harmonies for pitch in chord]
    actual = [pitch for _, _, pitch in sorted(notes)]
    assert max(abs(a-b) for a,b in zip(sorted(expected), sorted(actual))) < .00013
    duration = synthesize(notes, args.output / 'calcutta.wav')
    data = {'seconds_per_chord': args.seconds_per_chord, 'duration_seconds': duration,
            'outer_interval_cents': piece.outer_interval, 'golden_ratio': piece.golden_ratio,
            'chords': [{'ratio': f'{b}/{a}', 'start_seconds': i*args.seconds_per_chord,
                        'midi_pitches': piece.harmonies[i]} for i,(a,b,_) in enumerate(piece.ratios)]}
    (args.output / 'calcutta_harmonies.json').write_text(json.dumps(data, indent=2)+'\n')
    print(f'{len(piece.harmonies)} chords, {len(notes)} notes, {duration:.1f} seconds')
    print(f'Final distinct pitches: {len(set(piece.harmonies[-1]))}; outer span: {piece.outer_interval:.6f} cents')


if __name__ == '__main__':
    main()
