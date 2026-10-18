"""A fresh score: rhetorical rubato, independent clocks, and converging rhythmic suspensions."""
import json,copy,math,random,itertools,bisect
from pathlib import Path
import numpy as np
SEED=202610172012
# No previous notes, motifs, rhythms, harmonic itinerary, or form are imported.
SPEC=[
 ('A crooked invitation',36,72,56,'rubato',[3,2,4,3],[9,7,11,9]),
 ('Fluttering answers',32,92,106,'dialogue',[3,4,3,4,5,4],[6,4,6,4,8,4]),
 ('A quick backward glance',36,106,84,'tuplets',[5,4,6,5,1,0,2],[6,4,6,6,5,3,6]),
 ('Small steps on a wide ladder',40,68,88,'elastic_duo',[6,7,8,7,9],[8,8,10,6,8]),
 ('One pitch, changing light',36,52,66,'still',[8,9,10,11],[8,10,8,10]),
 ('Runs between raindrops',40,116,98,'cloud',[10,11,12,11,13],[8,8,10,6,8]),
 ('Breath before the turn',32,80,62,'landing',[12,13,14],[10,12,10]),
 ('The crowded approach',36,108,126,'tuplets',[14,15,16,15],[10,8,10,8]),
 ('Ornaments in the bass',32,62,76,'bass',[16,17,18],[10,12,10]),
 ('A long common thread',36,48,60,'rubato',[18,19,20,21],[8,10,8,10]),
 ('A chase in unequal steps',44,104,94,'three_clocks',[20,21,22,23,22],[8,8,12,10,6]),
 ('Turned around in the air',36,76,96,'dialogue',[23,24,25,24,26],[8,6,8,6,8]),
 ('One breath later',32,60,48,'elastic_duo',[26,27,28,29],[8]*4),
 ('A swarm of small departures',48,118,98,'cloud',[28,29,30,31,32,33],[8]*6),
 ('Unhurried return',44,46,58,'still',[32,33,34,35,36],[8,8,12,8,8]),
 ('Arriving without a slide',36,86,64,'landing',[36,37,38,37,39],[8,8,8,4,8]),
 ('The last grace',24,54,38,'coda',[39,38,39],[8,6,10])]
POOLS=[([38,32],[12,47]),([44,25],[34,35,48]),([51,40,42],[33,52]),([12,50],[32,18]),([43,29],[47,15]),([32,33,34,40,44,51],[49]),([4,35],[43,27]),([42,44,35,38,41,51],[46]),([47,48],[32,34,18]),([39,52],[43,11]),([44,45,42,38,50,36],[49]),([35,12],[31,34]),([25,4],[32,15]),([32,33,34,35,36,37,38,39,40,41,42,43,44],[45,46]),([8,12,52],[14,43]),([38,43],[35,34]),([11,32],[42,27])]

def triads(p):
 out=[]
 for r in range(32):
  for target,label in [(433.832,'sharp-major'),(386.314,'major'),(315.641,'minor')]:
   th=min(range(32),key=lambda v:abs((p[v]-p[r])*100-target))
   fi=min(range(32),key=lambda v:abs((p[v]-p[r])*100-701.955))
   error=abs((p[th]-p[r])*100-target)+2*abs((p[fi]-p[r])*100-701.955)
   if error<55 and len({r,th,fi})==3:out.append((error,[r,th,fi],label))
 if not out:
  error,r,f=min((abs((p[f]-p[r])*100-701.955),r,f) for r in range(32) for f in range(32) if p[f]-p[r]>3)
  return [(error,[r,f],'closest fifth')]
 return sorted(out)

def compose():
 rng=random.Random(SEED)
 palette=json.loads(Path('calcutta_motifs/score.json').read_text())['voices']
 voices=copy.deepcopy(palette)
 for source,program,name in [(7,12,'Dry marimba attack'),(10,65,'Dry alto-sax sustain')]:
  v=copy.deepcopy(voices[source]);v.update(voice=len(voices)+1,new_calibration=True)
  v['sound']={'engine':'FluidSynth','name':name,'family':'sampled','program':program};voices.append(v)
 pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
 s=dict(title='Calcutta: Grace and Grain',seed=SEED,voices=voices,notes=[],harmonies=[],form=[],tempo_map=[],complete_presentations=[],rhythmic_landings=[],seconds_per_tick=.001,bpm=72)
 beat_grid=[0.];time_grid=[0.];section_data=[];beat0=0.
 # The conductor breathes continuously, not merely through section BPM switches.
 for si,(name,nbeats,b0,b1,mode,fields,lengths) in enumerate(SPEC):
  assert sum(lengths)==nbeats
  start_time=time_grid[-1]
  for j in range(nbeats*8):
   q=j/8;u=(q+.0625)/nbeats;base=b0+(b1-b0)*u
   breath=1+.19*math.sin(2*math.pi*q/7.3+si*.6)+.07*math.sin(2*math.pi*q/2.7)
   if mode in ('rubato','still','coda','landing'):breath+=.30*(q%8/8)**4
   if q>nbeats-3:breath*=1+.35*(q-(nbeats-3))/3
   dt=60/base*breath/8
   s['tempo_map'].append(dict(beat=beat0+q,seconds=time_grid[-1],bpm=60/(dt*8)))
   beat_grid.append(beat0+q+.125);time_grid.append(time_grid[-1]+dt)
  section_data.append(dict(index=si,name=name,beat_start=beat0,beat_end=beat0+nbeats,start_seconds=start_time,end_seconds=time_grid[-1],mode=mode,bpm_start=b0,bpm_end=b1,fields=fields,lengths=lengths))
  beat0+=nbeats
 def sec(q):return float(np.interp(q,beat_grid,time_grid))
 s['duration_seconds']=round(time_grid[-1],3);s['total_ticks']=round(s['duration_seconds']*1000)
 cursor=0.;seen=set()
 for d in section_data:
  cursor=d['beat_start']
  for c,length in zip(d['fields'],d['lengths']):
   h=dict(chord=c,start=round(sec(cursor)*1000),end=round(sec(cursor+length)*1000),beat_start=cursor,beat_end=cursor+length,section=d['index'])
   s['harmonies'].append(h);cursor+=length
 def field_at(t):
  return min(len(s['harmonies'])-1,max(0,bisect.bisect_right([h['start']/1000 for h in s['harmonies']],t)-1))
 pending=[]
 def event(part,a,b,degree,vel,section,role,full=False,explicit_pitch=None,ornamental=False,boundary_action=None):
  if b-a<.025 or a>=s['duration_seconds']:return
  a=max(0,a);b=min(b,s['duration_seconds']);hi=field_at(a+.00001);h=s['harmonies'][hi]
  fixed=pitches[h['chord']][degree] if explicit_pitch is None else explicit_pitch
  boundary=h['end']/1000
  spans=[j for j,hh in enumerate(s['harmonies']) if hh['start']/1000<b and hh['end']/1000>a]
  # A real held common tone is constant in Hz, never a retuned branch.
  legal_common=all(min(abs(v-fixed) for v in pitches[s['harmonies'][j]['chord']])<1e-10 for j in spans)
  if b>boundary and not legal_common:
   stop=max(a,min(b,boundary-.065))
   if stop-a>.025:event(part,a,stop,degree,vel,section,role,full,fixed,ornamental,'breath before change')
   # An audible gap and fresh attack make an answer, not a shifted sustain.
   if not ornamental and not full and rng.random()<.48 and b-boundary>.28:
    next_hi=min(hi+1,len(s['harmonies'])-1);ps=pitches[s['harmonies'][next_hi]['chord']]
    next_degree=min(range(32),key=lambda v:abs(ps[v]-fixed))
    event(part,boundary+.11,b,next_degree,vel-6,section,'rearticulated answer',False,None,False,'new attack after breath')
   return
  pending.append(dict(voice=part,start_tick=round(a*1000),duration_ticks=round(b*1000)-round(a*1000),pitch_index=degree,pitch=fixed,velocity=max(22,min(99,round(vel))),section=section,harmony=hi,harmony_spans=spans,role=role,full=full,is_ornament=ornamental,boundary_action=boundary_action or ('unchanged common tone' if len(spans)>1 else 'inside field')))
 def pool_at(t,lo=52,hi=86):
  ps=pitches[s['harmonies'][field_at(t)]['chord']];route=[]
  for v in sorted(range(32),key=lambda v:ps[v]):
   if lo<=ps[v]<=hi and (not route or (ps[v]-ps[route[-1]])*100>28):route.append(v)
  return route or [0,1,2]
 def degree_at(t,target,index_shift=0):
  ps=pitches[s['harmonies'][field_at(t)]['chord']];route=pool_at(t)
  j=min(range(len(route)),key=lambda j:abs(ps[route[j]]-target));return route[max(0,min(len(route)-1,j+index_shift))]
 def line(part,onsets,target,contour,vel,section,gate=.8,role='elastic phrase'):
  for j,t in enumerate(onsets):
   d=(onsets[j+1]-t if j+1<len(onsets) else 1.1)
   degree=degree_at(t,target,contour[j%len(contour)])
   arc=math.sin(math.pi*j/max(1,len(onsets)-1));level=vel+13*arc-(7 if j==len(onsets)-1 else 0)
   event(part,t,t+max(.06,d*gate),degree,level,section,role)
   # Grace material is a temporary exception to the original-pitches-only rule.
   chance=.12 if role in ('independent pulse cloud','tuplet counterpoint') else .47
   if j==0 or rng.random()>chance:continue
   hi=field_at(t);h=s['harmonies'][hi];ps=pitches[h['chord']];anchor=ps[degree]
   space=min(.85,(t-onsets[j-1])*.48,t-h['start']/1000-.035)
   if space<.12:continue
   kind=rng.choice(['chromatic approach','diatonic flourish','pentatonic sweep','microtonal turn','endpoint run'])
   if kind=='chromatic approach':offsets=[-3.1,-2.05,-1.08,-.43]
   elif kind=='diatonic flourish':offsets=[-5.2,-3.2,-2.1,-.95]
   elif kind=='pentatonic sweep':offsets=[-7.1,-5.0,-2.8,-1.15]
   elif kind=='microtonal turn':offsets=[.22,-.34,.13]
   else:
    order=sorted(set(ps));below=[v-anchor for v in order if v<anchor][-5:];offsets=below if len(below)>=2 else [-.7,.4,-.2]
   if j%3==1:offsets=[-x for x in offsets]
   if rng.random()<.24 and space>.4:offsets=offsets[:3]+[.45,-.18,.12]
   weights=np.array([rng.uniform(.7,1.2) for _ in offsets]);weights=weights/weights.sum()*space
   when=t-space
   for k,(offset,length) in enumerate(zip(offsets,weights)):
    pitch=max(48.,min(96.11271151650251,anchor+offset))
    event(part,when,when+length*.86,degree,level-19+6*k/max(1,len(offsets)-1),section,kind,False,pitch,True,'ornament within field')
    when+=length
 targets=[-14,-9,-6,-12,-18,-7,-13,-5,-12,-17,-7,-10,-16,-4,-19,-9,-25]
 for d in section_data:
  si=d['index'];mode=d['mode'];start=d['start_seconds'];end=d['end_seconds'];qs=d['beat_start'];qe=d['beat_end'];lead,back=POOLS[si];srng=random.Random(SEED+si*1019)
  # Completely fresh subjects for this score, and different ones in every section.
  contour=[0]+[srng.choice([-3,-2,-1,1,2,3]) for _ in range(srng.choice([6,8,9]))]+[srng.choice([-1,0,1])]
  target=57+(si*7)%19
  if mode in ('rubato','elastic_duo','dialogue','bass','coda'):
   for phrase,q in enumerate(np.arange(qs,qe-2,7 if mode!='coda' else 9)):
    count=srng.choice([5,7,8]);weights=np.array([srng.uniform(.65,1.55) for _ in range(count)])
    # Deliberate local pacing: stronger hesitations, accelerating middles, soft endings.
    weights[0]*=1.25;weights[-1]*=1.65;span=min(6.4,qe-q-.25)
    offsets=np.r_[0,np.cumsum(weights[:-1]/sum(weights)*span)]
    behind=.065 if phrase%2 else -.035
    times=[max(start+.01,sec(q+off)+behind+.012*math.sin(j*.8)) for j,off in enumerate(offsets)]
    part=lead[phrase%len(lead)]
    line(part,times,target,contour if phrase%2==0 else contour[::-1],61 if mode!='coda' else 43,si,.88,'rubato melodic sentence')
    if mode!='coda':
     times2=[sec(q+off)+.025 for off in [1.3,3.1,5.2] if q+off<qe-.2]
     line(lead[(phrase+1)%len(lead)],times2,target-7,[-1,1,0],43,si,.72,'independent reply')
  elif mode=='tuplets':
   for layer,part in enumerate(lead):
    step=[2/3,.8,.5,4/3,1/3,.6][layer%6]
    q=qs+(layer*.21)
    times=[]
    while q<qe-.4:
     # Tuplet scaffolding with expressive deviations rather than snapping every attack.
     times.append(sec(q)+.018*math.sin(len(times)*.65+layer)+(-.025 if layer%2 else .035))
     q+=step*(1+.018*math.sin(q*.7+layer))
    line(part,times,55+layer*4,contour[layer:]+contour[:layer],50+layer%3*3,si,.74,'tuplet counterpoint')
  elif mode in ('cloud','three_clocks'):
   midpoint=(start+end)/2;period=(end-start)/(qe-qs)
   for layer,part in enumerate(lead):
    # Similar but independent clocks: no privileged backing pulse.
    factor=(.69+layer*.023) if mode=='cloud' else [.73,1.01,1.37][layer%3]
    clock=period*factor;times=[];t=start+layer*.17
    while t<end-.2:
     times.append(t+.009*math.sin(len(times)*.81+layer));t+=clock*(1+.026*math.sin(len(times)*.17+layer))
    # Some lines enter late or leave early, shaping the density cloud.
    if layer%3==1:times=times[max(1,len(times)//5):]
    if layer%4==2:times=times[:max(2,len(times)*4//5)]
    line(part,times,51+layer*3,contour if layer%2==0 else contour[::-1],44+layer%4*3,si,.67,'independent pulse cloud')
  elif mode=='landing':
   land=sec(qe-4)
   for layer,part in enumerate(lead+back):
    # Back-calculate unequal local tempos so the final note lands on one downbeat.
    count=[11,7,9,6][layer%4];step=[.37,.79,.53,1.13][layer%4]
    times=[land-(count-1-j)*step for j in range(count)]
    times=[t for t in times if t>=start+.1]
    line(part,times,57+layer*4,contour if layer%2 else contour[::-1],57-layer*4,si,.9,'rhythmic suspension')
   s['rhythmic_landings'].append(dict(section=si+1,seconds=land,beat=qe-4,periods_seconds=[.37,.79,.53,1.13]))
  elif mode=='still':
   for layer,part in enumerate(lead):
    times=[sec(qs+off)+layer*.11 for off in [0,6.5,15,24.5,31] if qs+off<qe-2]
    line(part,times,57+layer*5,contour,46+layer*3,si,.93,'long-breathed line')
  # Sparse harmonic support, never the old short-short-long chordal gesture.
  if mode not in ('cloud','three_clocks'):
   for hi,h in enumerate(s['harmonies']):
    if h['section']!=si:continue
    a=h['start']/1000;b=h['end']/1000;ps=pitches[h['chord']]
    ts=triads(ps);chosen=min(ts[:12],key=lambda c:abs(ps[c[1][0]]-(50+si%4*4)))
    for j,v in enumerate(chosen[1]):
     part=back[j%len(back)];entry=a+.14+j*.19
     if entry<b-.3:event(part,entry,min(b-.06,entry+(b-a)*.66),v,34-j*3,si,'staggered inner chord')
  # Gabriel-style programming experiment: percussive front + sustained reed,
  # using our own samples, not his original Fairlight files or effects.
  if si in (3,9):
   for q in np.arange(qs+1,qe-1,4.7):
    t=sec(q);v=degree_at(t,64,si%3)
    event(51,t,t+.24,v,62,si,'sample composite attack')
    event(52,t+.018,min(end-.05,t+1.4),v,40,si,'sample composite sustain')
  if si in (4,9,14):event(18 if si!=9 else 47,start+.45,end-.5,0,33,si,'constant common-tone pedal')
  s['form'].append(dict(section=si+1,start_seconds=start,end_seconds=end,start_bar=qs/4+1,bars=(qe-qs)/4,strategies=[mode],name=d['name'],dynamic_db=targets[si],nominal_bpm=[d['bpm_start'],d['bpm_end']]))
 # Give every original field one clear full exposure after the sparse first scene.
 windows=[]
 for hi,h in enumerate(s['harmonies']):
  c=h['chord']
  if c in seen or h['section']==0:continue
  seen.add(c);a=h['start']/1000+.16;b=min(h['end']/1000-.07,sec(min(h['beat_end']-.1,h['beat_start']+3.8)))
  if b-a<.4:a=h['start']/1000;b=h['end']/1000-.03
  windows.append((a,b))
  for v in range(32):event(v,a+(v%4)*.025,b,v,47-(v%5)*3,h['section'],'complete field',True)
  s['complete_presentations'].append(dict(chord=c,start_seconds=a+.075,end_seconds=b,harmony=hi))
 assert seen==set(range(40))
 # Protect whole-field exposures and monophonic instruments without inventing pitches.
 fragments=[]
 for n in pending:
  pieces=[(n['start_tick']/1000,(n['start_tick']+n['duration_ticks'])/1000)]
  if not n['full']:
   for a,b in windows:
    result=[]
    for st,en in pieces:
     if en<=a or st>=b:result.append((st,en))
     else:
      if st<a:result.append((st,a))
      if en>b:result.append((b,en))
    pieces=result
  fragments.extend(dict(n,start_tick=round(a*1000),duration_ticks=round(b*1000)-round(a*1000)) for a,b in pieces if b-a>.025)
 for v in range(len(voices)):
  ns=sorted([n for n in fragments if n['voice']==v],key=lambda n:(n['start_tick'],not n['full'],-n['velocity']))
  unique=[]
  for n in ns:
   if unique and n['start_tick']==unique[-1]['start_tick']:continue
   unique.append(n)
  for i,n in enumerate(unique):
   stop=min(n['start_tick']+n['duration_ticks'],unique[i+1]['start_tick'] if i+1<len(unique) else s['total_ticks']);n['duration_ticks']=stop-n['start_tick']
   if n['duration_ticks']>=10:s['notes'].append(n)
 used=sorted({n['voice'] for n in s['notes']});mapping={v:i for i,v in enumerate(used)}
 s['voices']=[s['voices'][v] for v in used]
 for i,v in enumerate(s['voices']):v['voice']=i+1
 for n in s['notes']:n['voice']=mapping[n['voice']]
 s['notes'].sort(key=lambda n:(n['voice'],n['start_tick']))
 s['dynamic_envelope']=dict(section_center_db=targets,interpolation='linear decibels between scene centers')
 s['conductor_grid']=dict(beats=beat_grid,seconds=time_grid)
 # Recompute spans after gate protection/truncation; do not split common sustains.
 for n in s['notes']:
  stop=n['start_tick']+n['duration_ticks']
  spans=[j for j,h in enumerate(s['harmonies']) if h['start']<stop and h['end']>n['start_tick']]
  n['harmony_spans']=spans;n['harmony']=spans[0]
  if not n['is_ornament']:
   for hi in spans:assert min(abs(v-n['pitch']) for v in pitches[s['harmonies'][hi]['chord']])<1e-10
  if len(spans)>1:
   assert not n['is_ornament']
   assert all(min(abs(v-n['pitch']) for v in pitches[s['harmonies'][hi]['chord']])<1e-10 for hi in spans)
 s['ornament_permission']='This generation only: passing tones and ornaments may leave the original fields. Structural notes stay exact.'
 s['boundary_policy']='No sustained retuning: release before changes, reattack after a clear breath, or hold an unchanged exact common tone.'
 for c in s['complete_presentations']:
  mid=round((c['start_seconds']+c['end_seconds'])/2*1000)
  assert {n['pitch_index'] for n in s['notes'] if n['start_tick']<=mid<n['start_tick']+n['duration_ticks']}==set(range(32))
 for v in range(len(s['voices'])):
  own=[n for n in s['notes'] if n['voice']==v];assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
 return s
if __name__=='__main__':
 out=Path('calcutta_grace');out.mkdir(exist_ok=True);s=compose();(out/'score.json').write_text(json.dumps(s,indent=2));print(s['duration_seconds'],'seconds;',len(s['notes']),'notes;',len(s['voices']),'parts; temporary ornament exception; no retuned sustains')
