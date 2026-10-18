# Calcutta: full piece

A fresh full-length realization at quarter note = 100, 4/4. Duration: 9:21.6 (234 bars). The 40 original harmonies are paired as A/B, C/B, C/D, E/D, E/F, and so on; each pair is played for 2 bars, 2 bars, 1 bar, 1 bar. There are 39 pairs and 156 individual harmonic spans.

All 32 subdivision-tree endpoints remain independent voices, including coincident pitches. New seed 2026101744 generates 18,082 sounding segments with the simpler phrase rules from the last preview: quarter beats dominate, subdivisions remain quieter, and quiet pickups resolve into quarter-note anchors. Every voice sounds in each harmonic span. Phrases have clear breathing gaps, tenuto/ordinary/staccato articulation, and wide dynamic shaping.

The 24 sampled-instrument / 8 synthesizer assignments from the last preview are retained. Clean electric guitar, clean jazz guitar, and tubular bells now use GeneralUser GS instead of the compact TimGM6mb samples. All other sampled instruments still use TimGM6mb. The synths are real Surge XT, Vital, and Dexed VST3 engines. There is no reverb or chorus. Note entrances and endings are smoothed inside each written gate, without release tails or pitch detuning in the custom patches.

## Audio

- `calcutta_full_with_click.mp3`: full piece with quarter-note click, higher tone on beat 1. Same louder click level as the last preview.
- `calcutta_full_music.mp3`: identical music without the click. Both exports use the same musical gain.
- `calcutta_full.mid`: score with written dynamics and microtonal bends, using three MIDI ports for 32 independent voices. MIDI does not contain the instrument samples or VST patches. The exported bend range is two semitones; the audio renderer separately compensates for Dexed's default three-semitone range.

## Sample credits

GeneralUser GS by S. Christian Collins:
https://schristiancollins.com/generaluser.php
https://github.com/mrbumpy409/GeneralUser-GS

The source bank was downloaded from the author's repository:
https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/GeneralUser-GS.sf2

TimGM6mb is the compact General MIDI bank used in the preceding versions. All samples and plugin binaries remain external dependencies.

## Reproduce

Install the Python requirements, libfluidsynth, the two SoundFonts, and the Surge XT / Vital / Dexed VST3 builds described in SYNTH_SETUP.md. The existing synth_runtime layout and soundfont_runtime layout are used by the scripts. Place GeneralUser GS at `soundfont_runtime/GeneralUser-GS.sf2`.

```sh
python calcutta/full_piece.py
LD_LIBRARY_PATH=/path/to/fluidsynth/lib FLUIDSYNTH_LIBRARY=/path/to/libfluidsynth.so.3 python calcutta_full_fixed/render_full.py
ffmpeg -i calcutta_full/calcutta_full_with_click.wav -codec:a libmp3lame -q:a 2 calcutta_full/calcutta_full_with_click.mp3
ffmpeg -i calcutta_full/calcutta_full_music.wav -codec:a libmp3lame -q:a 2 calcutta_full/calcutta_full_music.mp3
```

The archive includes the generated score, MIDI, source scripts, prior metadata needed by the composer, and the custom raw VST3 patch states. It does not include the plugins or SoundFonts. `score.json` records exact note timings, branch identities, pitches, dynamics, harmonies, and the sample-bank upgrades.

## Corrected mix

Silent short reference renders during asynchronous Surge patch loading incorrectly produced a gain of 3200, burying the other instruments after master normalization. This correction warms and validates the plugin before rendering, balances each actual performed stem using one constant gain, rejects silent stems and excessive gain, and checks all 32 output levels. The shared note renderer now retries silent startup renders and fails explicitly if they remain silent. Rhythms, tuning, instruments, and note dynamics are unchanged. Corrected audio filenames end in `_corrected`.
