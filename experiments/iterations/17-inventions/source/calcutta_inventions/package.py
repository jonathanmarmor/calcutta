from pathlib import Path
import json,sys,inspect,zipfile
import mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from phrased_preview import midi
root=Path('calcutta_inventions');s=json.loads((root/'score.json').read_text())
fn=inspect.getsource(midi).replace("chr(65+h['chord'])","h['chord']+1").replace('.length-72',".length-score['duration_seconds']")
namespace={'mido':mido};exec(fn,namespace);namespace['midi'](s,root/'calcutta_inventions.mid')
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'
text='''# Calcutta: Small Inventions

9:21.6, quarter note = 100, 4/4. All 32 construction voices remain distinct. No click or reverb. Each instrument keeps its assigned position in the tuning ladder, following that position through the chord changes. Melodies therefore travel between instruments rather than transposing a single instrumental voice.

The dense opening still makes the changing harmonies explicit. It begins to thin at 2:52.8; from 3:21.6, there are 25 chamber studies centered on the tuning's sharp-third triads and seventh extensions. There are no reggae sections.

Several studies stay with one root family for six bars. Others switch between two roots or layer their triads. Melodies have returning motifs and altered answers, with slower accompaniment, contrary motion, canonic entries, sighing duets, and an occasional repeating bass ground. Accompaniment can be interrupted when one of its instruments joins the melody, producing moving inner voices. Note accents and sectional dynamic arcs both shape the phrasing.

The characteristic triads have thirds near 433.832 cents and fifths near 701.955 cents. Seventh extensions are selected near 968.826 or 1088.269 cents, with a maximum selection error of 40 cents. These are the consonant elements available in this unusual tuning, not ordinary just-intonation triads/sevenths. The table below reports their actual intervals. Some extensions sit more than an octave above the root.

The sound palette includes sampled winds, guitars, keyboards, bells and basses, plus Surge XT and Dexed. Two lines have new English-horn and French-horn colors. Each sound has one fixed calibration gain, preserving musical dynamics. Releases are gated cleanly with a short smoothing ramp, and struck/plucked instruments retain their natural decay.

## Listening map

| Time | Bars | Texture | Relative dynamic target |
|---|---|---|---|
'''
for f in s['form']:text+=f"| {clock(f['start_seconds'])} | {f['start_bar']}–{f['start_bar']+5} | {', '.join(t.replace('_',' ') for t in f['strategies'])} | {f['dynamic_db']:+} dB |\n"
text+='\nTargets describe the master envelope, not measured loudness. Transitions flow between section centers.\n\n## Chamber ideas\n\n'
for k,v in s['strategy_descriptions'].items():text+=f"- **{k.replace('_',' ').title()}:** {v}\n"
text+='\n## Sonority families\n\nThese are the two palettes explored by each study; not every study sounds both sevenths. Intervals are octave-reduced cents above their respective roots. Voice numbers refer to construction identity.\n\n| Time | Root voice | Palette voices | Intervals above root |\n|---|---|---|---|\n'
for h in s['consonance_highlights']:
 text+=f"| {clock(h['start_tick']*.05)} | {h['voices'][0]} | {', '.join(map(str,h['voices']))} | {', '.join(map(str,h['intervals_cents']))} |\n"
text+='''
## Reproduce

Run the composer and renderer from the archive root:

```sh
python calcutta/chamber_piece.py
python calcutta_inventions/render.py
```

Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, Surge XT (patch format 31 or newer), Dexed. The renderer expects plugin paths in `calcutta/mixed_synths.py`. SoundFonts: TimGM6mb and GeneralUser GS (https://schristiancollins.com/generaluser.php). Third-party binaries and sample banks are not bundled. Configure `FLUIDSYNTH_LIBRARY`/`LD_LIBRARY_PATH` when needed. The score, fixed calibration, and plugin states are included.

The MIDI contains 32 tracks on three ports with independent ±2-semitone pitch bends. It does not embed plugin states or the rendered master-envelope dynamics; the JSON score and renderer describe the supplied audio.
'''
(root/'calcutta_inventions_guide.md').write_text(text)
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
for v in range(32):
 own=[n for n in s['notes'] if n['voice']==v];assert own
 assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
for n in s['notes']:
 h=s['harmonies'][n['harmony']]
 assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end']
 assert n['pitch']==pitches[h['chord']][n['voice']]
assert not any('reggae' in n['strategy'] for n in s['notes'])
with zipfile.ZipFile(root/'calcutta_inventions_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 paths=[Path('calcutta')/x for x in ['chamber_piece.py','arrival_piece.py','prism_piece.py','mixed_synths.py','instrument_sketch.py','phrased_preview.py','polyphonic.py','calcutta.py','scalar_runs.py','render.py']]
 paths += [Path('calcutta_full/score.json'),Path('calcutta_full_fixed/levels.jsonl'),Path('composition_32_voices_v3/score_and_sounds.json')]
 paths+=list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
 paths += [root/x for x in ['score.json','render.py','package.py','calcutta_inventions.mid','calcutta_inventions_guide.md','levels.jsonl','section_levels.json'] if (root/x).exists()]
 for p in paths:z.write(p,str(p))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nmido\npedalboard==0.9.26\n')
print('Validated all 32 voices, construction pitches, monophony, harmonic boundaries, and no reggae')
