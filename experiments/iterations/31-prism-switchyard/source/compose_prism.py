"""Prism Switchyard: new material, changing ensembles and dedicated amplitude gates."""
from flow_base import FlowPiece
from pathlib import Path
import json,random,math,collections
ROOT=Path('suite')
NAMES=['plucked staircase / wind answers','slow brass lattice, quick wooden edges','overlapping contrapuntal ribbons','cut-glass interlocking gates','low ensemble / high solo exchanges','dry keyboard invention','seventh-chord relay, contrary motion','quiet sustained friction / single clear lead','gated chords with ungated melody','chamber dialogue, then expanding tutti','fast registral hocket / long bass','three clocks in acoustic colors','narrow unisons opening into fifths','asymmetric ringing-metal procession','widely spaced foreground over busy middle','returning gates, shifting duty cycles']
PLAN=[0,4,5,3,2,6,10,7,1,11,9,8,12,5,14,13,2,6,15,4,10,1,7,11,0,8,9,13,5,12,14,3,6]
class Prism(FlowPiece):
 def __init__(self):
  super().__init__(0);self.r=random.Random(202610183701);self.contour=[0,2,1,4,3,5,2];self.rhythm=[1,1.5,.5,2,1,.5,1.5]
  self.pool97=list(range(97));random.Random(202610183702).shuffle(self.pool97)
 def scene(self,i,a,b,style):
  pal=[self.pool97[(i*8+j)%97] for j in range(8)];before=len(self.notes)
  level=41+5*math.sin(i*1.21);reg=[68,79,60,76,71,83][i%6]
  # Different phrase shapes are newly drawn for every scene, not recycled themes.
  shape=[0];
  for j in range(5+i%3):shape.append(shape[-1]+self.r.choice([-2,-1,1,2,3]))
  shape=[x-min(shape) for x in shape]
  def line(j,period=1,register=None,offset=0,end=None,kind='scalar',v=0,gate=.91,shape0=None):
   self.line(f's{i}-line{j}',pal[j%8],a+offset,b if end is None else end,reg+(j%3-1)*8 if register is None else register,period,level+v,kind,shape if shape0 is None else shape0,False,.035,gate)
  def long(j,period=4,register=None,offset=0,v=-9,chord=False):
   t=a+offset;k=0
   while t<b-.2:
    c=self.chord(self.sec(t),i+k//2);p=min(c,key=lambda p:abs(p-(reg+j*2 if register is None else register))) if chord else self.pitch(self.sec(t),reg+j*2 if register is None else register)
    self.hit(f's{i}-held{j}',pal[j],t,min(period*.97,b-t),p,level+v+3*math.sin(k*.9+j),'sustained independent harmonic line',True)
    t+=period;k+=1
  def pulse(j,offset=0,step=2,register=56,v=-8):
   for k in range(math.ceil((b-a-offset)/step)):
    t=a+offset+k*step
    if t>=b-.1:break
    c=self.chord(self.sec(t),i+k//3);p=min(c,key=lambda p:abs(p-register))
    self.hit(f's{i}-anchor{j}',pal[j],t,min(step*.86,b-t),p,level+v+3*math.sin(k*.75),'gentle metrical anchor',True)
  if style==0:
   for j in range(4):line(j,[.5,1,1.5,.75][j],offset=j*.5,kind='chord',v=-j*2)
   for j in range(4,8):long(j,3+(j%2),register=52+(j-4)*9,offset=(j-4)*.2)
  elif style==1:
   for j in range(5):long(j,5+j*.5,register=52+j*7,offset=j*.08,chord=True)
   for j in range(5,8):line(j,[.5,.75,1][j-5],register=78+(j-5)*5,offset=.5*(j-5),v=-7)
  elif style==2:
   for j in range(8):line(j,[1,1.25,.75,1.5,2,.5,1,2.5][j],register=53+j*5,offset=j*.25,v=-5,shape0=shape if j%2 else shape[::-1])
  elif style in (3,8,15):
   for j in range(6):long(j,4 if style!=15 else 6,register=51+j*7,offset=j*.055,v=-8,chord=(j%2==0))
   for j in (6,7):line(j,[1.5,.75][j-6],register=74+(j-6)*9,offset=j%2,v=0,kind='chord')
   bpm=self.tempi[int(a//4)]
   for n in self.notes[before:]:
    j=next((j for j in range(6) if n['part']==f's{i}-held{j}'),None)
    if j is not None:n['dsp']={'type':'hard_gate','rate':bpm/60*[2,3,4,1.5,2.5,1][j], 'duty':[.42,.59,.32,.66,.48,.73][(j+i)%6], 'phase':j/6,'edge_ms':1.0}
  elif style==4:
   for j in range(4):line(j,1.5,register=49+j*4,offset=j*.25,end=a+9,kind='chord',v=-5)
   for j in range(4,8):line(j,.75 if j%2 else 1,register=75+(j-4)*4,offset=6+(j-4)*.25,v=-3)
   long(1,4,register=59,offset=8);long(2,4,register=65,offset=8)
  elif style==5:
   for j in range(6):line(j,[.75,1,1.5,2/3,1.25,.5][j],register=52+j*6,offset=j*.25,v=-5,kind='chord' if j%2 else 'scalar')
   long(6,4,register=54);long(7,6,register=87,offset=2)
  elif style==6:
   for j in range(8):line(j,[1,1.5,.75,2][j%4],register=51+j*5.5,offset=j*.4,kind='chord',shape0=list(range(4)) if j%2 else list(range(3,-1,-1)),v=-5)
  elif style==7:
   for j in range(6):long(j,7+j%3,register=58+j*3.7,offset=j*.15,v=-13)
   line(6,1.7,register=86,offset=.5,v=1);pulse(7,step=2,register=50,v=-11)
  elif style==9:
   for j in range(4):line(j,1 if j%2 else 1.5,register=56+j*8,offset=j*.5,v=-5)
   for j in range(4,8):line(j,.75,register=52+(j-4)*10,offset=7+(j-4)*.5,kind='chord',v=-6)
  elif style==10:
   # One melody moves through four colors while longer lines remain independently audible.
   t=a;k=0
   while t<b-.1:
    q=self.pool(self.sec(t));p=q[(i+k*2)%len(q)];d=[.5,.5,1,.75,.25,1.5][k%6]
    self.hit(f's{i}-hocket{k%4}',pal[k%4],t,min(d*.92,b-t),p,level-2,'registral hocket',True);t+=d;k+=1
   for j in range(4,8):long(j,3+j%3,register=49+(j-4)*9,offset=(j-4)*.3,v=-8)
  elif style==11:
   for j in range(8):line(j,[1,2/3,1.5][j%3],register=52+j*5,offset=(j%3)*.5,v=-7,shape0=shape[j%3:]+shape[:j%3])
  elif style==12:
   for j in range(8):
    t=a+j*.12;k=0
    while t<b-.2:
     c=self.chord(self.sec(t),i+k);target=68+(j%2)*.2 if t<a+5 else 51+j*5
     p=min(self.raw(self.sec(t)) if t<a+5 else c,key=lambda p:abs(p-target))
     self.hit(f's{i}-fan{j}',pal[j],t,min([1,2,3][j%3]*.95,b-t),p,level-8+3*math.sin(k),'unisons opening into chord tones',True);t+=[1,2,3][j%3];k+=1
  elif style==13:
   for j in range(8):line(j,[1.25,2,1.5,2.5][j%4],register=52+j*5,offset=j*.37,v=-7,kind='chord',gate=.97)
  elif style==14:
   for j in range(5):line(j,[.5,.75,2/3,1,1.5][j],register=61+j*4,offset=j*.25,v=-10)
   for j in range(5,8):line(j,[3,2.5,4][j-5],register=[49,85,93][j-5],offset=(j-5)*1.5,v=-1,kind='chord',gate=.96)
  # Make every scene boundary an audible change of ensemble. No new note crosses it.
  for n in self.notes[before:]:
   if n['start']<self.sec(a):
    oldend=n['start']+n['duration'];n['start']=round(self.sec(a),6);n['duration']=oldend-n['start'];n['fields']=[self.hi(n['start']+.000001)]
    if not n['is_passing']:n['pitch']=self.pitch(n['start']+.000001,n['pitch'])
   n['duration']=min(n['duration'],self.sec(b)-n['start']-.01)
  self.notes=[n for n in self.notes if n['duration']>=.095]
  self.scenes.append(dict(start=self.sec(a),end=self.sec(b),texture=NAMES[style],start_bar=int(a/4),end_bar=int(b/4),ensemble=pal,nominal_bpm=self.tempi[int(a/4)],hard_gate=style in (3,8,15)))
 def complete(self):
  for i,a in enumerate(range(0,self.nbars*4,16)):self.scene(i,a,min(a+16,self.nbars*4),PLAN[i%len(PLAN)])
  cut=self.sec(self.nbars*4-1.5)
  self.notes=[n for n in self.notes if n['start']<cut-.1]
  for n in self.notes:n['duration']=min(n['duration'],cut-n['start'])
  c=self.chord(cut,2)
  for j in range(3):self.hit('last-question'+str(j),[6,18,71][j],self.nbars*4-1.25+j*.2,.55,c[j%len(c)],36-j*5,'short dry unfinished question',True)
  s=self.finish();s.update(title='Prism Switchyard',slug='calcutta_prism_switchyard',seed=202610183701,areas=self.areas,metric_grid=self.beats,bar_tempi=self.tempi,final_chord_start=self.final_start,final_chord_fraction=(self.duration-self.final_start)/self.duration,instrument_pool=list(range(97)),tremolo_allowed=True,gate_policy='Dedicated sections only. Amplitude gates with 1ms edges; fixed pitch carriers.',instrument_policy='All 97 available source models, changing eight-color ensembles; no unchanged foundation across textures.')
  (ROOT/'scores'/'01.json').write_text(json.dumps(s,indent=2));return s
if __name__=='__main__':
 s=Prism().complete();counts=collections.Counter(n['instrument'] for n in s['notes']);assert len(counts)==97;print(s['title'],s['duration'],len(s['notes']),len(counts),min(counts.values()))
