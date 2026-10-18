"""Fresh soft sequence composition; seed and all decisions are reproducible."""
import json,random,copy,math
from pathlib import Path
import numpy as np
rng=random.Random(2026101831);root=Path('calcutta_murmur');root.mkdir(exist_ok=True)
old=json.loads(Path('calcutta_motifs/score.json').read_text())['voices']
new=json.loads(Path('palette_murmur/synths.json').read_text())
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
def legacy(i):
 v=copy.deepcopy(old[i]);s=v['sound'];s.setdefault('state_path',str(Path('composition_32_voices_v3/patches')/f"{v['patch_index']+1:02}_{s['engine'].replace(' ','_')}.vststate")) if s['engine']!='FluidSynth' else None
 return s
# Exact unison layers, not detuned oscillator stacks.
recipes=[('Amber cor anglais',[(new[0],1),(legacy(12),.32)]),('Wool and wire',[(new[4],1),(legacy(7),.27)]),('Porcelain breath',[(legacy(22),.85),(legacy(28),.22),(new[1],.4)]),('Satin clarinet',[(new[2],1),(legacy(10),.38)]),('Threaded harp',[(legacy(32),.7),(new[8],.8),(legacy(25),.22)]),('Rubberwood',[(legacy(47),.7),(new[0],.8),(legacy(24),.16)]),('Steel and tine',[(legacy(20),.55),(legacy(5),.55),(new[5],.35)]),('Copper Rhodes',[(legacy(11),.75),(new[5],.5),(legacy(16),.22)]),('Linen flute',[(new[3],.8),(legacy(29),.6)]),('Velvet bassoon',[(new[10],.9),(legacy(8),.45),(legacy(27),.15)]),('Sitar cloud',[(legacy(49),.45),(new[4],.9)]),('Small reed brass',[(new[5],.9),(legacy(12),.3),(legacy(25),.18)]),('Hollow panpipe',[(new[1],1),(legacy(9),.3)]),('Ladder trumpet',[(new[9],.85),(legacy(19),.3)]),('Air organ',[(new[11],.8),(legacy(15),.4)]),('Dark celeste',[(new[7],.9),(legacy(28),.2)])]
voices=[];parts=[]
for j,(name,layers) in enumerate(recipes):
 ids=[]
 for sound,gain in layers:
  ids.append(len(voices));voices.append(dict(sound=sound,pan=-.68+1.36*j/15,blend_gain=gain,reference_calibration=True,composite=j))
 parts.append(ids)
names=['Open windows','Two rooms answering','A stair in soft light','Glass against wool','Returning footsteps','Slow copper current','A narrowing corridor','Harpwork and shadow','Six quiet arguments','A tide of reeds','The sequence forgets one step','Still air','Threads rising apart','A low field opens','What remains']
orders=[[2,1,2,3],[3,4,3,5],[5,6,7],[7,8,7,9],[9,10,11],[12,11,13],[14,15,16],[17,18,17,19],[20,21,22],[23,24,25],[26,27,28],[29,30],[31,32,33],[34,35,36],[37,38,39,0]]
notes=[];harmonies=[];form=[];seen=set();t=0.;last=[-1.]*16

def emit(part,start,dur,pitch,velocity,hi,passing=False,role='sequence',attack=.13):
 start=max(start,last[part]+.055);end=min(start+dur,harmonies[hi]['end']/1000-.09)
 if end-start<.32:return
 last[part]=end
 for v in parts[part]:notes.append(dict(voice=v,start_tick=round(start*1000),duration_ticks=round((end-start)*1000),pitch=float(pitch),velocity=int(velocity),is_passing=passing,harmony_spans=[hi],role=role,attack_seconds=attack))
for si,(name,order) in enumerate(zip(names,orders)):
 begin=t;scene_len=[32,37,34,34,35,34,32,36,34,36,35,36,34,34,40][si];lengths=[scene_len/len(order)]*len(order)
 form.append(dict(section=si+1,name=name,start_seconds=begin,end_seconds=begin+scene_len,nominal_bpm=[rng.randint(48,72),rng.randint(48,72)],strategies=['static veils' if si in [3,8,11] else ['dialogue','ascending sequence','contrary motion','gradual accumulation','contracting register'][si%5]]))
 # Theme is new per scene, recognizable across repeats inside scene.
 shape=rng.choice([[0,1,3,2],[0,2,1,0,1],[0,-1,-2,0],[0,1,0,2,1]])
 rhythm=rng.choice([[.9,.7,1.4,1.8],[1.3,1.0,.8,1.6],[.75,1.1,1.5,1.0,1.7]])
 active=[si%8,(si*3+1)%8,(si*5+3)%8];active=list(dict.fromkeys(active))
 for oi,(ch,dur) in enumerate(zip(order,lengths)):
  hi=len(harmonies);harmonies.append(dict(chord=ch,start=round(t*1000),end=round((t+dur)*1000)))
  raw=sorted(set(pitches[ch]));pool=[]
  for p in raw:
   if not pool or p-pool[-1]>=.9:pool.append(p)
  # quiet complete inventories spread through time; no simultaneous tutti return
  if ch not in seen:
   seen.add(ch);inds=list(range(32));rng.shuffle(inds)
   if si%3==0:inds.sort(key=lambda k:pitches[ch][k],reverse=si%2==0)
   for k,idx in enumerate(inds):
    part=8+k%8;st=t+.12+k*(dur-2.1)/32
    emit(part,st,min(rng.uniform(1.15,2.0),(dur-2.1)/4-.08),pitches[ch][idx],rng.randint(26,37),hi,role='field mosaic',attack=.35)
  # careful sustained dissonances, independently entering/exiting
  if si in [3,8,11,14]:
   for k in range(3):emit((si+k)%8,t+.4+k*.7,dur-1.3-k*.7,raw[(len(raw)//2+k*3)%len(raw)],29+k*3,hi,role='quiet sustained interval',attack=.8)
  else:
   for ai,part in enumerate(active):
    base=(2+ai*3+oi+(si//3))%max(1,len(pool)-5);cursor=t+.25+ai*.85
    repeat=0
    while cursor<t+dur-1:
     # Stable contour and duration pattern; transposition one degree per repeat.
     trans=(repeat%3)*(1 if si%2==0 else -1);prev=None
     for ni,step in enumerate(shape):
      index=max(0,min(len(pool)-1,base+step+trans));p=pool[index]
      d=rhythm[ni%len(rhythm)]*(.88+.1*math.sin(si))
      if prev is not None and 2.0<abs(p-prev)<6 and rng.random()<.38 and d>1:
       # Natural connecting tone, never a compressed grace run.
       passing=(prev+p)/2
       emit(part,cursor,d*.45,passing,42,hi,True,'melodic connection',.1);cursor+=d*.49
       d*=.51
      vel=round(43+10*math.sin(math.pi*(ni+1)/(len(shape)+1))+rng.uniform(-4,4))
      emit(part,cursor,d*.89,p,vel,hi,role='recognizable sequence',attack=.12)
      cursor+=d;prev=p
     cursor+=.7 if repeat<2 else 1.4
     repeat+=1
   # One direction over scene: a gently moving separate sustained line.
   if si in [2,5,6,9,12,13]:
    part=7;idx=round((oi/(len(order)-1))*max(0,len(pool)-1));idx=idx if si%2==0 else len(pool)-1-idx
    emit(part,t+1.2,dur-2,pool[idx],36,hi,role='directional strand',attack=.5)
  t+=dur
# Every event fixed pitch, and all inventories actually present (mosaic scheduling can clip).
covered={ch:set() for ch in range(40)}
for n in notes:
 h=harmonies[n['harmony_spans'][0]]
 assert n['start_tick']>=h['start'] and n['start_tick']+n['duration_ticks']<=h['end']
 if not n['is_passing']:
  assert min(abs(n['pitch']-p) for p in pitches[h['chord']])<1e-9
  covered[h['chord']].update(i for i,p in enumerate(pitches[h['chord']]) if abs(n['pitch']-p)<1e-9)
assert all(len(v)==32 for v in covered.values()),{k:len(v) for k,v in covered.items() if len(v)!=32}
# a slow conductor map with continuous low-amplitude rubato
secs=np.arange(0,t+.125,.125);secs[-1]=t;bpm=59+7*np.sin(secs/37)+2*np.sin(secs/5);beats=np.r_[0,np.cumsum(np.diff(secs)*(bpm[:-1]+bpm[1:])/120)]
s=dict(title='Calcutta: Soft Machines',seed=2026101831,voices=voices,composites=[dict(name=n,components=[dict(name=s['name'],gain=g) for s,g in layers]) for n,layers in recipes],notes=notes,harmonies=harmonies,form=form,duration_seconds=t,total_ticks=round(t*1000),seconds_per_tick=.001,conductor_grid=dict(seconds=secs.tolist(),beats=beats.tolist()),tempo_map=[dict(beat=float(b),bpm=float(p)) for b,p in zip(beats,bpm)],coverage={str(k):len(v) for k,v in covered.items()},dynamic_envelope=dict(section_center_db=[-2,-1,0,-4,-2,0,-3,-1,-4,0,-2,-5,-1,-2,-6]))
(root/'score.json').write_text(json.dumps(s,indent=2));print(t,len(voices),len(notes),'passing components',sum(n['is_passing'] for n in notes))
