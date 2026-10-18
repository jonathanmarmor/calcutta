from pathlib import Path
import json,numpy as np,mido,copy
from pedalboard import load_plugin
out=Path('palette_murmur');out.mkdir(exist_ok=True)
rows=[]
def probe(p,name):
 a=p([(mido.Message('note_on',note=69,velocity=78).bytes(),0),(mido.Message('note_off',note=69).bytes(),.9)],duration=1,sample_rate=44100)
 x=a[0,8820:35280];spec=np.abs(np.fft.rfft(x));freq=np.fft.rfftfreq(len(x),1/44100)[np.argmax(spec)]
 assert float(np.sqrt(np.mean(a*a)))>1e-5
 print(name,'peak',round(freq,1),'RMS',round(float(np.sqrt(np.mean(a*a))),4),flush=True)
 # New oscillators must not introduce an octave offset or detuned unison.
 assert abs(freq/440-round(freq/440))<.02 and freq>=435,(name,freq)
p=load_plugin(str(next(Path('synth_runtime/tal').rglob('*.vst3')).resolve()));base=p.raw_state
for i,(name,cutoff,res,wave) in enumerate([('TAL soft amber',.49,.10,0.),('TAL hollow satin',.61,.18,.34),('TAL dusk reed',.39,.23,0.),('TAL open linen',.72,.05,.34)]):
 p.raw_state=base
 for k in ['chorus_1_enable','chorus_2_enable','reverb_wet','delay_wet','master_detune','vintage_noise','osc_3_volume','osc_2_volume','filter_drive','pitchwheel_cutoff','portamento_amount']:
  p.parameters[k].raw_value=0
 for k in ['lfo_1_amount','lfo_2_amount','free_ad_amount']:p.parameters[k].raw_value=.5
 p.osc_1_tune='0 Semitones';p.osc_2_tune='0 Semitones';p.pitchwheel_pitch=2.
 p.osc_1_waveform=wave;p.filter_cutoff=cutoff;p.filter_resonance=res;p.osc_1_volume=.65
 p.amp_attack=.08;p.amp_sustain=1;p.amp_release=0;p.filter_contour=0;p.amp_decay=0
 probe(p,name)
 state=out/f'tal_{i}.vststate';state.write_bytes(p.raw_state)
 rows.append(dict(engine='TAL-NoiseMaker',name=name,family='virtual analog',state_path=str(state)))
p=load_plugin(str(next(Path('synth_runtime/obxf').rglob('OB-Xf.vst3')).resolve()));base=Path('motif_patches/obxf_0.vststate').read_bytes()
for i,(name,cut,res,saw) in enumerate([('OB-X cloud wool',.40,.05,False),('OB-X small brass',.49,.08,True),('OB-X breath organ',.59,.02,False),('OB-X dark halo',.34,.12,True)]):
 p.raw_state=base;p.osc_1_saw_wave=saw;p.osc_1_pulse_wave=not saw;p.filter_4_pole_mode=True
 p.parameters['filter_cutoff_hz'].raw_value=cut;p.parameters['filter_resonance'].raw_value=res
 p.parameters['filter_env_amount'].raw_value=.04
 probe(p,name)
 state=out/f'ob_{i}.vststate';state.write_bytes(p.raw_state)
 rows.append(dict(engine='OB-Xf',name=name,family='Oberheim model',state_path=str(state)))
p=load_plugin(str(next(Path('synth_runtime/surge_current').rglob('Surge XT.vst3')).resolve()));base=Path('motif_patches/surge_0.vststate').read_bytes()
for i,(name,typ,cut,res) in enumerate([('Modular reed sustained','LP Vintage Ladder',1600,14),('Curtis-like round lead','LP 12 dB',2300,17),('Resonant velvet drone','LP Diode Ladder',700,24),('Air through a ladder','LP Vintage Ladder',3400,7)]):
 import sys;sys.path.insert(0,str(Path('calcutta').resolve()))
 from mixed_synths import Engines,palette
 eng=Engines(Path('synth_runtime'),Path('soundfont_runtime/GeneralUser-GS.sf2'));eng.paths['Surge XT']=next(Path('synth_runtime/surge_current').rglob('Surge XT.vst3'));p=eng.load(palette()[0])
 import time;time.sleep(.4)
 p.a_filter_1_type=typ;p.a_filter_1_cutoff=cut;p.a_filter_1_resonance=res;p.fx_chain_bypass='All FX Off';p.a_osc_drift=0;p.a_amp_eg_sustain=100;p.a_amp_eg_release='0.0 ms'
 probe(p,name)
 state=out/f'surge_{i}.vststate';state.write_bytes(p.raw_state)
 rows.append(dict(engine='Surge XT',name=name,family='modular analog inspired',state_path=str(state)))
(out/'synths.json').write_text(json.dumps(rows,indent=2))
