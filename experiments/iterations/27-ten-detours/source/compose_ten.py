"""Ten genuinely different deterministic designs for the original Calcutta fields."""
from pathlib import Path
import json,math,random,bisect,collections
import numpy as np
OUT=Path('suite');OUT.mkdir(exist_ok=True)
PITCHES=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
TITLES=['The Wrong Intermezzo','Crossing on the Stairs','Pocket Gongs, Plugged In','The Counting Choir','One Room, Twenty Doors','Brother Jacques at the Wrong Funeral','Butterfly Relays','Five People, One Cable','Take Your Cables Home','Jo, Ha, Trapdoor']
DURATIONS=[286,312,268,334,302,288,316,294,340,310]
PREMISES=[
 'A lyrical ABACBA serenade is repeatedly interrupted by a different, dry electronic personality; a structural paraphrase of Bartók’s Interrupted Intermezzo, not a melodic transcription.',
 'Opposing continuous acceleration/deceleration canons, inspired by the crossing speeds of Nancarrow’s Study 21; shaped sentences and new instrumental speakers preserve a perceptible process.',
 'Nested gong-like cycles, split wind melodies, and unequal dance groups meet DI guitars and resonant leads; structural borrowings, not a claim to perform any one tradition authentically.',
 'An original synthetic speaking voice counts Fibonacci numbers and comments on the tuning; a fixed-pitch formant vocoder turns its syllables into a strange dry choir.',
 'Twenty short doors: a promenade-like returning figure connects different borrowed formal devices, places and composerly habits; only public-domain tunes are actually quoted.',
 'Frère Jacques, Dies irae and a tiny familiar cadential joke are re-pitched into the actual fields, passed between acoustic instruments and analog/FM leads, then contradicted.',
 'The only tremolo piece: soft continuous tremolo, deep square audio gates, and many independently pulsing sustained layers. No other piece uses periodic amplitude gates.',
 'A close, conversational five-player ensemble with tiny shared timing inflections, DI guitar, Rhodes and a modular voice; selected instrument bodies exchange their spectral color without room reverb.',
 'A reverse accumulation: players stop, exchange their last phrases, and leave. The ending borrows the departure mechanism of Haydn’s Farewell, without a volume fade.',
 'Free introductions, drawn-out melody, asymmetric pulse and a fast exit: an original jo–ha–kyū-inspired trajectory, with early previews, counterpoint, brief detours, and no borrowed gagaku melody.'
]

class Piece:
 def __init__(self,k):
  self.k=k;self.r=random.Random(2026101800+k);self.dur=DURATIONS[k];self.notes=[];self.speech=[];self.sections=[]
  order=[1,2,3,0,2,4,3]+list(range(5,40))+[38,39]
  # Preserve neighboring areas, but vary routes between pieces.
  for i in range(8,len(order)-4,4):
   if (i+k)%3==0:order[i:i+3]=reversed(order[i:i+3])
  self.fields=[];width=self.dur/len(order)
  for i,ch in enumerate(order):self.fields.append(dict(chord=ch,start=i*width,end=(i+1)*width))
  self.starts=[h['start'] for h in self.fields]
 def hi(self,t):return min(len(self.fields)-1,max(0,bisect.bisect_right(self.starts,t)-1))
 def pool(self,t):
  p=[]
  for x in sorted(PITCHES[self.fields[self.hi(t)]['chord']]):
   if not p or x-p[-1]>=.9:p.append(x)
  return p
 def chord(self,t,index=0):
  pool=self.pool(t);raw=sorted(set(PITCHES[self.fields[self.hi(t)]['chord']]))
  cs=[]
  for r in pool:
   third=min(raw,key=lambda x:abs(x-r-4.33832));fifth=min(raw,key=lambda x:abs(x-r-7.01955))
   if abs(third-r-4.33832)<.65 and abs(fifth-r-7.01955)<.45:
    c=[r,third,fifth];ss=[x for x in raw if x>fifth and min(abs(x-r-9.68826),abs(x-r-11.08))<.6]
    if ss:c.append(min(ss,key=lambda x:min(abs(x-r-9.68826),abs(x-r-11.08))))
    cs.append(c)
  if not cs:return [pool[0],pool[min(2,len(pool)-1)]]
  return cs[index%len(cs)]
 def add(self,inst,t,d,p=None,v=53,role='line',degree=None,register=0,common=False,dsp=None,word=None):
  if t<0 or t>=self.dur:return
  hi=self.hi(t);h=self.fields[hi];pool=self.pool(t)
  if p is None:p=pool[max(0,min(len(pool)-1,(degree or 0)+register))]
  # A staggered/jittered new attack may fall just after a boundary.
  # Choose its nearest actual new-field pitch before it sounds; never retune a hold.
  raw=PITCHES[h['chord']]
  if min(abs(p-x) for x in raw)>1e-9:p=min(raw,key=lambda x:abs(x-p))
  stop=min(t+d,self.dur-.045)
  if not common:stop=min(stop,h['end']-.035)
  if stop-t<.09:return
  spans=[j for j,f in enumerate(self.fields) if f['start']<stop-1e-8 and f['end']>t+1e-8]
  assert all(min(abs(p-x) for x in PITCHES[self.fields[j]['chord']])<1e-9 for j in spans)
  n=dict(instrument=inst,start=round(t,5),duration=round(stop-t,5),pitch=float(p),velocity=max(20,min(72,round(v))),role=role,fields=spans,attack=.006 if inst not in [15,16,17,18,19] else .009)
  if dsp:n['dsp']=dsp
  if word is not None:n['word']=word
  self.notes.append(n)
 def line(self,inst,start,end,shape,iois,register=2,v=55,role='phrase',transpose=0,gate=.8,jitter=0,dsp=None):
  t=start;rep=0;lastpitch=None
  while t<end-.12:
   for j,degree in enumerate(shape):
    if t>=end-.12:break
    ioi=iois[j%len(iois)];pool=self.pool(t);index=max(0,min(len(pool)-1,register+degree+rep*transpose));p=pool[index]
    # Avoid rapid near-unison runs outside deliberate familiar quotations.
    if p==lastpitch and ioi<.32 and len(pool)>2:p=pool[(index+1)%len(pool)]
    self.add(inst,t+self.r.uniform(-jitter,jitter),min(ioi*gate,end-t),p,v=v+6*math.sin(math.pi*(j+1)/(len(shape)+1))+self.r.uniform(-3,3),role=role,dsp=dsp)
    lastpitch=p;t+=ioi
   t+=max(.18,sum(iois)*.13);rep+=1
 def frame(self,insts,t,d,index=0,v=34,role='consonant frame'):
  c=self.chord(t,index)
  for j,p in enumerate(c):self.add(insts[j%len(insts)],t+j*.045,d-j*.045,p,v=v-j,role=role)
 def scene(self,t,end,label):self.sections.append(dict(start=round(t,4),end=round(end,4),name=label))
 def finish(self):
  self.notes.sort(key=lambda x:(x['start'],x['instrument']))
  # Allocate independent monophonic MIDI voices without changing timing.
  lanes=collections.defaultdict(list);voices=[]
  for n in self.notes:
   slots=lanes[n['instrument']];slot=next((j for j,x in enumerate(slots) if x[0]<=n['start']-.003),None)
   if slot is None:slot=len(slots);slots.append([-1,len(voices)]);voices.append(dict(instrument=n['instrument'],lane=slot))
   n['voice']=slots[slot][1];slots[slot][0]=n['start']+n['duration']
  assert self.notes and len(set(h['chord'] for h in self.fields))==40
  assert self.k==6 or all('tremolo' not in str(n.get('dsp','')) for n in self.notes)
  s=dict(title=TITLES[self.k],number=self.k+1,seed=2026101800+self.k,duration=self.dur,premise=PREMISES[self.k],notes=self.notes,unpitched_speech=self.speech,harmonies=self.fields,sections=self.sections,voices=voices,pitch_policy='Exact original-field pitches only; all octave/register changes choose another existing pitch. Fixed common-tone bridges are allowed; no note is retuned while held.',tremolo_allowed=self.k==6)
  (OUT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2,default=lambda x:x.item()));return s

# 1. Bartók-like ABACBA form, with timbral changes within every returning region.
p=Piece(0);letters='ABACBA';cuts=np.array([0,44,98,142,180,232,286])
for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
 for m,t in enumerate(np.arange(a,b,11.)):
  end=min(b,t+11);kind=letters[j];p.scene(t,end,kind+' — '+['lyrical wood','wired reply','new register'][m%3])
  if kind=='A':
   inst=[18,10,5][m%3];p.line(inst,t+.1,end,[0,1,3,2],[.8,1.3,.6,1.7],register=3,v=58,role='returning serenade',transpose=1)
   p.line(12,t+.6,end,[0,2,1],[1.1,2.2,1.6],v=41,role='nylon accompaniment')
  elif kind=='B':
   p.frame([3,15,8],t+.12,min(4,end-t-.3),index=m,v=38);p.line(6,t+1,end,[0,2,1,3],[1.4,.7,.9,2],v=57,role='noble FM song')
  else:
   p.line(1,t+.08,end,[2,0,3,1],[.19,.36,.22,.81],v=55,role='quiet grotesque interruption',transpose=1);p.line(9,t+.7,end,[1,0,2],[.31,.62,1.24],v=45,role='Clavinet heckles')
p.finish()

# 2. Canon X with genuinely crossing local speed curves, not a uniform pulse.
p=Piece(1)
for t in np.arange(0,p.dur,12):p.scene(t,min(p.dur,t+12),'crossing clocks / new speakers '+str(int(t/12)%4+1))
for which in [0,1]:
 t=.1+which*.45;k=0
 while t<p.dur-.5:
  x=t/p.dur;period=(1.55*(.15/1.55)**x) if which==0 else (.15*(1.55/.15)**x)
  period*= [1,.5,1.5,.75,2][k%5]
  inst=([13,0,9,2] if which==0 else [10,7,15,1])[int(t/12)%4]
  p.add(inst,t,min(period*.82,3.8),degree=[0,2,1,3,4,2,5][k%7],register=2+which*3,v=55+3*math.sin(k),role='accelerating canon' if which==0 else 'decelerating canon')
  t+=period+(.42 if k%7==6 else 0);k+=1
for t in np.arange(4,p.dur,17):p.frame([20,18],t,2.8,index=int(t/17),v=30)
p.finish()

# 3. Nested punctuation / split wind melodies / unequal dance groups.
p=Piece(2)
for j,t in enumerate(np.arange(0,p.dur,10.5)):
 end=min(p.dur,t+10.5);kind=j%4;p.scene(t,end,['nested metal cycles','split panpipe melody','2+2+3 electric dance','gong punctuation / slower answers'][kind])
 if kind==0:
  for layer,(inst,period) in enumerate([(21,.66),(22,1.32),(23,2.64),(7,.44)]):p.line(inst,t+layer*.19,end,[0,2,1],[period,period*.5,period*1.5],register=layer+1,v=49-layer*3,role='nested cycle',transpose=1)
 elif kind==1:
  cursor=t+.1
  for k in range(30):
   if cursor>end-.2:break
   p.add([19,16,2,10][k%4],cursor,.31,degree=(k//2)%7,register=2,v=54,role='shared wind / synth melody');cursor+= [.36,.24,.48][k%3]
 elif kind==2:
  p.line(4,t+.1,end,[0,1,3,2,4],[.36,.36,.54,.36,.36],register=3,v=57,role='asymmetric dance lead');p.line(11,t+.2,end,[0,2,1],[.72,.72,1.08],v=44,role='DI steel-string grouping')
 else:
  p.frame([23,17,25],t+.1,4,index=j,v=34);p.line(0,t+1.1,end,[2,1,0],[1.8,2.7,1.3],register=3,v=53,role='slow modular phrase')
p.finish()

# 4. An unexpected counting choir. Speech is original synthetic voice, not sampled people.
p=Piece(3)
for j,t in enumerate(np.arange(0,p.dur,11.5)):
 end=min(p.dur,t+11.5);kind=j%5;p.scene(t,end,['numbers become song','three speaking choirs','the tuning comments','one long vowel / short instruments','voice becomes bass'][kind])
 if j in [0,5,13,21]:p.speech.append(dict(start=float(t+.05),word=[6,7,8,9][[0,5,13,21].index(j)],gain=.07))
 cursor=t+.7;k=0
 while cursor<end-.6:
  d=[1.15,1.6,1.3,2.1][(j+k)%4];word=(k+j)%6 if kind<2 else [7,8,9,10,11][(k+j)%5]
  p.add(27,cursor,min(d,end-cursor-.1),degree=[0,2,1,3][k%4],register=0 if kind==4 else 3,v=60,role='fixed-pitch speaking choir',word=word)
  if kind==1:p.add(27,cursor+.38,d*.78,degree=(k+1)%4,register=5,v=41,role='second counting choir',word=(word+2)%6)
  cursor+=d+.22;k+=1
 p.line([8,14,10,5,24][kind],t+.2,end,[0,1,3,2],[.7,.45,1.4,.9],register=2,v=43,role='instrument answers voice')
 if kind==3:p.add(6,t+.3,4.2,degree=4,register=4,v=43,role='glass behind a vowel')
p.finish()

# 5. Twenty doors: mapped formal devices, connected by a new recurring promenade.
p=Piece(4)
doors=['Pictures / promenade','Goshōraku / slow prelude','Kecak / interlock','Nancarrow / crossing','Bartók / interruption','Goldberg / canon','Boléro / new instrumentation','Ruchenitsa / 2+2+3','Ives / question and silence','Haydn / departing voices','Reich / displaced pattern','Satie / three-beat poise','Schumann / character miniature','Webern / isolated colors','North Indian theme and variation','Andean split winds','Gagaku / unequal bars','Frère Jacques / borrowed round','Dies irae / borrowed chant','New promenade / return changed']
for j in range(20):
 t=j*p.dur/20;end=(j+1)*p.dur/20;p.scene(t,end,doors[j]);kind=j%10
 if j%3==0:p.line(10,t+.08,min(t+3.6,end),[0,2,1,3],[.6,.4,.8,1.1],register=3,v=56,role='returning original promenade')
 if j>=10:
  if j==10:
   pattern=[.28,.28,.56,.28,.56,.84]
   p.line(9,t+.1,end,[0,1,3,2,4,1],pattern,register=3,v=54,role='stationary displaced pattern')
   p.line(1,t+.38,end,[0,1,3,2,4,1],pattern[1:]+pattern[:1],register=4,v=47,role='one subdivision displaced')
  elif j==11:
   cursor=t+.1
   while cursor<end-1:
    p.add(12,cursor,1.1,degree=0,v=45,role='three-beat bass')
    p.frame([8,18],cursor+1.2,1.8,index=j,v=36);cursor+=3.6
   p.line(6,t+.7,end,[0,1,2],[2.1,1.8,3.2],register=4,v=52,role='spare song above three')
  elif j==12:
   p.line(4,t+.1,t+5.5,[0,3,1,4],[.18,.27,.36,.72],register=3,v=55,role='character one')
   p.line(18,t+6.4,end,[2,1,0],[1.5,2.3,1.7],register=2,v=53,role='character two')
  elif j==13:
   for a in range(8):p.add([14,2,17,22,10,6,16,9][a],t+.2+a*1.7,.5+(a%3)*.4,degree=(a*3)%8,register=1,v=44+a%3*3,role='isolated color and silence')
  elif j==14:
   for a in range(3):p.line([9,1,13][a],t+.1+a*4.1,min(end,t+4+a*4.1),[0,2,1,3,1,2],[.3/(1+a*.25),.6/(1+a*.25),.3/(1+a*.25)],register=2+a,v=53,role='theme transformed in density')
  elif j==15:
   cursor=t+.1;a=0
   while cursor<end-.2:
    p.add([19,16][a%2],cursor,.42,degree=[0,1,3,2,4,3][a%6],register=3,v=55,role='two halves of a wind melody');cursor+=[.48,.36,.6][a%3];a+=1
   p.line(5,t+1,end,[0,2,1],[1.9,1.3,2.7],v=42,role='bass response to split winds')
  elif j==16:
   p.line(18,t+.1,end,[0,1,2],[1.4,2.1],register=3,v=53,role='alternating two and three spans')
   p.frame([3,17,25],t+2,3.8,index=j,v=33)
  elif j in [17,18]:
   degrees=[0,2,4,0,0,2,4,0,4,5,7] if j==17 else [5,4,5,2,4,0,2,2]
   cursor=t+.1;a=0
   while cursor<end-.3:
    target=60+degrees[a%len(degrees)];raw=PITCHES[p.fields[p.hi(cursor)]['chord']];note=min(raw,key=lambda x:abs(x-target));d=.58 if j==17 else .85
    p.add([16,6][j-17],cursor,d*.85,note,v=57,role='retuned public-domain allusion');cursor+=d;a+=1
  else:
   p.line(10,t+.1,end,[0,2,1,3],[.6,.4,.8,1.1],register=4,v=56,role='promenade comes home changed',transpose=1)
   p.frame([3,18],t+5,3.4,index=j,v=34)
  continue
 if kind==0:p.line(0,t+1.1,end,[0,2,3,1],[.33,.5,.66,1.2],register=3,v=57,role='colored procession',transpose=1)
 elif kind==1:
  p.add(18,t+.2,4.1,degree=3,register=2,v=51,role='drawn-out prelude');p.frame([3,17],t+3,3,index=j,v=34);p.add(18,t+7,3,p=72.,v=45,role='prelude takes another breath')
 elif kind==2:
  for a in range(3):p.line([9,4,16][a],t+a*.22,end,[0,2,1],[.44,.22,.66],register=2+a,v=51-a*3,role='interlocking voices')
 elif kind==3:
  for a in range(2):p.line([13,1][a],t+a*.31,end,[0,1,3,2],[.25+a*.3,.5+a*.1,.75-a*.2],register=2+a*3,v=53-a*4,role='tempo contrast',transpose=1)
 elif kind==4:
  p.line(18,t+.1,t+6,[0,1,3],[1,1.5,.8],register=3,v=54,role='song before interruption');p.line(5,t+5,end,[3,0,2,1],[.19,.28,.4,.75],v=51,role='interrupting synth')
 elif kind==5:
  for a in range(3):p.line([14,7,15][a],t+.1+a*.65,end,[0,1,3,2],[.4,.6,.8,.6],register=2+a,v=52-a*3,role='degree canon',transpose=1)
 elif kind==6:
  for a,inst in enumerate([16,10,2,8]):p.line(inst,t+a*1.3,end,[0,2,1,3],[.46,.46,.92,.69],register=2+a,v=42+a*2,role='orchestration adds parts')
 elif kind==7:p.line(4,t+.1,end,[0,1,2,4],[.4,.4,.6],register=3,v=57,role='unequal dance phrase');p.line(21,t+.5,end,[0,2,1],[.8,1.4,.6],v=41,role='metal punctuation')
 elif kind==8:
  p.add(25,t+.2,4.5,p=48.,v=28,role='still common-tone ground',common=True);p.line(26,t+.5,end,[0,2,1],[1.5,.7,2.8],register=3,v=53,role='unanswered dry trumpet')
 else:
  for a in range(4):p.line([13,3,10,17][a],t+a*.25,end-a*2,[0,2,1],[.5,.75,1],register=2+a,v=49-a*2,role='players leave the miniature')
p.finish()

# 6. Actual public-domain quotations, retuned to original fields rather than ET.
p=Piece(5)
fj=[0,2,4,0,0,2,4,0,4,5,7,4,5,7,7,9,7,5,4,0,7,9,7,5,4,0,0,-5,0,0,-5,0]
fjr=[.5]*8+[.5,.5,1,.5,.5,1]+[.25,.25,.25,.25,.5,.5]*2+[.5,.5,1,.5,.5,1]
dies=[5,4,5,2,4,0,2,2,5,5,7,5,4,2,0,2]
for j,t in enumerate(np.arange(0,p.dur,12)):
 end=min(p.dur,t+12);theme='Frère Jacques' if j%3!=2 else 'Dies irae';p.scene(t,end,theme+' — altered surroundings')
 shape=fj if theme=='Frère Jacques' else dies;rhythm=fjr if theme=='Frère Jacques' else [.7,.7,.7,.7,.7,.7,1.4,1.4]*2
 cursor=t+.1;k=0
 while cursor<end-.15:
  target=60+shape[k%len(shape)];raw=PITCHES[p.fields[p.hi(cursor)]['chord']];pitch=min(raw,key=lambda x:abs(x-target));ioi=rhythm[k%len(rhythm)]*(1.25 if j%4==1 else .9)
  p.add([16,2,10,6][j%4],cursor,ioi*.83,pitch,v=57,role='retuned public-domain quotation');cursor+=ioi;k+=1
 p.line([8,14,5][j%3],t+.4,end,[0,2,1],[1.1,.7,1.8],v=40,role='new contrapuntal surroundings')
 if j%5==4:p.frame([18,3],t+4,3,index=j,v=32)
p.finish()

# 7. Exclusive tremolo laboratory: hard gates and soft curves, many layers.
p=Piece(6)
for j,t in enumerate(np.arange(0,p.dur,9.8)):
 end=min(p.dur,t+9.8);mode=j%4;p.scene(t,end,['soft tremolo garden','independent square gates','hard / soft interwoven','tremolo thins to one'][mode]);layers=[5,8,12,2][mode]
 for k in range(layers):
  inst=[0,3,5,7,15,17,25,10,22,18,4,19][k];st=t+.1+k*.09
  rate=[1.3,2.1,3.7,5.2,6.8,8.6,10.1,12.4][(k+j)%8]
  hard=mode==1 or (mode==2 and k%2==0)
  dsp=dict(type='tremolo_hard' if hard else 'tremolo_soft',rate=rate,depth=1. if hard else .45+.4*((k%3)/2),phase=k*.71,duty=.3+(k%4)*.12)
  for q,offset in enumerate([0,3.5,7.]):
   if st+offset<end-.3:p.add(inst,st+offset,min(3.1,end-st-offset-.1),degree=(k+q)%8,register=k%3,v=42 if layers>6 else 51,role='independent amplitude layer',dsp=dsp)
 p.add(20,t+.2,2.4,degree=0,v=36,role='ungated bass landmark')
p.finish()

# 8. A small living ensemble, wired directly. Shared rhetorical timing,
# unshared sentences, and instrument-body filtering, but no artificial room.
p=Piece(7)
for j,t in enumerate(np.arange(0,p.dur,10.5)):
 end=min(p.dur,t+10.5);p.scene(t,end,['guitar leads / breathy answers','flute leans ahead','Rhodes in the pocket','modular takes the chair','five players trade one phrase'][j%5])
 leader=[10,15,8,0,18][j%5];shape=[0,2,1,3,2] if j%2 else [1,0,2,4,3]
 p.line(leader,t+.08,end,shape,[.53,.34,.92,.71,1.45],register=3,v=59,role='close lead',transpose=1,jitter=.025,dsp=dict(type='body',formants=[530,1230,2700]) if j%4==0 else None)
 p.line(20,t+.15,end,[0,1,0,2],[1.4,.9,1.8,1.1],register=0,v=42,role='DI bass breathing',jitter=.018)
 p.line([8,10,18,15][j%4],t+.7,end,[2,1,0],[.85,1.4,1.95],register=2,v=42,role='responsive acoustic line',jitter=.025)
 if j%3==1:p.line(1,t+2,end,[0,1,3,2],[.25,.5,.375,.875],register=5,v=45,role='brief modular invention')
p.finish()

# 9. Haydn-like departure mechanism, restarted in small tableaux before final exit.
p=Piece(8);band=[13,18,10,8,0,15,3,14,17,7]
for j,t in enumerate(np.arange(0,p.dur,12)):
 end=min(p.dur,t+12);progress=t/p.dur
 count=2+j%5 if progress<.57 else max(1,10-int((progress-.57)/.43*10))
 p.scene(t,end,'arriving / exchanging seats' if progress<.57 else f'{count} players still in the room')
 for a,inst in enumerate(band[:count]):
  p.line(inst,t+.1+a*.28,end,[0,1,3,2] if a%2==0 else [2,1,0],[.5+a*.12,.75+a*.18,1.1+a*.11],register=1+a%5,v=51-a*2,role='departing ensemble' if progress>.57 else 'passing the phrase',transpose=1)
# No master fade; last unison pair stops at its gate.
p.finish()

# 10. Jo–ha–kyū-inspired temporal trajectory, with previews at the start.
p=Piece(9)
for j,t in enumerate(np.arange(0,p.dur,11)):
 end=min(p.dur,t+11);x=t/p.dur
 stage='previews' if t<33 else 'jo / free breath' if x<.36 else 'ha / unequal movement' if x<.74 else 'kyū / running toward the door';p.scene(t,end,stage)
 if stage=='previews':
  inst=[18,1,10][j%3];p.line(inst,t+.1,end,[0,2,1,3],[1.4,.4,2.1,.7] if j%3==0 else [.2,.3,.6,.9],register=3,v=57,role='three different openings')
 elif 'jo /' in stage:
  p.line(18,t+.1,end,[0,1,3],[2.8,1.7,3.8],register=3,v=55,role='free drawn-out melody',gate=.95)
  p.frame([3,25,17],t+1.2,4,index=j,v=31)
 elif 'ha /' in stage:
  p.line(4,t+.1,end,[0,1,3,2],[.55,.55,.825,.55,.825],register=3,v=57,role='asymmetric pulse appears',transpose=1)
  p.line(14,t+.75,end,[2,0,1],[.8,1.2,.6],v=44,role='harp sees a different meter')
 else:
  scale=.32-.17*(x-.74)/.26
  for a,inst in enumerate([1,9,16]):p.line(inst,t+.1+a*.27,end,[0,1,3,2,4],[scale,scale*1.5,scale*.75,scale*2.5],register=2+a*2,v=55-a*3,role='fast final trajectories',transpose=1)
  p.add(20,t+.2,2.8,degree=0,v=35,role='still root against speed')
p.finish()

index=[]
for k in range(10):
 s=json.loads((OUT/'scores'/f'{k+1:02}.json').read_text());index.append(dict(number=k+1,title=s['title'],duration=s['duration'],premise=s['premise'],seed=s['seed'],notes=len(s['notes']),voices=len(s['voices']),sections=len(s['sections'])))
(OUT/'index.json').write_text(json.dumps(index,indent=2));print(json.dumps(index,indent=2))
