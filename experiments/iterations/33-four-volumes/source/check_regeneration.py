from pathlib import Path
import json,hashlib
import numpy as np
from compose_volumes import Volumes
from render_volumes import render_note
r=Path('suite');hashes={}
for k in range(16):
 p=r/'scores'/f'{k+1:02}.json';before=hashlib.sha256(p.read_bytes()).hexdigest();Volumes(k).complete();assert hashlib.sha256(p.read_bytes()).hexdigest()==before;hashes[str(k+1)]=before
checks=[]
for k,kind in [(5,'vocal'),(6,'effect'),(10,'gliss'),(12,'effect')]:
 s=json.loads((r/'scores'/f'{k:02}.json').read_text());n=next(n for n in s['notes'] if n.get(kind) and n['duration']>.3);x=render_note(n);assert np.isfinite(x).all() and np.array_equal(x,render_note(n));checks.append(dict(movement=k,kind=kind,note_id=n['id'],identical=True))
(r/'reproducibility.json').write_text(json.dumps(dict(all_sixteen_scores_regenerate_identically=True,score_sha256=hashes,special_renderer_checks=checks),indent=2));print('All sixteen scores regenerate identically; representative vocal, glide and DSP notes rerender identically.')
