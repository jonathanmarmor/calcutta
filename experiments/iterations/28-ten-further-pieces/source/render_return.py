"""Portable dry sampler: native synth/GM captures, exact-pitch playback and explicit DSP."""
from pathlib import Path
from functools import lru_cache
import sys,json,math,wave,subprocess
import numpy as np
from scipy.signal import butter,sosfilt,iirpeak,lfilter
from scipy.ndimage import uniform_filter1d
sys.path.insert(0,str(Path('calcutta').resolve()));from peak_balance import balance
RATE=24000;root=Path('suite');palette=json.loads((root/'palette.json').read_text())
@lru_cache(maxsize=108)
def atom(inst,ref):
 with np.load(root/'atoms'/f'{inst:02}.npz') as z:return z[str(ref)].astype(np.float32)
def note(n):
 count=round(n['duration']*RATE);inst=n['instrument']
 ref=min([48,72,96],key=lambda p:abs(n['pitch']-p));a0=atom(inst,ref);ratio=2**((n['pitch']-ref)/12)
 # Anti-alias before upward resampling; no pitch rounding or moving pitch bend.
 if ratio>1.02:a0=sosfilt(butter(4,.93/ratio,output='sos'),a0,axis=0).astype(np.float32)
 positions=np.arange(count)*ratio;ix=np.arange(len(a0));a=np.column_stack([np.interp(positions,ix,a0[:,ch],left=0,right=0) for ch in range(2)]).astype(np.float32)
 attack=min(round(n.get('attack',.006)*RATE),count//3);release=min(round(.008*RATE),count//3)
 if attack:a[:attack]*=(.5-.5*np.cos(np.linspace(0,np.pi,attack)))[:,None]
 if release:a[-release:]*=(.5+.5*np.cos(np.linspace(0,np.pi,release)))[:,None]
 return a*(n['velocity']/64)**1.6

def render(number):
 (root/'audio').mkdir(parents=True,exist_ok=True)
 s=json.loads((root/'scores'/f'{number:02}.json').read_text());count=round(s['duration']*RATE);mix=np.zeros((count,2),np.float32);stats={};rng=np.random.default_rng(202610181100+number)
 # Fixed positions make an ensemble; direct sample stereo is preserved.
 pans={i:float(rng.uniform(-.65,.65)) for i in range(36)}
 for n in s['notes']:
  assert not n.get('dsp')
  a=note(n);start=round(n['start']*RATE);stop=min(count,start+len(a));a=a[:stop-start]
  angle=(pans[n['instrument']]+1)*np.pi/4;pan=np.array([np.cos(angle),np.sin(angle)],np.float32)*np.sqrt(2)
  mix[start:stop]+=a*pan
  stats.setdefault(str(n['instrument']),0.);stats[str(n['instrument'])]+=float(np.sum(a*a))
 assert np.isfinite(mix).all() and all(x>1e-8 for x in stats.values())
 # Deliberate global loudness, preserving all internal dynamic relations. No fade.
 mix,metrics=balance(mix,RATE,target=.085,ceiling=.77)
 metrics.update(number=number,title=s['title'],duration=s['duration'],notes=len(s['notes']),instruments_sounding=len(stats),tremolo_events=sum('tremolo' in str(n.get('dsp','')) for n in s['notes']),passing_events=sum(n.get('is_passing',False) for n in s['notes']),sampled_events=sum(n['instrument']>=8 for n in s['notes']))
 wav=root/'audio'/f'{number:02}.wav'
 with wave.open(str(wav),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((np.clip(mix,-.999,.999)*32767).astype('<i2').tobytes())
 slug=s['slug']
 mp3=root/'audio'/f'{number:02}_{slug}.mp3'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-ar','48000','-codec:a','libmp3lame','-b:a','256k',str(mp3)],check=True)
 (root/'audio'/f'{number:02}_audit.json').write_text(json.dumps(metrics,indent=2));print('RENDERED',json.dumps(metrics),flush=True)
if __name__=='__main__':render(int(sys.argv[1]))
