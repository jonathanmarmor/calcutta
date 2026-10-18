"""Five new converging pieces, 64 genuinely different source presets per piece."""
from pathlib import Path
import random,json,collections,math
from flow_base import FlowPiece,FORMS
from pitch_core import TITLES,SLUGS
ROOT=Path('suite');palette=json.loads((ROOT/'palette.json').read_text())
class WidePiece(FlowPiece):
 def __init__(self,k):
  super().__init__(k);r=random.Random(202610182500+k)
  samples=list(range(8,len(palette)));r.shuffle(samples)
  self.full_palette=list(range(8))+samples[:56];r.shuffle(self.full_palette)
  self.ensembles=[];self.features=[]
  # New ordering and cells, retaining the established pulse/convergence framework.
  plan=FORMS[k];shift=[5,11,3,17,9][k];self.plan=plan[shift:]+plan[:shift]
  if k%2:self.plan=self.plan[:8]+list(reversed(self.plan[8:16]))+self.plan[16:]
 def compose_scene(self,i,a,b,style):
  allinst=self.full_palette;section=[allinst[(i*11+j*3)%64] for j in range(14)]
  features=[allinst[(2*i)%64],allinst[(2*i+1)%64]]
  for feature in features:
   if feature not in section:section.append(feature)
  self.palette=section;before=len(self.notes)
  super().compose_scene(i,a,b,style)
  new=self.notes[before:];groups=collections.defaultdict(list)
  for n in new:
   if ('foreground' in n['part'] or 'choir' in n['part'] or 'exposed' in n['part']) and not n['part'].endswith('-blend'):groups[n['part']].append(n)
  ordered=sorted(groups,key=lambda p:(len(groups[p]),sum(n['duration'] for n in groups[p])),reverse=True)
  if len(ordered)<2:
   for n in new:
    if 'pulse-' in n['part']:groups[n['part']].append(n)
   ordered=sorted(groups,key=lambda p:(len(groups[p]),sum(n['duration'] for n in groups[p])),reverse=True)
  for inst,part in zip(features,ordered):
   for n in groups[part]:n['instrument']=inst
   self.features.append(dict(section=i+1,instrument=inst,name=palette[inst]['name'],part=part))
  self.ensembles.append(dict(section=i+1,start=self.sec(a),end=self.sec(b),instruments=sorted(set(n['instrument'] for n in new)),featured=features))
  self.scenes[-1]['instruments']=sorted(set(n['instrument'] for n in new));self.scenes[-1]['featured_instruments']=features
 def complete(self):
  for i,a in enumerate(range(0,self.nbars*4,16)):self.compose_scene(i,a,min(a+16,self.nbars*4),self.plan[i%len(self.plan)])
  # Short, dry endings, with no held-note retuning or master fade.
  cut=self.sec(self.nbars*4-2.2);self.notes=[n for n in self.notes if n['start']<cut-.1]
  for n in self.notes:n['duration']=min(n['duration'],cut-n['start'])
  c=self.chord(self.sec(self.nbars*4-2),self.k)
  for j in range(1+self.k%3):self.hit('ending'+str(j),self.full_palette[(self.k*7+j)%64],self.nbars*4-2+j*.55,.7 if self.k%2 else 1.,c[j%len(c)],39-j*3,'dry last fragment',exact=True)
  s=self.finish();s.update(seed=202610182100+self.k,areas=self.areas,metric_grid=self.beats,bar_tempi=self.tempi,final_chord_start=self.final_start,final_chord_fraction=(self.duration-self.final_start)/self.duration,instrument_pool=self.full_palette,ensembles=self.ensembles,featured_assignments=self.features,vibrato_policy='All sustained carriers have strictly constant frequency; no source pitch modulation survives',instrument_policy='64 distinct source presets per piece, different pools and changing section ensembles')
  (ROOT/'scores'/f'{self.k+1:02}.json').write_text(json.dumps(s,indent=2));return s
if __name__=='__main__':
 for k in range(5):
  s=WidePiece(k).complete();counts=collections.Counter(n['instrument'] for n in s['notes']);dur=collections.defaultdict(float)
  for n in s['notes']:dur[n['instrument']]+=n['duration']
  missing=set(s['instrument_pool'])-set(counts);print(k+1,s['title'],len(s['notes']),'notes;',len(counts),'instruments; min attacks',min(counts.values()),'missing',missing,flush=True)
  assert not missing
 index=[{x:json.loads((ROOT/'scores'/f'{k+1:02}.json').read_text())[x] for x in ['number','title','slug','duration','final_chord_start','final_chord_fraction']} for k in range(5)]
 (ROOT/'index.json').write_text(json.dumps(index,indent=2))
