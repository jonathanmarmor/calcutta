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
