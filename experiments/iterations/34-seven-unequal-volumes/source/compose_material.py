from compose_foundation import Doors,ROOT,PITCHES
from plan import PIECES,VOLUMES
import math,json,collections
class Material(Doors):
 def segment(self,i,a,b,mode):
  custom=mode in ['chorale','chaconne','invention','concertino','sing','vocal_canon','trill','gliss','echo','reverse']
  if not custom:return super().segment(i,a,b,mode)
  self.scene_start=self.sec(a);end=min(self.sec(b),self.ending_start);before=len(self.notes);pal=[self.palette[((i*9+j)+(i//12)*5)%len(self.palette)] for j in range(12)];level=40+5*math.sin(i*.71+self.k*.4);reg=65+(i%4)*5
  if mode in ['chaconne','invention','concertino','chorale']:
   families=[[12,32,71,74,51,48,15,70,2,19,33,7],[14,46,68,49,27,59,30,73,5,20,24,41],[8,47,69,50,28,60,31,75,6,21,25,45]];pal=families[(i//2+self.k)%3][:]
  def event(j,t,d,p,v=0,role=mode):return self.emit(f'{i}-p{j}',pal[j%12],t,min(d,b-t),p,level+v,role,end)
  def poolpitch(t,target):return self.pitch(self.sec(t),target)
  def walking(j,period,register,offset=0,reverse=False):
   t=a+offset;k=0;cell=self.theme
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
