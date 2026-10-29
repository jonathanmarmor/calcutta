# Calcutta: Pulse and Convergence

Ten new pieces, **59:21 of music**; **59:39** in the continuous album with two-second gaps. The primary changes are fuller texture, a sustained expressive pulse, and a left-to-right harmonic journey that reaches the final golden-ratio field for at least the last third. No new compositional research or borrowed tunes/forms were used.

## Listening order

| Album time | Piece | Duration | Final field begins within piece | Final-field share |
|---|---|---|---|---|
| 0:00 | [01. Current and Grain](suite/audio/01_current_and_grain.mp3) | 6:15 | 3:52 | 38.0% |
| 6:17 | [02. Walking Lines](suite/audio/02_walking_lines.mp3) | 5:46 | 3:24 | 41.0% |
| 12:06 | [03. Reedwork](suite/audio/03_reedwork.mp3) | 6:56 | 4:18 | 37.8% |
| 19:04 | [04. Open Circuits](suite/audio/04_open_circuits.mp3) | 5:13 | 3:08 | 39.8% |
| 24:19 | [05. Copper and Wood](suite/audio/05_copper_and_wood.mp3) | 5:58 | 3:46 | 36.7% |
| 30:19 | [06. Four Corners](suite/audio/06_four_corners.mp3) | 6:02 | 3:32 | 41.2% |
| 36:23 | [07. Bright Undercurrent](suite/audio/07_bright_undercurrent.mp3) | 6:46 | 4:05 | 39.6% |
| 43:12 | [08. Interlaced](suite/audio/08_interlaced.mp3) | 4:50 | 3:01 | 37.6% |
| 48:04 | [09. Held in Motion](suite/audio/09_held_in_motion.mp3) | 6:11 | 3:36 | 41.6% |
| 54:18 | [10. Forward Rooms](suite/audio/10_forward_rooms.mp3) | 5:20 | 3:20 | 37.5% |

## How the progression works

Each piece advances through contiguous windows of the original forty fields. A typical route uses A–C, then B–F, then F/G, one field alone, a wider next neighborhood, and so on. Within a window, it can move back and forth. The window's lower and upper bounds never move backward. All forty fields are heard. The last window contains only field 39, the final finite golden-ratio approximation, and lasts about 37–42% of the piece. The full schedules are in `areas` and `harmonies` in each score.

This final residence is not a long static pad. Four-bar episodes continue to change the melodic cells, triad/seventh-root sequences, registers, leading instruments, instrumental choirs, timbral relays, inner lines, phrasing and dynamics. The harmonic field stays fixed while its contents keep moving. The final field is the original saved pitch set, not a newly calculated limiting tuning or an octave-repeating scale.

## Fuller texture and an expressive pulse

Four or more written notes are active during roughly 91–92% of every piece, with averages around six and peaks of ten to thirteen. One- or two-note passages occupy only about 3–4%, including breaths and endings. These are score occupancy measures, not a perceptual estimate of how many instruments the listener can distinguish. Quiet inner voices, a distributed instrumental pulse and several moving foreground lines usually coexist.

The shared 4/4 pulse is supplied by changing bass and upper instrumental activity, not drums or a metronome. Mild common tempo breathing, small timing offsets, metrical accents, varied durations and shaped velocities prevent identical mechanical attacks. The moving lines include eighths, dotted figures and occasional subsidiary clock relationships, but the primary pulse remains present. Textures change about every four bars, always inside thirty seconds. No recurring violent tutti attack is used as the formal engine.

The pieces have separate melodic contours, rhythms, orchestral palettes, tempi, section orders and short endings. Sampled piano, Rhodes, Clavinet, guitars, harp, winds, strings, basses and mallets remain prominent, with analog/FM sounds taking changing foreground and background roles. There are no vocals, tremolo/gating studies, click track or master fade in this set.

## Pitch policy

Structural notes are exact members of the active original harmony. No octave-equivalent pitches are invented. Rare added notes are genuine passing tones: brief, quieter, monotonic connectors between actual same-part structural endpoints in the same harmonic span. Their endpoint IDs are recorded and checked. No new sustained chord tones or neighboring-note ornaments are introduced. Structural notes end before incompatible changes; no held pitch is retuned. The golden-field residence permits these same rare passing connections but no other harmonic fields.

## Sound method

The custom exact-pitch sampler uses saved dry atoms captured in three registers per instrument. Synth sources come from previously configured Surge XT, OB-Xf, TAL-NoiseMaker and Dexed. Acoustic/electric colors were captured through FluidSynth from GeneralUser GS, by S. Christian Collins (1997–2025; license included). These are sampled performances, not new full-plugin performances or recordings of a live ensemble. Natural source attacks and decays remain, sampled sustains are finite, and transposition affects tone color.

No reverb, delay, chorus, deliberate vibrato or periodic amplitude DSP is added. Brief edge smoothing and an eight-millisecond release gate prevent accidental clicks without a lingering release. Stereo-linked peak control preserves the internal dynamic shapes. Source audio is 24 kHz stereo; listening files are 48 kHz / 256 kbps MP3. The continuous album has track chapters where supported.

## Reproduce and inspect

The source bundle preserves the public request and generation brief, ten explicit forms/seeds, exact note and harmony decisions, beat times, instrument palette, passing endpoints, saved sound atoms, MIDI and validation. No network or plugin installation is required to render these saved sources. Install the pinned Python requirements and FFmpeg, then run from the source root:

```sh
python compose_flow.py
python render_flow.py 1
# render numbers 2 through 10 in the same way
python package_flow.py
```

`compose_flow.py 4` regenerates only score 04. `pitch_core.py` supplies the pitch-selection and voice-allocation primitives. `validate_flow.py` checks the advancing adjacent-field route, final residence, every structural pitch and passing connector, constant pitch per note, independent voice lanes, actual density, nearby musical attacks on the primary beat grid, scene lengths, duration and output peaks. It does not pretend to judge musical expressiveness by those numerical checks.

MIDI encodes the real primary beat grid using a tempo event per quarter note. Note positions retain the small performance offsets; the independently paced secondary parts share that time axis. Each independent lane gets its own channel/port and pitch-bend sensitivity. A DAW must honor separate ports and bend range; MIDI does not embed the sampled instruments. Use the supplied renderer for the exact timbral arrangement. Public instructions and code are preserved, not a model's hidden reasoning transcript. Complete third-party banks and plugin binaries are excluded.
