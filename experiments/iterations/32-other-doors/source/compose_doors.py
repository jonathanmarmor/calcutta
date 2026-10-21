"""Other Doors: twelve unequal forms, deterministic event and orchestration decisions."""
from pathlib import Path
import math,random,bisect,json,collections
import numpy as np
from pitch_core import PitchCore,PITCHES
ROOT=Path('suite')
TRACKS=[
 ('The Small Door',52,'jewel','A quick succession of chamber apertures; a miniature journey rather than an overture.'),
 ('Reed Exchange',233,'dialogue','Unequal answering choirs, long wind lines, keyboard interruptions and changing protagonists.'),
 ('Fifths Under Glass',418,'graph','Walks through a graph of overlapping triads and sevenths; the same route changes register and color.'),
 ('A Very Short Parade',81,'genealogy','Construction-tree endpoints become a moving instrumental genealogy, folding and unfolding.'),
 ('Three Unequal Rivers',575,'rivers','Three phrase clocks with changing rational relationships; broad currents and fast tributaries.'),
 ('The Switches Are Singing',195,'gates','The sole amplitude-gate study: hard interlocks, ungated islands, variable duties and composite colors.'),
 ('One Window Left Open',41,'window','An intimate near-still miniature entirely within the destination field; a deliberate exception to the full journey.'),
 ('Orchard of Circuits',370,'relay','A cue-driven instrumental network: phrase endings hand energy, register and contour to another player.'),
 ('Thirty-Two Small Clocks',129,'clocks','Endpoint identities persist while unequal rhythmic clocks activate different branches of the construction.'),
 ('Rooms in a Long House',648,'rooms','An episodic large form with returning rooms transformed by changing harmony, ensemble and temporal scale.'),
 ('The Stair Remembers',176,'stair','Audible ascending and descending sequences through consonant chord subsets, with restrained mutations.'),
 ('An Unfinished Atlas',660,'atlas','A large additive/subtractive form: accumulate, clear, change direction, relocate, interrupt; a dry open-ended exit.')]
AREAS=[(0,2),(1,5),(5,6),(7,7),(8,12),(11,14),(14,15),(16,16),(17,21),(20,24),(24,27),(27,28),(29,32),(32,35),(35,38),(38,39)]
MODES=['ribbons','dialogue','chord_graph','genealogy','rivers','gates','still','relay','clocks','hocket','stair','slow_outer','chamber','fan','keyboard','subtraction']
class Doors(PitchCore):
 def __init__(self,k):
  self.k=k;self.title,self.duration,self.form,self.description=TRACKS[k];self.r=random.Random(202610210900+k);self.notes=[];self.counter=0;self.scenes=[];self.sequences=[];self.cues=[]
  self.slug=self.title.lower().replace(' ','_');self.seed=202610210900+k
  # A fresh primary grid for each track, with composed tempo plateaus and small phrase breathing.
  base=[116,86,72,129,92,101,57,94,107,83,98,78][k];beat=0;self.beats=[0.];bar=0
  while self.beats[-1]<self.duration-.6:
   bpm=base*[1,1.12,.88,1.04,.96,1.18,.83][(bar//6+k)%7]
   for q in range(4):
    self.beats.append(min(self.duration-.5,self.beats[-1]+60/bpm*(1+.008*math.sin(bar*.73+q*.8))))
    if self.beats[-1]>=self.duration-.5:break
   bar+=1
  self.nbeats=len(self.beats)-1;self.beats=np.array(self.beats);self.harmonies=[];self.areas=[]
  if self.form=='window':
   self.final_start=0.;self.harmonies=[dict(chord=39,start=0.,end=self.duration)];self.areas=[dict(first=39,last=39,start=0.,end=self.duration)]
  else:
   self.final_start=self.duration*.60
   weights=np.array([1.6,1.6,1.1,.7,1.35,1.,.85,.6,1.2,1.1,.9,.7,1.,.85,.75,.75]);weights*=np.array([1+.18*math.sin(i*1.9+k) for i in range(16)]);edges=np.r_[0,np.cumsum(weights)/sum(weights)*self.final_start]
   for i,(lo,hi) in enumerate(AREAS):
    start,end=float(edges[i]),float(edges[i+1]);self.areas.append(dict(first=lo,last=hi,start=start,end=end));order=list(range(lo,hi+1))
    if i==0:order=[1,2,0,2]
    elif len(order)==2:order=order+order[::-1]
    elif len(order)>2 and self.duration>200:order=order+[hi-1,hi]
    for j,ch in enumerate(order):self.harmonies.append(dict(chord=ch,start=start+(end-start)*j/len(order),end=start+(end-start)*(j+1)/len(order)))
   self.harmonies.append(dict(chord=39,start=self.final_start,end=self.duration));self.areas.append(dict(first=39,last=39,start=self.final_start,end=self.duration))
  self.starts=[h['start'] for h in self.harmonies]
  # Different actual sound inventories per work, with acoustic/electric and synthetic sources.
  count=[32,55,68,40,76,62,12,72,48,88,58,90][k];pool=list(range(97));self.r.shuffle(pool);self.palette=pool[:count]
  # Reeds, keys and classic synth colors get meaningful featured roles, not uniform random duties.
  required=([71,68,74,70,75,12,15,32,0,6] if self.form=='dialogue' else [0,1,2,3,4,5,6,7,12,15,19,33,41,51,71,74,88,96])
  if self.form=='window':required=[71,74,12,19,32,51]
  for j,inst in enumerate(required):
   if inst not in self.palette:self.palette[-1-j]=inst
  self.palette=list(dict.fromkeys(self.palette));self.usedsets=[]
 def sec(self,b):return float(np.interp(b,np.arange(len(self.beats)),self.beats))
 def bt(self,t):return float(np.interp(t,self.beats,np.arange(len(self.beats))))
 def add(self,part,inst,t,d,p,v,role,**kw):
  t=max(0.,t)
  if t>=self.duration-.2:return None
  h=self.hi(t);end=min(t+d,self.harmonies[h]['end']-.012,self.duration-.18)
  if end-t<.085:return None
  p=self.pitch(t,p);n=dict(id=self.counter,part=part,instrument=int(inst),start=round(t,6),duration=round(end-t,6),pitch=float(p),velocity=int(max(19,min(62,round(v)))),role=role,fields=[h],is_passing=False)
  self.counter+=1;self.notes.append(n);return n
 def emit(self,part,inst,b,d,p,v,role,limit,jitter=True):
  t=self.sec(b)+(self.r.uniform(-.012,.012) if jitter else 0);t=max(self.scene_start,t);end=min(self.sec(b+d),limit)
  n=self.add(part,inst,t,end-t,p,v,role)
  if n:n['beat']=float(b)
  return n
 def mode(self,i):
  f=self.form
  plans={
   'jewel':['hocket','chamber','stair','fan','slow_outer','ribbons'],
   'dialogue':['dialogue','chamber','keyboard','dialogue','slow_outer','ribbons','chord_graph'],
   'graph':['chord_graph','slow_outer','stair','chamber','chord_graph','fan','ribbons'],
   'genealogy':['genealogy','fan','hocket','genealogy','subtraction'],
   'rivers':['rivers','slow_outer','ribbons','rivers','dialogue','clocks','rivers','chord_graph'],
   'gates':['gates','gates','chamber','gates','hocket','gates','still','gates'],
   'window':['still','chamber','still','subtraction'],
   'relay':['relay','relay','keyboard','chamber','relay','fan','slow_outer'],
   'clocks':['clocks','genealogy','rivers','clocks','subtraction','hocket'],
   'rooms':['keyboard','slow_outer','dialogue','clocks','chord_graph','chamber','relay','fan','still','stair','ribbons','hocket','subtraction'],
   'stair':['stair','chord_graph','stair','dialogue','keyboard','stair','slow_outer'],
   'atlas':['ribbons','fan','slow_outer','relay','chord_graph','subtraction','keyboard','dialogue','stair','clocks','chamber','rivers','still','hocket']}
  plan=plans[f];return plan[i%len(plan)]
 def segment(self,i,a,b,mode):
  self.scene_start=self.sec(a);end=self.sec(b);before=len(self.notes);pal=[self.palette[(i*7+j)%len(self.palette)] for j in range(12)];self.usedsets.append(pal)
  if self.form=='dialogue':
   reeds=[71,68,74,70,75];pal[:3]=[reeds[(i+j)%5] for j in range(3)];pal[3:5]=[12,15]
  level=40+5*math.sin(i*.87+self.k*.6);reg=[65,77,59,83,71,68,79][(i+self.k)%7];dur=b-a
  shape=[0];
  for j in range(5+(i+self.k)%4):shape.append(shape[-1]+self.r.choice([-2,-1,1,1,2,3]))
  shape=[q-min(shape) for q in shape]
  def hit(j,t,d,p,v=0,role='phrase',inst=None,part=None):return self.emit(part or f'{i}-p{j}',pal[j%12] if inst is None else inst,t,min(d,b-t),p,level+v,role,end)
  def line(j,period=1,register=None,offset=0,stop=None,v=0,kind='scale',reverse=False,legato=.92):
   lo=a+offset;stop=b if stop is None else min(stop,b);t=lo;k=0;target=reg+(j%4-1.5)*7 if register is None else register;events=[]
   while t<stop-.12:
    pool=self.pool(self.sec(t));idx=min(range(len(pool)),key=lambda z:abs(pool[z]-target));cont=shape[::-1] if reverse else shape;degree=cont[k%len(cont)]-max(shape)//2+(k//len(cont))%3-1
    if kind=='chord':
     c=self.chord(self.sec(t),i+k//len(shape));p=c[(k+degree)%len(c)]
    else:p=pool[max(0,min(len(pool)-1,idx+degree))]
    rhythm=([1,.5,1.5,1,2,.5,1.5] if (i+j)%2 else [1.5,.5,1,2,1,1,.5]);ioi=period*rhythm[k%len(rhythm)]
    # Endings lengthen and breathe; no shared da-da-DUM tutti figure.
    if k%len(shape)==len(shape)-1:ioi*=1.4
    n=hit(j,t,min(ioi*legato,stop-t),p,v+4*math.sin((k%len(shape)+.5)/len(shape)*math.pi),kind+' shaped line')
    if n:events.append(n['id'])
    t+=ioi
    if k%len(shape)==len(shape)-1:t+=period*.6
    k+=1
   self.sequences.append(dict(section=i+1,part=f'{i}-p{j}',mode=kind,contour=shape[::-1] if reverse else shape,period_beats=period,note_ids=events))
  def hold(j,period=5,register=None,offset=0,v=-8):
   t=a+offset;k=0
   while t<b-.15:
    c=self.chord(self.sec(t),i+k);p=min(c,key=lambda p:abs(p-(reg+j*2 if register is None else register)));hit(j,t,min(period*.97,b-t),p,v+2*math.sin(k+j),'quiet sustained field member');t+=period;k+=1
  if mode=='ribbons':
   for j in range(8):line(j,[1,1.5,.75,2/3,1.25,2,.5,2.5][j],register=51+j*5.6,offset=j*.27,v=-j%3-5,reverse=j%2==0)
   if self.form=='atlas' and i%2==0:
    for j in (8,9):hold(j,6,register=54+(j-8)*33,v=-13)
  elif mode=='dialogue':
   mid=a+dur*.5
   for j in range(3):line(j,1 if i%2 else 1.5,register=58+j*10,offset=j*.13,stop=mid+1,v=-3)
   for j in range(3,6):line(j,.75 if i%2 else 1,register=54+(j-3)*12,offset=dur*.46+(j-3)*.2,v=-4,reverse=True)
   for j in range(6,9):hold(j,4+j%2,register=50+(j-6)*13,offset=j*.06,v=-10)
  elif mode=='chord_graph':
   # Nodes are consonant subsets. Choose the next node by low common-tone/voice-leading cost.
   t=a;k=0;prev=self.chord(self.sec(t),i)
   while t<b-.1:
    choices=[self.chord(self.sec(t),q) for q in range(12)];cost=lambda c:sum(min(abs(p-q) for q in prev) for p in c)+self.r.random()*.25
    ranked=sorted(choices,key=cost);c=ranked[(k//3)%min(4,len(ranked))];span=[2,3,4,2.5][(k+i)%4]
    for j,p in enumerate(c):hit(j,t+j*.12,min(span*.93,b-t-j*.12),p,-6-j*2+4*math.sin(k*.8),'overlapping triad/seventh graph')
    prev=c;t+=span;k+=1
   for j in range(4,8):line(j,[1,.75,2,1.5][j-4],register=52+(j-4)*11,offset=(j-4)*.5,v=-8,kind='chord',reverse=j%2==0)
  elif mode=='genealogy' or mode=='clocks':
   active=range((i*5)%16,(i*5)%16+16) if mode=='clocks' else range(0,32,2)
   for jj in active:
    voice=jj%32;inst=self.palette[(voice*7+i//2)%len(self.palette)];period=([1,1.5,2,2.5,3,4][voice%6] if mode=='clocks' else [1,2,3][voice%3]);t=a+(voice%5)*.2
    while t<b-.1:
     h=self.hi(self.sec(t));p=PITCHES[self.harmonies[h]['chord']][voice]
     hit(voice,t,min(period*.67,b-t),p,-10+3*math.sin(t*.5+voice),'construction endpoint clock',inst=inst,part=f'{i}-edge{voice}');t+=period
  elif mode=='rivers':
   ratios=[[1,4/3,5/4],[1,3/2,7/6],[1,5/3,4/5]][(i//2)%3]
   for j in range(9):
    river=j//3;period=ratios[river]*[.75,1.5,2.25][(i+river)%3];line(j,period,register=51+j*5,offset=(j%3)*.33,v=-6,reverse=river==1,legato=.97)
  elif mode=='gates':
   for j in range(8):hold(j,4+j%3,register=50+j*5.4,offset=j*.06,v=-10)
   tempo=60/(self.sec(min(a+1,self.nbeats))-self.sec(a))
   for n in self.notes[before:]:
    j=int(n['part'].split('-p')[1]);n['dsp']=dict(type='hard_gate',rate=tempo/60*[1,1.5,2,2.5,3,4,2/3,1.25][(j+i)%8],duty=[.32,.65,.48,.75][(j+i)%4],phase=j/8,edge_ms=1.)
   line(8,1.5,register=79,v=2,kind='chord');line(9,.75,register=65,offset=.5,v=-4)
  elif mode=='still':
   layers=3 if self.form=='window' else 7
   for j in range(layers):hold(j,7+j*.7,register=(61+j*6 if self.form=='window' else 52+j*5.8),offset=j*.31,v=-8 if self.form=='window' else -14)
   if self.form!='window':line(8,2.3,register=87,offset=1,v=0)
  elif mode=='relay':
   # A queue of cues, not independently generated background lines.
   queue=[(a+j*.6,j,reg+j*2,[0,1,3,2]) for j in range(5)];generation=0
   while queue and generation<160:
    queue.sort(key=lambda x:x[0]);t,j,target,cell=queue.pop(0)
    if t>=b-.2:continue
    span=0.;ids=[];period=[.5,.75,1,1.25][(j+generation)%4]
    for z,deg in enumerate(cell):
     at=t+span
     if at>=b-.1:break
     pool=self.pool(self.sec(at));base=min(range(len(pool)),key=lambda q:abs(pool[q]-target));p=pool[max(0,min(len(pool)-1,base+deg-1))];d=period*[1,1,1.5,2][z%4];n=hit(j,at,d*.93,p,-4+z,'cue network cell')
     if n:ids.append(n['id'])
     span+=d
    nxt=(j+3+generation%2)%10;mut=cell[1:]+cell[:1] if generation%3 else cell[::-1];trigger=t+span*.75+period*.3
    self.cues.append(dict(section=i+1,from_player=j,to_player=nxt,trigger_beat=trigger,note_ids=ids));queue.append((trigger,nxt,target+self.r.choice([-5,-2,2,5]),mut));generation+=1
   hold(10,5,register=53,v=-12);hold(11,7,register=90,offset=2,v=-14)
  elif mode=='hocket':
   for band in range(2):
    t=a+band*.5;k=0
    while t<b-.1:
     pool=self.pool(self.sec(t));ix=(k*2+band*5+i)%len(pool);ioi=[.5,.75,.5,1.25,1,.5,1.5][(k+band)%7];hit((k%4)+band*4,t,ioi*.92,pool[ix],-3-band*4,'timbral relay melody');t+=ioi;k+=1
   for j in range(8,12):hold(j,4+j%3,register=51+(j-8)*10,offset=(j-8)*.3,v=-10)
  elif mode=='stair':
   for j in range(7):line(j,[.75,1,1.5,2,.5,1.25,2.5][j],register=51+j*6,offset=j*.3,v=-5,kind='chord',reverse=(j+i)%2==0)
   hold(8,6,register=54,v=-11)
  elif mode=='slow_outer':
   for j in range(5):line(j,[.5,.75,1,2/3,1.25][j],register=61+j*4,offset=j*.33,v=-10)
   line(5,3,register=49,v=-1,kind='chord');line(6,3.5,register=91,offset=1.7,v=1,reverse=True);hold(7,5,register=78,v=-12)
  elif mode=='chamber':
   count=3 if self.form=='window' else 5
   for j in range(count):line(j,[1.5,2,1,.75,2.5][j],register=56+j*8,offset=j*.5,v=-3,reverse=j%2==1)
  elif mode=='fan':
   for j in range(10):
    t=a+j*.12;k=0
    while t<b-.1:
     fraction=(t-a)/max(dur,1);target=69+(j-4.5)*(1+fraction*6) if i%2 else 69+(j-4.5)*(7-fraction*6)
     hit(j,t,min(2.5+(j%3),b-t),target,-10+4*math.sin(k*.8),'unisons opening/closing into field');t+=2.7+j%3;k+=1
  elif mode=='keyboard':
   for j in range(8):line(j,[.5,.75,1,1.5,.75,2,1.25,2.5][j],register=51+j*5.5,offset=j*.25,v=-6,kind='chord' if j%2 else 'scale',reverse=j%2==1,legato=.84)
  elif mode=='subtraction':
   for j in range(9):
    stop=a+dur*(1-j*.065);line(j,[1,1.5,2,.75][j%4],register=51+j*5,offset=j*.2,stop=stop,v=-7,kind='chord',reverse=True)
   # One newly exposed high or low strand survives the clearing.
   line(10,2,register=92 if i%2 else 49,offset=dur*.55,v=0)
  self.scenes.append(dict(start=round(self.sec(a),6),end=round(end,6),texture=mode,start_beat=a,end_beat=b,ensemble=sorted(set(n['instrument'] for n in self.notes[before:])),section_level=level,form=self.form))
 def complete(self):
  a=0.;i=0
  while a<self.nbeats-.1:
   # Variable spans, not a fixed four-bar loop; changes always under 26 seconds.
   bars=[3,5,4,2,6,3,4][(i+self.k)%7];b=min(self.nbeats,a+bars*4)
   while self.sec(b)-self.sec(a)>25:b-=4
   if self.form=='window':b=min(self.nbeats,a+[12,8,12,8][i%4])
   self.segment(i,a,b,self.mode(i));a=b;i+=1
  # Missing short harmonic visits receive a brief pitched lens, not new harmony.
  for hidx,h in enumerate(self.harmonies):
   if not any(n['fields']==[hidx] for n in self.notes):
    self.add('harmonic-lens',self.palette[hidx%len(self.palette)],h['start']+.04,min(1.2,h['end']-h['start']-.08),PITCHES[h['chord']][hidx%32],30,'field coverage')
  cut=self.duration-1.35
  self.notes=[n for n in self.notes if n['start']<cut-.05]
  for n in self.notes:n['duration']=min(n['duration'],cut-n['start'])
  # Distinct dry exits: an interruption, a reply, an isolated interval, or an exposed last note.
  for j in range([2,1,3,1,2,1,1,3,2,1,3,2][self.k]):
   t=cut+.15+j*.18;p=self.chord(t,self.k)[j%len(self.chord(t,self.k))]
   self.add(f'last{j}',self.palette[(self.k+j)%len(self.palette)],t,.37 if self.k%2 else .55,p,34-j*4,'specific dry exit')
  self.notes.sort(key=lambda n:(n['start'],n['id']));slots=collections.defaultdict(list);voices=[]
  for n in self.notes:
   key=(n['part'],n['instrument']);own=slots[key];slot=next((j for j,(end,v) in enumerate(own) if end<=n['start']+1e-6),None)
   if slot is None:slot=len(own);own.append((-1,len(voices)));voices.append(dict(part=n['part'],instrument=n['instrument']))
   n['voice']=own[slot][1];own[slot]=(n['start']+n['duration'],n['voice'])
  s=dict(number=self.k+1,title=self.title,slug=self.slug,duration=self.duration,description=self.description,seed=self.seed,form=self.form,harmonies=self.harmonies,areas=self.areas,notes=self.notes,voices=voices,sections=self.scenes,sequences=self.sequences,cue_network=self.cues,metric_grid=self.beats.tolist(),final_chord_start=self.final_start,final_chord_fraction=(self.duration-self.final_start)/self.duration,instrument_pool=self.palette,pitch_policy='Exact original field members only; no added pitches, octave folding, or held retuning',tremolo_allowed=self.form=='gates',sound_policy='Saved sample-derived fixed-frequency models; no pitch modulation, reverb, delay, chorus, click or master ending fade')
  (ROOT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2));return s
if __name__=='__main__':
 index=[]
 for k in range(len(TRACKS)):
  s=Doors(k).complete();index.append({x:s[x] for x in ['number','title','slug','duration','description','form','final_chord_start']});print(k+1,s['title'],s['duration'],'s',len(s['notes']),'notes',len(set(n['instrument'] for n in s['notes'])),'sounds',flush=True)
 (ROOT/'index.json').write_text(json.dumps(index,indent=2))
