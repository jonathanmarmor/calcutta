# Calcutta: Soft Machines

8:43. A fresh fifteen-scene piece with softened entrances, sustained dissonance, and sixteen composite instruments. No click, reverb, delay, chorus, deliberate vibrato, or retuning of held notes.

## Listening

Quiet mosaics unfold all 32 construction pitches of every original field across time, rather than returning to full-ensemble attacks. In the foreground, short contours recur with stable rhythmic identities, shift through field degrees, and change their spacing. The score alternates dialogue, static sustained intervals, rising and falling strands, and changes of register. Passing tones connect wider melodic leaps at ordinary phrase speeds; they are tagged in the score and do not redefine the underlying fields. Each note ends before a harmony boundary.

The synthesizer palette includes twelve new TAL-NoiseMaker, OB-Xf, and Surge XT patches, plus Dexed FM and GeneralUser GS / TimGM samples. They evoke single-oscillator analog, Oberheim, ladder-filter, and FM approaches from the earlier research; these are new patches, not claimed reconstructions of particular records. All layered components play the same exact pitch, with independent fixed balance gains.

## Blended instruments

- **Amber cor anglais**: TAL soft amber × 1, English horn × 0.32.
- **Wool and wire**: OB-X cloud wool × 1, Clean electric guitar × 0.27.
- **Porcelain breath**: Pure wooden flute × 0.85, Celesta × 0.22, TAL hollow satin × 0.4.
- **Satin clarinet**: TAL dusk reed × 1, Clarinet × 0.38.
- **Threaded harp**: Harp × 0.7, Modular reed sustained × 0.8, Recorder × 0.22.
- **Rubberwood**: Growling fretless bass × 0.7, TAL soft amber × 0.8, French horn × 0.16.
- **Steel and tine**: Steel pans × 0.55, FM electric piano × 0.55, OB-X small brass × 0.35.
- **Copper Rhodes**: Rhodes electric piano × 0.75, OB-X small brass × 0.5, FM clarinet × 0.22.
- **Linen flute**: TAL open linen × 0.8, Flute × 0.6.
- **Velvet bassoon**: Resonant velvet drone × 0.9, Bassoon × 0.45, Nylon guitar × 0.15.
- **Sitar cloud**: Buzzy sitar × 0.45, OB-X cloud wool × 0.9.
- **Small reed brass**: OB-X small brass × 0.9, English horn × 0.3, Recorder × 0.18.
- **Hollow panpipe**: TAL hollow satin × 1, Pan pipes × 0.3.
- **Ladder trumpet**: Curtis-like round lead × 0.85, Muted trumpet × 0.3.
- **Air organ**: Air through a ladder × 0.8, Drawbar organ × 0.4.
- **Dark celeste**: OB-X dark halo × 0.9, Celesta × 0.2.

## Form

| Time | Scene |
|---|---|
| 0:00.0 | Open windows |
| 0:32.0 | Two rooms answering |
| 1:09.0 | A stair in soft light |
| 1:43.0 | Glass against wool |
| 2:17.0 | Returning footsteps |
| 2:52.0 | Slow copper current |
| 3:26.0 | A narrowing corridor |
| 3:58.0 | Harpwork and shadow |
| 4:34.0 | Six quiet arguments |
| 5:08.0 | A tide of reeds |
| 5:44.0 | The sequence forgets one step |
| 6:19.0 | Still air |
| 6:55.0 | Threads rising apart |
| 7:29.0 | A low field opens |
| 8:03.0 | What remains |

## Reproduce

Run `python calcutta/murmur_piece.py`, `python calcutta_murmur/render.py`, and `python calcutta_murmur/package.py` from the archive root. Install numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, TAL-NoiseMaker 5.0.6, OB-Xf 1.0.3, Surge XT with patch-format 31 support, Dexed, GeneralUser GS and TimGM6mb. Configure the native-library and plugin paths as shown in the renderer. Plugin binaries and sample banks are not bundled. Synth states, the original tuning matrix, source, fixed sound calibration results, and the complete millisecond score are included. MIDI carries independent pitch-bend tracks and the performed tempo map; it does not contain plugin states or the audio master envelope.
