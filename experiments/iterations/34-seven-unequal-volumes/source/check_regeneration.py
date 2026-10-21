from pathlib import Path
import json,hashlib
import numpy as np
from compose_seven import Seven
from render_seven import render_note
r=Path('suite');hashes={}
for k in range(33):
 p=r/'scores'/f'{k+1:02}.json';before=hashlib.sha256(p.read_bytes()).hexdigest();Seven(k).complete();assert hashlib.sha256(p.read_bytes()).hexdigest()==before;hashes[str(k+1)]=before
checks=[]
for k,kind in [(7,'vocal'),(15,'effect'),(26,'gliss'),(28,'effect'),(30,'vocal')]:
 s=json.loads((r/'scores'/f'{k:02}.json').read_text());n=next(n for n in s['notes'] if n.get(kind) and n['duration']>.3);x=render_note(n);assert np.isfinite(x).all() and np.array_equal(x,render_note(n));checks.append(dict(movement=k,kind=kind,note_id=n['id'],identical=True))
(r/'reproducibility.json').write_text(json.dumps(dict(all_thirty_three_scores_regenerate_identically=True,score_sha256=hashes,special_renderer_checks=checks),indent=2));print('All 33 scores regenerate identically; representative vocal, glide and DSP notes render identically.')
