# Calcutta: 32 voices, version 2

Duration 3:12; quarter note = 100; 4/4; two bars per harmony. The original 40 harmonies play once in order. The 32 branch identities, instruments, registers, and pans are the same as version 1.

Each part is generated sequentially from the beginning to the end. At every event onset:

1. Independently choose a note with probability 0.70 or a rest with probability 0.30.
2. Set maximum duration to min(8 eighth notes, eighth notes until the next harmony).
3. Choose duration uniformly from the integers 1 through that maximum.
4. Advance by that duration and repeat.

Consecutive notes and consecutive rests are allowed. Notes at consecutive onsets are separately articulated, including when their pitches are identical. Every event fits inside its harmony, so every voice makes a fresh choice at each chord change. The same rule applies to notes and rests. No selection is conditioned on other voices, previous notes/rests, or metrical stress.

All 32 voices retain the subdivision-tree endpoint they follow, without pitch sorting, octave displacement, or merging unisons. All 41 voice pairs that approach within 30 cents have different instrument families. The dry sampled-instrument rendering uses TimGM6mb and FluidSynth, with a short release inside each note gate, independent stereo positions, and instrument level balancing.

## Reproduce

Install libfluidsynth and a General MIDI soundfont, then:

```sh
python -m pip install -r requirements.txt
python rhythmic_voices_v2.py --soundfont /path/to/TimGM6mb.sf2 --output output
ffmpeg -i output/calcutta_32_voices_v2.wav -codec:a libmp3lame -q:a 2 output/calcutta_32_voices_v2.mp3
```

Seed: 20261017. The JSON contains all events, pitches, and assignments. The CSV lists construction branches and instruments. MIDI uses three ports, excluding percussion channels, with independent +/-2-semitone pitch bends; route all three ports when importing. The audio already includes the complete microtonal rendering.
