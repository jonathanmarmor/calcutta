"""Convert dry instrument captures into fixed-carrier, vibrato-free timbral models.
No time-varying frequency/phase, detuned oscillator pairs, chorus or LFO survives.
"""
from pathlib import Path
import sys,json,struct,math,hashlib
import numpy as np
from scipy.signal import stft,find_peaks
sys.path.insert(0,str(Path('calcutta').resolve()))
from soundfont_capture import SoundfontSynth
RATE=24000;OUT=Path('suite/models');OUT.mkdir(parents=True,exist_ok=True)
PROGRAMS=list(range(21))+[22]+list(range(24,44))+[45,46]+list(range(48,52))+list(range(56,80))+list(range(82,88))+[98,99]+list(range(104,109))+[110,111,112,114]
# Read actual bank preset names; no online preset-name assumptions.
bank=Path(sys.argv[1]);raw=bank.read_bytes();i=raw.find(b'phdr');size=struct.unpack_from('<I',raw,i+4)[0];names={}
for j in range(i+8,i+8+size-38,38):
 name=raw[j:j+20].split(b'\0')[0].decode(errors='replace');preset,bankno=struct.unpack_from('<HH',raw,j+20)
 if bankno==0:names[preset]=name
native=json.loads(Path('suite/native_sources.json').read_text());palette=[]

def model(audio,ref,inst,program):
 x=audio.mean(axis=1);f0=440*2**((ref-69)/12);nfft=8192
 # Fixed snapshots describe attack and body, not a modulation trajectory.
 _,ts,z=stft(x,fs=RATE,nperseg=nfft,noverlap=4096,boundary='zeros');mag=abs(z);freqs=np.fft.rfftfreq(nfft,1/RATE)
 early=np.mean(mag[:,(ts>=.05)&(ts<=.4)],axis=1);body=np.median(mag[:,(ts>=.35)&(ts<=1.7)],axis=1)
 count=min(128,int(10500/f0));harmonics=np.arange(1,count+1,dtype=float);a=[];s=[]
 for h in harmonics:
  band=abs(freqs-f0*h)<max(4.5,f0*h*.009)
  if not band.any():band[np.argmin(abs(freqs-f0*h))]=True
  a.append(float(max(early[band])));s.append(float(max(body[band])))
 a=np.array(a);s=np.array(s)
 # Freeze a few inharmonic partials for struck metals, never oscillating their pitch.
 metal=program in [8,10,11,14,98,112,114]
 if metal:
  peaks,_=find_peaks(body,distance=max(2,int(f0*.3/(RATE/nfft))));peaks=[p for p in peaks if f0*.8<freqs[p]<min(10500,f0*15)]
  peaks=sorted(peaks,key=lambda p:body[p],reverse=True)[:12];ratios=[1.];aa=[max(a[0],.15*max(a))];ss=[max(s[0],.15*max(s))]
  for peak in peaks:
   ratio=float(freqs[peak]/f0)
   if min(abs(ratio-r) for r in ratios)<.13:continue
   ratios.append(ratio);aa.append(early[peak]);ss.append(body[peak])
  harmonics=np.array(ratios);a=np.array(aa);s=np.array(ss)
 assert max(a)>1e-8,(inst,ref)
 # Keep a definite sustain while retaining a struck/plucked envelope when appropriate.
 plucked=program is not None and (program<16 or 24<=program<=39 or program in [45,46,98,104,105,106,107,108,112,114])
 if plucked:s=np.maximum(s,a*.2)
 # Normalize model power, not any performed voice stem.
 scale=.055/max(math.sqrt(float(np.sum(s*s))/2),1e-9);a*=scale;s*=scale
 phase=np.random.default_rng(inst*101+ref).uniform(-math.pi,math.pi,len(a))
 return dict(ratios=harmonics.astype(np.float32),attack=a.astype(np.float32),body=s.astype(np.float32),phase=phase.astype(np.float32),decay=np.array(3.5 if plucked else 0,dtype=np.float32),noise=np.array(.0015 if program in list(range(64,80)) else 0,dtype=np.float32),inharmonic=np.array(metal))

synth=SoundfontSynth(bank,RATE)
for inst,p in enumerate(native+[dict(name=names[p],engine='FluidSynth',program=p,family='sample-derived') for p in PROGRAMS]):
 program=p.get('program');entry=dict(p);entry.update(id=inst,method='fixed-carrier sample-derived resynthesis',vibrato=False,chorus=False,frequency_modulation=False)
 result={}
 for ref in [48,72,96]:
  if inst<8:
   with np.load(Path(sys.argv[2])/f'{inst:02}.npz') as z:audio=z[str(ref)].astype(np.float32)
  else:
   synth.lib.fluid_synth_all_sounds_off(synth.synth,0);synth.samples(128);synth.lib.fluid_synth_program_select(synth.synth,0,synth.sfid,0,program)
   for cc,v in [(1,0),(77,0),(91,0),(93,0),(10,64)]:synth.lib.fluid_synth_cc(synth.synth,0,cc,v)
   synth.lib.fluid_synth_pitch_bend(synth.synth,0,8192);synth.lib.fluid_synth_noteon(synth.synth,0,ref,78);audio=synth.samples(RATE*3)
  for key,value in model(audio,ref,inst,program).items():result[f'{ref}_{key}']=value
 np.savez_compressed(OUT/f'{inst:03}.npz',**result);palette.append(entry);print('Modeled',inst,p['name'],flush=True)
Path('suite/palette.json').write_text(json.dumps(palette,indent=2));Path('suite/model_provenance.json').write_text(json.dumps({'bank_name':'GeneralUser GS','bank_sha256':hashlib.sha256(raw).hexdigest(),'native_sources':native,'programs':PROGRAMS,'sample_rate':RATE,'vibrato_policy':'All sustained partial frequencies fixed; source modulation discarded, not merely CC-disabled'},indent=2));synth.close()
