from pathlib import Path
import sys,json,numpy as np
sys.path.insert(0,str(Path('calcutta').resolve()))
from soundfont_capture import SoundfontSynth
# Optional re-capture; saved atoms already suffice for every performance.
s=SoundfontSynth(Path(sys.argv[1]),24000)
more=[('Oboe',68),('Flute',73),('Cello',42),('Viola',41),('Violin',40),('Acoustic bass',32),('Celesta',8),('Clean electric guitar',27),('Trombone',57)]
palette=json.loads(Path('suite/palette.json').read_text())[:27]
for j,(name,prog) in enumerate(more,27):
 samples={}
 for p in [48,72,96]:
  s.lib.fluid_synth_all_sounds_off(s.synth,0);s.samples(128);s.lib.fluid_synth_program_select(s.synth,0,s.sfid,0,prog)
  for cc,val in [(1,0),(77,0),(91,0),(93,0),(10,64)]:s.lib.fluid_synth_cc(s.synth,0,cc,val)
  s.lib.fluid_synth_pitch_bend(s.synth,0,8192);s.lib.fluid_synth_noteon(s.synth,0,p,78)
  a=s.samples(24000*10);level=float(np.sqrt(np.mean(a[:48000]**2)));assert level>1e-7;a*=.055/level
  samples[str(p)]=a.astype(np.float16)
 np.savez_compressed(Path('suite/atoms')/f'{j:02}.npz',**samples)
 palette.append(dict(name=name,engine='FluidSynth',program=prog,family='sampled acoustic/electric'))
 print('Captured',j,name,flush=True)
Path('suite/palette.json').write_text(json.dumps(palette,indent=2));s.close()
