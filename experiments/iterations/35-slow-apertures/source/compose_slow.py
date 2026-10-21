"""Slow Apertures: fixed pitches, long tone envelopes and slowly emerging event clouds."""
from pathlib import Path
import json,random,math,collections
import numpy as np
ROOT=Path('suite');P=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches'];DURATION=840.;SEED=202610215900
# Most of the piece's energy is in steady bodies, including contrasting near-unison colors.
SUSTAIN=[0,2,3,4,5,6,7,12,13,19,24,26,27,28,32,33,38,41,46,47,48,49,52,54,56,57,59,60,62,64,65,67,68,69,70,71,73,74,75,77,79,80,81,82,85,86,88,96]
COLORS=[14,15,18,19,20,22,30,32,33,37,51,71,74,88,91,92,96,6]
def ease(u):return np.sin(np.clip(u,0,1)*np.pi/2)**2
def envelope(t,start,duration,attack,release):
 x=np.asarray(t)-start;return np.where((x>=0)&(x<duration),ease(x/max(attack,1e-8))*ease((duration-x)/max(release,1e-8)),0.)
def compose():
 r=random.Random(SEED);notes=[];clouds=[];counter=0;order=[1,2,0,2]+list(range(3,40));assert len(order)==41
 # Forty-one launch points, with the final field entered at 480 seconds.
 launches=[12.*j for j in range(len(order))];schedule=[dict(field=h,start=t,end=(launches[j+1] if j+1<len(order) else DURATION)) for j,(h,t) in enumerate(zip(order,launches))]
 def field_at(t):return schedule[max(j for j,h in enumerate(schedule) if h['start']<=t)]['field']
 def add(inst,start,dur,p,source,kind,gain=.1,attack=20,release=25,cloud=None):
  nonlocal counter
  start=max(0.,start);dur=min(dur,DURATION-start)
  if dur<.045:return
  attack=min(attack,dur*.64);release=min(release,dur*.68)
  n=dict(id=counter,instrument=inst,start=round(start,6),duration=round(dur,6),pitch=float(p),source_field=source,kind=kind,gain=float(gain),attack=attack,release=release,cloud=cloud)
  counter+=1;notes.append(n)
 for j,(h,t) in enumerate(zip(order[:-1],launches[:-1])):
  raw=sorted(P[h]);ranks=sorted(set([0,31]+[round(z*31/13) for z in range(1,13)]))
  for v,q in enumerate(ranks):
   onset=max(0,t+r.uniform(-2,6));dur=r.uniform(54,83);end=min(onset+dur,558.)
   # Early 1:2 is a short, quiet passing color rather than a focus.
   if h==0:end=min(end,onset+35)
   inst=SUSTAIN[(v*11+j*7)%len(SUSTAIN)];pitch=raw[q];gain=r.uniform(.045,.10)*(1 if pitch<83 else .74)
   if h==0:gain*=.52
   add(inst,onset,end-onset,pitch,h,'sustained field strand',gain,r.uniform(18,34),r.uniform(22,39))
 # Destination field: independent timbral waves, all actual positions represented.
 raw=sorted(P[39]);unique=[]
 for p in raw:
  if not unique or abs(p-unique[-1])>1e-7:unique.append(p)
 for wave,t in enumerate([475,509,548,588,630,671,708,744]):
  for v,p in enumerate(unique):
   start=t+r.uniform(0,13);dur=r.uniform(82,126);end=min(start+dur,DURATION-r.uniform(1,12))
   add(SUSTAIN[(v*13+wave*9+5)%len(SUSTAIN)],start,end-start,p,39,'destination timbre wave',r.uniform(.045,.092)*(1 if p<83 else .74),r.uniform(28,49),r.uniform(35,61))
 # Each cloud is a separate slow envelope around a note/chord or local field subset.
 designs=[(66,130,'neighbor trill',.13),(147,142,'expanding arpeggio',.14),(235,150,'triad mist',.12),(337,139,'sparse-to-dense lattice',.14),(430,154,'neighbor trill',.12),(522,164,'expanding arpeggio',.13),(615,151,'triad mist',.15),(694,139,'sparse-to-dense lattice',.12)]
 for ci,(a,length,kind,level) in enumerate(designs):
  attack=length*r.uniform(.31,.42);release=length*r.uniform(.34,.47);clouds.append(dict(id=ci,start=a,duration=length,attack=attack,release=release,kind=kind,maximum_gain=level))
  t=a;k=0
  while t<a+length-.15:
   strength=float(envelope(t,a,length,attack,release));field=field_at(t);raw=sorted(set(P[field]));pool=[]
   for p in raw:
    if not pool or p-pool[-1]>1.05:pool.append(p)
   reg=[69,78,61,85,73,66,80,59][ci];base=min(range(len(pool)),key=lambda z:abs(pool[z]-reg));inst=COLORS[(ci*5+k//13)%len(COLORS)]
   if kind=='neighbor trill':
    ix=min(len(pool)-2,base);p=pool[ix+k%2];step=.32+.11*math.sin(k*.09+ci);dur=step*1.35
   elif kind=='triad mist':
    # Choose actual pure-fifth / sharp-third relatives when available.
    root=pool[max(0,min(len(pool)-1,base-2))];targets=[root,root+4.33832,root+7.01955,root+11.08];target=targets[(k//2)%4];p=min(raw,key=lambda p:abs(p-target));step=.23+.55*(1-strength);dur=.75+strength*.55
   else:
    width=1+round(strength*min(7,len(pool)-2));index=max(0,min(len(pool)-1,base+int(round(math.sin(k*.72)*width))));p=pool[index];step=.13+.75*(1-strength)**1.7;dur=.26+strength*.37
   # Increasing event probability/density is independent of the cloud's amplitude envelope.
   if r.random()<.25+.75*strength:add(inst,t,dur,p,field,'cloud particle',level*r.uniform(.74,1.12),min(.11,dur*.28),min(.23,dur*.45),ci)
   t+=step;k+=1
 notes.sort(key=lambda n:(n['start'],n['id']));slots=collections.defaultdict(list);voices=[]
 for n in notes:
  lane=slots[n['instrument']];slot=next((j for j,(end,v) in enumerate(lane) if end<=n['start']+1e-6),None)
  if slot is None:slot=len(lane);lane.append((-1,len(voices)));voices.append(dict(instrument=n['instrument'],lane=slot))
  n['voice']=lane[slot][1];lane[slot]=(n['start']+n['duration'],n['voice'])
 score=dict(title='Slow Apertures',slug='calcutta_slow_apertures',duration=DURATION,seed=SEED,notes=notes,voices=voices,clouds=clouds,harmonic_launches=schedule,exclusive_final_field_start=558.,pitch_policy='Every fixed pitch is an exact member of its recorded source field. Gradual handoffs deliberately overlap neighboring source fields; no held pitch is bent or retuned.',sound_policy='Fixed-frequency sustained bodies, individual long envelopes and cloud envelopes; no vibrato, reverb, delay, chorus, click or master fade.')
 (ROOT/'score.json').write_text(json.dumps(score,indent=2));print('Composed',len(notes),'events;',sum(n['kind']!='cloud particle' for n in notes),'long strands;',len(set(n['instrument'] for n in notes)),'sounds',flush=True);return score
if __name__=='__main__':compose()
