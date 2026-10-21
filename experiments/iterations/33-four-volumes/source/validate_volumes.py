from pathlib import Path
import json,wave,subprocess,collections
import numpy as np
from plan import PIECES,VOLUMES
P=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches'];ROOT=Path('suite')
def validate(k,audio=True):
 s=json.loads((ROOT/'scores'/f'{k:02}.json').read_text());notes=s['notes'];coverage=set();counts=collections.Counter()
 for n in notes:
  h=s['harmonies'][n['fields'][0]];assert h['start']-1e-5<=n['start']<n['start']+n['duration']<=h['end']+1e-5,(k,n)
  if k==9:assert n['pitch']==round(n['pitch'])
  else:assert min(abs(n['pitch']-p) for p in P[h['chord']])<1e-8
  if n.get('gliss'):assert k==10 and min(abs(n['gliss']['to_pitch']-p) for p in P[h['chord']])<1e-8
  if n.get('vocal'):assert k in [5,8] and n['instrument'] in range(97,101)
  if n.get('effect'):assert k in [6,12] and n['effect']['type'] in ['multitap','reverse_grains']
  assert not n.get('dsp');coverage.add(h['chord']);counts[n['instrument']]+=1
 assert len(coverage)==40 and s['harmonies'][0]['chord']!=0
 for v in range(len(s['voices'])):
  own=[n for n in notes if n['voice']==v];assert all(a['start']+a['duration']<=b['start']+1e-5 for a,b in zip(own,own[1:]))
 assert all(a['first']<=b['first'] and a['last']<=b['last'] for a,b in zip(s['areas'],s['areas'][1:]));assert all(h['chord']==39 for h in s['harmonies'] if h['end']>s['final_chord_start']+1e-5)
 assert max(x['end']-x['start'] for x in s['sections'])<30
 out=dict(number=k,title=s['title'],duration=s['duration'],notes=len(notes),instruments=len(counts),tuning_mode=s['tuning_mode'],ending=s['ending'],vocal_notes=sum('vocal' in n for n in notes),gliss_notes=sum('gliss' in n for n in notes),effect_notes=sum('effect' in n for n in notes),fields=40,source_ids=sorted(counts),maximum_scene_seconds=max(x['end']-x['start'] for x in s['sections']))
 ts=np.arange(0,s['duration'],.2);layers=np.zeros(len(ts),int)
 for n in notes:layers[(ts>=n['start'])&(ts<n['start']+n['duration'])]+=1
 out.update(mean_written_layers=float(np.mean(layers)),fraction_four_or_more=float(np.mean(layers>=4)))
 if audio:
  with wave.open(str(ROOT/'audio'/f'{k:02}.wav')) as w:
   assert w.getframerate()==24000 and abs(w.getnframes()/24000-s['duration'])<1e-4
   total=0;peak=0.;energy=0.;samples=0
   while block:=w.readframes(240000):
    x=np.frombuffer(block,'<i2').astype(np.float32)/32768;total+=len(block);peak=max(peak,float(max(abs(x))));energy+=float(np.dot(x,x));samples+=len(x)
   assert total==w.getnframes()*4 and peak<.78 and energy>0
  mp3=next((ROOT/'audio').glob(f'{k:02}_*.mp3'));d=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(mp3)]))['format']['duration']);assert abs(d-s['duration'])<.12
  audit=json.loads((ROOT/'audio'/f'{k:02}_audit.json').read_text());assert set(map(int,audit['source_energy']))==set(counts) and all(v>0 for v in audit['source_energy'].values());out.update(audio_peak=peak,audio_rms=(energy/samples)**.5,mp3_duration=d,all_scored_sources_positive_energy=True)
 return out
if __name__=='__main__':
 import sys
 audio='--score-only' not in sys.argv;out=[validate(k,audio) for k in range(1,17)];assert len(set(x['ending'] for x in out))==16
 assert {x['number'] for x in out if x['vocal_notes']}=={5,8};assert {x['number'] for x in out if x['effect_notes']}=={6,12};assert {x['number'] for x in out if x['gliss_notes']}=={10}
 for v,(_,seconds) in enumerate(VOLUMES):assert sum(x['duration'] for x in out[v*4:v*4+4])+6==seconds
 assert sum(x['duration'] for x in out)+24==7200
 (ROOT/('validation.json' if audio else 'score_validation.json')).write_text(json.dumps(out,indent=2));print('Validated 16 distinct endings, four volumes totaling 2 hours, bounded pitch/vocal/effects exceptions and harmonic routes.')
