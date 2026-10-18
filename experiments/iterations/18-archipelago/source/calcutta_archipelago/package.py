import json,sys,inspect,zipfile
from pathlib import Path
import mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from phrased_preview import midi
from calcutta import get_fibonacci_ratios
root=Path('calcutta_archipelago');s=json.loads((root/'score.json').read_text());ratios=get_fibonacci_ratios()
fn=inspect.getsource(midi).replace("chr(65+h['chord'])","h['chord']+1").replace('.length-72',".length-score['duration_seconds']")
namespace={'mido':mido};exec(fn,namespace);namespace['midi'](s,root/'calcutta_archipelago.mid')
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'
def ratio(i):a,b,_=ratios[i];return f'{a}:{b}'
text='''# Calcutta: Archipelago

9:01.2, quarter note = 100, 4/4. No click or reverb. A separate exploration of the same 40 existing harmonies, with no new pitches or altered tuning fields.

The piece starts in the 3:5 harmony with roughly three sounding voices. The 1:2 harmony appears once, for 2.4 seconds, at 0:44.4. It serves as a brief expressive interruption rather than an opening center.

There are 68 visits to the original fields. Harmonic durations range from four to 24 quarter-note beats, including changes midway through a bar. The progression revisits nearby fields and turns back before moving forward. Longer harmonic phrases gather these visits into larger dynamic shapes.

Inside an unchanged field, smaller existing sonorities form another progression: often A–B–C–A with unequal durations. A search favors the characteristic sharp-third triads and closely tuned fifths, connecting them by small movements among their actual pitches. Early fields without those triads use their closest available fifths. No note is octave-transposed or snapped to equal temperament. Octave-reduced intervals are used only to identify seventh extensions already present in the original collection.

The chamber textures include melody and accompaniment, contrary answers, canonic returns, held tones over moving inner chords, and two root families overlapping. Each fixed one-pitch instrumental voice keeps its construction identity, so melodies pass between instruments. Sections can use only a subset of the harmony. Every original harmony also receives one protected complete presentation: all 32 construction voices sound together briefly, with uneven soft timbral blends and competing solo attacks removed.

The palette retains sampled instruments, Surge XT, and Dexed, including the previous version's English-horn and French-horn lines. One fixed calibration gain per sound preserves the different musical levels. Attacks and releases are smoothed within the written gate; no click, reverb, or chorus is added.

## Larger phrases

| Time | End | Textures | Relative dynamic target |
|---|---|---|---|
'''
for f in s['form']:text+=f"| {clock(f['start_seconds'])} | {clock(f['end_seconds'])} | {', '.join(x.replace('_',' ') for x in f['strategies'])} | {f['dynamic_db']:+} dB |\n"
text+='\nTargets describe the master envelope, not measured loudness. Transitions flow between phrase centers.\n\n## Texture ideas\n\n'
for k,v in s['strategy_descriptions'].items():text+=f"- **{k.replace('_',' ').title()}:** {v}\n"
text+='\n## Harmonic itinerary\n\n“Complete” gives the protected window in which all 32 voices are sounding. Other visits explore subsets. Repeated late Fibonacci fields can be extremely close in pitch; their original numerical definitions are retained.\n\n| Start | Field | Duration in quarter beats | Texture | Complete window |\n|---|---|---|---|---|\n'
for x in s['visits']:
 window=f"{clock(x['full_start_tick']*.05)}–{clock(x['full_end_tick']*.05)}" if x['full'] else '—'
 text+=f"| {clock(x['start']*.05)} | {ratio(x['chord'])} | {x['beats']} | {x['texture'].replace('_',' ')} | {window} |\n"
text+='\n## Internal chord routes\n\nVoice numbers identify existing endpoints. These are internal palettes, not newly added global harmonies. The routes provide harmonic material; a texture may sustain, break, interleave, or partially voice them.\n\n| Start | Field | Root voice route | Chord members along the route |\n|---|---|---|---|\n'
for x in s['internal_progressions']:
 text+=f"| {clock(x['start_seconds'])} | {ratio(x['chord'])} | {' → '.join(map(str,x['roots']))} | {'; '.join(','.join(map(str,g)) for g in x['chord_voices'])} |\n"
text+='''
## Reproduce

Run from the archive root:

```sh
python calcutta/archipelago_piece.py
python calcutta_archipelago/render.py
```

Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, Surge XT supporting patch format 31, and Dexed. Plugin paths are in the renderer and `calcutta/mixed_synths.py`. SoundFonts: TimGM6mb and GeneralUser GS (https://schristiancollins.com/generaluser.php). Third-party binaries/sample banks are not bundled. Configure `FLUIDSYNTH_LIBRARY`/`LD_LIBRARY_PATH` as needed. The score, fixed calibration, source field pitches, source palette, and plugin states are included.

MIDI has 32 tracks on three ports with independent ±2-semitone bends. It does not embed plugin states or the audio master dynamic envelope; the JSON and renderer describe the supplied recording.
'''
(root/'calcutta_archipelago_guide.md').write_text(text)
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
for n in s['notes']:
 h=s['harmonies'][n['harmony']];assert n['pitch']==pitches[h['chord']][n['voice']]
 assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end']
for chord in range(40):
 x=next(x for x in s['visits'] if x['chord']==chord and x['full']);mid=(x['full_start_tick']+x['full_end_tick'])//2
 assert {n['voice'] for n in s['notes'] if n['start_tick']<=mid<n['start_tick']+n['duration_ticks']}==set(range(32))
assert s['visits'][0]['chord']!=0
assert sum(x['chord']==0 for x in s['visits'])==1
with zipfile.ZipFile(root/'calcutta_archipelago_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 names=['archipelago_piece.py','chamber_piece.py','arrival_piece.py','prism_piece.py','mixed_synths.py','instrument_sketch.py','phrased_preview.py','polyphonic.py','calcutta.py','scalar_runs.py','render.py']
 paths=[Path('calcutta')/x for x in names]
 paths += [Path(x) for x in ['calcutta_inventions/score.json','calcutta_full/score.json','calcutta_full_fixed/levels.jsonl','composition_32_voices_v3/score_and_sounds.json']]
 paths += list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
 paths += [root/x for x in ['score.json','render.py','package.py','calcutta_archipelago.mid','calcutta_archipelago_guide.md','levels.jsonl','section_levels.json'] if (root/x).exists()]
 for p in paths:z.write(p,str(p))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nmido\npedalboard==0.9.26\n')
print('Verified unchanged pitch fields and all 40 complete presentations; MIDI duration',mido.MidiFile(root/'calcutta_archipelago.mid').length)
