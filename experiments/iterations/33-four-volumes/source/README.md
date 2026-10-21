# Calcutta: Four Volumes

**Four continuous volumes · 16 movements · 2 hours**

A larger format than the previous album: four linked volumes of 24, 28, 32 and 36 minutes. Each has four movement chapters and its own balance of textures. The original Calcutta tuning remains the center, with two explicitly marked departures. Endings are individually composed rather than selected from one default cadence or fade.

| Volume | Length | Character |
|---|---|---|
| [1. Instruments of Return](calcutta_volume_1_instruments_of_return.mp3) | 24:00 | Instrumental conversations, a chaconne and changing contrapuntal ensembles. |
| [2. The Singing Circuit](calcutta_volume_2_the_singing_circuit.mp3) | 28:00 | Two wordless synthetic-vocal works, one echo work and an extended trill study. |
| [3. Fault Lines](calcutta_volume_3_fault_lines.mp3) | 32:00 | A tonal 12-ET detour, continuous glissandi, an unanswered dialogue and reversed-grain color. |
| [4. Long Weather](calcutta_volume_4_long_weather.mp3) | 36:00 | Longer processes, reorchestrated returns, spreading time, concertino and a phrase that folds backward. |

Each file contains four chapter markers. Support for displaying chapters depends on the player. Times below are relative to that volume, not the complete two-hour set. There are three two-second gaps inside each volume.

## Movements and endings

| Volume / time | Movement | Length | Ending |
|---|---|---|---|
| 1 / 0:00 | 01. The Hinge and the Answer | 4:10 | fifth answer |
| 1 / 4:12 | 02. A Pulse Leaves the Room | 6:32 | pulse withdraws, two isolated colors remain |
| 1 / 10:46 | 03. Chaconne of Unequal Steps | 9:01 | ground bass completes beneath an unresolved upper strand |
| 1 / 19:49 | 04. The Last Player Standing | 4:11 | successive exits at constant dynamic, last plucked note |
| 2 / 0:00 | 05. Mouths of Light | 7:12 | sung vowel closes into a soft humming consonant |
| 2 / 7:14 | 06. Echoes Have Their Own Meter | 5:02 | source stops, echoes finish the phrase |
| 2 / 12:18 | 07. The Trill Orchard | 8:01 | trill decelerates and settles on its lower neighbor |
| 2 / 20:21 | 08. A Sentence Interrupted | 7:39 | a new vocal sentence is cut mid-syllable |
| 3 / 0:00 | 09. An Ordinary Sky | 6:24 | unambiguous dominant-to-tonic cadence |
| 3 / 6:26 | 10. Continuous Ground | 9:33 | several slides meet on one fixed pitch |
| 3 / 16:01 | 11. Someone Forgot to Answer | 5:11 | a call followed by an intentional unanswered silence |
| 3 / 21:14 | 12. The Reversible Room | 10:46 | a reversed resonance breath, then a clean boundary |
| 4 / 0:00 | 13. The First Thing, Elsewhere | 8:29 | the opening returns in reversed orchestration |
| 4 / 8:31 | 14. Distance Between Footsteps | 12:17 | onsets spread farther apart without getting softer |
| 4 / 20:50 | 15. Concertino With a Missing Soloist | 6:06 | soloist leaves; ensemble gives the final answer |
| 4 / 26:58 | 16. Weather Beyond the Frame | 9:02 | the final phrase folds backward into its own first event |

## The planned departures

**Singing voices — movements 5 and 8 only.** Mouths of Light and A Sentence Interrupted use an original wordless formant ensemble: harmonic excitation shaped into vowel spectra, with brief breath/consonant entrances. Fundamental frequency stays fixed, with no vibrato. This is explicitly synthetic singing-like sound, not cloned singers, recorded vocals or a claim of intelligible human lyrics. Solo and canonic entries meet reeds, electric keys and the earlier analog/FM colors.

**Effects — movements 6 and 12 only.** Echoes Have Their Own Meter uses finite multi-tap repeats, including an ending where excitation stops before the echoes. The Reversible Room uses reversed grains and a final reverse-envelope resonance. Effects stay within allocated note spans and harmonic boundaries. The remaining fourteen movements have no added delay, reverb, chorus, audio reversal or other post effects. Ordinary synthesis, note-edge smoothing and the continuous glides are separate processes. The final movement's retrograde reverses event order; it does not reverse audio.

**Tuning — two exceptions.** An Ordinary Sky (9) is genuinely 12-tone equal temperament, in a conventional diatonic/tonal setting with an explicit G7-to-C cadence. Its inherited field labels are timing markers, not a claim that it plays Calcutta harmony. Continuous Ground (10) slides continuously between exact Calcutta field endpoints while fixed-pitch anchors remain; interior pitches deliberately leave the discrete fields. The other fourteen movements use only exact original field members, without passing tones or octave substitutes. Fifteen works preserve the advancing Calcutta field route, as written notes or glide anchors; their last 40% stays in the final field. No note is retuned merely to follow a new harmony.

**Trills — movement 7.** The Trill Orchard treats articulated alternating field pitches as foreground, accompaniment and counterpoint, with different rates and slower contrasting layers. It ends by slowing the alternation and settling on the lower neighbor. These are discrete note events, not vibrato.

## Familiar textures, unfamiliar pitches

The new chaconne, chorale, invention and concertino procedures bring recurring bass patterns, imitative parts, chordal phrases and clear solo/accompaniment relationships into the Calcutta fields. Other passages use cue-driven relays, multiple phrase clocks, moving chord subsets, hocket and changing registers. Materials, seeds, instrumentation and section plans are new. Most substantial scene changes happen sooner than 24 seconds, and no scene exceeds 30 seconds, including the endings.

The 97 inherited instrumental models preserve the dry, immediate sampled-source/acoustic/electric/analog/FM blend. Four new formant voice identities appear in the two vocal works. Instruments are sample-derived fixed-frequency reconstructions, not untouched samples or newly loaded live plugins. GeneralUser GS source provenance and license are included. Except for composed glissandi, there is no pitch modulation; no detune, chorus, click or master ending fade is added. Short note-edge smoothing controls accidental clicks while keeping attacks prompt. Effects exceptions are identified above.

Quiet sustained dissonance and internal fifth/triad/seventh subsets remain important. The endings try different rhetorical functions: answer, withdrawal, an unfinished upper thought, evaporation of players, humming closure, echo continuation, settling trill, interrupted singing, tonal cadence, convergence, missing response, reverse resonance, remembered opening, expanded time, ensemble answer and event retrograde. Some finish with silence or an intentionally unresolved thought. None uses a global ending fade.

## Reproduce and inspect

Unpack the source ZIP, install FFmpeg and the pinned Python requirements, then run:

```sh
python compose_volumes.py
python render_all.py
python export_volumes.py
python validate_volumes.py
python check_regeneration.py
python package_volumes.py
```

The compact saved models suffice; no native plugins, external sample bank, paid account or singer service is required. `plan.py` records the volume and movement form. `compose_volumes.py` contains new textures and each ending; `compose_foundation.py` preserves the earlier harmonic/phrase primitives with new seeds. `render_volumes.py` implements continuous pitch integration, formant singing and the two bounded effect types. Public request and implementation instructions are in `suite/BRIEF.md`. These are public generation decisions, not hidden reasoning.

Scores store every note, voice, harmonic span, phrase/cue decision, instrument assignment, glide endpoint/curve, vocal vowel, effect parameter, ending and primary tempo grid. MIDI uses separate pitch-bend lanes/ports and actual tempo maps. Glides have 20 ms pitch-bend control points with a wider bend range; audio integrates their pitch continuously. MIDI does not reproduce the custom voice/timbre synthesis or post effects. The provided renderer is authoritative for sound.

Validation checks harmonic boundaries, exact pitch membership or the two declared pitch exceptions, gate/effect/vocal confinement, sixteen different ending specifications, independent voice lanes, complete WAV bytes, MP3 duration, output peaks and positive energy from scored instruments. All sixteen scores regenerate identically; representative voice, glissando and DSP notes rerender identically. Volume files are encoded once from concatenated PCM, with four chapter markers each. Source audio is 24 kHz stereo; listening copies are 48 kHz / 256 kbps MP3. Metrics describe the score and files, not subjective realism or musical quality.
