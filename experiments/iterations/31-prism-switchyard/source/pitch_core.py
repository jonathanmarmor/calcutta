from pathlib import Path
import json,math,random,bisect,collections
import numpy as np
ROOT=Path("suite")
PITCHES=json.loads(Path("composition_32_voices_v3/score_and_sounds.json").read_text())["pitches"]
TITLES=['Changing Ensembles','Reed, Wire, Metal','Dry Color Fields','Passing Instruments','A Wider Room']
SLUGS=['changing_ensembles','reed_wire_metal','dry_color_fields','passing_instruments','wider_room']

class PitchCore:
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
    other={71: 5, 12: 6, 15: 4, 32: 2, 51: 3, 70: 1, 73: 7, 88: 0, 74: 4}.get(inst)
    if other is not None:
     nn=dict(n);nn['id']=self.counter;self.counter+=1;nn['part']=part+'-blend';nn['instrument']=other;nn['velocity']=max(16,round(n['velocity']*.45));nn['is_passing']=False
     # Passing notes remain individual; blends are field members only.
     if not passing:self.notes.append(nn)
   return n
 def frame(self,part,insts,a,b,rank=0,v=34,spacing=.17):
   c=self.chord(a,rank)
   for j,p in enumerate(c):self.add(part+str(j),insts[j%len(insts)],a+j*spacing,max(.2,b-a-j*spacing),p,v+self.r.uniform(-3,3)-j*.5,'quiet triad/seventh foundation')
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
