from pathlib import Path
import json,zipfile,importlib.metadata
r=Path('suite');out=Path('release');s=json.loads((r/'score.json').read_text());v=json.loads((r/'validation.json').read_text())
def clock(t):return f'{int(t)//60}:{int(t)%60:02}'
text='''# Calcutta: Slow Apertures

**14:00 · 58 timbral sources · 688 long sustained strands**

[Listen](calcutta_slow_apertures.mp3).

A mostly sustained movement across the full original register, from MIDI 48 to approximately 96.113. Different instrumental colors enter and leave over tens of seconds. Their steady spectra replace the previous prompt attacks and plucked decay. Individually shaped timbral waves overlap, while trills, arpeggiations and softer chordal particles gradually appear inside the sustained layer.

Individual sustained-tone entrances last roughly 18–49 seconds and exits roughly 22–61 seconds. The eight event clouds have longer group envelopes; their event density also rises and falls. Thus a texture can enter by both getting louder and becoming more populated, and leave through the reverse process. These are sin-squared note/cloud envelopes, not one master fade.

## Slowly appearing textures

| Approximate span | Texture |
|---|---|
'''
for c in s['clouds']:text+=f"| {clock(c['start'])}–{clock(c['start']+c['duration'])} | {c['kind']} |\n"
text+='''
The source harmonies launch about twelve seconds apart, but this movement deliberately overlaps their long fixed-pitch strands. Every tone keeps its original source-field pitch until its own fade ends; there is no pitch bend or mid-note retuning. Neighboring source fields therefore coexist during gradual handoffs. It begins beyond the 1:2 field, visits that field more quietly afterward, and traverses all forty source fields.

The final chord emerges around 7:55–8:00; after **9:18** only the destination field remains. That leaves slightly more than the last third entirely inside the golden-ratio harmony, with continued timbral and textural change. The ending consists of different strands and clouds withdrawing individually.

There is no reverb, delay, chorus, detuning, pitch LFO/vibrato, voice synthesis or click. The eight soft clouds alternate distinct original pitches rather than using vibrato or continuous glissandi. No passing tones or octave substitutes are added. Earlier constraints on immediate attacks/releases and short harmonic boundaries are intentionally superseded by this request for very long fades. The source models are the inherited sample-derived acoustic/electric/analog/FM colors, reconstructed here from steady spectra, not untouched samples or new live plugins.

## Inspect and reproduce

Unpack the source, install FFmpeg and the pinned Python requirements, then run:

```sh
python compose_slow.py
python render_slow.py
python export_midi.py
python validate_slow.py
python package_slow.py
```

The saved compact models suffice; no external bank or native plugin is required. The original request and public composition instructions are in `suite/BRIEF.md`. `suite/score.json` preserves each fixed pitch/source field, note envelope, cloud identity, timbre and voice lane. `compose_slow.py` records cloud density and note-selection logic; `render_slow.py` implements the steady carriers and slow envelopes. Source provenance and the GeneralUser GS license are included. Public decisions are retained, not hidden reasoning.

The MIDI uses independent pitch-bend lanes and CC11 expression curves for the note and group envelopes. It uses a seconds-based timing grid rather than implying a metrical pulse. External sound engines interpret program/envelope controls differently; the supplied renderer is authoritative. Source audio is 24 kHz stereo, with a 48 kHz / 256 kbps MP3 listening copy.

Validation checks exact source-field pitches, no held retuning, all forty source fields, long envelope spans, whole-register coverage through most of the body, exclusive final-field residence after 9:18, independent MIDI lanes, identical score regeneration, complete WAV bytes, MP3 length, output peaks and positive source energy. Sustaining tones account for approximately '''+str(round(v['sustained_energy_fraction']*100,1))+'''% of the summed individual layer energy before stereo summation. This is an energy accounting measure, not a perceptual loudness claim.
'''
(out/'calcutta_slow_apertures_guide.md').write_text(text);Path('README.md').write_text(text);Path('requirements.txt').write_text(''.join(f'{p}=={importlib.metadata.version(p)}\n' for p in ['numpy','scipy','mido']))
files=[Path(p) for p in ['README.md','requirements.txt','compose_slow.py','render_slow.py','render_base.py','export_midi.py','validate_slow.py','package_slow.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for p in (r/'models').glob('*.npz') if not p.name.startswith('.')]
files += [r/p for p in ['score.json','slow_apertures.mid','BRIEF.md','audio_audit.json','validation.json','palette.json','native_sources.json','model_provenance.json']]
dest=out/'calcutta_slow_apertures_source.zip';temp=dest.with_suffix('.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.as_posix())
with zipfile.ZipFile(temp) as z:assert z.testzip() is None
temp.replace(dest);print('Packaged audio, guide and repeatable source.')
