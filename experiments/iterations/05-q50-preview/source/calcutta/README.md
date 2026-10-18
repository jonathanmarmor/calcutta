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

## Polyphonic scalar-cell sketch

```sh
python polyphonic.py --whole-bpm 55 --seed 20261010 --output output/polyphonic
```

The harmony pattern is `(A B) x4, (C B) x4, (C D) x4, (E D) x4,
(E F) x4, ...` through all 40 modes. Each harmony lasts one 4/4 bar.
55 **whole notes** per minute means 220 quarter notes per minute, one bar
every approximately 1.091 seconds, and sixteenth-note onsets every 68 ms.

Seeded cells use mostly stepwise ascent, descent, arches, valleys, interleaved
thirds and short walks. Cells have 3–16 notes and last up to 1.5 bars, using
sixteenths, eighths, dotted eighths, quarters and longer endings. Starts and
durations are quantized to sixteenths. The original chord registers and
near-unison pitches are retained. A cell carries its degree count across
barlines; when the next mode has fewer degrees, the degree is clamped to its
highest available pitch. A held note is split and retuned at a harmony change.
Degree patterns reflect at the outer limits rather than wrapping registers.

Seven monophonic MIDI lanes support overlapping cells. Texture is usually
one to three lines, with intermittent five-to-seven-line episodes and clearings.
Some cells form repeated sequences with degree transposition, gaps, timbral
handoffs or a one-degree mutation. Each new cell receives a distinct harmonic
spectrum, envelope and stereo position; sequences sometimes deliberately
reuse the original cell's sound.

The audio renderer reads the exported MIDI pitches, timing, velocity and cell
IDs, then uses the custom instruments in the JSON score. General MIDI programs
in the MIDI are approximate substitutes; a normal MIDI player will not reproduce
the custom sound design. Pitch-bend sensitivity is +/-2 semitones on each of
seven channels. No pads, percussion, reverb or oscillator detuning are added.
Each note fades within its gate, so a lane has no overlapping release tails.
Audio is peak-normalized as a whole, preserving density and dynamic variation.

Output: MIDI, WAV and a JSON score containing modes, bar order, cells,
instruments, note events and density statistics. The generator verifies bar
order, MIDI round-trip tuning and timing, monophonic lanes, modal membership,
barline retuning and the seven-layer limit before rendering.

## Metered 16-bar sketch with instrument samples

Install FluidSynth's shared library and a General MIDI soundfont (for example,
on Ubuntu: `sudo apt install libfluidsynth3 timgm6mb-soundfont`), then run:

```sh
python instrument_sketch.py --soundfont /usr/share/sounds/sf2/TimGM6mb.sf2
```

This renders only the first 16 bars: `(A B) x4, (C B) x4`. The tempo is
quarter note = 50 BPM, with one harmony per 4/4 bar and sixteenths as the
smallest onset/duration unit. The total duration is 76.8 seconds.

Phrase onsets favor beat 1, then beat 3, then beats 2 and 4. Candidate cells
are selected with additional weight for their final-note onset or high/low
point falling on a quarter beat, especially 1 and 3. Accented velocities
reinforce that hierarchy. Pickups and other offbeat starts remain possible.
The seed makes the sketch reproducible.

Unlike the earlier additive sounds, this renderer uses actual instrument
samples: flute, nylon guitar, clarinet, marimba, cello, harp, oboe, piano,
bassoon, vibraphone and violin. Cell sequences can retain their instrument
or hand off to another. MIDI program numbers match the sampled renderer,
so a General MIDI player with the same soundfont can reproduce the instrument
choices. It may use different balance or release behavior.

Pitch bends preserve modal tuning. Chorus and reverb are disabled. Releases
are rendered within each note's gate and faded to zero before the next note
in its lane; no tails extend beyond a note. The WAV is rendered from the
exported MIDI, with sample instruments, cell panning and fixed instrument
balance applied before one overall peak normalization.
