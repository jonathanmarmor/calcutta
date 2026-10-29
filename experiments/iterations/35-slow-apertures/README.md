# Calcutta: Slow Apertures

**14:00 · 58 timbral sources · 688 long sustained strands**

[Listen](audio/calcutta_slow_apertures.mp3).

A mostly sustained movement across the full original register, from MIDI 48 to approximately 96.113. Different instrumental colors enter and leave over tens of seconds. Their steady spectra replace the previous prompt attacks and plucked decay. Individually shaped timbral waves overlap, while trills, arpeggiations and softer chordal particles gradually appear inside the sustained layer.

Individual sustained-tone entrances last roughly 18–49 seconds and exits roughly 22–61 seconds. The eight event clouds have longer group envelopes; their event density also rises and falls. Thus a texture can enter by both getting louder and becoming more populated, and leave through the reverse process. These are sin-squared note/cloud envelopes, not one master fade.

## Slowly appearing textures

| Approximate span | Texture |
|---|---|
| 1:06–3:16 | neighbor trill |
| 2:27–4:49 | expanding arpeggio |
| 3:55–6:25 | triad mist |
| 5:37–7:56 | sparse-to-dense lattice |
| 7:10–9:44 | neighbor trill |
| 8:42–11:26 | expanding arpeggio |
| 10:15–12:46 | triad mist |
| 11:34–13:53 | sparse-to-dense lattice |

The source harmonies launch about twelve seconds apart, but this movement deliberately overlaps their long fixed-pitch strands. Every tone keeps its original source-field pitch until its own fade ends; there is no pitch bend or mid-note retuning. Neighboring source fields therefore coexist during gradual handoffs. It begins beyond the 1:2 field, visits that field more quietly afterward, and traverses all forty source fields.

The final chord emerges around 7:55–8:00; after **9:18** only the destination field remains. That leaves slightly more than the last third entirely inside the golden-ratio harmony, with continued timbral and textural change. The ending consists of different strands and clouds withdrawing individually.

There is no reverb, delay, chorus, detuning, pitch LFO/vibrato, voice synthesis or click. The eight soft clouds alternate distinct original pitches rather than using vibrato or continuous glissandi. No passing tones or octave substitutes are added. Earlier constraints on immediate attacks/releases and short harmonic boundaries are intentionally superseded by this request for very long fades. The source models are the inherited sample-derived acoustic/electric/analog/FM colors, reconstructed here from steady spectra, not untouched samples or new live plugins.

## Inspect and reproduce

Unpack the source, install FFmpeg and the pinned Python requirements, then run:

```sh
python compose_slow.py
python render_slow.py
python export_midi.py
python validate_slow.py
python package_slow.py
```

The saved compact models suffice; no external bank or native plugin is required. The original request and public composition instructions are in `suite/BRIEF.md`. `suite/score.json` preserves each fixed pitch/source field, note envelope, cloud identity, timbre and voice lane. `compose_slow.py` records cloud density and note-selection logic; `render_slow.py` implements the steady carriers and slow envelopes. Source provenance and the GeneralUser GS license are included. Public decisions are retained, not hidden reasoning.

The MIDI uses independent pitch-bend lanes and CC11 expression curves for the note and group envelopes. It uses a seconds-based timing grid rather than implying a metrical pulse. External sound engines interpret program/envelope controls differently; the supplied renderer is authoritative. Source audio is 24 kHz stereo, with a 48 kHz / 256 kbps MP3 listening copy.

Validation checks exact source-field pitches, no held retuning, all forty source fields, long envelope spans, whole-register coverage through most of the body, exclusive final-field residence after 9:18, independent MIDI lanes, identical score regeneration, complete WAV bytes, MP3 length, output peaks and positive source energy. Sustaining tones account for approximately 83.4% of the summed individual layer energy before stereo summation. This is an energy accounting measure, not a perceptual loudness claim.
