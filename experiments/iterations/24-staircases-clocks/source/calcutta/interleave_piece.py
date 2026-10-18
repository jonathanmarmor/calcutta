"""Softly brighter chord-stack inventions in independent simultaneous tempos."""
from pathlib import Path
import json,random,copy,math
import numpy as np
R=random.Random(2026101757);out=Path('calcutta_interleave');out.mkdir(exist_ok=True)
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
base=json.loads(Path('calcutta_murmur/score.json').read_text());old=json.loads(Path('calcutta_motifs/score.json').read_text())['voices'];syn=json.loads(Path('palette_murmur/synths.json').read_text())
def oldsound(i):
 v=copy.deepcopy(old[i]);s=v['sound']
 if s['engine']!='FluidSynth' and 'state_path' not in s:s['state_path']=f"composition_32_voices_v3/patches/{v['patch_index']+1:02}_{s['engine'].replace(' ','_')}.vststate"
 return s
def gm(n,p):return dict(engine='FluidSynth',name=n,program=p,parameters={},family='sampled acoustic/electric')
recipes=[('Reed amber',[(oldsound(10),1),(syn[0],.5)]),('Guitar wool',[(oldsound(31),1),(syn[4],.38)]),('Rhodes glass',[(oldsound(11),1),(oldsound(22),.25)]),('Clavinet linen',[(gm('Clavinet',7),1),(syn[3],.38)]),('Harp copper',[(oldsound(32),1),(syn[5],.32)]),('Bassoon velvet',[(oldsound(8),1),(syn[10],.42)]),('Nylon air',[(oldsound(27),1),(syn[11],.35)]),('Horn satin',[(oldsound(24),1),(syn[1],.4)]),('Recorder cloud',[(oldsound(25),1),(syn[7],.3)]),('Panpipe FM',[(oldsound(9),1),(oldsound(16),.3)]),('Steel reed',[(oldsound(20),.9),(syn[2],.32)]),('Fretless thread',[(oldsound(47),1),(syn[8],.36)])]
for name,i in [('Solo clean guitar',31),('Solo Rhodes',11),('Solo flute',29),('Solo English horn',12),('Solo harp',32),('Solo piano',26)]:recipes.append((name,[(oldsound(i),1)]))
recipes += [('Solo Clavinet',[(gm('Clavinet',7),1)]),('Solo analog',[(syn[9],1)])]
voices=[];parts=[]
for j,(name,layers) in enumerate(recipes):
 ids=[]
 for sound,gain in layers:ids.append(len(voices));voices.append(dict(sound=sound,blend_gain=gain,pan=-.7+1.4*j/(len(recipes)-1),composite=j,reference_calibration=True))
 parts.append(ids)
notes=[];form=[];hs=[];sequences=[];chord_catalog={};last=[-1]*len(parts);seen=set();t=0
orders=[[1,2,1,3],[4,3,5],[6,7,8],[9,10,9,11],[12,13,14],[15,16,17],[18,19,20],[21,22,23],[24,25,26],[27,28,29],[30,31,32,33],[34,35,36],[37,38,39,0,39]]
names=['A guitar opens the door','Reeds at two speeds','The chord staircase','Clavinet in the windows','Rhodes and a turning ladder','Three clocks share a room','Fifths under a flute','Nylon counterweights','A bright seventh, held','Staircase in reverse','The clocks converge, almost','Horn over moving glass','One step missing']
lengths=[39,36,39,39,36,39,36,39,39,36,42,39,41]
def emit(part,st,dur,p,v,hi,role,attack=.012,passing=False):
 st=max(st,last[part]+.045);en=min(st+dur,hs[hi]['end']/1000-.065)
 if en-st<.3:return
 last[part]=en
 for voice in parts[part]:notes.append(dict(voice=voice,start_tick=round(st*1000),duration_ticks=round((en-st)*1000),pitch=float(p),velocity=round(v),is_passing=passing,harmony_spans=[hi],role=role,attack_seconds=attack))
def chordscan(ch):
 pool=[]
 for p in sorted(pitches[ch]):
  if not pool or p-pool[-1]>.005:pool.append(p)
 chords=[]
 for root in pool:
  fifth=min(pool,key=lambda x:abs(x-root-7.01955));third=min(pool,key=lambda x:abs(x-root-4.33832))
  if abs(fifth-root-7.01955)<.45 and abs(third-root-4.33832)<.65:
   chord=[root,third,fifth];opts=[p for p in pool if p>fifth and min(abs(p-root-9.68826),abs(p-root-11.08))<.55]
   if opts:chord.append(min(opts,key=lambda x:min(abs(x-root-9.68826),abs(x-root-11.08))))
   chords.append(chord)
 if not chords:
  pairs=[(abs(b-a-7.01955),[a,b]) for a in pool for b in pool if b>a]
  chords=[min(pairs)[1]]
 return pool,chords
for si,(name,order,duration) in enumerate(zip(names,orders,lengths)):
 start=t;form.append(dict(section=si+1,name=name,start_seconds=t,end_seconds=t+duration,nominal_bpm=[64,64],strategies=['independent clocks','chord-stack sequences','solo and unison blends']))
 weights=[1]*len(order)
 if si==12:weights=[1,1,1,.45,.8]
 times=np.array(weights)/sum(weights)*duration
 lead=[12,15,16,18,13,19,14,6,13,12,18,15,18][si]
 pattern=R.choice([[0,1,2,1,3],[2,1,0,1],[0,2,1,2,0],[1,0,2,3,2]])
 for oi,(ch,span) in enumerate(zip(order,times)):
  hi=len(hs);hs.append(dict(chord=ch,start=round(t*1000),end=round((t+span)*1000)));pool,chords=chordscan(ch);chord_catalog[str(ch)]=chords
  stack=sorted(chords,key=lambda x:x[0],reverse=si in [7,9,11]);sub=pool[::max(1,len(pool)//10)]
  # Full inventories are gentle, individually exposed points, never a tutti hit.
  if ch not in seen:
   seen.add(ch);inds=list(range(32));R.shuffle(inds)
   for k,idx in enumerate(inds):
    part=k%8;step=(span-1.4)/32
    emit(part,t+.12+k*step,min(1.7,step*8-.07),pitches[ch][idx],30+R.randrange(7),hi,'quiet inventory',.014)
  # A clearly audible solo repeats its contour through ascending/descending chords.
  cursor=t+.25;rep=0
  while cursor<t+span-1:
   chord=stack[rep%len(stack)];period=[.73,.91,1.17,.83][si%4]
   shape=pattern[:] if rep%4!=3 else pattern[:-1]+[pattern[-1]+1]
   sequences.append(dict(section=si+1,harmony=ch,part=lead,start_seconds=cursor,repeat=rep,chord=chord,period=period,contour=shape))
   for k,degree in enumerate(shape):
    p=chord[degree%len(chord)];hold=period*(1.65 if k==len(shape)-1 else .82)
    emit(lead,cursor,hold,p,56+9*math.sin((k+1)*math.pi/(len(shape)+1)),hi,'exposed chord-stack sequence',.008)
    cursor+=period*(1.9 if k==len(shape)-1 else 1)
   cursor+=.55;rep+=1
  # Simultaneous clocks: distinct stable speeds, not conductor rubato.
  for layer,period in enumerate(([1.35,1.01,.77] if si%3 else [1.61,1.18,.89])):
   part=[8,9,10][layer];cursor=t+.6+layer*.43;step=0
   while cursor<t+span-.6:
    chord=stack[(step//3+layer)%len(stack)];p=chord[(step+layer)%len(chord)]
    emit(part,cursor,period*R.choice([.75,1.5,2.2]),p,42+layer*3+R.randrange(8),hi,'simultaneous tempo '+str(round(60/period,2)),.012)
    cursor+=period*(2 if step%5==4 else 1);step+=1
  # A patient fifth or seventh is balanced well below the solo.
  chord=stack[oi%len(stack)]
  for j,p in enumerate(chord[::max(1,len(chord)-1)]):emit(11+j%1,t+1+j*span/2,span*.42,p,39,hi,'sustained consonant frame',.28)
  # late scenes alternate real instrumental solos with the layered timbres.
  if si in [4,6,8,10,11]:
   part=17 if si%2 else 16;cursor=t+span*.3
   for p in chord:emit(part,cursor,1.1,p,53,hi,'exposed acoustic reply',.008);cursor+=1.4
  t+=span
# Ending: remove the last planned cadence, a short breath, then a dry unexpected
# two-note clavinet question. Fixed master level through the cutoff, no fade.
cut=round((t-2.8)*1000);notes=[n for n in notes if n['start_tick']<cut]
for n in notes:n['duration_ticks']=min(n['duration_ticks'],cut-n['start_tick'])
hi=len(hs)-1;last[18]=t-2.8;pool,chords=chordscan(39)
emit(18,t-2.25,.78,chords[0][1],62,hi,'unanswered ending',.006)
emit(18,t-1.05,.86,chords[-1][0],58,hi,'unanswered ending',.006)
# Validate inventory, fixed pitches, monophony and structural field membership.
covered={i:set() for i in range(40)}
for n in notes:
 h=hs[n['harmony_spans'][0]];assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end']
 assert min(abs(n['pitch']-p) for p in pitches[h['chord']])<1e-9
 covered[h['chord']].update(i for i,p in enumerate(pitches[h['chord']]) if abs(n['pitch']-p)<1e-9)
assert all(len(v)==32 for v in covered.values()),{k:len(v) for k,v in covered.items() if len(v)<32}
secs=np.arange(0,t+.125,.125);secs[-1]=t;bpm=64+.7*np.sin(secs/23);beats=np.r_[0,np.cumsum(np.diff(secs)*(bpm[:-1]+bpm[1:])/120)]
s=dict(title='Calcutta: Staircases and Clocks',seed=2026101757,voices=voices,composites=[dict(name=n,components=[dict(name=s['name'],gain=g) for s,g in layers]) for n,layers in recipes],notes=notes,harmonies=hs,form=form,duration_seconds=t,total_ticks=round(t*1000),seconds_per_tick=.001,conductor_grid=dict(seconds=secs.tolist(),beats=beats.tolist()),tempo_map=[dict(beat=float(b),bpm=float(p)) for b,p in zip(beats,bpm)],sequences=sequences,chord_catalog=chord_catalog,coverage={str(k):len(v) for k,v in covered.items()},dynamic_envelope=dict(section_center_db=[-1,0,-1,-2,0,-1,-2,0,-3,-1,0,-2,-1]))
(out/'score.json').write_text(json.dumps(s,indent=2));print(t,len(voices),len(notes))
