"""Four Large Volumes: bounded exceptions, new textures and sixteen composed endings."""
from compose_foundation import Doors,ROOT,PITCHES
from plan import PIECES,VOLUMES
import json,math,collections,random
from pathlib import Path
class Volumes(Doors):
 def __init__(self,k):
  super().__init__(k);self.ending=PIECES[k][3];self.tuning_mode='12-ET' if k==8 else 'glissandi between exact field endpoints' if k==9 else 'exact Calcutta';self.ending_start=self.duration-[16,20,24,22,14,15,20,11,22,22,13,17,18,24,20,12][k]
 def raw(self,t):
  if self.k==8:return [p for p in range(48,97) if p%12 in [0,2,4,5,7,9,11]]
  return super().raw(t)
 def chord(self,t,rank=0):
  if self.k==8:
   step=int(t/(self.duration/48))%8;root=[60,57,62,67,65,62,67,60][step];degrees=[0,3,7] if step in [1,2,5] else [0,4,7]
   if step in [3,6]:degrees+=[10]
   return [p+12*(rank%2) for p in [root+d for d in degrees] if p+12*(rank%2)<=96]
  return super().chord(t,rank)
 def mode(self,i):
  plans=[
   ['dialogue','chorale','relay','slow_outer','invention','hocket'],
   ['clocks','rivers','chamber','fan','ribbons','subtraction','dialogue'],
   ['chaconne','invention','chaconne','chorale','concertino','chaconne','stair'],
   ['ribbons','hocket','relay','chamber','stair','subtraction'],
   ['sing','dialogue','sing','slow_outer','chorale','sing','hocket'],
   ['echo','keyboard','echo','rivers','chamber','echo','chord_graph'],
   ['trill','trill','slow_outer','trill','invention','trill','chamber'],
   ['vocal_canon','invention','vocal_canon','concertino','slow_outer','vocal_canon'],
   ['chaconne','invention','chorale','concertino','chaconne','keyboard'],
   ['gliss','gliss','still','gliss','slow_outer','gliss','fan'],
   ['chamber','dialogue','hocket','slow_outer','chord_graph','chorale'],
   ['reverse','relay','reverse','still','keyboard','reverse','chamber'],
   ['stair','relay','invention','dialogue','chord_graph','fan','slow_outer'],
   ['rivers','ribbons','slow_outer','fan','relay','subtraction','chaconne','clocks','chamber'],
   ['concertino','invention','concertino','chaconne','chorale','concertino'],
   ['invention','rivers','dialogue','chord_graph','relay','fan','slow_outer','stair','clocks']]
  return plans[self.k][i%len(plans[self.k])]
 def segment(self,i,a,b,mode):
  custom=mode in ['chorale','chaconne','invention','concertino','sing','vocal_canon','trill','gliss','echo','reverse']
  if not custom:return super().segment(i,a,b,mode)
  self.scene_start=self.sec(a);end=min(self.sec(b),self.ending_start);before=len(self.notes);pal=[self.palette[(i*9+j)%len(self.palette)] for j in range(12)];level=40+5*math.sin(i*.71+self.k*.4);reg=65+(i%4)*5
  if mode in ['chaconne','invention','concertino','chorale']:
   families=[[12,32,71,74,51,48,15,70,2,19,33,7],[14,46,68,49,27,59,30,73,5,20,24,41],[8,47,69,50,28,60,31,75,6,21,25,45]];pal=families[(i//2+self.k)%3][:]
  def event(j,t,d,p,v=0,role=mode):return self.emit(f'{i}-p{j}',pal[j%12],t,min(d,b-t),p,level+v,role,end)
  def poolpitch(t,target):return self.pitch(self.sec(t),target)
  def walking(j,period,register,offset=0,reverse=False):
   t=a+offset;k=0;cell=[0,1,3,2,4,3,2,0]
   while t<b-.1:
    pool=self.pool(self.sec(t));idx=min(range(len(pool)),key=lambda q:abs(pool[q]-register));q=cell[::-1][k%8] if reverse else cell[k%8];p=pool[max(0,min(len(pool)-1,idx+q-2+(k//8)%3))];d=period*[1,.5,1,1.5,1,2,.5,1][k%8];event(j,t,d*.93,p,-4+4*math.sin((k%8+.5)*math.pi/8));t+=d;k+=1
  if mode=='chorale':
   t=a;k=0
   while t<b-.1:
    c=self.chord(self.sec(t),i+k//2)
    for j in range(6):
     p=min(c,key=lambda p:abs(p-(51+j*7)));event(j,t+j*.055,min(3.8,b-t-j*.055),p,-8+3*math.sin(k*.8+j*.2))
    t+=4;k+=1
   walking(7,.75,81,.5);walking(8,1.5,62,1,True)
  elif mode=='chaconne':
   t=a;k=0
   while t<b-.1:
    c=self.chord(self.sec(t),i+k//8);p=c[[0,2,1,2,0,1,2,0][k%8]%len(c)];p=poolpitch(t,p-12 if p>62 else p)
    event(0,t,1.85,p,-4,'recurring ground bass');t+=2;k+=1
   for j in range(1,7):walking(j,[.5,.75,1,1.5,2,2/3][j-1],55+j*5,j*.35,j%2==0)
  elif mode=='invention':
   for j in range(8):walking(j,[.75,1,1.5,2/3,1.25,.5,2,2.5][j],52+j*5,j*.5,j%2==1)
  elif mode=='concertino':
   # Clear foreground solo; slower accompaniment in several colors.
   pal[0]=[71,33,12,59,0,74,15][i%7];walking(0,.75 if i%2 else 1.25,78,0)
   for j in range(1,6):
    t=a+j*.2
    while t<b-.1:
     c=self.chord(self.sec(t),i+j);p=min(c,key=lambda p:abs(p-(52+j*6)));event(j,t,2.8+j*.2,p,-12+j*.3,'concertino accompaniment');t+=3+j*.25
   walking(6,1.5,60,2,True)
  elif mode in ['sing','vocal_canon']:
   for j in range(4):
    walking(j,([1.5,2,1,2.5][j] if mode=='sing' else 1.25),59+j*6,j*(.75 if mode=='sing' else 1.5),j%2==1)
   for j in range(4,9):walking(j,[2,.75,1.5,1,2.5][j-4],52+(j-4)*9,j*.15,j%2==0)
   for n in self.notes[before:]:
    j=int(n['part'].split('-p')[1])
    if j<4:n['vocal']={'vowel':['a','o','u','e','i'][(n['id']//3+j)%5],'syllable':['na','lo','mu','ya'][j],'register':j,'air':.025};n['instrument']=97+j;n['velocity']=min(60,n['velocity']+4)
  elif mode=='trill':
   for j in range(7):
    t=a+j*.3;k=0
    while t<b-.1:
     pool=self.pool(self.sec(t));idx=min(range(len(pool)),key=lambda z:abs(pool[z]-(53+j*6)));idx=min(len(pool)-2,max(0,idx));p=pool[idx+k%2];d=[.25,1/3,.5,2/3,.375,.75,.5][j]*(1+.12*math.sin(k*.17));event(j,t,d*.87,p,-5+4*math.sin(k*.4+j),'alternating field-pitch trill');t+=d;k+=1
   for j in (8,9):walking(j,2,60+(j-8)*23,j*.15)
  elif mode=='gliss':
   for j in range(6):
    t=a+j*.4;k=0
    while t<b-.1:
     p=poolpitch(t,52+j*7+3*math.sin(i+k));d=min(3+(j%3)*1.5,b-t);n=event(j,t,d,p,-6,'continuous endpoint slide')
     if n and n['duration']>.3:
      endpoint=poolpitch(t, p+([-7,5,9,-5,4,7][j] if k%2 else [7,-5,-9,5,-4,-7][j]));n['gliss']={'to_pitch':endpoint,'shape':'smoothstep','endpoints_are_field_members':True}
     t+=d+.15;k+=1
   walking(7,1.5,62,.5);walking(8,2.5,86,1)
  elif mode in ['echo','reverse']:
   for j in range(7):walking(j,[.75,1,1.5,2,.5,1.25,2.5][j],52+j*6,j*.35,j%2==1)
   for n in self.notes[before:]:
    j=int(n['part'].split('-p')[1])
    if j in [0,2,4,6]:n['effect']={'type':'multitap' if mode=='echo' else 'reverse_grains','delay':.11+(j%3)*.083,'feedback':.42,'wet':.38,'grain_seconds':.17+(j%3)*.047}
  self.scenes.append(dict(start=round(self.sec(a),6),end=round(end,6),texture=mode,start_beat=a,end_beat=b,ensemble=sorted(set(n['instrument'] for n in self.notes[before:])),section_level=level,form=self.form))
 def endings(self):
  a=self.ending_start;d=self.duration-a;k=self.k;self.scene_start=a;c=self.chord(a,k);raw=self.raw(a);self.notes=[n for n in self.notes if n['start']<a-.03]
  for n in self.notes:n['duration']=min(n['duration'],a-n['start']-.015)
  def n(j,t,dur,p,v=36,inst=None):return self.add('ending-'+str(j),self.palette[(j*7+k)%len(self.palette)] if inst is None else inst,t,dur,p,v,'ending: '+self.ending)
  if k==0:
   for j in range(5):n(j,a+j*.7,1.5,c[j%len(c)],39-j)
   root=c[0];fifth=min(raw,key=lambda p:abs(p-root-7.01955));n(6,a+7,d-7.4,root,32,71);n(7,a+7.13,d-7.53,fifth,30,12)
  elif k==1:
   for j in range(6):
    t=a+j*.17
    while t<a+d*(.35+j*.08):n(j,t,.7,self.pitch(t,53+j*6),33+j%3);t+=1.4+j*.13
   n(8,self.duration-4,.6,c[-1],31,19);n(9,self.duration-1.6,.8,c[0],29,32)
  elif k==2:
   ground=[0,2,1,2,0,1,2,0]
   for j,degree in enumerate(ground):
    t=a+j*2.4;cc=self.chord(t,0);p=self.pitch(t,cc[degree%len(cc)]-12);n(0,t,2.2,p,35,12)
   for j in range(5):
    t=a+j*3.1;n(1,t,3.8,self.pitch(t,75+[0,2,5,3,7][j]),33,71)
   n(1,self.duration-7.2,6.8,self.pitch(a,88),32,71)
   n(0,self.duration-1.1,.7,c[0],35,12)
  elif k==3:
   for j in range(9):
    t=a+j*.12;stop=self.duration-2-j*1.8
    while t<stop:n(j,t,min(1.1,stop-t),self.pitch(t,53+j*5),34);t+=1.6+j*.07
   n(12,self.duration-1.3,.5,c[0],34,51)
  elif k==4:
   for j in range(4):
    z=n(j,a+j*.21,d-j*.21-.35,self.pitch(a,60+j*6),36-j,97+j)
    if z:z['vocal']={'vowel':'o','syllable':'mu','register':j,'air':.018,'close_to_hum':True}
  elif k==5:
   for j in range(4):
    z=n(j,a+j*.3,d-j*.3-.2,c[j%len(c)],39-j,12 if j%2 else 33)
    if z:z['effect']={'type':'multitap','delay':.53+j*.07,'feedback':.56,'wet':.72,'excitation_seconds':1.1+j*.25}
  elif k==6:
   p=min(raw,key=lambda p:abs(p-74));pool=self.pool(a);ix=min(range(len(pool)-1),key=lambda j:abs(pool[j]-p));t=a;step=.11;q=0
   for j in range(4):n(10+j,a,.65+d*.45,c[j%len(c)],27,71+j)
   while t<self.duration-4:
    n(0,t,min(step*.86,self.duration-4-t),pool[ix+q%2],37+3*math.sin(q*.4),15);t+=step;step*=1.065;q+=1
   n(0,self.duration-3.7,3.3,pool[ix],35,15)
  elif k==7:
   for j in range(4):
    t=a+j*.65
    while t<self.duration-.2:
     z=n(j,t,min(1.6,self.duration-.04-t),self.pitch(t,61+j*5+(int(t)%3)*2),39,97+j)
     if z:z['vocal']={'vowel':['a','e','o','i'][j],'syllable':'la','register':j,'air':.02}
     t+=1.9
   z=n(5,self.duration-.75,.70,self.pitch(self.duration-.75,79),43,98)
   if z:z['vocal']={'vowel':'a','syllable':'na','register':1,'air':.02,'interrupted':True}
  elif k==8:
   # Explicit G7 -> C major; every written pitch is an integer MIDI note.
   for step,(cc,span) in enumerate([([55,59,62,65],5),([60,64,67],4),([55,59,62,65],5),([48,60,64,67,72],7)]):
    t=a+[0,5,9,14][step]
    for j,p in enumerate(cc):n(step*10+j,t+j*.035,span-.15-j*.035,p,37-j*.5,8 if j%2 else 48)
  elif k==9:
   target=min(raw,key=lambda p:abs(p-72))
   for j in range(7):
    p=min(raw,key=lambda p:abs(p-(target+(j-3)*4)));z=n(j,a+j*.2,d-j*.2-.45,p,34, [46,48,71,74,0,33,12][j])
    if z:z['gliss']={'to_pitch':target,'shape':'smoothstep','arrive_fraction':.72,'endpoints_are_field_members':True}
  elif k==10:
   for j in range(5):n(j,a+j*.8,1.3,self.pitch(a,58+j*7),36-j, [71,12,74,19,32][j])
   n(8,a+7,.65,c[-1],39,74)
   # Four seconds of unanswered silence are intentional, not a fade.
  elif k==11:
   for j in range(5):
    z=n(j,a+j*.2,5.5,c[j%len(c)],34,[0,12,71,33,19][j]);
    if z:z['effect']={'type':'reverse_grains','grain_seconds':.24+j*.03,'wet':.55,'delay':.19,'feedback':.2}
   z=n(9,self.duration-5.2,4.8,c[0],35,7)
   if z:z['effect']={'type':'reverse_grains','grain_seconds':4.8,'wet':1.,'delay':.17,'feedback':.2,'reverse_envelope':True}
  elif k==12:
   first=self.notes[:12]
   for j,z in enumerate(first):n(j,a+j*.7,min(2.8,self.duration-(a+j*.7)-.2),self.pitch(a+j*.7,z['pitch']),z['velocity']-3,self.palette[-1-j%len(self.palette)])
   n(20,self.duration-3.8,3.4,self.pitch(a,first[0]['pitch']),35,self.palette[-1])
  elif k==13:
   t=a;interval=.6;j=0
   while t<self.duration-4.5:n(j%4,t,min(3.8,self.duration-.3-t),c[j%len(c)],36, [12,71,19,33][j%4]);t+=interval;interval*=1.28;j+=1
  elif k==14:
   for j in range(8):n(0,a+j*.65,.56,self.pitch(a,72+[0,2,4,1,5,3,2,0][j]),43-j*.5,71)
   for j,p in enumerate(c):n(10+j,a+9+j*.18,d-9-j*.18-.4,p,32-j,[12,48,19,33][j%4])
  elif k==15:
   # Event-level retrograde, with original timbres and pitches; no audio DSP.
   cell=[(0.,.65,60,12),(1.,.4,78,71),(1.6,.8,67,33),(2.8,.5,84,6),(3.5,1.,72,19)]
   for j,(off,length,target,inst) in enumerate(cell):n(j,a+off,length,self.pitch(a,target),37-j,inst)
   pivot=a+6.3
   for j,(off,length,target,inst) in enumerate(reversed(cell)):
    reverse_onset=4.5-off-length;n(10+j,pivot+reverse_onset,length,self.pitch(a,target),37-(4-j),inst)
  self.scenes.append(dict(start=a,end=self.duration,texture='ending: '+self.ending,start_beat=self.bt(a),end_beat=self.nbeats,ensemble=sorted(set(n['instrument'] for n in self.notes if n['start']>=a)),section_level=36,form='composed ending'))
 def complete(self):
  a=0.;i=0;limit=self.bt(self.ending_start)
  while a<limit-.1:
   bars=[3,5,4,2,6,3,4][(i+self.k)%7];b=min(limit,a+bars*4)
   while self.sec(b)-self.sec(a)>24:b-=4
   self.segment(i,a,b,self.mode(i));a=b;i+=1
  self.endings()
  for hidx,h in enumerate(self.harmonies):
   if not any(n['fields']==[hidx] for n in self.notes):self.add('field-lens',self.palette[hidx%len(self.palette)],h['start']+.04,min(1,h['end']-h['start']-.08),self.raw(h['start']+.04)[hidx%len(self.raw(h['start']+.04))],29,'brief field lens')
  self.notes=[n for n in self.notes if n['duration']>.03];self.notes.sort(key=lambda n:(n['start'],n['id']));slots=collections.defaultdict(list);voices=[]
  for n in self.notes:
   key=(n['part'],n['instrument']);own=slots[key];slot=next((j for j,(e,v) in enumerate(own) if e<=n['start']+1e-6),None)
   if slot is None:slot=len(own);own.append((-1,len(voices)));voices.append(dict(part=n['part'],instrument=n['instrument']))
   n['voice']=own[slot][1];own[slot]=(n['start']+n['duration'],n['voice'])
  s=dict(number=self.k+1,volume=self.k//4+1,title=self.title,slug=self.slug,duration=self.duration,description=self.description,seed=self.seed,harmonies=self.harmonies,areas=self.areas,notes=self.notes,voices=voices,sections=self.scenes,sequences=self.sequences,cue_network=self.cues,metric_grid=self.beats.tolist(),final_chord_start=self.final_start,final_chord_fraction=.4,instrument_pool=sorted(set(n['instrument'] for n in self.notes)),tuning_mode=self.tuning_mode,ending=self.ending,ending_start=self.ending_start,vocal_allowed=self.k in [4,7],effects_allowed=self.k in [5,11],gliss_allowed=self.k==9,pitch_policy='Exact original fields except movement 9 (12-ET) and movement 10 (continuous glissandi).')
  (ROOT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2));return s
if __name__=='__main__':
 index=[]
 for k in range(16):
  s=Volumes(k).complete();index.append({x:s[x] for x in ['number','volume','title','slug','duration','description','tuning_mode','ending','ending_start']});print(k+1,s['title'],s['duration'],len(s['notes']),'notes',flush=True)
 (ROOT/'index.json').write_text(json.dumps(index,indent=2))
