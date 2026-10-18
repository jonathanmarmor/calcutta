"""Small contrapuntal studies inside Calcutta's converging chord progression."""
import json,math,random,collections,copy
from pathlib import Path
import arrival_piece
SEED=202610171851
FORM=['cantabile','triad_residence','seventh_dialogue','contrary_invention','layered_trios','melody_and_bells','root_madrigal','sighing_duet','seventh_residence','triad_residence','two_part_canon','layered_trios','cantabile','passacaglia','seventh_dialogue','contrary_invention','melody_and_bells','root_madrigal','seventh_residence','sighing_duet','layered_trios','two_part_canon','cantabile','triad_residence','farewell']
DESC={
 'cantabile':'A shaped upper melody, then its answer, over a quiet sustained triad; a short lower countermelody appears in the gaps.',
 'triad_residence':'A single sharp-third triad is explored through sustained, broken, and overlapping voicings before another root answers.',
 'seventh_dialogue':'Two four-note sonorities alternate, with a slower seventh crossing the moving triad underneath.',
 'contrary_invention':'Two recurring motifs move in opposite contours, then exchange their rhythmic roles over a sparse harmonic floor.',
 'layered_trios':'Two major-triad families in contrasting registers overlap; one holds while the other unfolds, then they exchange roles.',
 'melody_and_bells':'A sustained melodic thread above gently spaced plucked notes; a small middle voice answers the melody.',
 'root_madrigal':'Two root families trade related melodic sentences, then sing together in a brief three-part close.',
 'sighing_duet':'Paired descending figures answer ascending pickups, with long phrase endings and a quietly changing chord underneath.',
 'seventh_residence':'A seventh sonority is given a whole six-bar span, with its seventh sustained above a breathing triad.',
 'two_part_canon':'A small turning motif returns after a beat in another register, with a longer answer and a quiet held support.',
 'passacaglia':'A slow recurring bass figure supports a repeated upper motif whose ending changes, then settles.',
 'farewell':'Fragments of the earlier melody and its two chord families alternate, becoming quieter and more widely spaced.'}

def sonorities(p):
    result=[]
    for r in range(32):
        third=min(range(32),key=lambda v:abs((p[v]-p[r])*100-433.832))
        fifth=min(range(32),key=lambda v:abs((p[v]-p[r])*100-701.955))
        error=abs((p[third]-p[r])*100-433.832)+abs((p[fifth]-p[r])*100-701.955)*2
        if error>25 or len({r,third,fifth})<3:continue
        possible=[]
        for v in range(32):
            if v in (r,third,fifth) or not 0<p[v]-p[r]<25:continue
            interval=((p[v]-p[r])*100)%1200
            err,target=min((abs(interval-t),t) for t in (968.826,1088.269))
            if err<40:possible.append((err+max(0,p[v]-p[r]-12)*.4,v,target))
        seventh=min(possible)[1] if possible else None
        result.append(dict(root=r,triad=[r,third,fifth],seventh=seventh,error=error))
    # One representative per distinct root pitch; favor sampled wind/plucked colors later.
    unique={}
    for x in result:unique.setdefault(round(p[x['root']],3),x)
    return sorted(unique.values(),key=lambda x:p[x['root']])

def compose():
    arrival_piece.SEED=SEED
    s=arrival_piece.compose();pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
    # New chamber colors for two formerly wavetable-synth lines.
    for v,program,name in [(12,69,'English horn'),(24,60,'French horn')]:
        s['voices'][v]['sound']={'engine':'FluidSynth','name':name,'family':'wind','program':program}
        s['voices'][v]['new_calibration']=True
    cut=14*288
    s['notes']=[n for n in s['notes'] if n['start_tick']<cut]
    s['unsplit_events']=[e for e in s['unsplit_events'] if e['start']<cut]
    s['consonance_highlights']=[];s['hocket_routes']=[];s['chamber_studies']=[]
    s['strategy_descriptions'].update(DESC)
    pending=[[] for _ in range(32)]
    def add(v,t,d,vel,section,tag,role):
        if d<3 or t>=288:return
        start=section*288+round(t);end=section*288+min(288,round(t+d))
        pending[v].append(dict(voice=v,start=start,end=end,velocity=max(24,min(100,round(vel))),section=section,strategy=tag,role=role))
    for idx,tag in enumerate(FORM):
        si=idx+14;rng=random.Random(SEED+si*97);base=si*288
        p=pitches[s['harmonies'][si*4]['chord']];choices=sonorities(p)
        assert len(choices)>=4
        # Keep a root for a whole study, returning to it after contrasting answers.
        low=[c for c in choices if 48<=p[c['root']]<=67]
        A=copy.deepcopy(low[(idx//2)%len(low)])
        options=[c for c in choices if 3<p[c['root']]-p[A['root']]<15]
        B=copy.deepcopy(options[(idx*3)%len(options)] if options else choices[-1])
        # Disjoint equivalent endpoints where two chord families meet.
        used=set(A['triad']+([A['seventh']] if A['seventh'] is not None else []))
        for j,v in enumerate(B['triad']):
            alternatives=[x for x in range(32) if abs(p[x]-p[v])<.001 and x not in used]
            if alternatives:B['triad'][j]=alternatives[-1]
        s['form'][si]['strategies']=[tag]
        roots=[A,B]
        reserved=set(A['triad']+B['triad'])|{c['seventh'] for c in roots if c['seventh'] is not None}
        # Melody is a hocket of stable one-pitch voices: retain a scale-like subset
        # in actual register and avoid accompaniment voices where equivalents exist.
        def scale(lo,hi):
            candidates=sorted(range(32),key=lambda v:(p[v],v in reserved,v))
            out=[]
            for v in candidates:
                if not lo<=p[v]<=hi:continue
                if out and (p[v]-p[out[-1]])*100<75:continue
                if out and (p[v]-p[out[-1]])*100>350:continue
                out.append(v)
            if len(out)<4:
                out=[]
                for v in candidates:
                    if lo-5<=p[v]<=hi+5 and (not out or (p[v]-p[out[-1]])*100>75):out.append(v)
            return out
        upper=scale(p[A['root']]+7,p[A['root']]+21)
        lower=scale(p[A['root']]-1,p[A['root']]+12)
        def line(route,start,pattern,durations,vel,role,reverse=False,transpose=0):
            t=start;route=route[::-1] if reverse else route
            for j,(degree,d) in enumerate(zip(pattern,durations)):
                if t>=288:break
                v=route[(degree+transpose)%len(route)]
                arch=math.sin(math.pi*j/max(1,len(pattern)-1))
                add(v,t,min(d-2,288-t),vel+10*arch-(6 if j==len(pattern)-1 else 0),si,tag,role)
                t+=d
        motif=[0,1,3,2,1,2,0];rhythm=[12,6,18,12,12,12,24] # 2-bar sentence
        answer=[3,2,1,2,0,1,0];answer_rhythm=[18,6,12,12,12,12,24]
        def hold(c,t,d,vel=44,seventh=False):
            for j,v in enumerate(c['triad']):add(v,t,d,vel-j*4,si,tag,'triad accompaniment')
            if seventh and c['seventh'] is not None:add(c['seventh'],t+6,max(3,d-6),vel-7,si,tag,'seventh')
        def broken(c,t,length,vel=43,step=24):
            route=c['triad'];j=0
            while t<length:
                add(route[j%3],t,min(step-3,length-t),vel+[2,-8,-3][j%3],si,tag,'broken triad');t+=step;j+=1
        if tag in ('cantabile','melody_and_bells'):
            if tag=='cantabile':
                hold(A,0,90,43);hold(A,108,78,38);hold(B,204,78,44)
            else:broken(A,0,192,42);broken(B,192,288,40,step=12)
            line(upper,0,motif,rhythm,75,'melody')
            line(upper,96,answer,answer_rhythm,69,'melody',transpose=1)
            line(upper,192,[0,1,2,1,0],[12,12,24,12,36],70,'melody')
            line(lower,54,[0,1,2,1],[12,12,12,36],48,'countermelody',reverse=True)
            line(lower,174,[0,1,2],[12,12,48],49,'countermelody')
        elif tag in ('triad_residence','seventh_residence'):
            seven=tag=='seventh_residence'
            hold(A,0,90,60,seven);hold(A,108,78,48,seven)
            for j,v in enumerate(A['triad']):add(v,192+j*12,82-j*12,62-j*8,si,tag,'triad unfolding')
            if seven and A['seventh'] is not None:add(A['seventh'],186,90,48,si,tag,'seventh')
            line(upper,30,[0,1,2,1,0],[12,12,24,12,36],68,'melodic gloss')
            line(upper,150,[2,1,0],[12,12,48],59,'melodic gloss')
        elif tag=='seventh_dialogue':
            for t,c in [(0,A),(72,B),(144,A),(216,B)]:
                hold(c,t,64,53,True)
                line(upper if c is A else lower,t+12,[0,1,2,1],[12,6,18,24],62,'reply',reverse=c is B)
        elif tag=='layered_trios':
            hold(A,0,132,48,True);broken(B,12,144,55,12)
            hold(B,144,132,47,True);broken(A,156,288,51,12)
            line(upper,36,[0,1,2,1],[12,12,24,36],70,'foreground')
            line(lower,180,[2,1,0],[12,24,48],62,'foreground')
        elif tag in ('contrary_invention','two_part_canon'):
            hold(A,0,132,32);hold(B,156,126,34)
            for t in (0,96,192):
                line(upper,t,motif,rhythm,70,'first contrapuntal line',reverse=t==96)
                if tag=='contrary_invention':line(lower,t+12,answer,[12,12,18,6,24,12,12],62,'second contrapuntal line',reverse=t!=96)
                else:line(lower,t+12,motif,rhythm,59,'answering canon')
        elif tag=='root_madrigal':
            line(A['triad'],0,[0,1,2,1,0],[12,12,24,12,36],71,'first root sentence')
            line(B['triad'],84,[0,1,2,1,0],[12,12,24,12,36],67,'second root sentence')
            line(A['triad'],180,[0,1,2,1,0],[12,12,24,12,48],65,'first root sentence')
            line(B['triad'],192,[2,1,0,1],[18,6,24,48],58,'second root sentence')
            if B['seventh'] is not None:add(B['seventh'],204,72,42,si,tag,'held seventh')
        elif tag=='sighing_duet':
            hold(A,0,132,38);hold(B,156,126,37)
            for t in (0,96,192):
                line(upper,t,[3,2,1,2,0],[12,24,12,12,36],69,'upper sigh')
                line(lower,t+24,[0,1,2,1],[12,12,24,36],59,'lower answer',reverse=True)
        elif tag=='passacaglia':
            for t in range(0,264,48):
                add(A['triad'][0],t,42,58 if t%96==0 else 47,si,tag,'bass ground')
                add(A['triad'][2],t+24,20,35,si,tag,'bass fifth')
            for j,t in enumerate((0,96,192)):line(upper,t,motif if j!=1 else answer,rhythm,72-j*3,'varying melody',transpose=j%2)
            line(lower,60,[0,1,2],[12,12,48],47,'inner answer')
        elif tag=='farewell':
            hold(A,0,60,42,True);hold(B,108,72,33,True)
            line(upper,24,[2,1,0],[12,24,36],59,'remembered melody')
            line(lower,150,[0,1,0],[12,24,48],45,'remembered reply')
            hold(A,240,46,29)
        study=dict(section=si+1,start_seconds=base*.05,texture=tag,root_voices=[A['root']+1,B['root']+1],triad_voices=[[v+1 for v in c['triad']] for c in roots],seventh_voices=[None if c['seventh'] is None else c['seventh']+1 for c in roots])
        s['chamber_studies'].append(study)
        for c in roots:
            voices=c['triad']+([c['seventh']] if c['seventh'] is not None else [])
            s['consonance_highlights'].append(dict(section=si+1,start_tick=base,chord=s['harmonies'][si*4]['chord'],voices=[v+1 for v in voices],label='sharp-third triad'+(' with seventh' if len(voices)==4 else ''),root_midi=p[c['root']],intervals_cents=[round(((p[v]-p[c['root']])*100)%1200,3) for v in voices]))
    # Resolve shared instrument ownership by shortening an interrupted note.
    for v,events in enumerate(pending):
        events.sort(key=lambda e:(e['start'],-e['velocity']));unique=[]
        for e in events:
            if unique and unique[-1]['start']==e['start']:continue
            unique.append(e)
        for j,e in enumerate(unique):
            e['end']=min(e['end'],unique[j+1]['start'] if j+1<len(unique) else s['total_ticks'])
            if e['end']-e['start']<3:continue
            s['unsplit_events'].append(e)
            for hi,h in enumerate(s['harmonies']):
                a=max(e['start'],h['start']);b=min(e['end'],h['end'])
                if b>a:s['notes'].append(dict(voice=v,start_tick=a,duration_ticks=b-a,pitch=pitches[h['chord']][v],velocity=e['velocity'],section=e['section'],strategy=e['strategy'],role=e['role'],harmony=hi))
    s['dynamic_envelope']['section_center_db'][14:]=[-9,-12,-8,-6,-10,-13,-7,-15,-9,-13,-5,-8,-15,-7,-10,-4,-12,-6,-13,-16,-7,-10,-15,-18,-26]
    for f,db in zip(s['form'],s['dynamic_envelope']['section_center_db']):f['dynamic_db']=db
    s['notes'].sort(key=lambda n:(n['voice'],n['start_tick']))
    s['seed']=SEED;s['title']='Calcutta: Small Inventions'
    assert not any('reggae' in n['strategy'] for n in s['notes'])
    s['strategy_descriptions']={k:v for k,v in s['strategy_descriptions'].items() if k in {n['strategy'] for n in s['notes']}}
    for v in range(32):
        own=[n for n in s['notes'] if n['voice']==v];assert own
        assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
    return s
if __name__=='__main__':
    root=Path('calcutta_inventions');root.mkdir(exist_ok=True)
    s=compose();(root/'score.json').write_text(json.dumps(s,indent=2));print(len(s['notes']),'notes;',len(s['chamber_studies']),'chamber studies; no reggae')
