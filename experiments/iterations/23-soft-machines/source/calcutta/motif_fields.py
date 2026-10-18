"""Flexible harmonic phrases and smaller progressions inside unchanged Calcutta fields."""
import json,copy,random,math,itertools
from pathlib import Path
from chamber_piece import sonorities
SEED=202610171948
TICK_SECONDS=.05
TEXTURES=['song','interwoven','seventh_garden','two_roots','canon','chord_melody','suspension','quiet_trios','invention','farewell']
DESCRIPTIONS={
 'song':'A returning turning melody above a soft triad; its answer begins before the accompaniment finishes.',
 'interwoven':'Two root families alternate and overlap, with contrary melodic replies and common tones carried through.',
 'seventh_garden':'A slow seventh rests over changing triads; an upper line explores the available nearby pitches.',
 'two_roots':'Two internal chords ask and answer, then their notes interleave in a brief conversation.',
 'canon':'A short motif reappears a quarter note later in another register over a nearly motionless accompaniment.',
 'chord_melody':'A foreground melodic route connects changing internal triads, with soft broken-chord replies.',
 'suspension':'One existing pitch is held while the other chord members change underneath, then the melodic thread answers.',
 'quiet_trios':'Two softly blended trios take turns, with an exposed line emerging between their entries.',
 'invention':'A small ascending subject and a descending answer share unequal rhythmic shapes; the subject returns with a changed ending.',
 'farewell':'Earlier motifs and their two root families return as quiet, widely spaced fragments.'}

def compose():
    rng=random.Random(SEED)
    old=json.loads(Path('calcutta_inventions/score.json').read_text())
    pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
    s={k:copy.deepcopy(old[k]) for k in ['voices','near_unison_pairs']}
    s.update(title='Calcutta: Archipelago',seed=SEED,bpm=100,harmonies=[],form=[],notes=[],unsplit_events=[],internal_progressions=[],strategy_descriptions=DESCRIPTIONS)
    visits=[]
    def visit(chord,beats,texture,group,full=False):visits.append(dict(chord=chord,beats=beats,texture=texture,group=group,full=full))
    # Begin inside the sequence, with a sparse question and a few expressive turns.
    for j,(c,b) in enumerate(zip([2,3,2,3,2,3,2,3,3,4,5,4,3,4,5,4],[6,6,4,4,8,8,3,5,8,4,4,6,4,6,6,10])):
        visit(c,b,['song','two_roots','quiet_trios'][j%3],0,False)
    visit(0,4,'quiet_trios',1,True) # one brief expressive appearance, never the opening center
    for j,(c,b) in enumerate([(1,10),(2,12),(4,14),(3,10),(5,16),(7,12),(6,14),(8,16),(7,6),(9,16),(8,6),(10,18),(11,16),(12,14)]):
        visit(c,b,['interwoven','song','chord_melody','invention'][j%4],1+j//5,c not in (7,8) or j in (5,7))
        if j==9:
            for cc in [6,7,6,7,6,7]:visit(cc,4,'invention',2,False)
        if j==13:
            for cc,bb in zip([9,10,11,10,9,10],[4,4,6,4,4,8]):visit(cc,bb,'canon',3,False)
    for block,start in enumerate(range(13,40,4)):
        group=4+block
        cs=[min(39,start+1),start,min(39,start+2),min(39,start+1),min(39,start+3),min(39,start+2)]
        bs=[16,20,12,6,24,10]
        textures=[['song','interwoven','seventh_garden','canon','two_roots','suspension'],
                  ['quiet_trios','chord_melody','invention','song','seventh_garden','interwoven'],
                  ['canon','seventh_garden','suspension','two_roots','chord_melody','quiet_trios']][block%3]
        seen=set()
        for c,b,tag in zip(cs,bs,textures):
            full=c not in seen;seen.add(c);visit(c,b,tag,group,full)
    for c,b,tag in [(38,10,'suspension'),(39,18,'farewell')]:visit(c,b,tag,11,False)
    # Ensure exactly one complete exposure of every original harmony.
    seen=set()
    for x in visits:
        x['full']=x['full'] and x['chord'] not in seen
        if x['full']:seen.add(x['chord'])
    assert seen==set(range(40))
    cursor=0
    for i,x in enumerate(visits):
        x.update(start=cursor,end=cursor+x['beats']*12,index=i)
        cursor=x['end']
        s['harmonies'].append(dict(chord=x['chord'],start=x['start'],end=x['end'],beats=x['beats'],bars=x['beats']/4,full_presentation=x['full'],texture=x['texture']))
    s['total_ticks']=cursor;s['duration_seconds']=cursor*TICK_SECONDS
    pending=[[] for _ in range(32)]
    def add(v,start,duration,velocity,tag,role,priority=1):
        start=round(start);end=min(cursor,round(start+duration))
        if end-start<3:return
        pending[v].append(dict(voice=v,start=start,end=end,velocity=max(22,min(102,round(velocity))),strategy=tag,role=role,priority=priority))
    def voicelead(a,b,p):
        av=sorted(p[v] for v in a['triad']);bv=sorted(p[v] for v in b['triad'])
        return sum(abs(x-y) for x,y in zip(av,bv))/min(len(av),len(bv))
    previous_chords=None
    for vi,x in enumerate(visits):
        start=x['start'];L=x['end']-start;p=pitches[x['chord']];tag=x['texture']
        candidates=sonorities(p)
        if not candidates:
            # Early collections may not contain the characteristic triad.
            # Explore their closest fifths without inventing a pitch.
            pairs=sorted((abs((p[b]-p[a])*100-701.955),a,b) for a in range(32) for b in range(32) if 3<p[b]-p[a]<10)
            candidates=[dict(root=a,triad=[a,b],seventh=None,error=e) for e,a,b in pairs[:12]]
        unique={}
        for c in candidates:unique.setdefault(tuple(round(p[v],3) for v in c['triad']),c)
        candidates=list(unique.values())
        target=51+(x['group']*3)%18
        A=min(candidates,key=lambda c:abs(p[c['root']]-target)+c['error']*.02)
        if previous_chords and vi%3:
            prior=previous_chords[-1]
            A=min(candidates,key=lambda c:voicelead(prior,c,p)+abs(p[c['root']]-target)*.15+c['error']*.01)
        different=[c for c in candidates if abs(p[c['root']]-p[A['root']])>2]
        B=min(different,key=lambda c:voicelead(A,c,p)+c['error']*.01) if different else A
        different2=[c for c in candidates if c is not A and c is not B]
        C=min(different2,key=lambda c:voicelead(B,c,p)+abs(p[c['root']]-p[A['root']])*.12) if different2 else A
        # A–B–C–A, with unequal lengths, is an internal progression in this field.
        progression=[A,B,C,A] if L>=144 else [A,B,A] if L>=96 else [A,B]
        previous_chords=progression
        # Full collection blooms: postpone them beyond the opening questions.
        full_window=None
        if x['full']:
            a=start+(24 if L>=96 else 0);b=min(x['end']-3,a+(60 if L>=144 else max(30,L//2)))
            full_window=(a,b)
            for v in range(32):
                entry=a+(v%3)*3
                color=.5+.5*((v*7+vi*3)%13)/12
                add(v,entry,b-entry,55*color**(1/1.7),tag,'complete harmony',5)
            x['full_start_tick']=a+6;x['full_end_tick']=b
        def hold(c,t,d,vel=42,seventh=False):
            for j,v in enumerate(c['triad']):add(v,t,d,vel-j*4,tag,'inner chord')
            if seventh and c['seventh'] is not None:add(c['seventh'],t+6,max(3,d-6),vel-5,tag,'seventh',2)
        def chord_changes():
            # Three or four internal changes within a longer unchanged harmony.
            weights=[.31,.24,.28,.17] if len(progression)==4 else [.4,.35,.25] if len(progression)==3 else [.58,.42]
            t=start
            for ci,(c,w) in enumerate(zip(progression,weights)):
                d=round(L*w/6)*6;d=max(6,min(d,x['end']-t))
                if ci==len(progression)-1:d=x['end']-t
                yield c,t,d
                t+=d
        reserved={v for c in progression for v in c['triad']}
        # Deduplicate near unisons; construct an actual-register melodic scale.
        ordered=sorted(range(32),key=lambda v:(p[v],v in reserved,v))
        center=p[A['root']]+8
        route=[]
        for v in ordered:
            if center-3<=p[v]<=center+12 and (not route or (p[v]-p[route[-1]])*100>=75):route.append(v)
        if len(route)<4:
            route=[]
            for v in ordered:
                if 52<=p[v]<=83 and (not route or (p[v]-p[route[-1]])*100>=75):route.append(v)
        route=route or A['triad']
        lower=[]
        for v in ordered:
            if p[A['root']]-2<=p[v]<=p[A['root']]+10 and (not lower or (p[v]-p[lower[-1]])*100>=75):lower.append(v)
        lower=lower or A['triad']
        motif=[0,1,3,2,1,2,0];answer=[3,2,1,2,0,1,0]
        def line(pool,t,pattern,durations,vel,role,reverse=False,offset=0):
            pool=pool[::-1] if reverse else pool
            for j,(degree,d) in enumerate(zip(pattern,durations)):
                if t>=x['end']-3:break
                v=pool[(degree+offset)%len(pool)]
                d=min(d,x['end']-t-1)
                add(v,t,max(3,d-2),vel+9*math.sin(math.pi*j/max(1,len(pattern)-1))-(8 if j==len(pattern)-1 else 0),tag,role,3)
                t+=d
        sparse=vi<9
        for ci,(c,t,d) in enumerate(chord_changes()):
            # A full exposure takes precedence and its listening window is left clear.
            vel=36 if sparse else 41
            if tag in ('song','canon','invention','suspension','seventh_garden'):
                hold(c,t,max(3,d-3),vel,seventh=tag=='seventh_garden')
            elif tag in ('two_roots','quiet_trios','farewell'):
                hold(c,t,max(3,d-6),46 if sparse else 52,seventh=tag=='farewell')
            elif tag in ('interwoven','chord_melody'):
                route2=c['triad'];step=24 if tag=='interwoven' else 12
                for j,tt in enumerate(range(t,t+d-3,step)):
                    add(route2[j%len(route2)],tt,min(step*2-3,t+d-tt-3),45+[0,-8,-3][j%3],tag,'broken inner chord')
                if ci%2==0:hold(progression[(ci+1)%len(progression)],t+12,max(3,d-15),32)
        for cycle,t in enumerate(range(start,x['end']-12,96)):
            if tag in ('song','chord_melody','seventh_garden'):
                line(route,t,motif if cycle%2==0 else answer,[12,6,18,12,12,12,24],71 if not sparse else 66,'melody',offset=cycle%2)
                if not sparse:line(lower,t+54,[0,1,2,1],[12,12,12,36],47,'inner answer',reverse=True)
            elif tag in ('canon','invention'):
                line(route,t,motif,[12,6,18,12,12,12,24],68,'subject')
                line(lower,t+12,motif if tag=='canon' else answer,[12,12,6,18,12,24,12],58,'counterpoint',reverse=tag=='invention')
            elif tag in ('suspension','interwoven'):
                v=A['seventh'] if A['seventh'] is not None else A['triad'][-1]
                add(v,t,min(78,x['end']-t-3),48,tag,'held existing tone',2)
                line(route,t+24,[0,1,2,1,0],[12,12,24,12,36],64,'answering melody')
            elif tag in ('two_roots','quiet_trios'):
                line(route,t+12,[0,1,2,1],[12,12,24,36],60,'small melody',reverse=cycle%2==1)
            elif tag=='farewell':line(route,t+12,[2,1,0],[12,24,48],48,'remembered melody')
        s['internal_progressions'].append(dict(visit=vi+1,chord=x['chord'],start_seconds=start*.05,texture=tag,roots=[c['root']+1 for c in progression],chord_voices=[[v+1 for v in c['triad']] for c in progression],seventh_voices=[None if c['seventh'] is None else c['seventh']+1 for c in progression],voiceleading_mean_semitones=[round(voicelead(a,b,p),4) for a,b in zip(progression,progression[1:])]))
    # Protect full presentations by removing competing solo attacks in their windows.
    windows=[(x['full_start_tick']-6,x['full_end_tick']) for x in visits if x['full']]
    for v,events in enumerate(pending):
        fragments=[]
        for e in events:
            pieces=[(e['start'],e['end'])]
            if e['role']!='complete harmony':
                for a,b in windows:
                    nextpieces=[]
                    for st,en in pieces:
                        if en<=a or st>=b:nextpieces.append((st,en))
                        else:
                            if st<a:nextpieces.append((st,a))
                            if en>b:nextpieces.append((b,en))
                    pieces=nextpieces
            fragments.extend(dict(e,start=a,end=b) for a,b in pieces if b-a>=3)
        fragments.sort(key=lambda e:(e['start'],-e['priority'],-e['velocity']))
        unique=[]
        for e in fragments:
            if unique and e['start']==unique[-1]['start']:continue
            unique.append(e)
        for j,e in enumerate(unique):
            e['end']=min(e['end'],unique[j+1]['start'] if j+1<len(unique) else cursor)
            if e['end']-e['start']<3:continue
            s['unsplit_events'].append(e)
            for hi,h in enumerate(s['harmonies']):
                a=max(e['start'],h['start']);b=min(e['end'],h['end'])
                if b>a:s['notes'].append(dict(voice=v,start_tick=a,duration_ticks=b-a,pitch=pitches[h['chord']][v],velocity=e['velocity'],strategy=e['strategy'],role=e['role'],harmony=hi,section=visits[hi]['group']))
    # Larger phrases gather several revisits and describe their own dynamic arc.
    targets=[-15,-7,-10,-8,-13,-8,-12,-5,-11,-8,-16,-24]
    for group in sorted({x['group'] for x in visits}):
        xs=[x for x in visits if x['group']==group]
        s['form'].append(dict(section=group+1,start_seconds=xs[0]['start']*.05,end_seconds=xs[-1]['end']*.05,start_bar=xs[0]['start']/48+1,bars=(xs[-1]['end']-xs[0]['start'])/48,strategies=list(dict.fromkeys(x['texture'] for x in xs)),dynamic_db=targets[group]))
    s['dynamic_envelope']=dict(section_center_db=[f['dynamic_db'] for f in s['form']],interpolation='linear decibels between phrase centers')
    s['visits']=visits
    s['notes'].sort(key=lambda n:(n['voice'],n['start_tick']))
    assert s['harmonies'][0]['chord']!=0
    for chord in range(40):
        x=next(x for x in visits if x['chord']==chord and x['full']);mid=(x['full_start_tick']+x['full_end_tick'])//2
        assert {n['voice'] for n in s['notes'] if n['start_tick']<=mid<n['start_tick']+n['duration_ticks']}==set(range(32))
    for v in range(32):
        own=[n for n in s['notes'] if n['voice']==v];assert own
        assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
    return s
if __name__=='__main__':
    out=Path('calcutta_archipelago');out.mkdir(exist_ok=True);s=compose()
    (out/'score.json').write_text(json.dumps(s,indent=2))
    print(len(s['notes']),'notes;',len(s['visits']),'visits;',s['duration_seconds'],'seconds; all 40 full presentations verified')
