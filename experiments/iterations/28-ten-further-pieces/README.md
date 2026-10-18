# Calcutta: Ten Further Pieces

Ten new pieces, **56:24 of music**, or **56:42** in the continuous listening file with two-second gaps. This returns to the techniques developed before Ten Detours, with no new composition research, external formal models, quotations, vocals or tremolo/gating study. All melodic material is newly generated.

## Listening order

| Album time | Track | Length | Character |
|---|---|---|---|
| 0:00 | [01. Grain and Line](audio/01_grain_and_line.mp3) | 5:54 | Guitar, Rhodes and reeds carry intersecting melodies; chord-stack sequences become dialogue and then exposed lines. |
| 5:56 | [02. Tall Rooms](audio/02_tall_rooms.mp3) | 5:18 | Broad piano/cello/woodwind spacing opens into interlock and quicker counterpoint, then lets individual tones stand alone. |
| 11:16 | [03. Many Small Clocks](audio/03_small_clocks.mp3) | 5:42 | Clavinet, marimba, reeds and strings keep distinct expressive clocks; several slow layers and faster lines exchange roles. |
| 17:00 | [04. Shared Breath](audio/04_shared_breath.mp3) | 5:30 | Small wind/brass choirs answer each other; solos emerge between coordinated phrases and woven responses. |
| 22:32 | [05. Wood and Wire](audio/05_wood_and_wire.mp3) | 6:06 | Plucked and mallet attacks hand a melody between colors, opening into long winds and then measured contrapuntal detail. |
| 28:40 | [06. The Long Way Through](audio/06_long_way_through.mp3) | 5:06 | English horn, cello, guitar and piano sustain longer melodic sentences, with occasional genuine passing connections and quieter inner activity. |
| 33:48 | [07. Close Weave](audio/07_close_weave.mp3) | 5:48 | Acoustic lines overlap in a close, brisk weave, broken by bare solos, slow frames and passages of generous space. |
| 39:38 | [08. Inside the Chord](audio/08_inside_the_chord.mp3) | 5:24 | Triads and sevenths are revoiced and sequenced inside the fields; quiet dissonance, single lines and synth/sample blends interrupt their continuity. |
| 45:04 | [09. Moving Floors](audio/09_moving_floors.mp3) | 6:00 | Slow bass and accompaniment move beneath quicker expressive parts, then the tempo relationships and foreground instruments change. |
| 51:06 | [10. Loose Threads](audio/10_loose_threads.mp3) | 5:36 | Short exposed ideas grow into layered counterpoint, break apart, and return in altered registers and timbres without a recurring borrowed form. |

## Musical constraints

The original forty Calcutta fields remain the harmonic source. Structural notes are actual pitches in the active field, not octave-equivalent substitutions. The pieces move locally between neighboring fields, with some reversals, differing dwell times and later convergence. None opens on the 1:2 field. Every field is heard, usually through subsets; these are not exhaustive 32-voice statements of every field.

Additional pitches are rare, brief passing tones. Each lies strictly between two structural notes in the same melodic part and same field, moves in their direction, sounds more quietly than its originating note, and lasts at most 440 milliseconds. The score records the actual endpoint note IDs. Connectors without a real destination are rejected. No extra sustained chord tones, neighbor-note ornaments, octave folding, moving held pitches, fast ornamental runs or glissandi are introduced. Structural notes end before a field changes.

Each piece has a new motif, rhythm, ensemble and explicitly chosen sequence of textures. Techniques include chord-root sequences, mutation, opposing melodic contours, small coordinated choirs, several independent expressive tempi, timbral hocket, sustained quiet dissonance, solo plus accompaniment, and transparent counterpoint. Strongly voiced chord stabs and the recurring short-short-long gesture are not the basis of this set. The scenes last roughly 10–18 seconds, always under thirty. Each piece contains one/two-line passages as well as five-to-seven-layer passages. The endings are individually written and dry; there is no master fade.

## Instruments and sound

Approximately nine in ten attacks use sampled instruments. Piano, Rhodes, Clavinet, acoustic and electric guitars, harp, mallets, reeds, flute, cello, viola, violin and acoustic/fretless bass share the foreground with analog/FM colors. Synths also appear as inner voices, restrained layers, occasional leads and small unison components. The instrumental assignments change through a piece instead of remaining attached to one pitch.

The source is a custom exact-pitch sampler using three dry reference registers per timbre. Eight synth sources were previously captured from Surge XT, OB-Xf, TAL-NoiseMaker and Dexed; sampled acoustic/electric sources use GeneralUser GS through FluidSynth. Nine additional sampled colors were captured for this set. GeneralUser GS is by S. Christian Collins (1997–2025); its license is included. These are sampler-based performances, not new full-plugin renders or recordings of a live ensemble. They retain the source instruments' natural attack/decay differences. Sampling/transposition changes tone color and captured sustains have finite lengths.

No reverb, delay, chorus, click, periodic gating or deliberate vibrato is added. Note edges receive only brief click-prevention smoothing and an eight-millisecond release gate. Stereo-linked peak control sets a moderate listening level while retaining internal dynamics. The source renders use 24 kHz stereo audio; listening copies are 48 kHz / 256 kbps MP3.

## Reproduce and inspect

The `source/` folder includes the original pitch lists, all ten deterministic composers/form plans, score decisions, exact passing-tone endpoints, MIDI, saved dry sound atoms, palette, validation, public request/brief and renderer. Saved atoms suffice; no plugin installation or network access is needed to render them. Install Python dependencies from `requirements.txt` and FFmpeg, then run from `source/`:

```sh
python compose_return.py
python render_return.py 1
# render numbers 2 through 10 in the same way
python package_return.py
```

For a single piece, `python compose_return.py 3` regenerates score 03. The renderer never silently selects a new seed. Scores contain absolute timings for the independently paced lines. MIDI uses a fixed 60-BPM time ruler with 1000 ticks per second, independent channels/ports and per-note pitch bend; its tempo map is not a separate conductor for every line. A DAW must honor the MIDI ports and pitch-bend range. MIDI does not embed the sampler tones; use the included renderer for the supplied audio.

`validate_return.py` verifies every structural pitch, genuine passing endpoints, constant pitch, harmonic boundaries, independent voice lanes, field coverage, frequent changes, sparse/dense passages, duration and output peak. The public `suite/BRIEF.md` and code expose the generation specification; they are not a model's hidden reasoning transcript. Complete third-party sound banks and plugin executables are excluded.
