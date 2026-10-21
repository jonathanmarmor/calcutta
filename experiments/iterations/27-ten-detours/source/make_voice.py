"""Original synthetic speech, then formant-envelope data for fixed-pitch vocal resynthesis."""
import os,subprocess,wave,json
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly,butter,sosfilt
r=Path('suite/voice');r.mkdir(exist_ok=True)
texts=['one','two','three','five','eight','thirteen','count again','the fifth is here','the third is sharp','almost the same','hold','stop']
env=os.environ.copy();env['LD_LIBRARY_PATH']=str(Path('synth_runtime/espeak/usr/lib/x86_64-linux-gnu').resolve())
centers=np.geomspace(100,8200,22)
for i,text in enumerate(texts):
 p=r/f'{i:02}.wav'
 subprocess.run(['synth_runtime/espeak/usr/bin/espeak-ng','--path=synth_runtime/espeak/usr/lib/x86_64-linux-gnu','-v','en-us','-s','138','-p','44','-w',str(p),text],env=env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 with wave.open(str(p)) as w:a=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768;rate=w.getframerate()
 a=resample_poly(a,24000,rate).astype(np.float32);a/=max(.01,float(np.max(np.abs(a))));features=[]
 for c in centers:
  lo=max(60,c/1.27);hi=min(11000,c*1.27)
  filt=butter(2,[lo,hi],btype='bandpass',fs=24000,output='sos');b=sosfilt(filt,a)
  energy=np.sqrt(np.maximum(0,sosfilt(butter(2,24,fs=24000,output='sos'),b*b)))
  features.append(energy[::120])
 features=np.array(features,np.float32);features/=max(1e-5,float(np.max(features)))
 np.savez_compressed(r/f'{i:02}.npz',speech=a.astype(np.float16),envelopes=features,centers=centers.astype(np.float32))
(r/'texts.json').write_text(json.dumps(texts,indent=2));print('Generated',len(texts),'original speech phrases')
