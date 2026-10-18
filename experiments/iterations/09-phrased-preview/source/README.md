# Calcutta: phrased rhythm preview

72 seconds; quarter note = 100; 4/4; 30 bars. All 32 construction endpoints remain distinct voices.

## Harmonic order

Each row lasts six bars. Numbers are bar counts:

| Group | Sequence |
|---|---|
| 1 | A2 B2 A1 B1 |
| 2 | C2 B2 C1 B1 |
| 3 | C2 D2 C1 D1 |
| 4 | E2 D2 E1 D1 |
| 5 | E2 F2 E1 F1 |

## Rhythm

Each voice independently generates phrases mostly 2–6 quarter notes long. Inter-phrase breaths are selected from 0.75–2.5 beats, with weighted re-entry toward metrical supports. Inside each phrase, note attacks predominate; occasional quarter-beat internal breaks add articulation. Staccato, ordinary, and tenuto gates occupy about 57%, 84%, or 97% of the chosen rhythmic span. Phrase-ending notes favor tenuto and lower dynamics. Accents, an arched dynamic contour, and small independent variations shape the phrases.

Attack placement favors beat 1, then beat 3, then the other quarter-note beats, then eighths and sixteenths. The five six-bar groups favor regular four-beat meter, a 3+3+2 eighth-note overlay, triplets, a three-quarter-note cross-accent, and regular meter again. Individual phrases adopt the shared mode with 75% probability, otherwise keeping the ordinary meter. A grid of 12 ticks per quarter represents both sixteenths and eighth-note triplets exactly; articulation gates may use finer ticks.

Each voice follows the same construction branch through the changing tunings. Phrases can cross harmony boundaries; sounding notes are split and retuned at the boundary. Every voice sounds in every harmony. No coverage repairs were needed for this seed. The preview contains 719 phrases and 3,460 sounding note segments, with 5–31 simultaneous voices (about 20 on average).

## Sounds

The previous dry palette is retained: 9 Surge XT, 9 Vital, 8 Dexed, and 6 TimGM6mb/FluidSynth sounds. Eight disjoint sound swaps change 16 of the voice assignments. All 41 voice pairs approaching within 30 cents retain different timbre families. The fixed voice pans remain the same.

There is no reverb, chorus, pitch vibrato, or release tail in the custom synth patches. Their sustain envelopes remain flat. Piano, vibraphone, and tubular bells retain natural decay. A 32-sample edge rounding occurs entirely inside each gate. Rendering uses a consistent synth velocity and applies the written dynamic envelope as a gain per note, so accents work consistently across patches. MIDI exports the written velocities for use in other hosts.

## Reproduce

Install `numpy`, `mido`, `pedalboard==0.9.26`, libfluidsynth, TimGM6mb, and the Surge XT, Vital and Dexed Linux VST3 plugins. Plugin versions and runtime layout are documented in `SOUND_PALETTE.md`. Plugin binaries and soundfonts are not included.

From the extracted archive root:

```sh
python phrased_preview.py --previous composition_32_voices_v3/score_and_sounds.json --runtime /path/to/synth_runtime --soundfont /path/to/TimGM6mb.sf2 --patches composition_32_voices_v3/patches --output output
```

Seed: 2026101716. The bundled patch states are Pedalboard raw VST3 states. MIDI uses three ports to preserve 32 independent microtonal channels; the pitch-bend range is two semitones in the MIDI export. The renderer compensates separately for Dexed's three-semitone default. Match synth patches and route all ports when using the MIDI; it cannot embed the VST sounds.

`phrased_preview.json` records every note, phrase, harmony, articulation, dynamic, and patch assignment. `voice_sounds.csv` lists the new assignments. `validation.json` summarizes the score checks and texture.
