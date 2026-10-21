"""Original dry lead patches, inspired by documented techniques, not recovered presets."""
from pathlib import Path
import sys,time,json,numpy as np,mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from mixed_synths import Engines,palette
from pedalboard import load_plugin
out=Path('palette_frontier');out.mkdir(exist_ok=True);rows=[]
eng=Engines(Path('synth_runtime'),Path('soundfont_runtime/GeneralUser-GS.sf2'));eng.paths['Surge XT']=next(Path('synth_runtime/surge_current').rglob('Surge XT.vst3'))
def save(p,engine,name,family):
 time.sleep(.15);a=eng.note(dict(engine=engine,name=name),p,69,44100);rms=float(np.sqrt(np.mean(a*a)));assert rms>1e-5
 x=a[8820:35280].mean(axis=1);f=np.fft.rfftfreq(len(x),1/44100)[np.argmax(np.abs(np.fft.rfft(x)))];assert abs(f/440-round(f/440))<.02 and f>435,(name,f)
 path=out/f'lead_{len(rows)}.vststate';path.write_bytes(p.raw_state);rows.append(dict(engine=engine,name=name,family=family,state_path=str(path),reference_rms=rms));print(name,rms,f,flush=True)
for name,typ,cut,res in [('Open modular saw','LP Vintage Ladder',6800,12),('Resonant sequencer lead','LP 12 dB',3300,36)]:
 p=eng.load(palette()[0]);time.sleep(.2);p.a_filter_1_type=typ;p.a_filter_1_cutoff=cut;p.a_filter_1_resonance=res
 save(p,'Surge XT',name,'analog lead')
p=load_plugin(str(next(Path('synth_runtime/obxf').rglob('OB-Xf.vst3')).resolve()))
for i,(name,cut,res,saw) in enumerate([('Oberheim silver pulse',.69,.17,False),('Oberheim touch brass',.73,.08,True)]):
 p.raw_state=Path(f'palette_murmur/ob_{i}.vststate').read_bytes();p.parameters['filter_cutoff_hz'].raw_value=cut;p.parameters['filter_resonance'].raw_value=res;p.osc_1_saw_wave=saw;p.osc_1_pulse_wave=not saw
 vals=p.parameters['amp_env_attack_ms'].valid_values;p.parameters['amp_env_attack_ms'].value=min(vals,key=lambda x:abs(float(x.split()[0])-6))
 save(p,'OB-Xf',name,'Oberheim lead')
p=load_plugin(str(next(Path('synth_runtime/tal').rglob('*.vst3')).resolve()))
for i,(name,cut,res) in enumerate([('TAL bright hollow lead',.87,.16),('TAL rubber reed',.64,.34)]):
 p.raw_state=Path(f'palette_murmur/tal_{i}.vststate').read_bytes();p.amp_attack=.002;p.filter_cutoff=cut;p.filter_resonance=res
 save(p,'TAL-NoiseMaker',name,'single oscillator lead')
for i,name in [(22,'FM glass cantilena'),(24,'FM harmonic organ')]:
 p=eng.load(palette()[i]);save(p,'Dexed',name,'FM lead')
(out/'synths.json').write_text(json.dumps(rows,indent=2));eng.gm.close()
