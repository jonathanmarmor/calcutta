"""Ten fuller, metrically grounded Calcutta pieces following a convergent harmonic route."""
from pitch_core import *
from pathlib import Path
import bisect,json,math,random
import numpy as np
ROOT=Path('suite');(ROOT/'scores').mkdir(parents=True,exist_ok=True)
BASE_TEMPOS=[79,96,86,103,74,91,78,106,88,96]
FINAL_BARS=[52,48,56,48,52,56,52,48,56,48]
AREAS=[(0,2),(1,5),(5,6),(7,7),(8,12),(11,14),(14,15),(16,16),(17,21),(20,24),(24,27),(27,28),(29,32),(32,35),(35,38),(38,39)]
PALETTES=[
 [10,8,15,29,27,14,20,24,2,6,12,28,30,22],
 [8,9,10,17,28,32,13,24,1,7,29,27,14,22],
 [15,27,28,17,29,30,12,8,5,3,14,13,24,31],
 [9,8,34,29,15,20,24,27,0,4,12,28,13,22],
 [12,14,24,21,15,29,10,8,2,6,27,28,33,22],
 [27,28,29,30,17,8,13,10,3,5,24,14,32,15],
 [8,34,10,15,27,29,20,24,1,6,14,28,9,22],
 [15,27,28,29,30,31,13,24,2,0,10,17,8,14],
 [18,29,28,8,10,13,32,14,7,5,15,27,22,30],
 [13,8,10,15,27,29,20,24,4,6,14,28,9,22]
]
# Distinct section trajectories; each returns to pulse without a uniform drum pattern.
FORMS=[
 [0,2,3,1,5,4,6,0,8,3,1,7,2,5,9,4,0,6,3,10,1,8,5,2,7,0,9,6,4,3,1,8,5,10],
 [2,0,6,4,1,3,8,5,2,9,0,7,6,1,4,10,3,8,2,5,9,0,4,6,1,7,10,3,8,2,5,0,9,1],
 [3,5,0,4,7,1,2,9,6,3,8,0,10,5,4,1,3,6,7,2,9,5,0,8,4,10,1,3,6,2,7,9,5,0],
 [6,2,0,8,4,1,9,3,5,6,10,2,7,0,4,8,1,9,6,3,5,2,10,4,0,7,8,1,9,3,6,5,2,0],
 [2,6,1,0,8,3,5,9,4,10,2,7,6,0,1,8,3,5,9,2,4,7,10,6,0,8,1,3,5,9,2,4,7,0],
 [3,0,5,1,4,9,7,2,8,6,3,10,0,5,1,4,9,8,2,7,6,3,0,10,5,1,4,9,2,8,6,7,3,0],
 [0,6,2,5,1,8,3,4,10,9,6,0,7,2,5,1,8,4,3,9,0,6,10,5,2,7,1,8,3,4,9,6,0,5],
 [4,6,0,3,1,9,2,8,5,7,4,10,6,0,3,9,1,2,8,4,5,7,10,6,0,3,1,9,4,2,8,5,6,0],
 [5,0,7,3,1,4,8,9,2,6,5,10,0,3,7,1,4,9,8,2,5,6,0,10,3,7,1,4,8,9,2,5,6,0],
 [0,3,2,8,1,5,9,4,6,7,0,10,3,1,2,8,5,4,9,6,7,0,3,10,1,8,2,5,4,9,6,0,7,3]
]
TEXTURES=['melody and layered accompaniment','interleaved triad/seventh sequences','shared melody / active inner lines','small choirs answering across a pulse','counterpoint with a secondary clock','long line over quicker inner parts','brisk sampled-instrument weave','broad harmony with moving edges','composite lead / exposed acoustic countervoice','three related evolving cells','register-crossing chord-root sequences']

class FlowPiece(PitchCore):
 def __init__(self,k):
  self.k=k;self.r=random.Random(202610182100+k);self.counter=0;self.notes=[];self.scenes=[];self.sequences=[];self.palette=PALETTES[k];self.nbars=80+FINAL_BARS[k]
  self.contour=[0]
  for j in range(6+k%3):self.contour.append(self.contour[-1]+self.r.choice([-2,-1,1,1,2]))
  low=min(self.contour);self.contour=[x-low for x in self.contour]
  self.rhythm=[self.r.choice([.5,.75,1,1,1.5,2]) for _ in self.contour]
  if self.rhythm[:2]==[.5,.5]:self.rhythm[1]=1.5
  # One shared pulse, breathing by a few percent, with coherent phrase-level timing.
  self.beats=[0.];self.tempi=[]
  for bar in range(self.nbars):
   section=bar//4;shape=[1,1.07,.93,1.12,.98,.89,1.04,1.][(section//2+k)%8]
   tempo=BASE_TEMPOS[k]*shape*(1+.012*math.sin(bar*.61+k));self.tempi.append(tempo)
   for q in range(4):self.beats.append(self.beats[-1]+60/tempo*(1+.006*math.sin(bar*1.7+q*.9)))
  self.duration=self.beats[-1]+.45
  # Four eight-bar windows, different in each piece, retain the 80-bar journey.
  eligible=[i for i,(lo,hi) in enumerate(AREAS) if hi-lo>=2];eight={1,4,8,12}
  if k%2:eight={1,4,9,12}
  if k in [2,5,8]:eight={1,8,9,12}
  self.areas=[];self.harmonies=[];bar=0
  for i,(lo,hi) in enumerate(AREAS):
   bars=8 if i in eight else 4;window=list(range(lo,hi+1));slots=bars if len(window)<=bars else bars*2
   if lo==hi:order=window*slots
   elif len(window)==2:order=[window[(j+k%2)%2] for j in range(slots)]
   else:
    order=window[:]
    while len(order)<slots:
     # Neighbor walks after the first pass make the region audible as a region.
     old=order[-1];opts=[x for x in window if 0<abs(x-old)<=2];order.append(self.r.choice(opts))
    # Change the internal route without omitting any field.
    if slots>=len(window)+2 and i%3==k%3:order=window[:2]+[window[0]]+window[2:]+order[len(window)+1:]
    order=order[:slots]
   if i==0:order=([1,2,0,2] if k%2==0 else [2,1,0,1]) # original index 0 is 1:2; do not open there
   self.areas.append(dict(first=lo,last=hi,start=self.sec(bar*4),end=self.sec((bar+bars)*4),start_bar=bar,bars=bars))
   for j,ch in enumerate(order):self.harmonies.append(dict(chord=ch,start=self.sec(bar*4+j*bars*4/slots),end=self.sec(bar*4+(j+1)*bars*4/slots)))
   bar+=bars
  assert bar==80
  self.final_start=self.sec(80*4)
  self.areas.append(dict(first=39,last=39,start=self.final_start,end=self.duration,start_bar=80,bars=FINAL_BARS[k]))
  self.harmonies.append(dict(chord=39,start=self.final_start,end=self.duration))
  merged=[]
  for h in self.harmonies:
   if merged and h['chord']==merged[-1]['chord']:merged[-1]['end']=h['end']
   else:merged.append(h)
  self.harmonies=merged;self.starts=[h['start'] for h in merged]
 def sec(self,beat):return float(np.interp(max(0,min(beat,self.nbars*4)),np.arange(len(self.beats)),self.beats))
 def metrical(self,beat):
  q=beat%4
  if abs(q)<.03:return 5
  if abs(q-2)<.03:return 3
  if abs(q-round(q))<.03:return 1
  return -2
 def hit(self,part,inst,beat,length,target,v,role,exact=False,blend=False,lag=0):
  if beat>=self.nbars*4:return None
  t=self.sec(beat)+lag+self.r.uniform(-.009,.009);t=max(0,t);end=self.sec(min(self.nbars*4,beat+length))
  if end-t<.1:return None
  p=target if exact else self.pitch(t,target)
  n=self.add(part,inst,t,end-t,p,v+self.metrical(beat),role,blend=blend)
  if n:n['beat']=beat
  return n
 def line(self,part,inst,a,b,register=72,period=1,v=49,kind='scalar',shape=None,blend=False,passing=.07,gate=.88):
  shape=list(self.contour if shape is None else shape);beat=a;rep=0
  while beat<b-.15:
   motif=shape[:]
   if rep%4==3:motif[-1]+=1 if (rep+self.k)%2 else -1
   events=[]
   for j,degree in enumerate(motif):
    if beat>=b-.16:break
    t=self.sec(beat);pool=self.pool(t)
    if kind=='chord':
     c=self.chord(t,rep+self.k+int(a//16));p=c[degree%len(c)]
    else:
     idx=min(range(len(pool)),key=lambda z:abs(pool[z]-register));index=idx+degree-max(shape)//2+(rep%3-1)*(1 if self.k%2 else -1);index=abs(index)%(2*(len(pool)-1));index=min(index,2*(len(pool)-1)-index);p=pool[index]
    ioi=period*self.rhythm[j%len(self.rhythm)]
    if j==len(motif)-1:ioi*=1.5
    lag=.013 if inst in [15,17,18,27,28,29,30,31] else -.004
    onset=self.sec(beat)+lag+self.r.uniform(-.008,.008);onset=max(0,onset);limit=self.sec(min(b,beat+ioi))
    p=self.pitch(onset,p)
    vel=v+self.metrical(beat)+5*math.sin(math.pi*(j+.7)/(len(motif)+.5))+self.r.uniform(-2.5,2.5)
    events.append(dict(t=onset,beat=beat,ioi=ioi,end=limit,p=p,v=vel));beat+=ioi
   for j,e in enumerate(events):
    nxt=events[j+1] if j+1<len(events) else None;span=e['end']-e['t']
    can=nxt and self.hi(e['t'])==self.hi(nxt['t']) and .6<span<1.8 and 1.6<abs(nxt['p']-e['p'])<4.8 and self.r.random()<passing
    if can:
     p=(nxt['p']+e['p'])/2
     if min(abs(x-p) for x in self.raw(e['t']))<.035:can=False
    n=self.add(part,inst,e['t'],max(.1,span*(.62 if can else gate)),e['p'],e['v'],kind+' metrical phrase',blend=blend)
    if n:n['beat']=e['beat']
    if can and n:
     pn=self.add(part,inst,e['t']+span*.72,min(.4,span*.22),p,e['v']-11,'unaccented passing connection',passing=True,anchors={'from_pitch':n['pitch'],'to_pitch':nxt['p'],'to_start':round(nxt['t'],6),'from_id':n['id']})
   if events:self.sequences.append(dict(part=part,instrument=inst,start=events[0]['t'],repeat=rep,contour=motif,period_beats=period))
   beat+=period*self.r.choice([.5,.75,1.25]);rep+=1
 def foundation(self,section,a,b,sparse=False):
  pal=self.palette;ac=[x for x in pal if x>=8];regs=[55,68,79];count=1 if sparse else 3
  # Independently articulated inner voices; the harmony never arrives as a loud tutti stab.
  for layer in range(count):
   inst=ac[(section+layer*3+3)%len(ac)] if layer!=2 or section%4 else pal[8]
   for hi,h in enumerate(self.harmonies):
    lo=max(a,float(np.interp(h['start'],self.beats,np.arange(len(self.beats)))));end=min(b,float(np.interp(h['end'],self.beats,np.arange(len(self.beats)))))
    if end-lo<.25:continue
    t=lo+.11*layer;step=0
    while t<end-.15:
     length=[2.9,3.7,2.2,4.6][(step+layer+section)%4]
     c=self.chord(self.sec(t),section+step//3+layer);p=min(c,key=lambda p:abs(p-regs[layer]));p=self.pitch(self.sec(t),p)
     self.hit(f'{section}-inner{layer}-{hi}',inst,t,min(length*.96,end-t),p,29+layer*1.5+3*math.sin(step*.8+section),'soft moving harmonic inner line',exact=True)
     t+=length;step+=1
  # A musical pulse distributed between bass and changing upper instruments.
  for bar in range(int(a//4),int(b//4)):
   for j,q in enumerate([0,2]):
    beat=bar*4+q;c=self.chord(self.sec(beat),section+(bar%3));target=c[(bar+j)%len(c)]
    target=self.pitch(self.sec(beat),target-12 if target>65 else target)
    self.hit(f'{section}-bass',pal[6],beat,1.8,target,36+2*math.sin(bar*.9+j),'walking harmonic pulse',exact=True,lag=.003)
   for j,q in enumerate([1,3]):
    beat=bar*4+q;c=self.chord(self.sec(beat),section+bar//2);inst=ac[(section+bar//2+1)%len(ac)];target=c[(j+bar)%len(c)]
    self.hit(f'{section}-pulse-{bar%2}',inst,beat,.92+self.r.random()*.18,target,34+2*math.sin(bar+j),'quiet answering pulse',exact=True,lag=.014)
   if not sparse and bar%3!=1:
    beat=bar*4+self.r.choice([.5,1.5,2.5,3.5]);target=self.pitch(self.sec(beat),73+(bar%4)*2)
    self.hit(f'{section}-pickup',ac[(section+4)%len(ac)],beat,.42,target,30,'small linking pickup',exact=True,lag=-.005)
 def compose_scene(self,i,a,b,style):
  pal=self.palette;ac=[x for x in pal if x>=8];sparse=i in [13+(self.k%4)] # one short exception, under 4% of a piece
  self.foundation(i,a,b,sparse=sparse)
  lead=ac[(i+self.k)%len(ac)] if i%5!=3 else pal[8+(i%2)]
  reg=[70,77,65,81,73][(i+self.k)%5];level=48+4*math.sin(i*.7+self.k)
  self.scenes.append(dict(start=self.sec(a),end=self.sec(b),texture=TEXTURES[style],start_bar=int(a/4),end_bar=int(b/4),nominal_bpm=self.tempi[int(a/4)],sparse_exception=sparse))
  if sparse:
   self.line(f'{i}-exposed',lead,a+.5,b,reg,1.1,level,passing=.09);return
  def line(j,inst=None,period=1,register=None,v=None,kind='scalar',shape=None,blend=False,offset=0):
   self.line(f'{i}-foreground{j}',lead if inst is None else inst,a+offset,b,reg if register is None else register,period,level if v is None else v,kind,shape,blend)
  if style==0:
   line(0);line(1,ac[(i+3)%len(ac)],1.5,reg-9,level-8,'chord',offset=.75);line(2,ac[(i+5)%len(ac)],.75,reg+4,level-12,shape=self.contour[::-1],offset=1.5)
  elif style==1 or style==10:
   line(0,period=.75,kind='chord');line(1,ac[(i+4)%len(ac)],1,reg-7,level-8,'chord',self.contour[::-1],offset=.5)
   line(2,ac[(i+6)%len(ac)],1.5,reg+5,level-13,'chord',offset=1.0)
  elif style==2:
   t=a;j=0
   while t<b-.25:
    pool=self.pool(self.sec(t));base=min(range(len(pool)),key=lambda z:abs(pool[z]-reg));p=pool[(base+self.contour[j%len(self.contour)])%len(pool)];ioi=[.5,1,.5,1.5,.5,2][(j+self.k)%6]
    self.hit(f'{i}-hocket{j%4}',ac[(i+j)%len(ac)],t,min(ioi*.9,b-t),p,level,'melody passed through sampled colors',exact=True);t+=ioi;j+=1
   line(1,ac[(i+2)%len(ac)],1.0,reg-5,level-8,'chord',offset=.5);line(2,ac[(i+5)%len(ac)],.75,reg+7,level-12,offset=1.)
  elif style==3:
   for half,(lo,hi) in enumerate([(a,a+(b-a)*.56),(a+(b-a)*.46,b)]):
    for j in range(3):self.line(f'{i}-choir{half}-{j}',ac[(i+half*3+j)%len(ac)],lo+j*.04,hi,reg+[-7,0,6][j],1 if half==0 else .75,level-9-j,kind='chord',shape=self.contour if half==0 else self.contour[::-1],passing=0)
   line(3,ac[(i+7)%len(ac)],1.5,reg-3,level-12,offset=1.5)
  elif style==4:
   line(0,period=1.);line(1,ac[(i+3)%len(ac)],2/3,reg-5,level-10,shape=self.contour[::-1],offset=.5)
   line(2,ac[(i+6)%len(ac)],1.5,reg+6,level-12,'chord',offset=1.)
  elif style==5:
   line(0,period=2.,v=level+1);line(1,ac[(i+3)%len(ac)],.5,reg-7,level-13,'chord',offset=.5)
   line(2,ac[(i+5)%len(ac)],1.,reg+6,level-11,shape=self.contour[::-1],offset=1.)
  elif style==6:
   for j in range(4):line(j,ac[(i+j*2)%len(ac)],[.5,.75,1,1.5][j],reg+[-7,3,8,-12][j],level-4-j*3,shape=self.contour[j:]+self.contour[:j],offset=j*.5)
  elif style==7:
   line(0,period=1.5,kind='chord');line(1,ac[(i+4)%len(ac)],1.25,reg-7,level-9,offset=.75)
   line(2,ac[(i+6)%len(ac)],.5,reg+4,level-15,'chord',offset=1.)
  elif style==8:
   line(0,blend=True);line(1,ac[(i+2)%len(ac)],.75,reg-7,level-6,shape=self.contour[::-1],offset=.5);line(2,ac[(i+5)%len(ac)],1.5,reg+6,level-12,'chord',offset=1.)
  else:
   for j in range(3):line(j,ac[(i+j*3)%len(ac)],[.75,1,1.5][j],reg+[-7,4,9][j],level-5-j*3,shape=self.contour[j:]+self.contour[:j],offset=j*.5)
 def complete(self):
  plan=FORMS[self.k]
  for i,a in enumerate(range(0,self.nbars*4,16)):self.compose_scene(i,a,min(a+16,self.nbars*4),plan[i%len(plan)])
  # Each exit has a small specific gesture, not an automatic master fade.
  cut=self.sec(self.nbars*4-2.4);self.notes=[n for n in self.notes if n['start']<cut-.1]
  for n in self.notes:n['duration']=min(n['duration'],cut-n['start'])
  c=self.chord(self.sec(self.nbars*4-2),self.k)
  for j in range(1+self.k%3):
   inst=[self.palette[0],self.palette[2],self.palette[4]][j];beat=self.nbars*4-2.1+j*.6
   self.hit('last'+str(j),inst,beat,.6 if self.k%2 else 1.2,c[(j+self.k)%len(c)],41-j*4,'individual final fragment',exact=True)
  s=self.finish();s.update(seed=202610182100+self.k,areas=self.areas,metric_grid=self.beats,bar_tempi=self.tempi,final_chord_start=self.final_start,final_chord_fraction=(self.duration-self.final_start)/self.duration,requested_policy='Adjacent harmonic windows progress left to right; only field 39 after the convergence point. Shared expressive primary pulse, substantially fuller textures.')
  (ROOT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2));return s

if __name__=='__main__':
 import sys
 selected=[int(sys.argv[1])-1] if len(sys.argv)>1 else range(10)
 for k in selected:
  s=FlowPiece(k).complete();print(k+1,s['title'],round(s['duration'],1),'sec',len(s['notes']),'notes',round(100*s['final_chord_fraction'],1),'% final field',flush=True)
 index=[]
 for k in range(10):
  p=ROOT/'scores'/f'{k+1:02}.json'
  if p.exists():
   s=json.loads(p.read_text());index.append({x:s[x] for x in ['number','title','slug','duration','final_chord_start','final_chord_fraction']})
 (ROOT/'index.json').write_text(json.dumps(index,indent=2))
