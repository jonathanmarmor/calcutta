"""Capture native synth and sampled-instrument atoms for the dry hybrid sampler."""
from pathlib import Path
import sys,json,time,numpy as np
from scipy.signal import resample_poly
from pedalboard import load_plugin
sys.path.insert(0,str(Path('calcutta').resolve()))
from mixed_synths import Engines,RATE
from instrument_sketch import SoundfontSynth
out=Path('suite/atoms');out.mkdir(exist_ok=True,parents=True)
patches=json.loads(Path('palette_frontier/synths.json').read_text())
for name,program in [('Rhodes',4),('Clavinet',7),('Jazz guitar',26),('Steel guitar',25),('Nylon guitar',24),('Piano',0),('Harp',46),('Clarinet',71),('Recorder',74),('Bassoon',70),('English horn',69),('Pan pipes',75),('Fretless bass',35),('Steel pans',114),('Vibraphone',11),('Tubular bells',14),('Marimba',12),('Drawbar organ',16),('Muted trumpet',59)]:patches.append(dict(engine='FluidSynth',name=name,program=program,parameters={}))
e=Engines(Path('synth_runtime'),Path('soundfont_runtime/runtime/usr/share/sounds/sf2/TimGM6mb.sf2'));e.gm.close();e.gm=SoundfontSynth(Path('synth_runtime/GeneralUser-GS.sf2'),RATE)
e.paths['Surge XT']=next(Path('synth_runtime/surge_current').rglob('Surge XT.vst3'));e.paths['OB-Xf']=next(Path('synth_runtime/obxf').rglob('OB-Xf.vst3'));e.paths['TAL-NoiseMaker']=next(Path('synth_runtime/tal').rglob('*.vst3'));e.paths['Dexed']=next(Path('synth_runtime/dexed').rglob('Dexed.vst3'))
for i,p in enumerate(patches):
 path=out/f'{i:02}.npz'
 if path.exists():continue
 plug=None
 if p['engine']!='FluidSynth':
  plug=load_plugin(str(e.paths[p['engine']].resolve()));plug.raw_state=Path(p['state_path']).read_bytes();time.sleep(.3)
  if p['engine']=='TAL-NoiseMaker':plug.amp_attack=.002
 samples={};rms=[]
 for pitch in [48,72,96]:
  a=e.note(p,plug,pitch,RATE*(10 if p['engine']!='FluidSynth' or p.get('program') in [71,74,70,69,75,16,59] else 7))
  a=resample_poly(a,80,147,axis=0).astype(np.float32)
  level=float(np.sqrt(np.mean(a[:48000]**2)));assert level>1e-6,(p['name'],pitch)
  # One reference gain per register, never normalization of a performed part.
  a*=.055/level;samples[str(pitch)]=a.astype(np.float16);rms.append(level)
 np.savez_compressed(path,**samples);p['reference_rms']=rms
 print('Captured',i,p['name'],path.stat().st_size,flush=True)
 if plug is not None:del plug
Path('suite/palette.json').write_text(json.dumps(patches,indent=2));e.gm.close()
