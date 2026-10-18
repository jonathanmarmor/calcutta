"""Mobile instrumental lines and temporary choirs inside Archipelago's original fields."""
import copy,json,random,math
from pathlib import Path
import motif_fields as archipelago_piece
SEED=202610171948
CHOIRS={
 0:dict(name='flute, clarinet, and nylon guitar',lead=[29,10],chord=[27,12,8]),
 1:dict(name='three harps with a muted-trumpet singer',lead=[35,32],chord=[32,33,34]),
 2:dict(name='muted-trumpet trio and winds',lead=[35,36],chord=[35,36,37,4,8]),
 3:dict(name='clarinet duet with keyboards',lead=[38,39],chord=[5,11,15]),
 4:dict(name='two wooden flutes above harps',lead=[40,41],chord=[32,33,34]),
 5:dict(name='two sine harmoniums and muted trumpets',lead=[42,43],chord=[35,36,37]),
 6:dict(name='oboe, bassoon, and English horn',lead=[4,8],chord=[12,14,27]),
 7:dict(name='harps with a quiet synth duet',lead=[32,33],chord=[42,43,34]),
 8:dict(name='muted trumpets answering wooden flutes',lead=[35,40],chord=[36,37,41]),
 9:dict(name='clarinet duet and clean guitars',lead=[38,39],chord=[7,31,11]),
 10:dict(name='sine harmoniums with organ',lead=[42,43],chord=[14,15,11]),
 11:dict(name='Rhodes and a single harp',lead=[11,32],chord=[27,14,33])}

def compose():
 archipelago_piece.SEED=SEED
 s=archipelago_piece.compose()
 p=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
 rng=random.Random(SEED)
 for i,v in enumerate(s['voices']):v['calibration_voice']=i
 def clone(source,pan,name=None,program=None):
  v=copy.deepcopy(s['voices'][source]);v['pan']=pan;v['voice']=len(s['voices'])+1
  if program is not None:
   v['sound']={'engine':'FluidSynth','name':name,'family':name,'program':program};v['new_calibration']=True
  s['voices'].append(v)
 for pan in (-.65,0,.65):clone(27,pan,'Harp',46)
 for pan in (-.55,0,.55):clone(19,pan)
 for pan in (-.4,.4):clone(10,pan)
 for pan in (-.45,.45):clone(22,pan)
 for pan in (-.6,.6):clone(21,pan)
 for spec in json.loads(Path('motif_patches/palette.json').read_text()):
  v=copy.deepcopy(s['voices'][3]);v['voice']=len(s['voices'])+1;v['sound']=spec;v['reference_calibration']=True;v.pop('new_calibration',None);s['voices'].append(v)
 for i in range(2):
  v=copy.deepcopy(s['voices'][3]);v['voice']=len(s['voices'])+1;v['sound']={'engine':'Surge XT','name':['Ladder velvet bass','Dry resonant lead'][i],'family':'analog inspired','state_path':f'motif_patches/surge_{i}.vststate'};v['reference_calibration']=True;v.pop('new_calibration',None);s['voices'].append(v)
 for pan in (-.25,.25):clone(0,pan,'Growling fretless bass',35)
 for pan in (-.5,.5):clone(27,pan,'Buzzy sitar',104)
 assert len(s['voices'])==53
 CHOIRS[0].update(name='dry Oberheim pulse and fretless bass',lead=[44,10],chord=[49,27,12])
 CHOIRS[1].update(name='harps, fretless bass, and buzzy sitar',lead=[51,32],chord=[32,33,34,49])
 CHOIRS[2].update(name='resonant analog leads and muted trumpets',lead=[48,35],chord=[35,36,37,50])
 CHOIRS[3].update(name='Oberheim brass choir and sitar',lead=[45,51],chord=[44,45,46,52])
 CHOIRS[4].update(name='wooden flutes and velvet ladder bass',lead=[40,41],chord=[47,32,33])
 CHOIRS[5].update(name='resonant analog sequence and Oberheim pulse',lead=[48,44],chord=[45,46,49])
 CHOIRS[6].update(name='winds, sitar, and fretless bass',lead=[4,52],chord=[12,49,50])
 CHOIRS[7].update(name='harps and Oberheim trios',lead=[32,46],chord=[44,45,34])
 CHOIRS[8].update(name='trumpets, flutes, and fretless counterpoint',lead=[35,40],chord=[36,50,41])
 CHOIRS[9].update(name='clarinets, sitar, and resonant lead',lead=[38,48],chord=[51,52,39])
 CHOIRS[10].update(name='radically stretched Oberheim choir',lead=[44,45],chord=[46,47,15])
 CHOIRS[11].update(name='distant pulse, Rhodes, and fretless bass',lead=[44,11],chord=[49,32,14])
 # Preserve original complete exposures; all other pitches may change instrument.
 original=[];events=[]
 for n in s['notes']:
  e=dict(n,pitch_index=n['voice'],original_voice=n['voice'],start=n['start_tick'],end=n['start_tick']+n['duration_ticks'])
  if n['role']=='complete harmony':original.append(e)
  else:events.append(e)
 windows=[(x['full_start_tick']-6,x['full_end_tick']) for x in s['visits'] if x['full']]
 gem_visits=set(range(len(s['visits'])))
 melodic_roles={'melody','inner answer','subject','counterpoint','answering melody','small melody','remembered melody'}
 events=[e for e in events if not(e['harmony'] in gem_visits and e['role'] in melodic_roles)]
 s['invention_details']=[]
 for hi,x in enumerate(s['visits']):
  if hi not in gem_visits:continue
  pitches=p[x['chord']];palette=s['internal_progressions'][hi];A=[v-1 for v in palette['chord_voices'][0]];B=[v-1 for v in palette['chord_voices'][1]]
  # Distinct endpoints in actual register; preserve microsteps as well as wider gaps.
  ordered=[]
  for v in sorted(range(32),key=lambda v:pitches[v]):
   if not ordered or abs(pitches[v]-pitches[ordered[-1]])>.0001:ordered.append(v)
  third=A[min(1,len(A)-1)];fifth=A[-1]
  neighbors=[v for v in ordered if v not in A and 15<abs(pitches[v]-pitches[third])*100<350]
  neighbor=min(neighbors,key=lambda v:abs(abs(pitches[v]-pitches[third])*100-75)) if neighbors else A[0]
  pairs=[(abs(pitches[b]-pitches[a])*100,a,b) for a,b in zip(ordered,ordered[1:]) if 55<pitches[a]<84]
  tight=min(pairs,key=lambda z:abs(z[0]-64.2)) if pairs else (0,A[0],third)
  subject=[A[0],third,fifth,third,neighbor,third,A[0]]
  durations=[12,12,18,6,12,12,24]
  tag=x['texture'];start=x['start'];end=x['end']
  def line(route,t,ds,vel,part,role):
   for j,(v,d) in enumerate(zip(route,ds)):
    if t>=end-3:break
    stop=min(end,t+d-2)
    events.append(dict(pitch_index=v,original_voice=v,start=t,end=stop,pitch=pitches[v],velocity=max(26,round(vel+10*math.sin(math.pi*j/max(1,len(route)-1))-(8 if j==len(route)-1 else 0))),harmony=hi,section=x['group'],strategy=tag,role=role,preferred_line=part))
    t+=d
  # Persistent motif families survive harmonic shuttles and mutate by degree.
  # Compact density, fleeting fragments, and huge augmentation deliberately coexist.
  family=x['group']%5
  shapes=[[0,1,0,2,1],[0,2,1,3,2,4],[3,2,0,1],[0,1,2,1,0],[0,0,2,1,3]][family]
  base_rhythm=[[12,6,6,12,12],[6,6,12,6,6,12],[18,6,12,12],[12,12,24,12,36],[6,6,18,6,12]][family]
  degrees=[]
  for v in ordered:
   if 48<=pitches[v]<=86 and (not degrees or (pitches[v]-pitches[degrees[-1]])*100>30):degrees.append(v)
  degrees=degrees or ordered
  anchor=min(range(len(degrees)),key=lambda j:abs(pitches[degrees[j]]-pitches[third]))
  scale=[.5,1,1,2,4,8][x['group']%6]
  if x['group']==10:scale=8
  if x['group']==0:scale=1 # highly audible two-/three-field shuttles
  rhythms=[max(3,round(d*scale/3)*3) for d in base_rhythm]
  length=sum(rhythms)
  for cycle,t in enumerate(range(start,end-6,max(12,length))):
   # Sequential transposition through actual endpoint degrees, then a changed ending.
   trans=(cycle+hi%3)%4-1
   shape=shapes[::-1] if cycle%4==2 else shapes[:]
   if cycle%4==3:shape[-1]+=1
   if (hi+cycle)%5==0:shape=[-d for d in shape]
   route=[degrees[max(0,min(len(degrees)-1,anchor+trans+d-1))] for d in shape]
   if x['group']%3==1 and cycle%3==2:route=route[:3]
   vel=61 if x['group']==10 else 70
   line(route,t,rhythms,vel,0,'motif subject')
   # Answer at another degree, offset and rhythmically transformed.
   if x['beats']>=8 or x['group']==0:
    answer_route=[degrees[max(0,min(len(degrees)-1,anchor+2-d))] for d in shape]
    answer_rhythm=[max(3,round(d*(2 if cycle%2 else .5)/3)*3) for d in rhythms]
    line(answer_route,t+(12 if scale<=2 else 24),answer_rhythm,51,1,'motif countersequence')
  # Chordal motifs, with strongly shaped and unequal timbral balances.
  if hi%4==1:
   for j,off in enumerate(range(0,end-start-6,24 if x['group']%2 else 12)):
    triad=A if j%3!=2 else B
    for k,v in enumerate(triad):
     events.append(dict(pitch_index=v,original_voice=v,start=start+off,end=min(end-1,start+off+(8 if j%3<2 else 18)),pitch=pitches[v],velocity=[52,35,25,41,30,22][j%6]-k*5,harmony=hi,section=x['group'],strategy=tag,role='chordal motif'))
  s['invention_details'].append(dict(visit=hi+1,start_seconds=start*.05,chord=x['chord'],subject_voices=[v+1 for v in subject],subject_intervals_cents=[round((pitches[b]-pitches[a])*100,3) for a,b in zip(subject,subject[1:])],neighbor_step_cents=round((pitches[neighbor]-pitches[third])*100,3),close_pair_cents=round(tight[0],3)))
 # Very slow subjects run across whole harmonic phrases rather than restarting.
 for group in (5,10):
  xs=[x for x in s['visits'] if x['group']==group];begin=xs[0]['start'];finish=xs[-1]['end']
  events=[e for e in events if not(e['section']==group and e['role'] in ('motif subject','motif countersequence'))]
  pattern=[0,1,0,2,1];ds=[96,48,48,96,96];t0=begin;cycle=0
  while t0<finish:
   for degree,d in zip(pattern,ds):
    stop=min(finish,t0+d-3)
    for hi,h in enumerate(s['harmonies']):
     a=max(t0,h['start']);b=min(stop,h['end'])
     if b-a<3:continue
     pitches=p[h['chord']];scale=[]
     for v in sorted(range(32),key=lambda v:pitches[v]):
      if 55<=pitches[v]<=83 and (not scale or (pitches[v]-pitches[scale[-1]])*100>30):scale.append(v)
     index=max(0,min(len(scale)-1,2+degree+cycle%2));v=scale[index]
     events.append(dict(pitch_index=v,original_voice=v,start=a,end=b,pitch=pitches[v],velocity=58-3*cycle,harmony=hi,section=group,strategy='radical augmentation',role='motif subject',preferred_line=0))
    t0+=d
    if t0>=finish:break
   cycle+=1
 # Keep protected complete harmonies clear, including the newly written subjects.
 fragments=[]
 for e in events:
  pieces=[(e['start'],e['end'])]
  for a,b in windows:
   result=[]
   for st,en in pieces:
    if en<=a or st>=b:result.append((st,en))
    else:
     if st<a:result.append((st,a))
     if en>b:result.append((b,en))
   pieces=result
  fragments.extend(dict(e,start=a,end=b) for a,b in pieces if b-a>=3)
 # Allocate complete monophonic lines, retaining timbre across moving pitches.
 occupied=[[] for _ in range(53)];last=[None]*53;out=[]
 for e in original:
  v=e['original_voice'];occupied[v].append((e['start'],e['end']));out.append(dict(e,voice=v))
 def free(v,e):return not any(a<e['end'] and b>e['start'] for a,b in occupied[v])
 for e in sorted(fragments,key=lambda e:(e['start'],0 if e.get('preferred_line')==0 else 1,-e['velocity'])):
  group=CHOIRS[e['section']]
  is_melody=e['role'] in melodic_roles or e['role'] in ('interval subject','microstep subject','contrary answer','canonic answer','motif subject','motif countersequence')
  if is_melody:
   pref=group['lead'];part=e.get('preferred_line',0 if 'answer' not in e['role'] and e['role']!='counterpoint' else 1)
   preferred=pref[part%len(pref)]
   seats=[preferred]+[v for v in pref if v!=preferred]+group['chord']
  else:
   seats=group['chord']+group['lead']
   # Some accompaniment keeps its original pitch/timbre anchor.
   if rng.random()<.18:seats=[e['original_voice']]+seats
  options=[v for v in dict.fromkeys(seats) if free(v,e)]
  if not options:options=[v for v in range(53) if free(v,e)]
  assert options,'Insufficient monophonic instrument seats'
  if is_melody and preferred in options:v=preferred
  else:
   v=min(options,key=lambda v:seats.index(v)*.7 if last[v] is None and v in seats else ((abs(last[v]-e['pitch'])*.12 if last[v] is not None else 1)+(seats.index(v)*.35 if v in seats else 8)))
  occupied[v].append((e['start'],e['end']));last[v]=e['pitch'];out.append(dict(e,voice=v))
 s['notes']=[]
 for e in out:
  s['notes'].append(dict(voice=e['voice'],pitch_index=e['pitch_index'],start_tick=e['start'],duration_ticks=e['end']-e['start'],pitch=e['pitch'],velocity=e['velocity'],role=e['role'],strategy=e['strategy'],harmony=e['harmony'],section=e['section']))
 s['notes'].sort(key=lambda n:(n['voice'],n['start_tick']))
 s['unsplit_events']=out;s['title']='Calcutta: Obsessions';s['seed']=SEED
 s['motif_plan']={'degree_shapes':[[0,1,0,2,1],[0,2,1,3,2,4],[3,2,0,1],[0,1,2,1,0],[0,0,2,1,3]],'time_scales':[.5,1,2,4,8],'operations':['degree sequence','inversion','retrograde','ending mutation','rhythmic augmentation','rhythmic diminution','fragmentation','cross-field remapping']}
 s['orchestration']={str(k):v['name'] for k,v in CHOIRS.items()}
 for f in s['form']:f['choir']=CHOIRS[f['section']-1]['name']
 used=sorted({n['voice'] for n in s['notes']});mapping={old:new for new,old in enumerate(used)}
 s['voices']=[s['voices'][old] for old in used]
 for i,v in enumerate(s['voices']):v['voice']=i+1
 for n in s['notes']:n['voice']=mapping[n['voice']]
 for e in s['unsplit_events']:e['voice']=mapping[e['voice']]
 for v in range(len(s['voices'])):
  own=[n for n in s['notes'] if n['voice']==v];assert own,f'Unused instrument {v}'
  assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
 for n in s['notes']:
  assert n['pitch']==p[s['harmonies'][n['harmony']]['chord']][n['pitch_index']]
 for chord in range(40):
  x=next(x for x in s['visits'] if x['chord']==chord and x['full']);mid=(x['full_start_tick']+x['full_end_tick'])//2
  assert {n['pitch_index'] for n in s['notes'] if n['start_tick']<=mid<n['start_tick']+n['duration_ticks']}==set(range(32))
 return s
if __name__=='__main__':
 root=Path('calcutta_motifs');root.mkdir(exist_ok=True);s=compose();(root/'score.json').write_text(json.dumps(s,indent=2))
 print(len(s['notes']),'notes;',len(s['voices']),'instrumental lines;',len(s['invention_details']),'field-specific inventions')
