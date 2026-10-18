# Reproduction

Use Python 3.12, `numpy`, `mido`, and `pedalboard==0.9.26`; native renders additionally need FluidSynth and ffmpeg. Native binaries and sound banks are external dependencies. Earlier additive renders do not require the VST engines. Read the setup document inside each snapshot: do not substitute a newer algorithm for an old source file.

```sh
python experiments/reproduce.py 24-staircases-clocks prepare
python experiments/reproduce.py 24-staircases-clocks --list
python experiments/reproduce.py 24-staircases-clocks score
```

`prepare` copies the immutable snapshot into ignored `build/iterations/<id>`. `score` runs the composer only for entries whose command is explicitly registered. Other snapshots preserve the original README CLI with its options; `--list` locates those documents and entry points. This is important for early previews that combine score creation with native rendering.

Set `CALCUTTA_SYNTH_RUNTIME` and `CALCUTTA_SOUNDFONT_RUNTIME` to directories matching the saved layout, or supply the expected paths inside the prepared working directory. `FLUIDSYNTH_LIBRARY` points at libfluidsynth.so.3; include its directory in `LD_LIBRARY_PATH` on Linux when needed. Example sound engines: Surge XT (later states require patch-format 31 support), Vital, Dexed 1.0.1, OB-Xf 1.0.3, TAL-NoiseMaker 5.0.6; GeneralUser GS and TimGM6mb. Do not substitute Surge XT 1.3.4 for newer-format states. New TAL states have a ±2-semitone pitch-bend range; Dexed audio compensates for its saved ±3 range. MIDI uses declared ±2 bends and multiple ports.

Score regeneration is distinct from audio reproduction. Saved score JSON is authoritative for exact notes and timings; fixed sound states and renderer specify timbre and dynamics. Native plugin versions, sample banks and scheduling can produce small audio differences. Full byte-identical audio regeneration has not been claimed. Original exports and their hashes are preserved.

The slow polyphonic version shares the earlier source but has its own saved score/MIDI; use that score’s tempo. Audio-only auditions cannot be reconstructed exactly from unavailable note selections. They are archived honestly rather than supplied with invented generators.

`python experiments/verify.py` checks all archive hashes, Python syntax, indexed assets, and score availability. Thirteen full-piece generators (iterations 13–24 and 26) additionally underwent actual repeat-score checks in isolated prepared directories; see validation.json.

The latest recording uses prompt foreground attacks (6–14 ms outer edge smoothing) and reserves longer attacks for a small set of sustained background notes. Its renderer shortens TAL’s native envelope as well. The preceding Soft Machines snapshot keeps its original slower attacks so the comparison remains available.
