"""Prepare immutable iteration snapshots and run registered deterministic composers."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent
COMMANDS={
 '26-bright-detours':['calcutta/detour_piece.py'],
 '14-dialogues':['calcutta/dialogue_piece.py'], '15-prisms':['calcutta/prism_piece.py'],
 '16-arrivals':['calcutta/arrival_piece.py'], '17-inventions':['calcutta/chamber_piece.py'],
 '18-archipelago':['calcutta/archipelago_piece.py'], '19-choirs':['calcutta/mobile_choirs.py'],
 '20-motifs':['calcutta/motif_choirs.py'], '21-elastic':['calcutta/elastic_piece.py'],
 '22-grace':['calcutta/grace_piece.py'], '23-soft-machines':['calcutta/murmur_piece.py'],
 '24-staircases-clocks':['calcutta/interleave_piece.py'], '13-corrected-full':['calcutta/full_piece.py']}
p=argparse.ArgumentParser();p.add_argument('iteration');p.add_argument('action',choices=['prepare','score'],nargs='?',default='prepare');p.add_argument('--list',action='store_true');a=p.parse_args()
source=ROOT/'iterations'/a.iteration/'source'
if not source.is_dir():p.error('No generation source was retained for this diagnostic; see its manifest.')
if a.list:
 print('Registered command:',COMMANDS.get(a.iteration,'Use original README CLI with its explicit options.'))
 for x in sorted(source.rglob('*')):
  if x.suffix=='.md':print(x.relative_to(source))
 sys.exit(0)
dest=REPO/'build'/'iterations'/a.iteration;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(source,dest,dirs_exist_ok=True)
for key,subdir in [('CALCUTTA_SYNTH_RUNTIME','synth_runtime'),('CALCUTTA_SOUNDFONT_RUNTIME','soundfont_runtime')]:
 value=os.environ.get(key)
 if value:
  path=dest/subdir
  if not path.exists():path.symlink_to(Path(value).resolve(),target_is_directory=True)
print('Prepared',dest,flush=True)
if a.action=='score':
 cmd=COMMANDS.get(a.iteration)
 if cmd is None:p.error('Use this snapshot’s documented CLI; score/render may be combined. No command has been invented.')
 subprocess.run([sys.executable,*cmd],cwd=dest,check=True)
