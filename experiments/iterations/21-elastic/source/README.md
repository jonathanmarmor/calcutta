# Calcutta: Elastic Weather

9:08.7. A wholly new score made from the same 40 original tuning fields and a reused sound palette. No previous note sequences, motifs, rhythms, harmonic itinerary, or form were imported. The repeated dense short-short-long chord gesture has been removed. Complete fields still receive one soft, protected exposure each, without recurring chordal stabs.

The opening is sparse and starts in the 3:5 field. Neighboring early fields converse; the 1:2 field appears briefly rather than anchoring the piece. All 40 original harmonies are heard in full somewhere. Every other sounding pitch is also an actual endpoint of its current original field; no new tuning or octave-transposed pitch has been added.

## Time and expression

The conductor changes tempo continuously in eighth-of-a-beat steps, with breath-shaped acceleration, hesitation, and cadential slowing. Nominal scene tempos range from 36 to 116 quarter notes per minute; the expressive conductor momentarily spans approximately 24–145. Instrumental lines may run independently of that conductor.

Rubato sentences use unequal note spacing, shaped dynamics, 35 ms anticipation or 65 ms delay, and smaller continuous timing inflections. Tuplet scenes include thirds and fifths, with slight expressive deviations. Pulse clouds have six to thirteen neighboring but genuinely independent clocks, with slow rate drift and changing entrances/density; they do not consist of a backing pulse plus one different-tempo solo.

Two rhetorical suspensions work backward from a future downbeat. Four lines use periods of 0.37, 0.79, 0.53, and 1.13 seconds, approaching that common landing from different tempos. Their final attacks align to the millisecond score. Held notes follow their construction positions when crossing a harmonic change.

The larger form alternates these timing behaviors with transparent long-breathed music. There is no click, delay, reverb, chorus, or deliberate vibrato. Attacks/releases are smoothed inside the written gates.

## Listening map

| Time | Scene | Nominal conductor BPM | Texture |
|---|---|---|---|
| 0:00.0 | First breath | 58 → 74 | rubato |
| 0:27.4 | Questions in two fields | 84 → 100 | dialogue |
| 0:48.9 | Leaning forward, falling back | 96 → 80 | elastic duo |
| 1:16.8 | Three in the opening | 72 → 88 | tuplets |
| 1:41.3 | The long approach | 74 → 58 | landing |
| 2:12.7 | Six neighboring clocks | 108 → 92 | cloud |
| 2:41.6 | Windows held open | 48 → 64 | still |
| 3:22.9 | The flexible thread | 88 → 78 | elastic duo |
| 3:46.2 | Five through four | 92 → 112 | tuplets |
| 4:10.1 | Almost without a pulse | 44 → 52 | rubato |
| 4:47.8 | Many nearly equal tempos | 116 → 82 | cloud |
| 5:17.9 | A distant downbeat | 70 → 88 | landing |
| 5:47.2 | Breath, answer, interruption | 58 → 76 | dialogue |
| 6:16.8 | Three independent clocks | 98 → 86 | three clocks |
| 6:43.3 | The bass takes its time | 66 → 54 | bass |
| 7:15.9 | The slower answer | 52 → 44 | still |
| 8:04.1 | The gathering of pulses | 106 → 88 | cloud |
| 8:31.8 | After the landing | 48 → 36 | coda |

## Planned landings

- **2:07.6:** four independent lines arrive together, inside scene 5.
- **5:44.3:** four independent lines arrive together, inside scene 12.

## Sounds and research

The palette retains dry OB-Xf, Surge XT, Dexed, winds, guitars, keyboards, basses, and plucked sounds. A marimba attack plus a quieter sustaining sax sample is a new programming experiment inspired by Larry Fast's description of the technique behind “Shock the Monkey,” using our own sample bank rather than his Fairlight files or melody. It is not presented as an exact patch recreation.

See `synth_configurations.md` for documented configurations and performance/programming details from Stevie Wonder, Ozric Tentacles, Peter Gabriel/Larry Fast, and Kate Bush. Historical effects chains are described there but not copied into this dry render. Exact patch claims are distinguished from practical inferences and modern reconstructions.

## Reproduce

Run from the archive root:

```sh
python calcutta/elastic_piece.py
python calcutta_elastic/render.py
python calcutta_elastic/package.py
```

Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, OB-Xf 1.0.3, Surge XT with patch-format 31 support, and Dexed. SoundFonts: TimGM6mb and GeneralUser GS (https://schristiancollins.com/generaluser.php). Third-party binaries/sample banks are not bundled; configure their paths as shown by the renderer. Fixed instrument calibration and saved synth states are included.

The composer reads only the voice palette from `calcutta_motifs/score.json`, and the original endpoint matrix from `composition_32_voices_v3/score_and_sounds.json`. It creates all musical events and the form afresh. `seconds_per_tick` is 0.001: note timing is stored in milliseconds, unlike earlier scores.

The MIDI includes the performed microtiming and a dense real tempo map at PPQ 960, with 53 instrumental tracks on four ports and independent ±2-semitone pitch bends. It is checked to agree with the audio duration within 5 ms. It does not embed plugin states or the rendered master-volume envelope. The JSON/renderer remain authoritative for the supplied audio.
