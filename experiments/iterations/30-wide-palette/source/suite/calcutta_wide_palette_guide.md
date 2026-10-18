# Calcutta: Wide Palette

Five new pieces, **30:32 of music**, with **64 instrument sounds per piece** (the previous set used 14–16). Different pools and changing section ensembles are written into the scores. The pieces begin on the 2:3 or 3:5 field, never 1:2. The fuller textures, expressive pulse and adjacent-window harmonic convergence are retained.

| Album time | Piece | Duration | Final field begins | Sounds |
|---|---|---|---|---|
| 0:00 | [01. Changing Ensembles](audio/01_changing_ensembles.mp3) | 6:41 | 4:01 | 64 |
| 6:43 | [02. Reed, Wire, Metal](audio/02_reed_wire_metal.mp3) | 5:20 | 3:20 | 64 |
| 12:06 | [03. Dry Color Fields](audio/03_dry_color_fields.mp3) | 6:22 | 3:42 | 64 |
| 18:30 | [04. Passing Instruments](audio/04_passing_instruments.mp3) | 4:59 | 3:05 | 64 |
| 23:31 | [05. A Wider Room](audio/05_wider_room.mp3) | 7:09 | 4:23 | 64 |

## The instrument palette

The expanded library has 97 source sounds. Each piece uses eight earlier synth colors plus a different selection of 56 sampled-source presets: pianos and electric pianos, organs, Clavinet, guitars, basses, strings, winds, brass, mallets, plucked instruments and other pitched colors. These are actual distinct source presets, not counts of octave/register changes or renamed copies. Related presets such as different pianos count as different sounds. The full names, usage counts and featured assignments are in `instrumentation.json`; every scene records its actual ensemble. Some appearances are brief, others prominent.

The earlier open-saw/resonant, Oberheim pulse/brass, TAL hollow/reed and FM glass/organ colors return in vibrato-free resynthesized form. Quieter unison components provide occasional blends, while individual instruments stay exposed. Section ensembles change rather than maintaining one fixed orchestration for the entire piece. No added room, delay, chorus, click or master ending fade is used.

## Strictly no vibrato

All sustained partial frequencies are fixed throughout each note. The model builder extracts attack and body spectra from dry sources and discards their time-varying pitch trajectory; zeroing a modulation controller alone would not remove vibrato embedded in samples. The renderer uses constant-frequency harmonic wavetables or a small bank of constant-frequency inharmonic partials for struck metals. It has no pitch LFO, detuned pair, chorus or cyclic amplitude effect. Short one-way spectral settling, modeled pluck decay and faint stationary breath noise preserve instrumental differences without periodic pitch modulation.

These are sample-derived resynthesized instruments. Their attack/body color comes from the source, while their envelopes and steady pitch are reconstructed. They can sound different from the unprocessed recordings. The acoustic/electric sources are GeneralUser GS by S. Christian Collins (license included); the earlier native synth captures supply the eight synthetic models. Source rendering is 24 kHz stereo; listening files are 48 kHz / 256 kbps MP3. Note entrances and releases have short click-prevention gates.

## Composition and pitch

The five pieces have fresh cells, rhythmic material and section orders. Four or more written notes remain active most of the time, with brief thin exceptions. An expressive common primary pulse supports the contrapuntal and layered phrases. Every four-bar scene changes texture and instrumentation.

The original forty fields are traversed through advancing contiguous neighborhoods, with local back-and-forth movement. At least the final third uses only the final golden-ratio field while internal chord sequences, register, rhythm and instrumentation continue moving. Structural pitches are exact field members. Rare added pitches are brief, quieter monotonic passing connections between actual same-part structural endpoints inside one field. No extra sustained pitches or held-note retuning are introduced.

## Reproduce and inspect

Install the pinned Python requirements and FFmpeg, then run from the source root:

```sh
python compose_wide.py
python render_wide.py 1
# repeat for numbers 2 through 5
python package_wide.py
```

Saved model coefficients suffice; no bank download or plugin installation is needed for these renders. Optional model rebuilding uses `build_models.py` with the GeneralUser SF2 path and the earlier native capture directory as arguments. The bank SHA-256 and native source metadata are preserved; complete third-party banks and plugin executables are excluded.

Scores preserve all notes, advancing harmonic windows, the primary beat grid, passing endpoints, instrument pools, section ensembles and featured assignments. Validation checks all 64 instruments actually sound, varying ensembles, the opening field, pitch membership, genuine passing function, final-third residence, full texture, pulse, independent lanes and complete audio duration. Model flags and the fixed-carrier renderer encode the vibrato prohibition. Occupancy and onset metrics describe the score, not subjective expressiveness.

MIDI follows the actual primary tempo grid with independent ports and per-note pitch bends. Its program hints refer to the original source presets; external playback needs its own modulation controls. Use the supplied fixed-carrier renderer to preserve the no-vibrato sound. Public instructions, code and decisions are included, not hidden model reasoning.
