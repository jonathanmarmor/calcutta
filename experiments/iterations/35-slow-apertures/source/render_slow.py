"""Steady instrumental bodies; slow envelopes are composed note/group amplitudes."""
from pathlib import Path
import json,math,wave,subprocess
import numpy as np
from scipy.signal import butter,sosfilt
from render_base import model,tables,RATE
from calcutta.peak_balance import balance
from compose_slow import envelope
R=Path('suite')
def note(n,clouds):
 count=round(n['duration']*RATE);t=np.arange(count)/RATE;f=440*2**((n['pitch']-69)/12);ref=min([48,72,96],key=lambda p:abs(n['pitch']-p));m=model(n['instrument'],ref)
 if bool(m['inharmonic']):
  x=np.zeros(count,np.float32)
  for ratio,amp,phase in zip(m['ratios'],m['body'],m['phase']):
   if f*float(ratio)<10500:x+=np.cos(2*np.pi*f*float(ratio)*t+float(phase))*float(amp)
 else:
  _,table=tables(n['instrument'],ref,int(10500/f));x=np.interp((t*f%1)*4096,np.arange(4097),table).astype(np.float32)
 if float(m['noise']):
  rng=np.random.default_rng(202610219001+n['id']);air=rng.normal(0,float(m['noise']),count);x+=sosfilt(butter(2,[800,6500],btype='bandpass',fs=RATE,output='sos'),air).astype(np.float32)
 x*=envelope(t,0,n['duration'],n['attack'],n['release']).astype(np.float32)*n['gain']
 if n['cloud'] is not None:
  c=clouds[n['cloud']];x*=envelope(t+n['start'],c['start'],c['duration'],c['attack'],c['release']).astype(np.float32)
 return x

def render():
 s=json.loads((R/'score.json').read_text());mix=np.zeros((round(s['duration']*RATE),2),np.float32);rng=np.random.default_rng(202610219002);pans={i:float(rng.uniform(-.78,.78)) for i in range(97)};energies={};kinds={}
 for n in s['notes']:
  x=note(n,s['clouds']);start=round(n['start']*RATE);end=min(len(mix),start+len(x));x=x[:end-start];angle=(pans[n['instrument']]+1)*np.pi/4;pan=np.array([math.cos(angle),math.sin(angle)],np.float32)*math.sqrt(2);mix[start:end]+=x[:,None]*pan;e=float(np.dot(x,x));energies[n['instrument']]=energies.get(n['instrument'],0)+e;kinds[n['kind']]=kinds.get(n['kind'],0)+e
 assert np.isfinite(mix).all();mix,metrics=balance(mix,RATE,target=.078,ceiling=.75);out=Path('release');out.mkdir(exist_ok=True);wav=out/'calcutta_slow_apertures.wav';temp=wav.with_suffix('.tmp.wav')
 with wave.open(str(temp),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((np.clip(mix,-.999,.999)*32767).astype('<i2').tobytes())
 temp.replace(wav);mp3=out/'calcutta_slow_apertures.mp3';temp=mp3.with_suffix('.tmp')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-ar','48000','-codec:a','libmp3lame','-b:a','256k','-metadata','title=Slow Apertures','-metadata','artist=Jonathan Marmor','-f','mp3',str(temp)],check=True);temp.replace(mp3)
 metrics.update(duration=s['duration'],notes=len(s['notes']),instrument_energy=energies,layer_energy=kinds,sustained_energy_fraction=sum(v for k,v in kinds.items() if k!='cloud particle')/sum(kinds.values()),fixed_frequency_carriers=True);(R/'audio_audit.json').write_text(json.dumps(metrics,indent=2));print('Rendered Slow Apertures; sustained energy',metrics['sustained_energy_fraction'],flush=True)
if __name__=='__main__':render()
