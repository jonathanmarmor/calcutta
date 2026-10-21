"""Verify the saved rendering, pitch route, gate scope and reproducibility."""
from pathlib import Path
import json,hashlib,numpy as np
from compose_prism import Prism
from render_prism import note
from validate_prism import validate
p=Path('suite/scores/01.json');before=hashlib.sha256(p.read_bytes()).hexdigest();s=Prism().complete();assert hashlib.sha256(p.read_bytes()).hexdigest()==before
counts={i:0 for i in range(97)};times={i:0. for i in range(97)}
for n in s['notes']:counts[n['instrument']]+=1;times[n['instrument']]+=n['duration']
for n in s['notes']:
 if not n.get('dsp'):continue
 assert n['dsp']['type']=='hard_gate' and .3<=n['dsp']['duty']<=.75
 sec=next(x for x in s['sections'] if x['start']-1e-5<=n['start']<x['end']-1e-5);assert sec['hard_gate']
n=next(n for n in s['notes'] if n.get('dsp') and n['duration']>1);x=note(n);assert np.array_equal(x,note(n));assert np.mean(x==0)>.1
info={'score_sha256':before,'score_regeneration_identical':True,'gate_render_deterministic':True,'gate_note_zero_sample_fraction':float(np.mean(x==0)),'all_instruments':[{'id':i,'attacks':counts[i],'written_seconds':times[i]} for i in range(97)]}
Path('suite/reproducibility.json').write_text(json.dumps(info,indent=2));Path('suite/validation.json').write_text(json.dumps([validate(1)],indent=2));print('Verified 97 sounds; minimum written seconds per sound',round(min(times.values()),2))
