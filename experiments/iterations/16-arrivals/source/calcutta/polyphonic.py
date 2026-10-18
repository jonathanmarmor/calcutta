"""Seeded scalar-cell counterpoint through Calcutta's alternating modes."""
import argparse
import copy
import json
import math
from pathlib import Path
import random
import wave

import mido
import numpy as np

from calcutta import Calcutta
from scalar_runs import distinct_pitches

PPQ = 480
STEP = 120
PALETTES = [
    ('round reed', 71, [1, .16, .3, .04, .1, .02]),
    ('glass', 8, [1, .04, .18, .02, .08, .03]),
    ('wood', 12, [1, .4, .16, .08, .02, .01]),
    ('flute', 73, [1, .13, .05, .03, .01, .005]),
    ('soft brass', 60, [1, .42, .23, .12, .06, .025]),
    ('plucked wire', 24, [1, .32, .2, .14, .09, .07]),
    ('hollow', 80, [1, .01, .33, .01, .14, .01]),
    ('muted electric', 27, [1, .5, .08, .04, .03, .015]),
]


def progression(count):
    bars = []
    for lower in range(count-1):
        pair = [lower, lower+1] if lower % 2 == 0 else [lower+1, lower]
        bars.extend(pair * 4)
    return bars


def instrument(rng, number):
    name, program, amplitudes = rng.choice(PALETTES)
    # Each new cell has a distinct fixed harmonic spectrum and envelope.
    # No detuned oscillators: beating is a property of the tuning.
    return {'id': number, 'family': name, 'program': program,
            'harmonics': [a*rng.uniform(.72, 1.3) for a in amplitudes],
            'attack_seconds': rng.uniform(.002, .009),
            'decay_seconds': rng.uniform(.06, .3),
            'sustain': rng.uniform(.25, .75),
            'pan': rng.uniform(-.85, .85)}


def template(rng):
    length = rng.choices([3, 4, 5, 7, 9, 12, 16], [1, 2, 3, 4, 3, 2, 1])[0]
    shape = rng.choice(['up', 'down', 'arch', 'valley', 'interleave', 'walk'])
    sign = rng.choice([-1, 1])
    offsets = []
    value = 0
    for i in range(length):
        if shape == 'up': value = i
        elif shape == 'down': value = -i
        elif shape == 'arch': value = min(i, length-1-i)
        elif shape == 'valley': value = -min(i, length-1-i)
        elif shape == 'interleave': value = sign*((i//2) + (2 if i % 2 else 0))
        elif i: value += rng.choices([-2, -1, 1, 2], [1, 4, 4, 1])[0]
        offsets.append(value)
    durations = [rng.choices([1, 2, 3, 4], [6, 4, 1, 1])[0] for _ in offsets]
    if rng.random() < .45:
        durations[-1] = rng.choice([3, 4, 6])
    # Cap the longest phrase at one and a half bars.
    while sum(durations) > 24 and len(durations) > 3:
        durations.pop(-2)
        offsets.pop(-2)
    while sum(durations) > 24:
        i = max(range(len(durations)), key=durations.__getitem__)
        durations[i] -= 1
    return {'shape': shape, 'offsets': offsets, 'durations': durations}


def reflect(degree, count):
    if count == 1: return 0
    folded = degree % (2*(count-1))
    return folded if folded < count else 2*(count-1)-folded


def compose(seed=20261010, whole_bpm=55, bar_count=None, metered=False):
    rng = random.Random(seed)
    modes = [distinct_pitches(h) for h in Calcutta().harmonies]
    bars = progression(len(modes))
    if bar_count is not None:
        bars = bars[:bar_count]
    total = len(bars)*16
    occupancy = np.zeros((7, total), dtype=bool)
    targets = []
    for bar in range(len(bars)):
        # Long stretches of one to three voices, occasional crowded episodes,
        # and clearings. No metrical accent is imposed on the sixteenth grid.
        phase = bar % 32
        if phase in [13, 14, 15]: target = rng.choice([5, 6, 7])
        elif phase in [23, 31]: target = 0
        else: target = rng.choices([1, 2, 3], [4, 5, 2])[0]
        targets.extend([target]*16)
    cells = []
    instruments = []
    sequence_count = 0

    def place(start, motif, anchor, timbre_id=None, source=None, mutation=False):
        nonlocal sequence_count
        duration = sum(motif['durations'])
        if start+duration > total: return None
        lanes = [lane for lane in range(7) if not occupancy[lane, start:start+duration].any()]
        if not lanes: return None
        # Do not fill planned clearings with new cells or sequence repetitions.
        if targets[start] == 0: return None
        lane = rng.choice(lanes)
        if timbre_id is None:
            timbre_id = len(instruments)
            instruments.append(instrument(rng, timbre_id))
        cell = {'id': len(cells), 'start_step': start, 'length_steps': duration,
                'lane': lane, 'anchor_degree': anchor, 'instrument': timbre_id,
                'motif': copy.deepcopy(motif), 'source_cell': source,
                'mutation': mutation, 'velocity': rng.randint(62, 90)}
        cells.append(cell)
        occupancy[lane, start:start+duration] = True
        if source is not None: sequence_count += 1
        return cell

    for step in range(total):
        target = targets[step]
        position = step % 16
        onset_probability = (.72 if position == 0 else .58 if position == 8
                             else .42 if position % 4 == 0 else .11) if metered else .52
        if target and occupancy[:, step].sum() < target and rng.random() < onset_probability:
            mode = modes[bars[step//16]]
            motif = template(rng)
            if metered:
                candidates = [motif] + [template(rng) for _ in range(7)]
                def stress(onset):
                    beat = onset % 16
                    return 6 if beat == 0 else 4 if beat == 8 else 2.5 if beat % 4 == 0 else .3
                def fit(candidate):
                    starts = np.cumsum([0]+candidate['durations'][:-1]).tolist()
                    peak = max(range(len(starts)), key=lambda i:candidate['offsets'][i])
                    low = min(range(len(starts)), key=lambda i:candidate['offsets'][i])
                    return (stress(step+starts[-1]) + stress(step+starts[peak])
                            + stress(step+starts[low]))**2
                motif = rng.choices(candidates, weights=[fit(c) for c in candidates])[0]
            # Distribute cells among bass, middle and high register.
            register = rng.choice([(48, 64), (60, 79), (76, 97)])
            eligible = [i for i,p in enumerate(mode) if register[0] <= p < register[1]]
            anchor = rng.choice(eligible or list(range(len(mode))))
            cell = place(step, motif, anchor)
            if cell is not None and rng.random() < .22:
                next_start = step + cell['length_steps']
                interval = rng.choice([-4, -2, 0, 2, 4])
                for repeat in range(rng.randint(1, 3)):
                    if metered:
                        gaps = list(range(9))
                        next_start += rng.choices(gaps, weights=[stress(next_start+g) for g in gaps])[0]
                    else:
                        next_start += rng.choice([0, 0, 2, 4, 8])
                    seq = copy.deepcopy(motif)
                    mutate = rng.random() < .24
                    if mutate:
                        index = rng.randrange(len(seq['offsets']))
                        seq['offsets'][index] += rng.choice([-1, 1])
                    same_instrument = rng.random() < .5
                    repeated = place(next_start, seq, anchor+(repeat+1)*interval,
                                     cell['instrument'] if same_instrument else None,
                                     source=cell['id'], mutation=mutate)
                    if repeated is None: break
                    next_start += repeated['length_steps']

    notes = []
    crossings = 0
    for cell in cells:
        cursor = cell['start_step']
        start_mode = modes[bars[cursor//16]]
        for offset, duration in zip(cell['motif']['offsets'], cell['motif']['durations']):
            # Degree identity is carried across modes; bounds reflect the cell's
            # initial degree pattern, then clamp in shorter destination scales.
            degree = reflect(cell['anchor_degree']+offset, len(start_mode))
            end = cursor+duration
            position = cursor
            while position < end:
                bar = position//16
                mode = modes[bars[bar]]
                finish = min(end, (bar+1)*16)
                mapped_degree = min(degree, len(mode)-1)
                velocity = cell['velocity']
                if metered:
                    beat = position % 16
                    velocity += 14 if beat == 0 else 9 if beat == 8 else 5 if beat % 4 == 0 else -7
                    if offset in [min(cell['motif']['offsets']), max(cell['motif']['offsets'])]:
                        velocity += 3
                notes.append({'start_step': position, 'duration_steps': finish-position,
                              'pitch': mode[mapped_degree], 'degree': mapped_degree,
                              'mode': bars[bar], 'cell': cell['id'], 'lane': cell['lane'],
                              'instrument': cell['instrument'], 'velocity': min(115,velocity)})
                if finish < end: crossings += 1
                position = finish
            cursor = end
    density = occupancy.sum(axis=0)
    tempo = round(60000000/(whole_bpm*4))
    return {'seed': seed, 'whole_notes_per_minute': whole_bpm, 'tempo': tempo,
            'metered': metered,
            'seconds_per_step': mido.tick2second(STEP, PPQ, tempo),
            'bars': bars, 'modes': modes, 'cells': cells, 'instruments': instruments,
            'notes': notes, 'stats': {'bars': len(bars), 'cells': len(cells),
            'instruments': len(instruments), 'sequence_cells': sequence_count,
            'notes': len(notes), 'held_note_boundary_splits': crossings,
            'max_layers': int(density.max()),
            'density_steps': {str(i): int((density == i).sum()) for i in range(8)}}}


def write_midi(piece, path):
    midi = mido.MidiFile(ticks_per_beat=PPQ)
    conductor = mido.MidiTrack()
    midi.tracks.append(conductor)
    conductor.append(mido.MetaMessage('set_tempo', tempo=piece['tempo']))
    conductor.append(mido.MetaMessage('time_signature', numerator=4, denominator=4))
    for bar, mode in enumerate(piece['bars']):
        conductor.append(mido.MetaMessage('marker', text=f'Bar {bar+1}: mode {mode+1}',
                                         time=0 if bar == 0 else 16*STEP))
    for lane in range(7):
        track = mido.MidiTrack()
        midi.tracks.append(track)
        track.append(mido.MetaMessage('track_name', name=f'Melodic lane {lane+1}'))
        for control, value in [(101, 0), (100, 0), (6, 2), (38, 0), (101, 127), (100, 127)]:
            track.append(mido.Message('control_change', channel=lane, control=control, value=value))
        events = []
        for cell in piece['cells']:
            if cell['lane'] != lane: continue
            instr = piece['instruments'][cell['instrument']]
            tick = cell['start_step']*STEP
            events.extend([(tick, 1, mido.MetaMessage('text', text=f'cell:{cell["id"]} instrument:{instr["id"]} {instr["family"]}')),
                           (tick, 1, mido.Message('program_change', channel=lane, program=instr['program'])),
                           (tick, 1, mido.Message('control_change', channel=lane, control=10,
                                                value=round((instr['pan']+1)*63.5)))])
        for note in piece['notes']:
            if note['lane'] != lane: continue
            tick = note['start_step']*STEP
            key = round(note['pitch'])
            bend = round((note['pitch']-key)/2*8192)
            events.extend([(tick, 2, mido.Message('pitchwheel', channel=lane, pitch=bend)),
                           (tick, 3, mido.Message('note_on', channel=lane, note=key, velocity=note['velocity'])),
                           (tick+note['duration_steps']*STEP, 0,
                            mido.Message('note_off', channel=lane, note=key))])
        previous = 0
        for tick, _, msg in sorted(events, key=lambda event: (event[0],event[1])):
            track.append(msg.copy(time=tick-previous))
            previous = tick
    midi.save(path)


def read_midi(path):
    """Read back pitch bends and cell assignments from this composition's MIDI."""
    notes = []
    for lane, track in enumerate(mido.MidiFile(path).tracks[1:]):
        tick, bend, cell = 0, 0, None
        active = None
        for msg in track:
            tick += msg.time
            if msg.type == 'text' and msg.text.startswith('cell:'):
                cell = int(msg.text.split()[0].split(':')[1])
            elif msg.type == 'pitchwheel': bend = msg.pitch
            elif msg.type == 'note_on' and msg.velocity:
                assert active is None, 'Lane is not monophonic'
                active = (tick, msg.note, msg.note+2*bend/8192, cell, msg.velocity)
            elif msg.type == 'note_off':
                assert active is not None and active[1] == msg.note
                start, _, pitch, note_cell, velocity = active
                notes.append({'start_step': start//STEP, 'duration_steps': (tick-start)//STEP,
                              'pitch': pitch, 'cell': note_cell, 'lane': lane, 'velocity': velocity})
                assert start % STEP == tick % STEP == 0
                active = None
        assert active is None
    return notes


def render(piece, midi_notes, path, rate=44100):
    seconds = piece['seconds_per_step']
    count = math.ceil(len(piece['bars'])*16*seconds*rate)
    audio = np.zeros((count, 2), dtype=np.float32)
    for note in midi_notes:
        cell = piece['cells'][note['cell']]
        instr = piece['instruments'][cell['instrument']]
        start = round(note['start_step']*seconds*rate)
        end = round((note['start_step']+note['duration_steps'])*seconds*rate)
        t = np.arange(end-start, dtype=np.float64)/rate
        duration = (end-start)/rate
        frequency = 440*2**((note['pitch']-69)/12)
        signal = np.zeros(len(t))
        for h, amplitude in enumerate(instr['harmonics'], 1):
            if frequency*h < rate/2:
                signal += amplitude*np.sin(2*np.pi*frequency*h*t)
        signal /= sum(instr['harmonics'])
        attack = min(instr['attack_seconds'], duration/4)
        fade = min(.008, duration/4)
        envelope = np.minimum(t/attack, 1) * np.clip((duration-t)/fade, 0, 1)
        envelope *= instr['sustain']+(1-instr['sustain'])*np.exp(-t/instr['decay_seconds'])
        signal *= envelope*(note['velocity']/127)**1.4
        angle = (instr['pan']+1)*np.pi/4
        audio[start:end,0] += signal*np.cos(angle)
        audio[start:end,1] += signal*np.sin(angle)
    audio *= .88/float(np.max(np.abs(audio)))
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((audio*32767).astype('<i2').tobytes())
    return len(audio)/rate


def validate(piece, actual):
    assert piece['bars'] == progression(len(piece['modes']))[:len(piece['bars'])]
    assert 0 < len(piece['bars']) <= (len(piece['modes'])-1)*8
    wanted = sorted(piece['notes'], key=lambda n:(n['lane'],n['start_step']))
    actual = sorted(actual, key=lambda n:(n['lane'],n['start_step']))
    assert len(wanted) == len(actual)
    for a,b in zip(wanted,actual):
        for k in ['start_step','duration_steps','lane','cell','velocity']: assert a[k] == b[k]
        assert abs(a['pitch']-b['pitch']) <= 1/8192
        assert a['pitch'] == piece['modes'][piece['bars'][a['start_step']//16]][a['degree']]
        assert a['start_step']//16 == (a['start_step']+a['duration_steps']-1)//16
    assert piece['stats']['max_layers'] <= 7
    assert all(3 <= len(c['motif']['offsets']) <= 16 and c['length_steps'] <= 24 for c in piece['cells'])
    assert any(c['start_step'] % 16 for c in piece['cells'])
    if len(piece['bars']) >= 64:
        assert piece['stats']['max_layers'] >= 6


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=20261010)
    parser.add_argument('--whole-bpm', type=float, default=55)
    parser.add_argument('--output', type=Path, default=Path('output/polyphonic'))
    args = parser.parse_args()
    if not math.isfinite(args.whole_bpm) or not 1 <= args.whole_bpm <= 1000:
        parser.error('--whole-bpm must be between 1 and 1000')
    args.output.mkdir(parents=True, exist_ok=True)
    piece = compose(args.seed, args.whole_bpm)
    midi = args.output/'calcutta_polyphonic.mid'
    write_midi(piece,midi)
    actual = read_midi(midi)
    validate(piece,actual)
    piece['stats']['duration_seconds'] = render(piece,actual,args.output/'calcutta_polyphonic.wav')
    (args.output/'calcutta_polyphonic.json').write_text(json.dumps(piece,indent=2)+'\n')
    print(json.dumps(piece['stats'],indent=2))


if __name__ == '__main__': main()
