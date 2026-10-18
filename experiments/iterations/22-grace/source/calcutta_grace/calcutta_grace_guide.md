# Calcutta: Grace and Grain

8:46.7. New themes, a new seventeen-scene form, and a different harmonic itinerary, using the original 40 fields and the established dry instrumental palette.

## Permission for this recording only

Passing tones, grace notes, and melodic ornaments may leave the original pitch collections in this version. Structural notes and full-field presentations remain exact original pitches. No new global harmonies are defined. The exception does not carry forward to subsequent generations unless requested again.

The score tags every added ornament with `is_ornament`. It contains 946 ornament notes: 843 lie outside the active original field, while others use existing endpoints. They are mostly short and softer than their target notes. Their patterns include chromatic-like approaches, uneven diatonic-like flourishes, pentatonic-sized sweeps, small microtonal turns, and original-endpoint runs. Runs are compressed into the space before a target, with varied internal timing, rather than imposed as a constant fast subdivision.

## No sustained retuning

Every rendered note has one fixed pitch for its complete duration. A note can cross a harmony boundary only if that unchanged pitch is genuinely present in every field it crosses. The score has 71 verified common-tone bridges.

Other phrases end before the boundary with a breath. Some answer after a roughly 110 ms gap with a new, nearby pitch and a fresh attack. No pitch-wheel adjustment occurs while a note remains held. This replaces the former practice of splitting a branch sustain at a boundary and immediately sounding its shifted continuation.

Three bass-pedal passages deliberately carry an unchanged common tone through changing fields. Protected whole-field listening windows may interrupt those pedals, after which they return on the same pitch. Structural material is checked against each field it actually sounds through; passing ornaments are kept inside one field's time span and released before its change.

## Form and timing

The piece retains continuous conductor rubato, intentional anticipation/delay, tuplets, independent nearby pulses, and back-calculated rhythmic suspensions that land together. Sound releases remain immediate and smoothed; no click, delay, reverb, chorus, or deliberate vibrato is added.

| Time | Scene | Nominal conductor BPM | Texture |
|---|---|---|---|
| 0:00.0 | A crooked invitation | 72 → 56 | rubato |
| 0:36.2 | Fluttering answers | 92 → 106 | dialogue |
| 0:56.2 | A quick backward glance | 106 → 84 | tuplets |
| 1:19.3 | Small steps on a wide ladder | 68 → 88 | elastic duo |
| 1:50.5 | One pitch, changing light | 52 → 66 | still |
| 2:29.7 | Runs between raindrops | 116 → 98 | cloud |
| 2:52.2 | Breath before the turn | 80 → 62 | landing |
| 3:21.1 | The crowded approach | 108 → 126 | tuplets |
| 3:39.9 | Ornaments in the bass | 62 → 76 | bass |
| 4:08.2 | A long common thread | 48 → 60 | rubato |
| 4:51.0 | A chase in unequal steps | 104 → 94 | three clocks |
| 5:18.0 | Turned around in the air | 76 → 96 | dialogue |
| 5:43.5 | One breath later | 60 → 48 | elastic duo |
| 6:20.4 | A swarm of small departures | 118 → 98 | cloud |
| 6:47.3 | Unhurried return | 46 → 58 | still |
| 7:41.7 | Arriving without a slide | 86 → 64 | landing |
| 8:12.8 | The last grace | 54 → 38 | coda |

## Rhythmic landings

- **3:16.8:** four lines approach at different local tempos and resolve together.
- **8:08.3:** four lines approach at different local tempos and resolve together.

## Reproduce

Run from the archive root:

```sh
python calcutta/grace_piece.py
python calcutta_grace/render.py
python calcutta_grace/package.py
```

Python dependencies: numpy, mido, pedalboard 0.9.26. Other dependencies: FluidSynth, ffmpeg, OB-Xf 1.0.3, Surge XT with patch-format 31 support, Dexed, TimGM6mb, and GeneralUser GS. Plugin/sample-bank binaries are not bundled. Configure paths as shown in the renderer. The archive includes source, score, tuning matrix, sound palette, instrument calibration, and saved synth states.

The composer reads only the previous voice palette and original endpoint matrix; it does not import previous notes or form. Millisecond score timing is exported to MIDI with a dense real tempo map. The 52 monophonic instrumental tracks use four ports with independent ±2-semitone pitch bends. MIDI does not embed plugin states or the rendered master-volume envelope.
