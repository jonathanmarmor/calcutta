# Calcutta: Prisms

A 9:21.6 piece for 32 distinct instrumental voices. Quarter note = 100, 4/4. No click, reverb, or chorus. Each voice follows its original position in the tuning ladder; no voices are merged when pitches converge.

Shared attacks have unequal instrumental balances and shaped dynamic arcs. A few timbres lead while others sit much further back. Longer sustains remain, alongside shared breaths and exposed entries.

Pitch-aware hockets connect single-note voices into little melodies. The search uses actual sounding register, choosing steps of 75–335 cents and favoring 100, 200, and 300 cents. It searches anew when the tuning changes; pitches are never snapped to equal temperament or reassigned between voices.

Exposed harmonic windows bring out the tuning's sharp-third major triads and four-note extensions. The latter use the nearest available harmonic seventh (968.826 cents) or major seventh (1088.269 cents), within 40 cents. These are approximate consonant elements, not ordinary equal-tempered or pure just-intonation chords. Early harmonies without a suitable triad expose their closest available fifth instead.

The form alternates coordinated ensembles, exposed voices, and hybrids. Recurring strategies change speakers and register. The central convergence and final apertures occur only once. Section-wide dynamics flow independently of note accents, with a large crest, a retreat, and a fading ending.

## Interaction strategies

- **Breathing Chorale:** Common long-short phrases and shared breaths; the voices articulate as one body.
- **Antiphonal Choirs:** Left and right choirs trade questions and answers, occasionally overlapping at the hinge.
- **Sustained Arch:** Long held tones enter in waves, overlap, and withdraw; short gestures appear through the held texture.
- **Reggae Layers:** Sparse bass pillars, middle-register offbeat chords, and exposed upper-register responses interlock.
- **Scalar Hocket:** Single-note instruments form turning scalar melodies from measured steps of 75–335 cents, favoring half steps, whole steps, and minor thirds.
- **Pillars And Lace:** Slow sustained pillars support sparse, individually exposed phrases.
- **Rhythmic Canon:** Four choirs pass the same rhythmic sentence at staggered quarter-note offsets.
- **Diminishing Echoes:** A phrase passes through four choirs with progressively quieter answers and longer final sustains.
- **Solo And Tutti:** A few speakers ask expressive questions; the ensemble answers with short punctuation or a long assent.
- **Convergence Fan:** A one-time central accumulation: entrances spread into a full choir, unite, then fall away.
- **Triad Lanterns:** Exposed sharp-major triads with closely tuned fifths emerge from silence.
- **Consonant Windows:** Measured fifths, thirds, and triads are illuminated in contrasting soft instrumental blends.
- **Seventh Responses:** Four-note sonorities answer triads, choosing the closest available harmonic or major seventh.
- **Closing Apertures:** A one-time coda of exposed duos and diminishing held fragments with clear spaces between them.

## Listening map

Times are section boundaries; dynamic transitions flow between sections.

| Time | Bars | Texture | Dynamic target* |
|---|---|---|---|
| 0:00.0 | 1–6 | triad lanterns | -16 dB |
| 0:14.4 | 7–12 | antiphonal choirs | -10 dB |
| 0:28.8 | 13–18 | sustained arch | -8 dB |
| 0:43.2 | 19–24 | reggae layers | -5 dB |
| 0:57.6 | 25–30 | scalar hocket | -12 dB |
| 1:12.0 | 31–36 | antiphonal choirs | -7 dB |
| 1:26.4 | 37–42 | consonant windows | -15 dB |
| 1:40.8 | 43–48 | rhythmic canon | -11 dB |
| 1:55.2 | 49–54 | scalar hocket | -9 dB |
| 2:09.6 | 55–60 | sustained arch | -16 dB |
| 2:24.0 | 61–66 | reggae layers + scalar hocket | -7 dB |
| 2:38.4 | 67–72 | diminishing echoes | -10 dB |
| 2:52.8 | 73–78 | breathing chorale | -12 dB |
| 3:07.2 | 79–84 | solo and tutti | -4 dB |
| 3:21.6 | 85–90 | rhythmic canon + pillars and lace | -6 dB |
| 3:36.0 | 91–96 | scalar hocket | -13 dB |
| 3:50.4 | 97–102 | antiphonal choirs | -5 dB |
| 4:04.8 | 103–108 | scalar hocket | -8 dB |
| 4:19.2 | 109–114 | seventh responses | -14 dB |
| 4:33.6 | 115–120 | convergence fan | +0 dB |
| 4:48.0 | 121–126 | sustained arch | -18 dB |
| 5:02.4 | 127–132 | diminishing echoes | -14 dB |
| 5:16.8 | 133–138 | reggae layers | -10 dB |
| 5:31.2 | 139–144 | solo and tutti | -5 dB |
| 5:45.6 | 145–150 | pillars and lace + scalar hocket | -9 dB |
| 6:00.0 | 151–156 | rhythmic canon | -7 dB |
| 6:14.4 | 157–162 | antiphonal choirs | -3 dB |
| 6:28.8 | 163–168 | breathing chorale | -8 dB |
| 6:43.2 | 169–174 | reggae layers + scalar hocket | -4 dB |
| 6:57.6 | 175–180 | seventh responses | -12 dB |
| 7:12.0 | 181–186 | sustained arch | -16 dB |
| 7:26.4 | 187–192 | diminishing echoes + scalar hocket | -10 dB |
| 7:40.8 | 193–198 | solo and tutti | -3 dB |
| 7:55.2 | 199–204 | scalar hocket | -6 dB |
| 8:09.6 | 205–210 | antiphonal choirs + pillars and lace | -2 dB |
| 8:24.0 | 211–216 | breathing chorale | -8 dB |
| 8:38.4 | 217–222 | reggae layers | -5 dB |
| 8:52.8 | 223–228 | sustained arch | -14 dB |
| 9:07.2 | 229–234 | closing apertures | -22 dB |

*Relative section-envelope targets, not measured output loudness. Instrument activity and accents also shape the result.

## Reproduction

The source archive contains the deterministic composer, renderer, score, fixed calibration, pitch source, and synth states. Run from the archive root. Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg; install Vital, Surge XT, and Dexed VST3 plugins under `synth_runtime` using the paths in `calcutta/mixed_synths.py`. SoundFonts: TimGM6mb plus GeneralUser GS (https://schristiancollins.com/generaluser.php), placed as shown by the renderer. These third-party binaries and sample banks are not bundled. The MIDI has 32 tracks on three ports and requires independent pitch-bend channels with ±2-semitone ranges. It does not embed synth presets or the master audio dynamic envelope; the renderer/score are authoritative for the supplied recording.

## Exposed consonances

The listed intervals are octave-reduced distances from the chosen root; instruments may voice these across different octaves. Voice numbers preserve construction identity.

| Time | Voices | Sonority | Intervals above root (cents) |
|---|---|---|---|
| 0:00.0 | 1, 28 | closest available fifth | fifth error +92.093 cents |
| 0:04.8 | 32, 6, 5 | sharp major triad | 0.0, 451.884, 701.51 |
| 0:09.6 | 1, 28 | closest available fifth | fifth error +92.093 cents |
| 0:12.0 | 32, 6, 5 | sharp major triad | 0.0, 451.884, 701.51 |
| 1:26.4 | 13, 15, 18 | sharp major triad | 0.0, 433.456, 701.79 |
| 1:31.2 | 18, 20, 22 | sharp major triad | 0.0, 433.975, 702.019 |
| 1:36.0 | 13, 15, 18 | sharp major triad | 0.0, 433.456, 701.79 |
| 1:38.4 | 18, 20, 22 | sharp major triad | 0.0, 433.975, 702.019 |
| 4:19.2 | 17, 12, 21, 31 | sharp major seventh | 0.0, 433.832, 701.955, 1071.574 |
| 4:24.0 | 10, 19, 14, 28 | sharp major seventh | 0.0, 433.832, 701.955, 1071.574 |
| 4:28.8 | 17, 12, 21, 31 | sharp major seventh | 0.0, 433.832, 701.955, 1071.574 |
| 4:31.2 | 10, 19, 14, 28 | sharp major seventh | 0.0, 433.832, 701.955, 1071.574 |
| 6:57.6 | 2, 4, 6, 25 | sharp major seventh | 0.0, 433.832, 701.955, 1071.574 |
| 7:02.4 | 23, 27, 29, 11 | sharp major seventh | 0.0, 433.832, 701.955, 996.09 |
| 7:07.2 | 2, 4, 6, 25 | sharp major seventh | 0.0, 433.832, 701.955, 1071.574 |
| 7:09.6 | 23, 27, 29, 11 | sharp major seventh | 0.0, 433.832, 701.955, 996.09 |

The word “seventh” identifies a four-note extension of the triad; the exact interval in the table distinguishes its type and tuning deviation.
