"""A dense harmonic exposition, opening gradually into Prisms' varied textures."""
import json,random,math,collections
from pathlib import Path
import prism_piece as prism
SEED=202610171804
DENSE_SECTIONS=12
TRANSITION_SECTIONS=2
DESCRIPTIONS={
 'arrival_chorale':'All 32 pitches arrive together after a shared breath; a sustained chord opens into a softer repeated answer.',
 'harmonic_breaths':'Dense sustained choirs take turns inside each harmony, joining at every harmonic arrival.',
 'arrival_waves':'Every new chord enters in a close wave; a few quarter-note pulses animate the sustained ensemble.',
 'opening_aperture':'The full chord announces each change, then thins to a few voices and exposed lines before its next arrival.'}

def compose():
    prism.SEED=SEED
    score=prism.compose()
    pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
    cutoff=(DENSE_SECTIONS+TRANSITION_SECTIONS)*288
    score['notes']=[n for n in score['notes'] if n['start_tick']>=cutoff]
    score['unsplit_events']=[e for e in score['unsplit_events'] if e['start']>=cutoff]
    score['consonance_highlights']=[e for e in score['consonance_highlights'] if e['start_tick']>=cutoff]
    score['hocket_routes']=[e for e in score['hocket_routes'] if e['start_tick']>=cutoff]
    score['strategy_descriptions'].update(DESCRIPTIONS)
    seed=random.Random(SEED)
    # Fixed, gentle color differences across the opening; no note/stem auto-leveling.
    color=[seed.uniform(.49,.84) for _ in range(32)]
    for v in seed.sample(list(range(32)),8):color[v]=seed.uniform(.88,1.04)
    arrivals=[]
    def emit(v,start,end,vel,section,tag,harmony):
        if end-start<3:return
        vel=round(vel*color[v]**(1/1.7))
        vel=max(24,min(102,vel))
        score['notes'].append(dict(voice=v,start_tick=start,duration_ticks=end-start,pitch=pitches[harmony['chord']][v],velocity=vel,section=section,strategy=tag,harmony=harmony['index']))
        score['unsplit_events'].append(dict(voice=v,start=start,end=end,velocity=vel,section=section,strategy=tag))
    for si in range(DENSE_SECTIONS+TRANSITION_SECTIONS):
        rng=random.Random(SEED+si*733)
        tag=['arrival_chorale','harmonic_breaths','arrival_waves','arrival_chorale'][si%4] if si<DENSE_SECTIONS else 'opening_aperture'
        score['form'][si]['strategies']=[tag]
        # Cadential shape over each A–B–A–B harmonic group, with different section arcs.
        phrase_shape=[74,83,64,53] if si%2==0 else [55,67,82,61]
        for k,h0 in enumerate(score['harmonies'][si*4:si*4+4]):
            h=dict(h0,index=si*4+k);start=h['start'];end=h['end'];L=end-start
            ranked=sorted(range(32),key=lambda v:pitches[h['chord']][v]);groups=[ranked[j::4] for j in range(4)]
            level=phrase_shape[k]+rng.randint(-3,3)
            for v in range(32):
                group=next(j for j,g in enumerate(groups) if v in g)
                if tag=='arrival_chorale':
                    # One chord-sized phrase with a long first word and a soft cadence.
                    split=start+(60 if L==96 else 30)
                    emit(v,start,split-3,level,si,tag,h)
                    emit(v,split,end-3,level-19+(3 if group==si%4 else 0),si,tag,h)
                elif tag=='harmonic_breaths':
                    # Shared arrival; staggered breaths inside a dense sustained chord.
                    hinge=start+(48 if L==96 else 24)
                    emit(v,start,hinge-3,level,si,tag,h)
                    reentry=hinge+(group%2)*6
                    emit(v,reentry,end-3,level-13+group*2,si,tag,h)
                elif tag=='arrival_waves':
                    enter=start+(group%2)*3
                    pulse_group=(si+k)%4
                    if group==pulse_group:
                        for j,t in enumerate(range(start,end-6,12)):
                            emit(v,max(t,enter),min(t+10,end-3),level+[-8,2,-12,-19][j%4],si,tag,h)
                    else:emit(v,enter,end-3,level-6,si,tag,h)
                else:
                    # Transition: retain a clear complete arrival, then expose the inside.
                    hold=24 if L==96 else 12
                    emit(v,start,start+hold-3,level-7,si,tag,h)
                    if group==(k+si)%4:
                        emit(v,start+hold,end-3,level-22,si,tag,h)
                    elif v in ranked[::8]:
                        t=start+hold+6+(ranked.index(v)//8)*6
                        emit(v,t,min(t+16,end-3),level-12,si,tag,h)
            arrivals.append(dict(start_tick=start,chord=h['chord'],section=si+1,strategy=tag))
    score['harmonic_arrivals']=arrivals
    score['opening_design']=dict(dense_until_seconds=DENSE_SECTIONS*14.4,transition_until_seconds=cutoff*.05,voices_at_each_arrival=32,breath_before_change_seconds=.15)
    score['dynamic_envelope']['section_center_db'][:14]=[-11,-9,-7,-10,-6,-9,-5,-8,-6,-10,-7,-11,-13,-12]
    for f,db in zip(score['form'],score['dynamic_envelope']['section_center_db']):f['dynamic_db']=db
    score['seed']=SEED
    score['notes'].sort(key=lambda n:(n['voice'],n['start_tick']))
    for v in range(32):
        own=[n for n in score['notes'] if n['voice']==v];assert own
        assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
    # The full harmonic membership is present at every opening arrival.
    for a in arrivals:
        assert len({n['voice'] for n in score['notes'] if a['start_tick']<=n['start_tick']<=a['start_tick']+3})==32
    return score
if __name__=='__main__':
    out=Path('calcutta_arrivals');out.mkdir(exist_ok=True)
    s=compose();(out/'score.json').write_text(json.dumps(s,indent=2))
    print('Notes',len(s['notes']),'complete harmonic arrivals',len(s['harmonic_arrivals']),'; opening design',s['opening_design'])
