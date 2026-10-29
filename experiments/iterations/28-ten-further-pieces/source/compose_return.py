"""Ten new Calcutta pieces: internally developed material, no quotations/research.
The public brief and each piece's explicit form are in suite/BRIEF.md and DESIGNS.
"""
from pathlib import Path
import random,math,json,bisect,collections
import numpy as np
ROOT=Path('suite');(ROOT/'scores').mkdir(parents=True,exist_ok=True)
PITCHES=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
TITLES=['Grain and Line','Tall Rooms','Many Small Clocks','Shared Breath','Wood and Wire','The Long Way Through','Close Weave','Inside the Chord','Moving Floors','Loose Threads']
SLUGS=['grain_and_line','tall_rooms','small_clocks','shared_breath','wood_and_wire','long_way_through','close_weave','inside_the_chord','moving_floors','loose_threads']
DURATIONS=[354,318,342,330,366,306,348,324,360,336]
STYLES=['melody with accompaniment','sequences through chord roots','independent expressive clocks','choirs in dialogue','timbral melody / hocket','quiet dissonance with foreground','staggered melodic imitation','one exposed voice','interlocking cells','inner chord progression','bright measured counterpoint','long song / small inner figures','neighboring-field hinge','changing composite / solo color','continuous melodic ascent or descent','fifth and seventh exchanges','acoustic chamber counterpoint','long transparent threads']
# Explicitly different trajectories. No imported musical forms or tunes.
DESIGNS=[
 [0,4,3,1,7,16,2,5,8,11,9,4,6,17,10,1,13,7,2,15,16,5,8,0,14,3],
 [7,9,4,17,0,11,5,1,3,6,17,10,9,2,7,15,14,4,11,8,5,16,0,17],
 [16,2,7,8,11,4,2,3,17,6,10,5,2,1,13,7,8,16,2,14,9,4,11,6,17,3],
 [3,0,7,4,16,3,9,1,11,6,5,3,8,17,10,12,0,2,7,15,3,14,16,11,4,9],
 [4,7,0,8,1,16,13,3,17,2,4,9,10,11,7,6,8,14,0,15,5,4,16,1,3,17,13,0],
 [0,17,4,11,6,7,1,5,14,16,0,3,2,7,9,11,6,15,13,5,8,0,17,14],
 [6,7,16,10,3,17,8,1,4,6,11,2,9,7,16,5,10,14,3,6,13,4,15,8,0,17,1,16],
 [9,7,0,15,4,5,1,17,3,9,10,11,16,7,1,8,5,14,15,4,2,9,0,13,17,6],
 [11,4,7,2,16,10,0,8,17,1,3,2,14,6,9,7,10,13,16,5,2,4,11,15,0,8,3,17],
 [7,4,16,17,8,0,3,1,5,14,7,13,6,2,9,11,4,10,17,0,8,15,3,16,1,5,14,7]
]
# Each palette has acoustic soloists, short/long sampled colors and restrained synths.
ENSEMBLES=[
 [10,8,27,14,29,20,2,24,15,6,12,30],
 [13,18,29,22,12,28,7,15,33,3,14,17],
 [9,24,15,29,8,32,1,27,10,4,22,30],
 [27,28,17,26,8,14,3,29,10,5,15,31],
 [12,14,24,10,15,22,4,21,8,2,28,29],
 [18,29,10,13,27,32,5,8,15,6,14,28],
 [15,27,28,29,30,13,2,24,9,0,10,17],
 [8,22,18,29,10,25,3,14,27,7,13,20],
 [20,8,9,17,12,28,1,24,10,6,27,29],
 [13,10,15,28,14,29,4,8,27,0,22,12]
]

class Piece:
 def __init__(self,k):
  self.k=k;self.r=random.Random(202610181100+k);self.duration=DURATIONS[k];self.notes=[];self.scenes=[];self.sequences=[];self.counter=0
  # Neighbor exchanges first; later fields sometimes reverse locally. This is a preference, not a pitch rule.
  order=[2,3,2,4,3,2,4,3,5,4,5,6,7,6,8,7,9]+list(range(10,40))+[38,39,0,39]
  if k%3==1:order[2:6]=[2,3,2,4];order.insert(10,3)
  if k%3==2:order[8:13]=[4,5,4,6,5];order.insert(14,6)
  for i in range(20,len(order)-5,7):
   if (i+k)%2:order[i:i+2]=reversed(order[i:i+2])
  order.insert(11,1) # a brief expressive 1:2 visit; none of the pieces opens there
  weights=[(1.45 if i<17 else .87)*self.r.uniform(.8,1.25) for i in range(len(order))];total=sum(weights);cursor=0.;self.harmonies=[]
  for ch,w in zip(order,weights):
   end=cursor+self.duration*w/total;self.harmonies.append(dict(chord=ch,start=cursor,end=end));cursor=end
  self.harmonies[-1]['end']=self.duration;self.starts=[h['start'] for h in self.harmonies];self.palette=ENSEMBLES[k]
  self.contour=[0];pos=0
  for i in range(6+k%3):pos+=self.r.choice([-2,-1,1,1,2]);self.contour.append(pos)
  lo=min(self.contour);self.contour=[x-lo for x in self.contour]
  self.rhythm=[self.r.choice([.5,.75,1,1.25,1.5,2]) for _ in self.contour]
  # Never the habitual short-short-long cell; all sequences start with fresh material.
  if self.rhythm[0]==self.rhythm[1]:self.rhythm[1]*=1.5
 def hi(self,t):return min(len(self.harmonies)-1,max(0,bisect.bisect_right(self.starts,t)-1))
 def raw(self,t):return sorted(set(PITCHES[self.harmonies[self.hi(t)]['chord']]))
 def pool(self,t):
  out=[]
  for x in self.raw(t):
   if not out or x-out[-1]>=1.05:out.append(x)
  return out
 def pitch(self,t,target):return min(self.raw(t),key=lambda p:abs(p-target))
 def chord(self,t,rank=0):
  raw=self.raw(t);out=[]
  for root in raw:
   third=min(raw,key=lambda p:abs(p-root-4.33832));fifth=min(raw,key=lambda p:abs(p-root-7.01955))
   if abs(third-root-4.33832)<.55 and abs(fifth-root-7.01955)<.32:
    c=[root,third,fifth];opts=[p for p in raw if p>fifth+.8 and min(abs(p-root-9.68826),abs(p-root-11.08))<.4]
    if opts:c.append(min(opts,key=lambda p:min(abs(p-root-9.68826),abs(p-root-11.08))))
    if not out or root-out[-1][0]>.5:out.append(c)
  if not out:
   pairs=[(abs(b-a-7.01955),[a,b]) for a in raw for b in raw if b>a];out=[min(pairs)[1]]
  return out[rank%len(out)]
 def add(self,part,inst,t,d,p,v,role,passing=False,anchors=None,blend=False):
  if t<0 or t>=self.duration-.12:return None
  h=self.hi(t);end=min(t+d,self.duration-.08,self.harmonies[h]['end']-.018)
  if end-t<.095:return None
  if not passing:p=self.pitch(t,p)
  n=dict(id=self.counter,part=part,instrument=inst,start=round(t,6),duration=round(end-t,6),pitch=float(p),velocity=round(max(23,min(70,v))),role=role,fields=[h],is_passing=passing,attack=.006 if inst not in [27,28,29,30,31] else .012)
  if anchors:n['anchors']=anchors
  self.counter+=1;self.notes.append(n)
  if blend:
   other={10:6,8:16,27:24,29:7,15:9,13:5,14:2,28:22}.get(inst)
   if other is not None:
    nn=dict(n);nn['id']=self.counter;self.counter+=1;nn['part']=part+'-blend';nn['instrument']=other;nn['velocity']=max(23,n['velocity']-15);nn['is_passing']=False
    # Passing notes remain individual; blends are field members only.
    if not passing:self.notes.append(nn)
  return n
 def phrase(self,part,inst,a,b,beat=.7,register=70,v=52,shape=None,kind='scalar',passing=.12,sequence=True,blend=False,gate=.85,stretch=1.):
  shape=list(self.contour if shape is None else shape);t=a;rep=0;previous_target=register;step=0
  while t<b-.2:
   contour=shape[:]
   if rep%4==3:contour[-1]+=self.r.choice([-1,1])
   base=register+(rep%4-1)*1.8*(1 if self.k%2==0 else -1)
   events=[]
   for j,degree in enumerate(contour):
    if t>=b-.14:break
    pool=self.pool(t)
    if kind=='chord':
     c=self.chord(t,rep+int(register/12));p=c[degree%len(c)]
    elif kind=='linear':p=min(pool,key=lambda x:abs(x-(base+degree*1.6)))
    else:
     idx=min(range(len(pool)),key=lambda z:abs(pool[z]-base));ix=idx+degree-(max(shape)//2);ix=abs(ix)%(2*(len(pool)-1));ix=min(ix,2*(len(pool)-1)-ix);p=pool[ix]
    ioi=beat*self.rhythm[j%len(self.rhythm)]*stretch
    # Different measured phrasing inside stable independent tempos.
    if j==len(contour)-1:ioi*=1.4
    accent=7*math.sin(math.pi*(j+.8)/(len(contour)+.6));vel=v+accent+self.r.uniform(-3,3)
    events.append(dict(t=t,ioi=ioi,p=p,v=vel));t+=ioi;step+=1
   for j,e in enumerate(events):
    nxt=events[j+1] if j+1<len(events) else None
    can=nxt and self.hi(e['t'])==self.hi(nxt['t']) and 1.6<abs(nxt['p']-e['p'])<4.8 and .65<e['ioi']<2.15 and self.r.random()<passing
    if can:
     p=(e['p']+nxt['p'])/2
     if min(abs(p-x) for x in self.raw(e['t']))<.035:can=False
    n=self.add(part,inst,e['t'],min(e['ioi']*(.64 if can else gate),b-e['t']),e['p'],e['v'],kind+' phrase',blend=blend)
    if can and n:
     # Always an unaccented, brief connector between two structural field pitches.
     pn=self.add(part,inst,e['t']+e['ioi']*.72,min(e['ioi']*.22,.44),p,e['v']-11,'passing connection',passing=True,anchors={'from_pitch':e['p'],'to_pitch':nxt['p'],'to_start':round(nxt['t'],6),'from_id':n['id']})
   self.sequences.append(dict(part=part,instrument=inst,start=a if rep==0 else events[0]['t'] if events else t,repeat=rep,contour=contour,beat=beat,kind=kind))
   t+=beat*self.r.choice([.65,1.1,1.7]);rep+=1
   if not sequence:break
 def frame(self,part,insts,a,b,rank=0,v=34,spacing=.17):
  c=self.chord(a,rank)
  for j,p in enumerate(c):self.add(part+str(j),insts[j%len(insts)],a+j*spacing,max(.2,b-a-j*spacing),p,v+self.r.uniform(-3,3)-j*.5,'quiet triad/seventh foundation')
 def scene(self,idx,a,b,sty,density,tempo):
  self.scenes.append(dict(start=a,end=b,texture=STYLES[sty],density=density,nominal_bpm=tempo))
  # Shorter phrase units retain the scene identity across harmonic changes.
  local=[a]+[h['start'] for h in self.harmonies if a+.2<h['start']<b-.2]+[b]
  for seg,(x,y) in enumerate(zip(local,local[1:])):
   self.texture(idx,seg,x+.055,y-.06,sty,density,tempo)
 def texture(self,idx,seg,a,b,sty,density,tempo):
  if b-a<.5:return
  r=self.r;pal=self.palette;beat=60/tempo;dur=b-a;tag=f'{idx}-{seg}-';lead=pal[(idx+seg)%len(pal)];ac=[x for x in pal if x>=8];lead=ac[(idx+seg)%len(ac)] if idx%4!=2 else pal[6+(seg%2)*3]
  reg=[67,76,61,82][(idx+self.k)%4];level=48+5*math.sin(idx*.53+self.k)
  primary=lambda inst,offset=0,bpm=1,register=reg,v=level,kind='scalar',blend=False: self.phrase(tag+'lead'+str(offset),inst,a+offset,b,beat*bpm,register,v,kind=kind,passing=.16,blend=blend)
  if sty==0:
   primary(lead,kind='linear');self.phrase(tag+'accomp',ac[(idx+3)%len(ac)],a+.3,b,beat*1.65,57,35,kind='chord',passing=0)
  elif sty==1:
   self.phrase(tag+'stack',lead,a,b,beat*.65,reg,level,kind='chord',passing=0,blend=idx%3==0)
   self.phrase(tag+'descending',ac[(idx+4)%len(ac)],a+beat*.8,b,beat*.93,reg-8,level-13,shape=list(reversed(self.contour)),kind='chord',passing=0)
  elif sty==2:
   for layer,ratio in enumerate([1.,1.31,.73,.53][:2+min(2,density//3)]):
    self.phrase(tag+'clock'+str(layer),pal[(idx+layer*3)%len(pal)],a+layer*.21,b,beat*ratio,reg+[-9,5,-1,10][layer],level-6-layer*2,shape=self.contour[layer:]+self.contour[:layer],passing=.08,stretch=[1,1.1,.93,1.04][layer])
  elif sty==3:
   mid=a+dur*.51
   for group,(aa,bb) in enumerate([(a,mid+.15),(a+dur*.46,b)]):
    for layer in range(2 if density<5 else 3):
     self.phrase(tag+'choir'+str(group)+str(layer),ac[(idx+group*3+layer)%len(ac)],aa+layer*.025,bb,beat*(1 if group==0 else .85),reg+layer*5-group*4,level-9-layer*3,kind='chord',shape=self.contour if group==0 else self.contour[::-1],passing=0)
  elif sty==4:
   t=a;j=0;shape=self.contour;last=None
   while t<b-.15:
    pool=self.pool(t);base=min(range(len(pool)),key=lambda z:abs(pool[z]-reg));p=pool[(base+shape[j%len(shape)])%len(pool)]
    ioi=beat*[.75,1.25,.5,1.5,1,2][(j+self.k)%6];inst=ac[(idx+j)%len(ac)]
    self.add(tag+'hocket'+str(j%len(ac)),inst,t,min(ioi*.9,b-t),p,level+5*math.sin(j*.8),'continuous melody handed between colors');t+=ioi;j+=1
   self.frame(tag+'floor',[pal[5],8],a+.2,a+dur*.7,idx,30)
  elif sty==5:
   raw=self.raw(a);cluster=[x for x in raw if 62<x<80][::2][:6]
   for j,p in enumerate(cluster):self.add(tag+'held'+str(j),ac[(idx+j)%len(ac)],a+j*.19,min(dur*.8,b-a-j*.19),p,29+j%3,'quiet held dissonance')
   primary(lead,offset=dur*.23,bpm=1.25,v=level-1,kind='linear')
  elif sty==6 or sty==16:
   n=2+min(3,density//2)
   for j in range(n):
    self.phrase(tag+'canon'+str(j),ac[(idx+j)%len(ac)],a+j*beat*.67,b,beat*(1 if sty==6 else [1,1.17,.83,1.5,.67][j]),reg+[-8,0,7,-3,11][j],level-6-j*2,shape=self.contour[j%3:]+self.contour[:j%3],passing=.1)
  elif sty==7:
   self.phrase(tag+'solo',ac[idx%len(ac)] if idx%3 else pal[6],a,b,beat*1.3,reg,level+3,kind='linear',passing=.24,sequence=False,gate=.95)
   if dur>4:self.add(tag+'reply',ac[(idx+4)%len(ac)],a+dur*.79,min(1.9,dur*.2),self.pitch(a+dur*.79,reg-7),37,'single answer')
  elif sty==8:
   for j in range(2+min(3,density//2)):
    self.phrase(tag+'interlock'+str(j),pal[(idx+j*2)%len(pal)],a+j*beat*.36,b,beat*[.61,1.17,.83,1.5,.71][j],reg+[-5,6,0,12,-12][j],level-8-j,shape=self.contour[:4+j%3],passing=.1,gate=.7)
  elif sty==9:
   for repeat,t in enumerate(np.arange(a,b,beat*3.3)):
    c=self.chord(float(t),idx+repeat);self.frame(tag+'voicing'+str(repeat),[ac[(idx+j)%len(ac)] for j in range(4)],float(t),min(b,float(t)+beat*2.9),idx+repeat,32+repeat%3,spacing=.12)
   primary(lead,offset=beat*.8,bpm=.8,v=level-4)
  elif sty==10:
   for j in range(2+min(2,density//3)):
    self.phrase(tag+'quick'+str(j),ac[(idx+j*3)%len(ac)],a+j*beat*.46,b,beat*[.52,.75,1.,1.17][j],reg+[-5,6,0,-12][j],level-5-j*3,passing=.04,gate=.78)
  elif sty==11:
   self.phrase(tag+'song',lead,a,b,beat*2.6,reg,level+1,kind='linear',passing=.15,gate=.97)
   self.phrase(tag+'inner',ac[(idx+2)%len(ac)],a+beat*.6,b,beat*.55,reg-7,level-14,kind='chord',passing=0,gate=.67)
   if density>4:self.phrase(tag+'bass',ac[(idx+5)%len(ac)],a+.3,b,beat*2,55,35,kind='chord',passing=0)
  elif sty==12:
   primary(lead,bpm=.9,kind='chord');self.phrase(tag+'hinge',ac[(idx+2)%len(ac)],a+beat*.4,b,beat*1.15,reg-4,level-10,shape=self.contour[::-1],kind='linear',passing=.12)
  elif sty==13:
   primary(lead,kind='linear',blend=seg%2==0);self.phrase(tag+'answer',ac[(idx+5)%len(ac)],a+dur*.46,b,beat*.81,reg+3,level-11,passing=.05)
  elif sty==14:
   direction=1 if (idx+self.k)%2 else -1
   self.phrase(tag+'arc',lead,a,b,beat*.85,reg,level,shape=list(range(6))[::direction],kind='linear',passing=.18,blend=idx%4==0)
   for j in range(1+min(3,density//2)):self.phrase(tag+'counterarc'+str(j),ac[(idx+j+1)%len(ac)],a+(j+1)*beat*.47,b,beat*[1.3,1.7,.7,1.][j],reg-8+j*4,level-11-j,shape=list(range(5))[::(-direction)],kind='linear',passing=.09)
  elif sty==15:
   self.phrase(tag+'fifths',ac[idx%len(ac)],a,b,beat*1.4,reg-5,level-6,shape=[0,2,0,1,3,2],kind='chord',passing=0)
   self.phrase(tag+'sevenths',pal[6] if idx%3==1 else ac[(idx+3)%len(ac)],a+beat*.7,b,beat*.9,reg+4,level-9,shape=[3,1,2,0,2],kind='chord',passing=0)
  elif sty==17:
   c=self.chord(a,idx)
   for j,p in enumerate(c[:3]):self.add(tag+'thread'+str(j),ac[(idx+j)%len(ac)],a+j*.37,min(6.5,b-a-j*.37),p,32+j*2,'long exposed consonant thread')
   if dur>3:self.phrase(tag+'smallvoice',lead,a+dur*.55,b,beat*1.8,reg,level-7,passing=.15,sequence=False)
  # Dense scenes can add a quiet independent part; sparse scenes stay sparse.
  if density>=7 and sty not in [2,5,6,8,10,16]:self.phrase(tag+'extra',ac[(idx+6)%len(ac)],a+.9,b,beat*1.23,reg-12,level-16,kind='chord',passing=0)
 def finish(self):
  # Every harmonic field is audible, even if a rare field falls in a scene breath.
  for j,h in enumerate(self.harmonies):
   if not any(n['fields']==[j] and not n['is_passing'] for n in self.notes):self.frame('field'+str(j),[13,18],h['start']+.1,min(h['end']-.1,h['start']+2.4),j,34)
  # Resolve passing anchors against actual emitted destination notes; remove any
  # truncated phrase connector that did not genuinely reach its structural target.
  keep=[]
  for n in self.notes:
   if n['is_passing']:
    a=n['anchors'];dest=[x for x in self.notes if x['part']==n['part'] and not x['is_passing'] and abs(x['start']-a['to_start'])<1e-5 and abs(x['pitch']-a['to_pitch'])<1e-8]
    if not dest:continue
    fr=next(x for x in self.notes if x['id']==a['from_id'])
    if fr['fields']!=n['fields'] or dest[0]['fields']!=n['fields']:continue
    assert min(fr['pitch'],dest[0]['pitch'])<n['pitch']<max(fr['pitch'],dest[0]['pitch'])
    a['to_id']=dest[0]['id']
   keep.append(n)
  self.notes=sorted(keep,key=lambda n:(n['start'],n['id']))
  # Preserve true melodic identity in the MIDI: one channel/port per part/instrument.
  lanes=collections.defaultdict(list);voices=[]
  for n in self.notes:
   key=(n['part'],n['instrument']);slots=lanes[key];slot=next((j for j,(end,_) in enumerate(slots) if end<=n['start']+1e-6),None)
   if slot is None:slot=len(slots);slots.append((-1,len(voices)));voices.append(dict(part=n['part'],instrument=n['instrument']))
   n['voice']=slots[slot][1];slots[slot]=(n['start']+n['duration'],n['voice'])
  # The final event gets a clear dry stop. No master fade or copied cadence.
  last=self.duration-.32
  self.notes=[n for n in self.notes if n['start']<last]
  for n in self.notes:n['duration']=min(n['duration'],last-n['start'])
  s=dict(number=self.k+1,title=TITLES[self.k],slug=SLUGS[self.k],duration=self.duration,seed=202610181100+self.k,harmonies=self.harmonies,sections=self.scenes,notes=self.notes,voices=voices,sequences=self.sequences,unpitched_speech=[],motif=self.contour,rhythm=self.rhythm,pitch_policy='Original field members. Added notes only brief unaccented passing connections strictly between two same-part structural field pitches in one harmony. No octave folding or sustained retuning.',tremolo_allowed=False)
  (ROOT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2));return s

def compose(k):
 p=Piece(k);plan=DESIGNS[k];weights=[p.r.uniform(.83,1.23) for _ in plan];scale=p.duration/sum(weights);t=0
 for idx,(sty,w) in enumerate(zip(plan,weights)):
  end=t+w*scale
  density=[2,6,3,8,1,5,7,2,4][(idx+k*2)%9]
  if sty in [7,17]:density=min(3,density)
  if sty in [2,6,8,10,16]:density=max(4,density)
  # Each piece has deliberately different tempo proportions and register/dynamic paths.
  tempos=[[66,82,54,98,71],[48,62,88,56,76],[86,112,64,91,73],[72,58,94,68,84],[91,68,108,55,79],[53,76,61,92,68],[104,79,121,64,91],[59,88,67,103,52],[81,111,62,96,72],[65,96,53,84,109]][k]
  tempo=tempos[(idx//2+idx%3)%len(tempos)]
  p.scene(idx,t,end,sty,density,tempo);t=end
 # Ten small, specifically written exits, all at fixed level through their stops.
 cut=p.duration-3.4
 p.notes=[n for n in p.notes if n['start']<cut-.1]
 for n in p.notes:n['duration']=min(n['duration'],cut-n['start'])
 c=p.chord(p.duration-2.8,k);d=p.duration
 if k==0:
  p.add('ending-guitar',10,d-3.,.7,c[1],48,'last guitar question');p.add('ending-guitar',10,d-1.8,1.25,c[-1],43,'question left open')
 elif k==1:
  p.add('ending-piano',13,d-2.9,1.1,c[0],40,'piano releases first');p.add('ending-cello',29,d-2.55,2.1,c[-1],37,'cello remains alone')
 elif k==2:
  for j,inst in enumerate([9,15,29]):p.add('ending-arrival'+str(j),inst,d-1.8+j*.035,1.35-j*.1,c[j%len(c)],36-j,'clocks meet once')
 elif k==3:
  p.add('ending-oboe',27,d-3.,.9,c[1],43,'short choir question');p.add('ending-flute',28,d-1.65,1.2,c[-1],39,'one player answers')
 elif k==4:
  for j,inst in enumerate([14,12,8]):p.add('ending-relay'+str(j),inst,d-3.+j*.84,.72,c[j%len(c)],44-j*3,'relay changes its final color')
 elif k==5:
  p.add('ending-bass',32,d-3.,.6,c[0],39,'bass clears the space');p.add('ending-horn',18,d-2.2,1.9,c[1],46,'unaccompanied last breath')
 elif k==6:
  p.add('ending-clarinet',15,d-3.,1.1,c[-1],45,'counterpoint leaves a fragment');p.add('ending-guitar',10,d-1.3,.85,c[0],40,'low dry reply')
 elif k==7:
  p.add('ending-cell',29,d-3.,2.55,c[0],37,'held pitch exposed');p.add('ending-fm',7,d-2.8,1.25,c[-1],29,'upper color stops first')
 elif k==8:
  p.add('ending-fretless',20,d-3.,1.2,c[0],42,'floor disappears');p.add('ending-clav',9,d-1.1,.44,c[1],47,'a missing continuation')
 else:p.add('ending-piano',13,d-3.,.75,c[-1],43,'unexpected early full stop')
 p.scenes[-1]['ending']='individually written dry exit; no master fade'
 return p.finish()

if __name__=='__main__':
 import sys
 selected=[int(sys.argv[1])-1] if len(sys.argv)>1 else range(10)
 for k in selected:
  s=compose(k);print(k+1,TITLES[k],len(s['notes']),'events;',sum(n['is_passing'] for n in s['notes']),'passing',flush=True)
 index=[dict(number=k+1,title=TITLES[k],slug=SLUGS[k],duration=DURATIONS[k],design=[STYLES[i] for i in DESIGNS[k]]) for k in range(10)]
 (ROOT/'index.json').write_text(json.dumps(index,indent=2))
