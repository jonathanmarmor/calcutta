"""Validate pitch identity, route, voice allocation, DSP scope and complete audio."""
from pathlib import Path
import json,hashlib,wave,subprocess,collections
import numpy as np
ROOT=Path('suite');P=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
def validate(k,audio=True):
 s=json.loads((ROOT/'scores'/f'{k:02}.json').read_text());ns=s['notes'];coverage=set();inst=set();gates=0
 for n in ns:
  h=s['harmonies'][n['fields'][0]];assert h['start']-1e-5<=n['start']<n['start']+n['duration']<=h['end']+1e-5
  assert min(abs(n['pitch']-p) for p in P[h['chord']])<1e-8;assert not n['is_passing'];inst.add(n['instrument']);coverage.add(h['chord'])
  if n.get('dsp'):
   g=n['dsp'];assert k==6 and g['type']=='hard_gate' and .3<=g['duty']<=.75 and g['edge_ms']==1.;gates+=1
 for v in range(len(s['voices'])):
  own=[n for n in ns if n['voice']==v];assert all(a['start']+a['duration']<=b['start']+1e-5 for a,b in zip(own,own[1:]))
 for n in ns:
  area=next(a for a in s['areas'] if a['start']-1e-5<=n['start']<a['end']+1e-5);h=s['harmonies'][n['fields'][0]];assert area['first']<=h['chord']<=area['last']
 assert all(a['first']<=b['first'] and a['last']<=b['last'] for a,b in zip(s['areas'],s['areas'][1:]));assert s['harmonies'][0]['chord']!=0
 assert s['final_chord_fraction']>=1/3;assert all(h['chord']==39 for h in s['harmonies'] if h['end']>s['final_chord_start']+1e-5)
 assert coverage==({39} if k==7 else set(range(40)))
 assert max(x['end']-x['start'] for x in s['sections'])<=25.01
 counts=collections.Counter(n['instrument'] for n in ns);assert len(counts)>=(10 if k==7 else 30)
 pal=json.loads((ROOT/'palette.json').read_text());assert all(not pal[i]['vibrato'] and not pal[i]['frequency_modulation'] for i in inst)
 ts=np.arange(0,s['duration'],.1);layers=np.zeros(len(ts),int)
 for n in ns:layers[(ts>=n['start'])&(ts<n['start']+n['duration'])]+=1
 out=dict(number=k,title=s['title'],duration=s['duration'],notes=len(ns),source_sounds=len(inst),source_ids=sorted(inst),fields=len(coverage),gated_notes=gates,mean_written_layers=float(np.mean(layers)),fraction_four_or_more=float(np.mean(layers>=4)),maximum_written_layers=int(max(layers)),texture_procedures=sorted(set(x['texture'] for x in s['sections'])),maximum_scene_seconds=max(x['end']-x['start'] for x in s['sections']),final_chord_fraction=s['final_chord_fraction'],pitch_check='All exact original field members; no passing tones, octave substitutes or held retuning')
 if audio:
  with wave.open(str(ROOT/'audio'/f'{k:02}.wav')) as w:
   assert w.getframerate()==24000 and abs(w.getnframes()/24000-s['duration'])<1e-4
   total=0;peak=0.;energy=0.;samples=0
   while block:=w.readframes(24000*10):
    x=np.frombuffer(block,'<i2').astype(np.float32)/32768;total+=len(block);peak=max(peak,float(max(abs(x))));energy+=float(np.dot(x,x));samples+=len(x)
   assert total==w.getnframes()*4 and peak<.78 and energy>0
  mp3=next((ROOT/'audio').glob(f'{k:02}_*.mp3'));d=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(mp3)]))['format']['duration']);assert abs(d-s['duration'])<.12
  audit=json.loads((ROOT/'audio'/f'{k:02}_audit.json').read_text());assert set(map(int,audit['source_instrument_energy']))==inst and all(v>0 for v in audit['source_instrument_energy'].values());assert audit['constant_frequency_carriers']
  out.update(audio_peak=peak,audio_rms=(energy/samples)**.5,audio_duration=d,all_sources_render_positive_energy=True)
 return out
if __name__=='__main__':
 import sys
 audio='--score-only' not in sys.argv;results=[validate(k,audio) for k in range(1,13)];assert set(i for x in results for i in x['source_ids'])==set(range(97));assert sum(x['duration'] for x in results)+22==3600
 (ROOT/('validation.json' if audio else 'score_validation.json')).write_text(json.dumps(results,indent=2))
 print('Validated twelve forms, exact pitches, advancing harmonic regions, final-field residence, DSP scope and 60:00 album duration.')
 for x in results:print(x['number'],x['source_sounds'],x['mean_written_layers'],x['fraction_four_or_more'])
