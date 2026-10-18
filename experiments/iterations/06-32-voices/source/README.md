# Calcutta: 32 rhythmic voices

A 3:12 piece at quarter note = 100, in 4/4. Each of the original 40 harmonies lasts two bars; the progression plays once in its original order.

The 32 voices follow the 16 final subdivision branches and each branch's lower/upper endpoint. They are not reassigned by pitch sorting, merged at unisons, or moved by octaves. Each voice keeps one sampled General MIDI instrument and a stereo position throughout. Instrument assignment separates all 41 pairs that come within 30 cents anywhere in the progression into different timbre families.

Each voice alternates notes and rests, drawing each duration independently and uniformly from 1–8 eighth notes. Starting note/rest states are independently randomized. These streams continue across bars and harmony changes. A sounding note that crosses a harmony boundary is retriggered at that branch's new pitch; its original rhythmic duration continues. Only events at the end of the piece are truncated.

The dry render uses TimGM6mb through FluidSynth, with per-instrument level balancing and a short release inside each note's gate. The score JSON retains the original logical events and the boundary-split notes. voice_instruments.csv identifies every construction branch and instrument.

## Reproduce

Install Python requirements with `python -m pip install -r requirements.txt`, plus libfluidsynth and a General MIDI soundfont. Then:

```sh
python rhythmic_voices.py --soundfont /path/to/TimGM6mb.sf2 --output output
ffmpeg -i output/calcutta_32_voices.wav -codec:a libmp3lame -q:a 2 output/calcutta_32_voices.mp3
```

Seed: 20261017. MIDI uses three MIDI ports and excludes percussion channels, preserving independent program changes and +/-2-semitone pitch bends for all 32 voices. Route all three ports when importing into a DAW. Pitch-bend rounding error is below 0.013 cents. The WAV/MP3 already contain the complete microtonal rendering.

The bundled supporting modules are the existing project renderers; rhythmic_voices.py is the entry point for this version.
