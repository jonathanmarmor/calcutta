"""Bright Detours: exposed synth leads; frequent textural turns; shaped independent clocks."""
from pathlib import Path
import copy,json,math,random
import numpy as np
R=random.Random(2026101758);out=Path('calcutta_detours');out.mkdir(exist_ok=True)
lead=json.loads(Path('palette_frontier/synths.json').read_text());old=json.loads(Path('calcutta_motifs/score.json').read_text())['voices'];pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
def oldsound(i):
 v=copy.deepcopy(old[i]);s=v['sound']
 if s['engine']!='FluidSynth' and 'state_path' not in s:s['state_path']=f"composition_32_voices_v3/patches/{v['patch_index']+1:02}_{s['engine'].replace(' ','_')}.vststate"
 return s
def gm(n,p):return dict(engine='FluidSynth',name=n,program=p,family='sampled acoustic/electric',parameters={})
recipes=[(p['name'],[(p,1.)]) for p in lead]
recipes += [(n,[(s,1.)]) for n,s in [('Rhodes',oldsound(11)),('Clavinet',gm('Clavinet',7)),('Clean jazz guitar',oldsound(31)),('Flute',oldsound(29)),('English horn',oldsound(12)),('Harp',oldsound(32)),('Bassoon',oldsound(8)),('Piano',oldsound(26)),('Fretless bass',oldsound(47)),('Steel pans',oldsound(20)),('Pan pipes',oldsound(9)),('Muted trumpet',oldsound(19))]]
recipes += [('Reed-mallet hybrid',[(gm('Marimba',12),.8),(oldsound(16),.32)]),('Nylon-FM hybrid',[(oldsound(27),.9),(oldsound(22),.32)])]
voices=[];parts=[]
for j,(name,layers) in enumerate(recipes):
 ids=[]
 for sound,gain in layers:ids.append(len(voices));voices.append(dict(sound=sound,blend_gain=gain,pan=R.uniform(-.65,.65),composite=j,reference_calibration=True))
 parts.append(ids)
notes=[];hs=[];form=[];last=[-1.]*len(parts);t=0.;seqs=[]
styles=['Angular open saw','Glass slows the room','Resonant burst sequencer','Rhodes / Clavinet dialogue','An Oberheim seventh, suspended','Quick hocket through three colors','Rubber-reed ballad','Seven against five, in phrases','Very slow divided canon','Dry machines, uneven sentences','A field of different walking speeds','Acoustic window, analog reply','Chord staircase accelerates','A still chord with restless edges','A melody changes its instrument','FM / Clavinet quicksilver','Fast foreground falls away','Composite sample invention','Counterpoint adds a floor','A question changes scale']
# Several very different ideas precede any long development.
style_order=[0,1,2,4,3,5,8,6,7,9,11,12,13,10,14,15,4,16,17,18,2,8,0,7,13,11,15,12,6,14,9,1,18,4,16,17,10,5,8,12,7,13,15,19,6,2]
order=[1,2,3,0,3,4,5,4]+list(range(6,31))+[32,31,33,34,35,34,36,37,38,37,39,38,39]
assert len(order)==len(style_order),(len(order),len(style_order))
durations=[8,9,8,7,10,9,12,10,11,9,10,12,13,11,8,9,14,10,11,12,9,13,10,12,14,10,9,12,13,10,8,14,12,13,10,11,12,8,14,11,12,13,9,10,12,10]
assert len(durations)==len(order)
def emit(part,st,dur,p,v,hi,role,attack=.008):
 st=max(st,last[part]+.025);en=min(st+dur,hs[hi]['end']/1000-.045)
 if en-st<.105:return
 last[part]=en
 for voice in parts[part]:notes.append(dict(voice=voice,start_tick=round(st*1000),duration_ticks=round((en-st)*1000),pitch=float(p),velocity=round(v),is_passing=False,harmony_spans=[hi],role=role,attack_seconds=attack))
def scan(ch):
 pool=[]
 for p in sorted(pitches[ch]):
  if not pool or p-pool[-1]>=.9:pool.append(p)
 # Every selected note is an actual original pitch; no octave folding.
 chords=[]
 raw=sorted(set(pitches[ch]))
 for r in pool:
  third=min(raw,key=lambda x:abs(x-r-4.33832));fifth=min(raw,key=lambda x:abs(x-r-7.01955))
  if abs(third-r-4.33832)<.65 and abs(fifth-r-7.01955)<.45:
   chord=[r,third,fifth];opts=[p for p in raw if p>fifth and min(abs(p-r-9.68826),abs(p-r-11.08))<.55]
   if opts:chord.append(min(opts,key=lambda x:min(abs(x-r-9.68826),abs(x-r-11.08))))
   chords.append(chord)
 if not chords:
  pairs=[(abs(b-a-7.01955),[a,b]) for a in pool for b in pool if b>a];chords=[min(pairs)[1]]
 return pool,chords

def phrase(part,st,limit,pool,shape,iois,velocity,hi,role,offset=0,gate=.8,transpose=0):
 cursor=st;rep=0
 while cursor<limit-.15:
  contour=shape[:]
  # Recognizable repetition; every third sentence loses or redirects one syllable.
  if rep%3==2:contour=contour[:-1]+[contour[-1]+1]
  for k,degree in enumerate(contour):
   if cursor>=limit-.12:break
   index=(degree+offset+rep*transpose)%len(pool);p=pool[index];ioi=iois[k%len(iois)]
   v=velocity+7*math.sin(math.pi*(k+1)/(len(contour)+1))+R.uniform(-3,3)
   emit(part,cursor,min(ioi*gate,limit-cursor),p,v,hi,role)
   cursor+=ioi
  cursor+=max(.22,sum(iois)*.18);rep+=1
 seqs.append(dict(part=part,start_seconds=st,end_seconds=min(limit,cursor),role=role,iois_seconds=iois,shape=shape))

for i,(ch,sty,dur) in enumerate(zip(order,style_order,durations)):
 start=t;hi=len(hs);hs.append(dict(chord=ch,start=round(t*1000),end=round((t+dur)*1000)));pool,chords=scan(ch);stack=sorted(chords,key=lambda x:x[0],reverse=i%4==3);c=stack[i%len(stack)];q=lambda x:pool[x%len(pool)]
 form.append(dict(section=i+1,name=styles[sty],start_seconds=t,end_seconds=t+dur,nominal_bpm=[64,64],strategies=[styles[sty]],harmony=ch,texture_type=sty))
 end=t+dur-.12
 if sty==0:
  phrase(0,t+.05,end,pool,[0,2,1,3,2],[.24,.38,.66,.21,1.15],60,hi,'exposed open modular lead',offset=i%4,transpose=1)
  emit(16,t+.2,2.6,pool[0],42,hi,'bass punctuation');emit(10,t+dur*.65,1.3,c[1],48,hi,'single guitar reply')
 elif sty==1:
  phrase(6,t+.1,end,pool,[1,2,4],[2.4,1.7,3.2],58,hi,'slow glass lead',offset=len(pool)//3,gate=.94)
  phrase(15,t+1,end,c,[0,2,1],[2.8,3.1,1.9],40,hi,'spacious piano answers',gate=.63)
 elif sty==2:
  phrase(1,t+.05,end,pool,[0,2,1,3,4,2],[.19,.31,.17,.22,.48,.85],59,hi,'resonant synth burst lead',offset=2,transpose=1)
  emit(16,t+.3,3.4,c[0],43,hi,'slow fretless floor')
  phrase(17,t+2,end,c,[1,0,2],[1.25,.75,1.6],40,hi,'steel counter-sentence')
 elif sty==3:
  phrase(8,t+.1,t+dur*.52,c,[0,1,2,1],[.55,.3,.95,.65],58,hi,'Rhodes question')
  phrase(9,t+dur*.44,end,pool,[2,1,3,2],[.23,.49,.33,.85],57,hi,'Clavinet answer',offset=2)
  emit(3,t+dur*.57,2.4,c[-1],51,hi,'exposed brass interruption')
 elif sty==4:
  for j,p in enumerate(c):emit([3,12,14,19][j%4],t+.1+j*.24,dur-1-j*.24,p,47 if j==0 else 34,hi,'held Oberheim / wind seventh',.008 if j==0 else .05)
  phrase(13,t+dur*.55,end,pool,[2,3,1],[.54,.37,1.45],43,hi,'harp edges')
 elif sty==5 or sty==14:
  cursor=t+.1
  for k in range(round(dur/(.25 if sty==5 else .6))):
   if cursor>end-.12:break
   v=[0,2,9,11,4,13][k%6];ioi=([.18,.24,.31,.21,.46,.75] if sty==5 else [.6,.33,.9,.44,1.4])[k%(6 if sty==5 else 5)]
   emit(v,cursor,ioi*.82,q(k//2+(k%2)*2),55 if v<8 else 48,hi,'fast hocket' if sty==5 else 'melody by timbral relay');cursor+=ioi
  emit(14,t+.5,dur*.7,c[0],31,hi,'bassoon continuous ground')
 elif sty==6:
  phrase(5,t+.12,end,pool,[1,3,2],[1.7,2.1,3.4],61,hi,'slow rubber synth song',offset=len(pool)//3,gate=.96)
  phrase(10,t+.8,end,c,[0,1,2],[1.2,2.3,1.8],43,hi,'guitar behind the phrase',gate=.7)
 elif sty==7:
  phrase(2,t+.1,end,pool,[0,1,3,2,4],[.28,.56,.28,.84,.56],57,hi,'five-part pulse sentence',offset=2,transpose=1)
  phrase(7,t+.6,end,pool,[2,0,1,3],[.4,.6,1.0,.2],49,hi,'seven against five sentence',offset=5,transpose=-1)
  emit(16,t+.2,dur*.7,c[0],37,hi,'bass beneath independent phrases')
 elif sty==8:
  phrase(6,t+.05,end,pool,[1,2,3],[3.6,2.7,4.3],57,hi,'very slow FM canon',offset=2,gate=.95)
  phrase(14,t+2.4,end,pool,[1,2,3],[3.6,2.7,4.3],45,hi,'slow bassoon canon',offset=1,gate=.92)
 elif sty==9:
  phrase(1,t+.08,end,c,[0,2,1,0],[.16,.32,.24,.64],57,hi,'rapid unequal synth cycle')
  phrase(4,t+.53,end,pool,[0,1,3],[.27,.54,.81],49,hi,'independent hollow lead cycle',offset=5,transpose=1)
  emit(12,t+.7,4.1,c[1],36,hi,'unhurried cor anglais')
 elif sty==10:
  for k,part in enumerate([1,2,4,7,8,13]):
   scale=[.38,.51,.67,.89,1.19,1.53][k]
   phrase(part,t+k*.33,end,pool,[0,2,1,3],[scale,scale*1.5,scale*.5,scale*2.25],51-k,hi,'multi-tempo shaped counterpoint',offset=k+1,transpose=1,gate=.72)
 elif sty==11:
  phrase(11,t+.1,end,pool,[2,3,1,2],[.7,.48,1.4,.95],58,hi,'exposed flute invention',offset=3,transpose=1)
  phrase(8,t+.65,end,c,[1,0,2],[.9,1.5,.6],44,hi,'Rhodes counterpoint')
  emit(0,t+dur*.6,2.5,c[-1],52,hi,'open modular answers the flute')
 elif sty==12:
  cursor=t+.12;k=0
  while cursor<end-.2:
   c2=stack[(k//3)%len(stack)];p=c2[k%len(c2)];ioi=.95-.68*min(1,(cursor-t)/dur)
   emit(0,cursor,ioi*.88,p,58+4*math.sin(k),hi,'accelerating chord-stack lead');cursor+=ioi*(1.8 if k%7==6 else 1);k+=1
  phrase(10,t+.5,end,c,[2,1,0],[1.7,2.8,1.2],42,hi,'descending guitar counterweight',gate=.85)
 elif sty==13:
  emit(3,t+.08,dur-.3,c[-1],54,hi,'long exposed Oberheim line');emit(16,t+.7,dur*.8,c[0],34,hi,'held fretless root')
  phrase(9,t+1,end,c,[1,0,2],[.31,.18,1.28],44,hi,'Clavinet loose edge')
 elif sty==15:
  phrase(7,t+.08,end,pool,[0,1,3,2,4],[.23,.35,.47,.23,.94],57,hi,'FM organ rapid lead',offset=2,transpose=1)
  phrase(9,t+.46,end,c,[2,1,0],[.31,.62,.93],48,hi,'Clavinet independent answer')
 elif sty==16:
  phrase(4,t+.05,t+dur*.48,pool,[0,1,2,4,3],[.15,.22,.29,.43,.58],57,hi,'fast hollow lead then empty room',offset=3,transpose=1)
  emit(12,t+dur*.55,dur*.36,c[1],53,hi,'sudden slow cor anglais');emit(6,t+dur*.68,dur*.23,c[-1],47,hi,'slow glass after speed')
  form[-1]['internal_change_seconds']=t+dur*.52
 elif sty==17:
  phrase(20,t+.08,end,pool,[0,2,1,3],[.44,.77,.33,1.43],59,hi,'attack-body composite invention',offset=2,transpose=1)
  phrase(21,t+.85,end,c,[2,0,1],[1.3,.65,2.1],44,hi,'nylon-FM reply')
 elif sty==18:
  for k,part in enumerate([2,0,6,10,18]):phrase(part,t+k*1.55,end,pool,[0,1,3,2],[.45+k*.11,.8+k*.15,.3+k*.09,1.3+k*.23],54-k*2,hi,'gradually adding independent inventions',offset=k+2,transpose=1)
 else:
  phrase(5,t+.08,end,pool,[0,2,1,4],[.72,1.44,.36,2.16],58,hi,'new question in neighboring field',offset=3,transpose=1)
  phrase(19,t+1.5,end,c,[2,1,0],[1.7,1.15,2.2],44,hi,'muted trumpet response')
 t+=dur
# End in mid-expectation: the machine goes away, a single FM tone remains,
# then stops at its written gate. No master fade or recycled Clavinet question.
cut=round((t-1.55)*1000)
notes=[n for n in notes if n['start_tick']<cut]
for n in notes:n['duration_ticks']=min(n['duration_ticks'],cut-n['start_tick'])
hi=len(hs)-1;last[6]=t-1.55;pool,_=scan(39);emit(6,t-1.28,.99,pool[2],52,hi,'unresolved glass ending')
assert set(h['chord'] for h in hs)==set(range(40))
for n in notes:
 h=hs[n['harmony_spans'][0]];assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end'];assert min(abs(n['pitch']-p) for p in pitches[h['chord']])<1e-9
for v in range(len(voices)):
 own=sorted([n for n in notes if n['voice']==v],key=lambda n:n['start_tick']);assert own and all(x['start_tick']+x['duration_ticks']<y['start_tick'] for x,y in zip(own,own[1:]))
assert max(durations)<=30
secs=np.arange(0,t+.125,.125);secs[-1]=t;bpm=64+.5*np.sin(secs/27);beats=np.r_[0,np.cumsum(np.diff(secs)*(bpm[:-1]+bpm[1:])/120)]
s=dict(title='Calcutta: Bright Detours',seed=2026101758,voices=voices,composites=[dict(name=n,components=[dict(name=s['name'],gain=g) for s,g in layers]) for n,layers in recipes],notes=notes,harmonies=hs,form=form,sequences=seqs,duration_seconds=t,total_ticks=round(t*1000),seconds_per_tick=.001,conductor_grid=dict(seconds=secs.tolist(),beats=beats.tolist()),tempo_map=[dict(beat=float(b),bpm=float(p)) for b,p in zip(beats,bpm)],dynamic_envelope=dict(section_center_db=[(-3 if sty in [1,4,8,13] else -1 if sty in [6,11,17] else 0) for sty in style_order]),pitch_policy='Only exact original-field pitches; selected subsets; no passing tones, octave shifts, glides, or retuned holds.',audit=dict(max_section_seconds=max(durations),min_section_seconds=min(durations),mean_section_seconds=float(np.mean(durations)),distinct_texture_types=len(set(style_order)),exposed_synth_parts=list(range(8)),fields_used=40))
(out/'score.json').write_text(json.dumps(s,indent=2));print(t,len(form),len(voices),len(notes),s['audit'])
