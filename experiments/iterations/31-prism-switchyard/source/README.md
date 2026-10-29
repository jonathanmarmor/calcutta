# Calcutta: Prism Switchyard

One new 6:42 piece. **97 source instrument sounds**, compared with 64 in each of the preceding five. Eight-color ensembles change every 11–14 seconds. There are sixteen texture procedures across 33 scenes, rather than one accompaniment pattern beneath every section. All 97 sounds have at least nine note attacks and a written phrase; instrumentation counts refer to source presets, including related variants, rather than 97 instrument families.

[Listen to the piece](suite/audio/01_calcutta_prism_switchyard.mp3).

Quiet sustained friction gives way to registral hockets, layered counterpoint, chord-stack relays, slow outer melodies over quicker inner voices, expanding dialogues and cut-off pulses. The five gated passages put six sustained layers through different amplitude gates, with two ungated melodic parts. Rates include 1, 1½, 2, 2½, 3 and 4 cycles per beat, and differing on/off proportions and phases. One-millisecond edge rounding prevents incidental digital clicks while leaving genuine off intervals. Tremolo is confined to these passages; there is no pitch modulation.

| Gate passage | Time |
|---|---|
| cut-glass interlocking gates | 0:35–0:46 |
| gated chords with ungated melody | 2:13–2:26 |
| returning gates, shifting duty cycles | 3:38–3:50 |
| gated chords with ungated melody | 5:01–5:14 |
| cut-glass interlocking gates | 6:17–6:29 |

The piece begins on the 2:3 field, traverses all forty original fields through advancing adjacent neighborhoods, and spends its last 40% in the final golden-ratio field. Triads, fifths, sevenths and quieter close dissonances continue to change within that final field. Structural notes are exact field members; ten brief softer passing notes connect actual endpoints in the same line and field. No octave substitutes or held-note retuning are used.

The acoustic, electric and synthetic colors use the preceding collection's saved sample-derived spectral models: fixed partial frequencies discard source vibrato, with short one-way spectral settling and modeled decay. They are resynthesized source colors, not untouched acoustic samples or newly installed synth engines. The GeneralUser source license and model provenance are included. No added reverb, delay, chorus, click or master ending fade. Short note-edge smoothing preserves prompt attacks and immediate releases.

## Reproduce

Install FFmpeg and the pinned Python requirements, then run from the source root:

```sh
python compose_prism.py
python render_prism.py 1
python export_prism.py
python check_prism.py
python package_prism.py
```

The saved 97 compact models are sufficient; no external sample bank or native plugin is needed to render. `suite/BRIEF_PRISM.md` records the request and public implementation instructions. `compose_prism.py` specifies the new textures and ensemble allocation; `flow_base.py` and `pitch_core.py` supply the preserved harmonic route and phrase primitives. The score stores every note, section, timbre assignment, amplitude-gate setting, beat grid and passing endpoint. Validation and regeneration reports record the checks, including all sounds contributing positive rendered energy.

`export_prism.py` writes independent-channel/port pitch-bend MIDI with the real primary tempo grid and section markers. MIDI does not encode the audio-gate DSP or the resynthesized timbre models: the provided renderer is authoritative for the sound and no-vibrato behavior. Audio is rendered at 24 kHz stereo and encoded as 48 kHz / 256 kbps MP3.

These instructions and saved decisions are public generation provenance, not a hidden reasoning transcript.
