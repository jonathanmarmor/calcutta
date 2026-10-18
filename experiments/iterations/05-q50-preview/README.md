# Sixteen bars at quarter = 50

More distinct instrumental timbres; 4/4 metrical hierarchy, sixteenth resolution, one harmony per bar.

[audio](calcutta_16_bars_q50.mp3) · [midi](calcutta_16_bars_q50.mid)

[Composition brief](BRIEF.md) · [Manifest and SHA-256 hashes](manifest.json)

frozen source and score available; external sound engines required.

Browse [frozen source](source/) or download [the original archive](source.zip). From the repository root, run `python experiments/reproduce.py 05-q50-preview prepare`, then use the snapshot’s own README/listening guide inside the prepared directory. `--list` prints entry points; `score` runs the known composer when a command has been verified. Archived audio is the historical reference: native plugin/platform variations can change rendered samples.

## Launch from the prepared snapshot root

```sh
python calcutta/instrument_sketch.py --seed 20261011 --soundfont /path/to/TimGM6mb.sf2 --output output
```

These early commands combine score creation and rendering. Native dependencies must be supplied for SoundFont/VST versions. The CLI was inspected against the saved source; early native audio has not been re-rendered during archival.
