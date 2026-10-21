"""Vibrato-free sample-derived resynthesis: fixed carriers, no LFO or detune pairs."""
from pathlib import Path
from functools import lru_cache
import sys,json,math,wave,subprocess
import numpy as np
from scipy.signal import butter,sosfilt
from scipy.ndimage import uniform_filter1d
sys.path.insert(0,str(Path('calcutta').resolve()));from peak_balance import balance
RATE=24000;ROOT=Path('suite');PALETTE=json.loads((ROOT/'palette.json').read_text())
@lru_cache(maxsize=300)
def model(inst,ref):
 with np.load(ROOT/'models'/f'{inst:03}.npz') as z:return {k[len(str(ref))+1:]:z[k].copy() for k in z.files if k.startswith(str(ref)+'_')}
@lru_cache(maxsize=512)
def tables(inst,ref,harmonic_limit):
 m=model(inst,ref);size=4096;out=[]
 for key in ['attack','body']:
  spec=np.zeros(size//2+1,complex)
  for ratio,amp,phase in zip(m['ratios'],m[key],m['phase']):
   h=round(float(ratio))
   if h<=harmonic_limit:spec[h]=float(amp)*np.exp(1j*float(phase))*size/2
  a=np.fft.irfft(spec,size).astype(np.float32);out.append(np.r_[a,a[:1]])
 return out

def note(n):
 count=round(n['duration']*RATE);t=np.arange(count)/RATE;freq=440*2**((n['pitch']-69)/12);inst=n['instrument'];ref=min([48,72,96],key=lambda p:abs(n['pitch']-p));m=model(inst,ref)
 if bool(m['inharmonic']):
  attack=np.zeros(count,np.float32);body=attack.copy()
  for ratio,a,b,phase in zip(m['ratios'],m['attack'],m['body'],m['phase']):
   hz=freq*float(ratio)
   if hz>10500:continue
   carrier=np.cos(2*np.pi*hz*t+float(phase));attack+=carrier*float(a);body+=carrier*float(b)
 else:
  a,b=tables(inst,ref,int(10500/freq));phase=(t*freq%1)*4096;axis=np.arange(4097)
  attack=np.interp(phase,axis,a).astype(np.float32);body=np.interp(phase,axis,b).astype(np.float32)
 # One-way spectral settling, no periodic pitch/amplitude modulation.
 transition=np.exp(-t/.09);ar=float(np.sqrt(np.mean(attack*attack)));br=float(np.sqrt(np.mean(body*body)));attack*=min(1.,1.8*br/max(ar,1e-9))
 x=(body*(1-transition)+attack*transition).astype(np.float32)
 decay=float(m['decay'])
 if decay:x*=.24+.76*np.exp(-t/decay)
 noise=float(m['noise'])
 if noise:
  rng=np.random.default_rng(inst*1000003+n['id']);air=rng.normal(0,noise,count).astype(np.float32);x+=sosfilt(butter(2,[800,6500],btype='bandpass',fs=RATE,output='sos'),air).astype(np.float32)
 a=min(round(.008*RATE),count//3);r=min(round(.008*RATE),count//3)
 if a:x[:a]*=.5-.5*np.cos(np.linspace(0,np.pi,a))
 if r:x[-r:]*=.5+.5*np.cos(np.linspace(0,np.pi,r))
 if n.get('dsp'):
  g=n['dsp'];assert g['type']=='hard_gate'
  phase=t*g['rate']+g['phase'];env=uniform_filter1d(((phase%1)<g['duty']).astype(np.float32),size=max(1,round(RATE*g['edge_ms']/1000)),mode='nearest');x*=env
 return x*(n['velocity']/64)**1.6

def render(number):
 (ROOT/'audio').mkdir(exist_ok=True);s=json.loads((ROOT/'scores'/f'{number:02}.json').read_text());mix=np.zeros((round(s['duration']*RATE),2),np.float32);rng=np.random.default_rng(202610182900+number);pans={i:float(rng.uniform(-.7,.7)) for i in range(len(PALETTE))};energies={}
 for n in s['notes']:
  x=note(n);start=round(n['start']*RATE);end=min(len(mix),start+len(x));x=x[:end-start];angle=(pans[n['instrument']]+1)*np.pi/4;pan=np.array([math.cos(angle),math.sin(angle)],np.float32)*math.sqrt(2);mix[start:end]+=x[:,None]*pan;energies.setdefault(n['instrument'],0.);energies[n['instrument']]+=float(np.sum(x*x))
 assert np.isfinite(mix).all() and all(x>1e-8 for x in energies.values())
 mix,metrics=balance(mix,RATE,target=[.082,.086,.08,.078,.087,.083,.060,.086,.080,.085,.085,.084][number-1],ceiling=.77);wav=ROOT/'audio'/f'{number:02}.wav'
 with wave.open(str(wav.with_suffix('.tmp.wav')),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((np.clip(mix,-.999,.999)*32767).astype('<i2').tobytes())
 wav.with_suffix('.tmp.wav').replace(wav)
 mp3=ROOT/'audio'/f"{number:02}_{s['slug']}.mp3";temporary=mp3.with_suffix('.tmp')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-ar','48000','-codec:a','libmp3lame','-b:a','256k','-f','mp3',str(temporary)],check=True)
 temporary.replace(mp3)
 metrics.update(number=number,title=s['title'],duration=s['duration'],notes=len(s['notes']),instruments_sounding=len(energies),constant_frequency_carriers=True,source_instrument_energy={str(k):v for k,v in energies.items()});(ROOT/'audio'/f'{number:02}_audit.json').write_text(json.dumps(metrics,indent=2));print('Rendered',number,s['title'],len(energies),'sounds',flush=True)
if __name__=='__main__':render(int(sys.argv[1]))
