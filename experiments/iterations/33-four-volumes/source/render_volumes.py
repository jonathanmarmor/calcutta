"""Fixed-pitch instruments, two formant-voice works, one glide work, two effect works."""
from pathlib import Path
import sys,json,math,wave,subprocess
import numpy as np
from scipy.signal import butter,sosfilt
from scipy.ndimage import uniform_filter1d
from render_base import model,tables,RATE
from calcutta.peak_balance import balance
ROOT=Path('suite')
VOWELS={'a':[(800,110),(1150,130),(2900,200)],'o':[(450,100),(800,110),(2830,190)],'u':[(350,85),(650,100),(2700,180)],'e':[(500,95),(1700,140),(2500,170)],'i':[(300,85),(2200,150),(3000,210)]}
def render_note(n):
 count=round(n['duration']*RATE);t=np.arange(count)/RATE;f0=440*2**((n['pitch']-69)/12);inst=n['instrument']
 if n.get('gliss'):
  g=n['gliss'];u=np.minimum(1,t/max(n['duration']*g.get('arrive_fraction',1.),1e-5));u=u*u*(3-2*u);p=n['pitch']+(g['to_pitch']-n['pitch'])*u;freq=440*2**((p-69)/12);cycles=np.cumsum(freq)/RATE;limit=int(10500/max(freq))
 else:cycles=t*f0;limit=int(10500/f0)
 if n.get('vocal'):
  v=n['vocal'];formants=VOWELS[v['vowel']];harmonics=np.arange(1,max(2,limit+1));hz=harmonics*f0;amps=np.zeros(len(harmonics))
  for center,width in formants:amps+=np.exp(-.5*((hz-center)/width)**2)
  amps=(.09+amps)/harmonics**.65;amps[0]+=.3;amps/=max(float(np.linalg.norm(amps)),1e-8);x=np.zeros(count,np.float32)
  for h,amp in zip(harmonics,amps):x+=np.sin(2*np.pi*cycles*h+(.19*h%1))*float(amp)*.36
  # Breath/consonant onset is stationary noise, not pitch modulation or effects.
  rng=np.random.default_rng(202610210000+n['id']);air=sosfilt(butter(2,[1200,6500],btype='bandpass',fs=RATE,output='sos'),rng.normal(0,1,count)).astype(np.float32);x+=air*v.get('air',.02)*np.exp(-t/.08)
  x*=np.minimum(1,t/.025)
  if v.get('close_to_hum'):
   close=np.clip((t/n['duration']-.4)/.5,0,1);hum=np.sin(2*np.pi*cycles)*.35+np.sin(4*np.pi*cycles)*.08;x=x*(1-close)+hum*close
 else:
  ref=min([48,72,96],key=lambda p:abs(n['pitch']-p));m=model(inst,ref)
  if bool(m['inharmonic']):
   attack=np.zeros(count,np.float32);body=attack.copy()
   for ratio,a,b,phase in zip(m['ratios'],m['attack'],m['body'],m['phase']):
    if (float(max(freq)) if n.get('gliss') else f0)*float(ratio)>10500:continue
    carrier=np.cos(2*np.pi*cycles*float(ratio)+float(phase));attack+=carrier*float(a);body+=carrier*float(b)
  else:
   a,b=tables(inst,ref,limit);phase=(cycles%1)*4096;axis=np.arange(4097);attack=np.interp(phase,axis,a).astype(np.float32);body=np.interp(phase,axis,b).astype(np.float32)
  transition=np.exp(-t/.09);ar=float(np.sqrt(np.mean(attack*attack)));br=float(np.sqrt(np.mean(body*body)));attack*=min(1.,1.8*br/max(ar,1e-9));x=(body*(1-transition)+attack*transition).astype(np.float32)
  if float(m['decay']):x*=.24+.76*np.exp(-t/float(m['decay']))
  if float(m['noise']):
   rng=np.random.default_rng(inst*1000003+n['id']);x+=sosfilt(butter(2,[800,6500],btype='bandpass',fs=RATE,output='sos'),rng.normal(0,float(m['noise']),count)).astype(np.float32)
 if n.get('effect'):
  e=n['effect']
  if e['type']=='multitap':
   dry=x.copy()
   if 'excitation_seconds' in e:
    exc=min(count,round(e['excitation_seconds']*RATE));dry[exc:]=0;edge=min(exc,round(.01*RATE));dry[exc-edge:exc]*=np.linspace(1,0,edge)
   wet=np.zeros_like(x);delay=round(e['delay']*RATE)
   for tap in range(1,14):
    shift=delay*tap
    if shift>=count:break
    wet[shift:]+=dry[:-shift]*e['feedback']**tap
   x=dry*(1-e['wet']*.4)+wet*e['wet']
  elif e['type']=='reverse_grains':
   size=max(16,round(e['grain_seconds']*RATE));wet=np.zeros_like(x)
   for start in range(0,count,size):
    stop=min(count,start+size);grain=x[start:stop][::-1].copy();edge=min(round(.004*RATE),len(grain)//3)
    if edge:grain[:edge]*=np.linspace(0,1,edge);grain[-edge:]*=np.linspace(1,0,edge)
    wet[start:stop]=grain
   x=x*(1-e['wet'])+wet*e['wet']
   if e.get('reverse_envelope'):x*=np.linspace(.1,1.,count)**.6
  else:raise ValueError(e['type'])
 a=min(round(.008*RATE),count//3);r=min(round(.008*RATE),count//3)
 if a:x[:a]*=.5-.5*np.cos(np.linspace(0,np.pi,a))
 if r:x[-r:]*=.5+.5*np.cos(np.linspace(0,np.pi,r))
 return x*(n['velocity']/64)**1.6

def render(k):
 s=json.loads((ROOT/'scores'/f'{k:02}.json').read_text());mix=np.zeros((round(s['duration']*RATE),2),np.float32);rng=np.random.default_rng(202610212500+k);pans={i:float(rng.uniform(-.72,.72)) for i in range(101)};energy={}
 for n in s['notes']:
  x=render_note(n);start=round(n['start']*RATE);end=min(len(mix),start+len(x));x=x[:end-start];angle=(pans[n['instrument']]+1)*np.pi/4;pan=np.array([math.cos(angle),math.sin(angle)],np.float32)*math.sqrt(2);mix[start:end]+=x[:,None]*pan;energy.setdefault(n['instrument'],0.);energy[n['instrument']]+=float(np.dot(x,x))
 assert np.isfinite(mix).all() and all(x>0 for x in energy.values());mix,metrics=balance(mix,RATE,target=.082 if k not in [5,8,11] else .076,ceiling=.77)
 root=ROOT/'audio';root.mkdir(exist_ok=True);wav=root/f'{k:02}.wav';temp=wav.with_suffix('.tmp.wav')
 with wave.open(str(temp),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes((np.clip(mix,-.999,.999)*32767).astype('<i2').tobytes())
 temp.replace(wav);mp3=root/f"{k:02}_{s['slug']}.mp3";temp=mp3.with_suffix('.tmp');subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-ar','48000','-codec:a','libmp3lame','-b:a','256k','-metadata','title='+s['title'],'-metadata','artist=Jonathan Marmor','-f','mp3',str(temp)],check=True);temp.replace(mp3)
 metrics.update(number=k,title=s['title'],duration=s['duration'],notes=len(s['notes']),instruments_sounding=len(energy),source_energy={str(i):v for i,v in energy.items()},vocal_notes=sum('vocal' in n for n in s['notes']),gliss_notes=sum('gliss' in n for n in s['notes']),effect_notes=sum('effect' in n for n in s['notes']));(root/f'{k:02}_audit.json').write_text(json.dumps(metrics,indent=2));print('Rendered',k,s['title'],flush=True)
if __name__=='__main__':render(int(sys.argv[1]))
