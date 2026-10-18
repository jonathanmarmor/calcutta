# Phrased rhythm preview

Speech-like phrases, breaths, accents and shared temporary metrical overlays; expanded harmonic phrase.

[audio](phrased_preview.mp3) · [midi](phrased_preview.mid)

[Composition brief](BRIEF.md) · [Manifest and SHA-256 hashes](manifest.json)

frozen source and score available; external sound engines required.

Browse [frozen source](source/) or download [the original archive](source.zip). From the repository root, run `python experiments/reproduce.py 09-phrased-preview prepare`, then use the snapshot’s own README/listening guide inside the prepared directory. `--list` prints entry points; `score` runs the known composer when a command has been verified. Archived audio is the historical reference: native plugin/platform variations can change rendered samples.

## Launch from the prepared snapshot root

```sh
python phrased_preview.py --previous composition_32_voices_v3/score_and_sounds.json --runtime /path/to/synth_runtime --soundfont /path/to/TimGM6mb.sf2 --patches composition_32_voices_v3/patches --output output
```

These early commands combine score creation and rendering. Native dependencies must be supplied for SoundFont/VST versions. The CLI was inspected against the saved source; early native audio has not been re-rendered during archival.
