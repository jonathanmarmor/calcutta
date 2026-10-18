# Full piece, corrected 32-voice mix

Upgrade guitar/bells and correct asynchronous synth loading/calibration that buried many voices. Includes click and no-click renders.

[audio](calcutta_full_music_corrected.mp3) · [click audio](calcutta_full_with_click_corrected.mp3) · [midi](calcutta_full.mid)

[Composition brief](BRIEF.md) · [Manifest and SHA-256 hashes](manifest.json)

frozen source and score available; external sound engines required.

Browse [frozen source](source/) or download [the original archive](source.zip). From the repository root, run `python experiments/reproduce.py 13-corrected-full prepare`, then use the snapshot’s own README/listening guide inside the prepared directory. `--list` prints entry points; `score` runs the known composer when a command has been verified. Archived audio is the historical reference: native plugin/platform variations can change rendered samples.
