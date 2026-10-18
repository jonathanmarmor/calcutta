# Calcutta: mixed synthesizers

This is the unchanged version-2 score: 32 construction-branch voices, independently chosen 70% notes / 30% rests; event lengths uniformly selected from 1 through min(8 eighths, time until next harmony). Quarter note = 100; 4/4; two bars per harmony; the original 40 harmonies once, lasting 3:12.

## Sound palette

9 custom Surge XT sounds, 9 custom Vital sounds, 8 custom Dexed sounds, and 6 TimGM6mb/FluidSynth sounds. The custom patches suggest reeds, winds, brass, electric tines, glass, metal, organ, classic analog waveforms, and unfamiliar digital colors. Names describe the intended character, rather than a sampled acoustic instrument or a factory preset. All synth patches start from the engines' initialization settings and are constructed by the supplied Python code.

Sustained synth envelopes hold at full level. Pitch LFOs, oscillator drift/detuning, reverb, delay, and chorus are absent. The GM exceptions include piano, vibraphone, and tubular bells, whose natural decay is retained, plus church organ, accordion, and clarinet. Note audio is gated exactly to its score duration, with no release tail. A 32-sample (0.73 ms) edge rounding inside the note prevents clicks. No compressors or effects are used in the mix; reference-level balancing, fixed voice panning, and global peak normalization are applied.

Every pair of voices that comes within 30 cents is assigned different sound families. Harmonic-spectrum measurements are also used when distributing patches among the voices, to encourage contrast at these convergences.

## Files

- `calcutta_mixed_synths.mp3` / `.wav`: full piece.
- `palette_audition.mp3`: all 32 sounds in palette order, each on A4 for 2.4 seconds, followed by 0.35 seconds of silence. This lets you compare timbre and sustain independently of the piece.
- `palette.json`: patch parameters and measured sustain ratios, in audition order.
- `voice_sounds.csv`: voice, construction branch, synth, patch name, and timbre family.
- `score_and_sounds.json`: complete pitches, timings, and sound assignment.
- `patches/*.vststate`: Pedalboard raw VST3 states, loaded by assigning bytes to `plugin.raw_state`; these are not DAW-native preset files.

## Reproduce

Install Python dependencies `numpy mido pedalboard`, FluidSynth, the TimGM6mb soundfont, and the Linux VST3 builds of Surge XT, Vital, and Dexed. The render used Surge XT nightly 2026-10-16 (6b696b5), Vital 1.5.5, Dexed 1.0.1, and Pedalboard 0.9.26. Plugins and soundfonts are not included in this archive. Download them from their official projects:

- https://surge-synthesizer.github.io/
- https://vital.audio/
- https://github.com/asb2m10/dexed/releases

The runtime directory layout expected by the script is:

- `surge/usr/lib/vst3/Surge XT.vst3`
- `vital/` containing `Vital.vst3` at any depth
- `dexed/Dexed.vst3`

```sh
python mixed_synths.py --runtime /path/to/runtime --soundfont /path/to/TimGM6mb.sf2 --score calcutta_32_voices_v2.json --output output
ffmpeg -i output/calcutta_mixed_synths.wav -codec:a libmp3lame -q:a 2 output/calcutta_mixed_synths.mp3
```

The script reuses any cached probes in its output directory; use a fresh output directory after changing patches. Dexed's default three-semitone pitch-bend range is compensated separately from the other engines' two-semitone range. The acoustic instrument labels in the legacy voice records are historical; the `sound` object contains the actual assignment for this rendering.
