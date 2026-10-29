"""Score, harmonic route, density, metrical onset and rendered audio checks."""
from pathlib import Path
import json,wave
import numpy as np
ROOT=Path('suite');PITCHES=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
def validate(number,audio=True):
 s=json.loads((ROOT/'scores'/f'{number:02}.json').read_text());notes=s['notes'];nd={n['id']:n for n in notes};coverage=set();passes=0
 for n in notes:
  h=s['harmonies'][n['fields'][0]];assert h['start']-1e-5<=n['start']<n['start']+n['duration']<=h['end']+1e-5;assert not n.get('dsp')
  if not n['is_passing']:assert min(abs(n['pitch']-x) for x in PITCHES[h['chord']])<1e-8;coverage.add(h['chord'])
  else:
   a=n['anchors'];f,t=nd[a['from_id']],nd[a['to_id']];assert f['part']==n['part']==t['part'];assert f['instrument']==n['instrument']==t['instrument'];assert f['fields']==n['fields']==t['fields'];assert not f['is_passing'] and not t['is_passing'];assert min(f['pitch'],t['pitch'])<n['pitch']<max(f['pitch'],t['pitch']);assert n['duration']<=.400001;assert n['velocity']<f['velocity'];assert f['start']<n['start']<t['start'];assert n['start']+n['duration']<=t['start']+1e-5;passes+=1
 assert len(coverage)==40
 for v in range(len(s['voices'])):
  own=sorted([n for n in notes if n['voice']==v],key=lambda n:n['start']);assert all(a['start']+a['duration']<=b['start']+1e-5 for a,b in zip(own,own[1:]))
 areas=s['areas'];assert all(a['first']<=b['first'] and a['last']<=b['last'] for a,b in zip(areas,areas[1:]))
 for h in s['harmonies']:
  mid=(h['start']+h['end'])/2
  area=next(a for a in areas if a['start']-1e-5<=mid<a['end']+1e-5)
  assert area['first']<=h['chord']<=area['last']
 # Every structural attack is also in the currently active adjacent-field area.
 for n in notes:
  area=next(a for a in areas if a['start']-1e-5<=n['start']<a['end']+1e-5)
  assert area['first']<=s['harmonies'][n['fields'][0]]['chord']<=area['last']
 assert s['final_chord_fraction']>=1/3
 assert all(h['chord']==39 for h in s['harmonies'] if h['end']>s['final_chord_start']+1e-5)
 assert max(sec['end']-sec['start'] for sec in s['sections'])<30
 times=np.arange(0,s['duration'],.1);layers=np.zeros(len(times),int)
 for n in notes:layers[(times>=n['start'])&(times<n['start']+n['duration'])]+=1
 fuller=float(np.mean(layers>=4));thin=float(np.mean((layers>=1)&(layers<=2)));assert fuller>.85 and thin<.08
 onsets=np.array(sorted(n['start'] for n in notes));beats=np.array(s['metric_grid'][2:-3]);idx=np.searchsorted(onsets,beats);distance=np.minimum(abs(onsets[np.maximum(idx-1,0)]-beats),abs(onsets[np.minimum(idx,len(onsets)-1)]-beats));pulse=float(np.mean(distance<.065));assert pulse>.8
 a=dict(number=number,title=s['title'],notes=len(notes),passing_notes=passes,fields=40,sampled_attack_fraction=sum(n['instrument']>=8 for n in notes)/len(notes),mean_active_notes=float(np.mean(layers)),maximum_layers=int(max(layers)),fraction_four_or_more=fuller,fraction_one_or_two=thin,quarter_beats_with_nearby_musical_attack=pulse,final_field_start=s['final_chord_start'],final_field_fraction=s['final_chord_fraction'],maximum_scene_seconds=max(sec['end']-sec['start'] for sec in s['sections']),pitch_audit='Exact structural field pitches; genuine same-field, same-part passing connections; no held-note retuning',harmonic_route_audit='Adjacent windows advance monotonically; final field 39 exclusively after convergence')
 if audio:
  with wave.open(str(ROOT/'audio'/f'{number:02}.wav')) as w:
   assert w.getframerate()==24000 and abs(w.getnframes()/24000-s['duration'])<.001
   data=w.readframes(w.getnframes());assert len(data)==w.getnframes()*4
   x=np.frombuffer(data,'<i2').astype(np.float32)/32768;assert np.isfinite(x).all() and max(abs(x))<.78
  m=json.loads((ROOT/'audio'/f'{number:02}_audit.json').read_text());assert m['notes']==len(notes);mp3=next((ROOT/'audio').glob(f'{number:02}_*.mp3'));duration=float(json.loads(__import__('subprocess').check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(mp3)]))['format']['duration']);assert abs(duration-s['duration'])<.12
  a['audio']=m
  assert m['constant_frequency_carriers'] and m['instruments_sounding']>=64
 assert s['harmonies'][0]['chord']!=0
 counts=__import__('collections').Counter(n['instrument'] for n in notes);assert len(counts)==64 and set(counts)==set(s['instrument_pool'])
 assert len(set(tuple(x['instruments']) for x in s['ensembles']))>20
 palette=json.loads((ROOT/'palette.json').read_text());assert all(not palette[i]['vibrato'] and not palette[i]['frequency_modulation'] for i in counts)
 a.update(instrument_count=len(counts),minimum_attacks_per_instrument=min(counts.values()),opening_field=s['harmonies'][0]['chord'],different_section_ensembles=len(set(tuple(x['instruments']) for x in s['ensembles'])),vibrato_audit='Fixed-frequency carriers; no pitch modulation parameters, detuned pairs or LFOs')
 return a
if __name__=='__main__':
 import sys
 audio='--score-only' not in sys.argv;out=[validate(k,audio) for k in range(1,6)];(ROOT/'validation.json').write_text(json.dumps(out,indent=2));print('Validated five expanded ensembles and progressive routes, final-third residence, fuller textures, pulse and pitch policy.')
