from pathlib import Path
import json,numpy as np,mido
from pedalboard import load_plugin
out=Path('motif_patches');out.mkdir(exist_ok=True)
p=load_plugin(str(next(Path('synth_runtime/obxf').rglob('OB-Xf.vst3')).resolve()))
base=p.raw_state
specs=[('Oberheim dry pulse',.56,.08,False,True),('Oberheim dry brass',.62,.12,True,False),('Oberheim round sequence',.43,.28,False,True)]
rows=[]
for i,(name,cutoff,res,saw,pulse) in enumerate(specs):
 p.raw_state=base
 for key in ['unison_detune','glide_slop','filter_slop','envelope_slop','level_slop','lfo_1_mod_1_amount','lfo_1_mod_2_amount','lfo_2_mod_1_amount','lfo_2_mod_2_amount','filter_env_to_pitch_semitones']:
  p.parameters[key].raw_value=0
 p.unison=False;p.glide=0;p.osc_1_saw_wave=saw;p.osc_1_pulse_wave=pulse
 p.parameters['osc_2_volume'].raw_value=0
 p.parameters['filter_cutoff_hz'].raw_value=cutoff;p.parameters['filter_resonance'].raw_value=res
 p.filter_4_pole_mode=i==2;p.amp_env_sustain=100
 for key,ms in [('amp_env_attack_ms',18),('amp_env_release_ms',8)]:
  vals=p.parameters[key].valid_values;p.parameters[key].value=min(vals,key=lambda x:abs(float(x.split()[0])-ms))
 p.parameters['filter_env_amount'].raw_value=.1 if i==1 else 0
 path=out/f'obxf_{i}.vststate';path.write_bytes(p.raw_state)
 a=p([(mido.Message('note_on',note=69,velocity=78).bytes(),0),(mido.Message('note_off',note=69).bytes(),.8)],duration=1,sample_rate=44100)
 assert np.sqrt(np.mean(a*a))>1e-6
 spec=np.abs(np.fft.rfft(a[0,8820:22050]));freq=np.fft.rfftfreq(13230,1/44100)[np.argmax(spec)]
 print(name,'RMS',round(float(np.sqrt(np.mean(a*a))),4),'strongest partial',freq,flush=True)
 rows.append(dict(engine='OB-Xf',name=name,family='Oberheim model',state_path=str(path)))
Path('motif_patches/palette.json').write_text(json.dumps(rows,indent=2))
surge=load_plugin(str(next(Path('synth_runtime/surge_current').rglob('Surge XT.vst3')).resolve()))
print('Filters',[x for x in surge.parameters['a_filter_1_type'].valid_values if any(t in x.lower() for t in ['ladder','vintage','diode'])])
source=json.loads(Path('calcutta_choirs/score.json').read_text())['voices'][3]
state=Path('composition_32_voices_v3/patches')/f"{source['patch_index']+1:02}_Surge_XT.vststate"
for i in range(2):
 surge.raw_state=state.read_bytes();surge.fx_chain_bypass='All FX Off';surge.a_osc_drift=0
 surge.a_filter_1_type='LP Vintage Ladder' if i==0 else 'LP Diode Ladder'
 surge.a_filter_1_cutoff=900 if i==0 else 2400;surge.a_filter_1_resonance=22 if i==0 else 35
 surge.a_amp_eg_sustain=100;surge.a_amp_eg_release='0.0 ms'
 (out/f'surge_{i}.vststate').write_bytes(surge.raw_state)
print('Saved two dry ladder-filter voices')
