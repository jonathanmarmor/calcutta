"""Verify archive integrity, links, and Python syntax without native synths."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
entries=json.loads((ROOT/'manifest.json').read_text());count=0
for e in entries:
 d=ROOT/'iterations'/e['id'];m=json.loads((d/'manifest.json').read_text())
 for name,digest in m['sha256'].items():
  f=d/name;assert f.is_file(),f;assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,f;count+=1
 for name in ['audio','click_audio','midi','archive']:
  if name in m:assert (ROOT/m[name]).is_file(),m[name]
 for f in (d/'source').rglob('*.py'):
  try:ast.parse(f.read_text())
  except SyntaxError as err:raise RuntimeError(f'{f}: {err}')
print(f'Verified {len(entries)} iterations and {count} hashed historical files.')
