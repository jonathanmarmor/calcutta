# Calcutta
A piece of music that gradually settles on a peculiar but consonant sustaining chord

## Run with Python 3

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python render.py --seconds-per-chord 4 --output output
```

This exports `calcutta.mid`, `calcutta.wav`, and `calcutta_harmonies.json`.
The original generator's pitches, chord order, and duplicate notes are preserved.
Four seconds per chord is a new listening default, not a timing specified in
the original composition. Use `--seconds-per-chord` to change it.

The MIDI has 32 voices, each on its own port/channel combination, using three
MIDI ports. Every voice sets its pitch-bend sensitivity to +/-2 semitones via
RPN, then applies a separate pitch bend for each chord. Pitch quantization error
is at most 0.0123 cents. Channel 10 is skipped. A DAW must honor the MIDI port
metadata or route the three groups to separate synth instances; collapsing
ports onto one instance causes conflicting bends. Set any synth's bend range
to +/-2 semitones if it does not honor RPN. Program 90 is a suggested warm pad;
the included synth uses its own sound rather than a General MIDI sound bank.

The WAV is synthesized from the exported MIDI using a steady additive tone
(fundamental plus three quieter harmonics), an 80 ms attack and 200 ms release.
It uses no effects or oscillator detuning, so audible beating comes from the
chord tuning. All voices are centered and the full rendering is peak-normalized.
It requires no soundfont. The renderer supports the fixed tempo and bend range
of its own export, not arbitrary external MIDI files.

To make a smaller listening file, install FFmpeg and run:

```sh
ffmpeg -i output/calcutta.wav -codec:a libmp3lame -q:a 2 output/calcutta.mp3
```

## Single-line scalar runs

```sh
python scalar_runs.py --output output/scalar_runs
```

For each of the original 40 chords, one unaccompanied line ascends through
every distinct pitch in the original register and descends back to the lowest
pitch, twice. Turning points are played once. Exact unisons and floating-point
noise within 0.0000001 cents are removed; musically close pitches are retained.
No octave folding, accompaniment, or additional pitches are used.

The default pulse is one note every 0.125 seconds (sixteenths at 120 BPM),
with a 90% gate. Use `--note-seconds .25` for half speed. Chord durations vary
with the number of distinct pitches. The output includes MIDI, WAV and a JSON
list of chord start times and pitches. This monophonic MIDI uses one channel
with a +/-2-semitone pitch-bend range.

For a dry sound with no temporal overlap between pitches, add `--clean-release`.
This uses a 5 ms attack and a 10 ms fade within each note's gate, ending at
note-off. The remaining 10% of each note interval is silent. WAV preserves
these exact silent gaps; lossy encodings can introduce small artifacts.
