# Calcutta: Staircases and Clocks

8:20. Thirteen new scenes with twelve unison blends and eight exposed individual instruments; prompt dry foreground attacks with a louder overall mix; slower entrances reserved for a few background notes. No click, reverb, delay, chorus, deliberate vibrato, or retuning of held notes.

## Listening

Quiet mosaics unfold all 32 construction pitches of every original field across time, rather than returning to full-ensemble attacks. In the foreground, short contours recur with stable rhythmic identities, shift through field degrees, and change their spacing. The score searches each original field for sharp-third triads and fifths, then fourth-note extensions near harmonic or major sevenths. Recurring contours climb and descend those root-ordered stacks, with a small fourth-repeat mutation. Separate lines maintain independent pulse periods (roughly 37–78 BPM), often with skipped attacks and longer holds. Conductor rubato is under 1 BPM. A light stereo-linked peak envelope raises average loudness while keeping dry, prompt attacks; it adds no ambience. This version uses only exact original-field pitches. The twelve composite instruments alternate with eight exposed single instruments. The ensemble stops before a short, unanswered solo Clavinet ending: no master fade. Each note ends before a harmony boundary.

The synthesizer palette includes twelve new TAL-NoiseMaker, OB-Xf, and Surge XT patches, plus Dexed FM and GeneralUser GS / TimGM samples. They evoke single-oscillator analog, Oberheim, ladder-filter, and FM approaches from the earlier research; these are new patches, not claimed reconstructions of particular records. All layered components play the same exact pitch, with independent fixed balance gains.

## Blended instruments

- **Reed amber**: Clarinet × 1, TAL soft amber × 0.5.
- **Guitar wool**: Clean jazz guitar × 1, OB-X cloud wool × 0.38.
- **Rhodes glass**: Rhodes electric piano × 1, Pure wooden flute × 0.25.
- **Clavinet linen**: Clavinet × 1, TAL open linen × 0.38.
- **Harp copper**: Harp × 1, OB-X small brass × 0.32.
- **Bassoon velvet**: Bassoon × 1, Resonant velvet drone × 0.42.
- **Nylon air**: Nylon guitar × 1, Air through a ladder × 0.35.
- **Horn satin**: French horn × 1, TAL hollow satin × 0.4.
- **Recorder cloud**: Recorder × 1, OB-X dark halo × 0.3.
- **Panpipe FM**: Pan pipes × 1, FM clarinet × 0.3.
- **Steel reed**: Steel pans × 0.9, TAL dusk reed × 0.32.
- **Fretless thread**: Growling fretless bass × 1, Modular reed sustained × 0.36.
- **Solo clean guitar**: Clean jazz guitar × 1.
- **Solo Rhodes**: Rhodes electric piano × 1.
- **Solo flute**: Flute × 1.
- **Solo English horn**: English horn × 1.
- **Solo harp**: Harp × 1.
- **Solo piano**: Grand piano × 1.
- **Solo Clavinet**: Clavinet × 1.
- **Solo analog**: Curtis-like round lead × 1.

## Form

| Time | Scene |
|---|---|
| 0:00.0 | A guitar opens the door |
| 0:39.0 | Reeds at two speeds |
| 1:15.0 | The chord staircase |
| 1:54.0 | Clavinet in the windows |
| 2:33.0 | Rhodes and a turning ladder |
| 3:09.0 | Three clocks share a room |
| 3:48.0 | Fifths under a flute |
| 4:24.0 | Nylon counterweights |
| 5:03.0 | A bright seventh, held |
| 5:42.0 | Staircase in reverse |
| 6:18.0 | The clocks converge, almost |
| 7:00.0 | Horn over moving glass |
| 7:39.0 | One step missing |

## Reproduce

Run `python calcutta/interleave_piece.py`, `python calcutta_interleave/render.py`, and `python calcutta_interleave/package.py` from the archive root. Install numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, TAL-NoiseMaker 5.0.6, OB-Xf 1.0.3, Surge XT with patch-format 31 support, Dexed, GeneralUser GS and TimGM6mb. Configure the native-library and plugin paths as shown in the renderer. Plugin binaries and sample banks are not bundled. Synth states, the original tuning matrix, source, fixed sound calibration results, and the complete millisecond score are included. MIDI carries independent pitch-bend tracks and the performed tempo map; it does not contain plugin states or the audio master envelope.
