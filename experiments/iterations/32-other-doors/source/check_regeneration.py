"""Recreate all twelve saved scores and check representative amplitude gating."""
import hashlib,json
from pathlib import Path
import numpy as np
from compose_doors import Doors
from render_doors import note
r=Path('suite');hashes={}
for k in range(12):
 p=r/'scores'/f'{k+1:02}.json';before=hashlib.sha256(p.read_bytes()).hexdigest();Doors(k).complete();assert hashlib.sha256(p.read_bytes()).hexdigest()==before;hashes[str(k+1)]=before
s=json.loads((r/'scores/06.json').read_text());n=next(n for n in s['notes'] if n.get('dsp') and n['duration']>1);x=note(n);assert np.array_equal(x,note(n));assert np.mean(x==0)>.1
(r/'reproducibility.json').write_text(json.dumps(dict(all_twelve_scores_regenerate_identically=True,score_sha256=hashes,representative_gate_note_renders_identically=True,representative_gate_zero_fraction=float(np.mean(x==0))),indent=2));print('All twelve scores regenerate identically; amplitude gates retain actual zero intervals.')
