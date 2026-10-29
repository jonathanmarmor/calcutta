"""Seven unequal volumes: different architectures, miniature scopes and long-form acts."""
from compose_material import Material
from compose_foundation import Doors,ROOT,PITCHES
from plan import PIECES,VOLUMES
from endings import finish_piece
import json,math,collections
class Seven(Material):
 def __init__(self,k):
  Doors.__init__(self,k);self.kind=PIECES[k][4];self.volume=PIECES[k][5];self.ending=PIECES[k][3];self.ending_start=self.duration-min(24,max(2.4,self.duration*.08));self.tuning_mode='12-ET' if k==10 else 'continuous field-endpoint glides' if k==25 else 'exact Calcutta'
  theme=[0]
  for j in range(7):theme.append(theme[-1]+self.r.choice([-2,-1,1,1,2,3]))
  self.theme=[v-min(theme) for v in theme]
  self.final_start=self.duration*.60
  if self.duration<90:
   chosen=[1,3,7,12,21,38];self.harmonies=[];self.areas=[]
   for j,ch in enumerate(chosen):
    a=self.final_start*j/6;b=self.final_start*(j+1)/6;self.harmonies.append(dict(chord=ch,start=a,end=b));self.areas.append(dict(first=ch,last=ch,start=a,end=b))
   self.harmonies.append(dict(chord=39,start=self.final_start,end=self.duration));self.areas.append(dict(first=39,last=39,start=self.final_start,end=self.duration))
  else:
   # The early 1:2 visit stays brief even in the longest movements.
   first=self.harmonies[:4];end=first[-1]['end'];weights=[1,1,.20,1];edges=[0]
   for w in weights:edges.append(edges[-1]+end*w/sum(weights))
   for j,h in enumerate(first):h['start']=edges[j];h['end']=edges[j+1]
  self.starts=[h['start'] for h in self.harmonies]
 def raw(self,t):
  if self.k==10:return [p for p in range(48,97) if p%12 in [0,2,4,5,7,9,11]]
  return Doors.raw(self,t)
 def chord(self,t,rank=0):
  if self.k==10:
   step=int(t/(self.duration/64))%8;root=[60,57,65,62,67,60,65,60][step];d=[0,3,7] if step in [1,3] else [0,4,7];return [root+v+12*(rank%2) for v in d if root+v+12*(rank%2)<=96]
  return Doors.chord(self,t,rank)
 def mode(self,i):
  plans={
   'arch':['dialogue','invention','chorale','rivers','relay','slow_outer','chord_graph','hocket','chamber'],
   'chamber':['chamber','slow_outer','dialogue'],
   'ground':['chaconne','concertino','chaconne','invention','chorale'],
   'clock':['clocks','rivers','hocket','subtraction'],
   'graph':['chord_graph','stair','slow_outer','fan','invention'],
   'jewel':['hocket','chamber','stair','chorale'],
   'voice':['sing','dialogue','vocal_canon','slow_outer','invention','chorale','sing'],
   'relay':['relay','invention','dialogue','chamber','relay','fan'],
   'chorale':['chorale','concertino','slow_outer','invention'],
   'trill':['trill','trill','slow_outer','trill','chaconne','trill','dialogue','chamber'],
   'tonal':['chaconne','invention','chorale','concertino','keyboard'],
   'concertino':['concertino','invention','slow_outer','concertino','chaconne'],
   'stair':['stair','chord_graph','invention','dialogue'],
   'reverse':['reverse','chamber','reverse','relay'],
   'fan':['fan','ribbons','slow_outer','chord_graph'],
   'invention':['invention','relay','chaconne','hocket'],
   'ribbons':['ribbons','clocks','slow_outer','chorale'],
   'still':['still','chamber','slow_outer','chorale'],
   'atlas':['ribbons','rivers','relay','fan','slow_outer','chorale','invention','subtraction','chord_graph','concertino','chamber'],
   'long_ground':['chaconne','invention','chaconne','concertino','chaconne','chorale','rivers','chaconne','stair','slow_outer'],
   'gliss':['gliss','gliss','still','gliss','slow_outer','gliss','fan','chamber'],
   'echo':['echo','keyboard','echo','rivers','chamber','echo','chord_graph']}
  plan=plans[self.kind];fraction=self.sec(min(i*16,self.nbeats))/self.duration;act=min(4,int(fraction*5));index=(i+act*(self.k%5+1))%len(plan)
  return plan[index]
 def complete(self):
  a=0.;i=0;limit=self.bt(self.ending_start)
  while a<limit-.1:
   bars=[2,5,3,6,4,2,4,3][(i+self.k)%8];b=min(limit,a+bars*4)
   while self.sec(b)-self.sec(a)>24:b-=4
   before=len(self.notes);self.segment(i,a,b,self.mode(i));progress=self.sec(a)/self.duration;act=min(4,int(progress*5))
   # Five larger-form acts shape register/density/dynamics above the scene layer.
   if self.duration>600:
    level=[0,-4,3,-6,1][act]
    for n in self.notes[before:]:n['velocity']=max(19,min(62,n['velocity']+level))
    if act==3 and i%3==1:
     keep={p for j,p in enumerate(sorted(set(n['part'] for n in self.notes[before:]))) if j%3!=1};self.notes=self.notes[:before]+[n for n in self.notes[before:] if n['part'] in keep]
   self.scenes[-1]['act']=act+1;self.scenes[-1]['actual_instruments']=sorted(set(n['instrument'] for n in self.notes[before:]));a=b;i+=1
  finish_piece(self)
  for hi,h in enumerate(self.harmonies):
   if not any(n['fields']==[hi] for n in self.notes):self.add('field-lens',self.palette[hi%len(self.palette)],h['start']+.025,min(.8,h['end']-h['start']-.055),self.raw(h['start']+.025)[hi%len(self.raw(h['start']+.025))],29,'field coverage')
  self.notes=[n for n in self.notes if n['duration']>.03];self.notes.sort(key=lambda n:(n['start'],n['id']));slots=collections.defaultdict(list);voices=[]
  for n in self.notes:
   own=slots[n['instrument']];slot=next((j for j,(end,v) in enumerate(own) if end<=n['start']+1e-6),None)
   if slot is None:slot=len(own);own.append((-1,len(voices)));voices.append(dict(part='nonoverlapping instrument lane '+str(slot),instrument=n['instrument']))
   n['voice']=own[slot][1];own[slot]=(n['start']+n['duration'],n['voice'])
  live_ids={n['id'] for n in self.notes}
  for seq in self.sequences:seq['note_ids']=[v for v in seq.get('note_ids',[]) if v in live_ids]
  self.sequences=[seq for seq in self.sequences if seq['note_ids']]
  for cue in self.cues:cue['note_ids']=[v for v in cue.get('note_ids',[]) if v in live_ids]
  self.cues=[cue for cue in self.cues if cue['note_ids']]
  s=dict(number=self.k+1,volume=self.volume,title=self.title,slug=self.slug,duration=self.duration,description=self.description,seed=self.seed,kind=self.kind,theme=self.theme,harmonies=self.harmonies,areas=self.areas,notes=self.notes,voices=voices,sections=self.scenes,sequences=self.sequences,cue_network=self.cues,metric_grid=self.beats.tolist(),final_chord_start=self.final_start,final_chord_fraction=.4,instrument_pool=sorted(set(n['instrument'] for n in self.notes)),tuning_mode=self.tuning_mode,ending=self.ending,ending_start=self.ending_start,vocal_allowed=self.k in [6,29],effects_allowed=self.k in [14,27],gliss_allowed=self.k==25,miniature_scope=self.duration<90,pitch_policy='Exact original fields except 11 (12-ET) and 26 (continuous field-endpoint slides). Miniatures select seven original fields; longer works traverse all forty.')
  (ROOT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2));return s
if __name__=='__main__':
 index=[]
 for k in range(len(PIECES)):
  s=Seven(k).complete();index.append({x:s[x] for x in ['number','volume','title','slug','duration','description','kind','ending','ending_start','tuning_mode','miniature_scope']});print(k+1,s['title'],s['duration'],len(s['notes']),'notes',flush=True)
 (ROOT/'index.json').write_text(json.dumps(index,indent=2))
