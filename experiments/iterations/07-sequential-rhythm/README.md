# Sequential note/rest decisions

Generate each rhythm from beginning to end: independent 70% notes / 30% rests, durations capped by the next change.

[audio](calcutta_32_voices_v2.mp3) · [midi](calcutta_32_voices_v2.mid)

[Composition brief](BRIEF.md) · [Manifest and SHA-256 hashes](manifest.json)

frozen source and score available; external sound engines required.

Browse [frozen source](source/) or download [the original archive](source.zip). From the repository root, run `python experiments/reproduce.py 07-sequential-rhythm prepare`, then use the snapshot’s own README/listening guide inside the prepared directory. `--list` prints entry points; `score` runs the known composer when a command has been verified. Archived audio is the historical reference: native plugin/platform variations can change rendered samples.

## Launch from the prepared snapshot root

```sh
python rhythmic_voices_v2.py --soundfont /path/to/TimGM6mb.sf2 --output output
```

These early commands combine score creation and rendering. Native dependencies must be supplied for SoundFont/VST versions. The CLI was inspected against the saved source; early native audio has not been re-rendered during archival.
