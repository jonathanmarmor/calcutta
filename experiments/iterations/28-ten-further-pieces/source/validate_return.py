from pathlib import Path
import json,wave,collections
import numpy as np
ROOT=Path('suite');PITCHES=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
def validate(number,audio=True):
 s=json.loads((ROOT/'scores'/f'{number:02}.json').read_text());notes=s['notes'];nd={n['id']:n for n in notes};coverage=set();count=0
 for n in notes:
  h=s['harmonies'][n['fields'][0]];assert h['start']-1e-5<=n['start']<n['start']+n['duration']<=h['end']+1e-5;assert n['duration']>.02;assert not n.get('dsp')
  if not n['is_passing']:
   assert min(abs(n['pitch']-x) for x in PITCHES[h['chord']])<1e-8;coverage.add(h['chord'])
  else:
   a=n['anchors'];f,t=nd[a['from_id']],nd[a['to_id']];assert f['part']==n['part']==t['part'];assert f['instrument']==n['instrument']==t['instrument'];assert f['fields']==n['fields']==t['fields'];assert not f['is_passing'] and not t['is_passing'];assert min(f['pitch'],t['pitch'])<n['pitch']<max(f['pitch'],t['pitch']);assert n['duration']<=.440001;assert n['velocity']<f['velocity'];assert f['start']<n['start']<t['start'];assert n['start']+n['duration']<=t['start']+1e-5;count+=1
 assert len(coverage)==40
 for v in range(len(s['voices'])):
  own=sorted([n for n in notes if n['voice']==v],key=lambda n:n['start']);assert all(a['start']+a['duration']<=b['start']+1e-5 for a,b in zip(own,own[1:]))
 assert max(sec['end']-sec['start'] for sec in s['sections'])<30
 times=np.arange(0,s['duration'],.1);layers=np.zeros(len(times),int)
 for n in notes:layers[(times>=n['start'])&(times<n['start']+n['duration'])]+=1
 sparse=float(np.sum((layers>=1)&(layers<=2))*.1);dense=float(np.sum(layers>=5)*.1);assert sparse>35 and dense>15
 a=dict(number=number,title=s['title'],notes=len(notes),passing_notes=count,fields=40,sampled_attack_fraction=sum(n['instrument']>=8 for n in notes)/len(notes),maximum_layers=int(max(layers)),sparse_seconds=round(sparse,1),dense_seconds=round(dense,1),maximum_section_seconds=max(sec['end']-sec['start'] for sec in s['sections']),pitch_audit='Structural notes are exact field members; passing notes validated against same-part, same-field structural endpoints; constant pitch per note')
 if audio:
  with wave.open(str(ROOT/'audio'/f'{number:02}.wav')) as w:
   assert w.getframerate()==24000 and abs(w.getnframes()/24000-s['duration'])<.001
   x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768;assert np.isfinite(x).all() and max(abs(x))<.78
  m=json.loads((ROOT/'audio'/f'{number:02}_audit.json').read_text());assert m['notes']==len(notes);a['audio']=m
 return a
if __name__=='__main__':
 out=[validate(k) for k in range(1,11)];(ROOT/'validation.json').write_text(json.dumps(out,indent=2));print('Validated ten pieces: exact structural pitches, genuine passing connections, all 40 fields, sparse/dense passages, independent monophony and audio gates.')
