"""Thirteen interacting orchestration strategies over Calcutta's complete progression."""
import copy,json,math,random,collections
from pathlib import Path
SEED=202610171717
FORM=[['breathing_chorale'],['antiphonal_choirs'],['sustained_arch'],['reggae_layers'],['timbre_relay'],['antiphonal_choirs'],['pillars_and_lace'],['rhythmic_canon'],['hocket_braid'],['sustained_arch'],['reggae_layers','timbre_relay'],['diminishing_echoes'],['breathing_chorale'],['solo_and_tutti'],['rhythmic_canon','pillars_and_lace'],['timbre_relay'],['antiphonal_choirs'],['hocket_braid'],['rotating_cantus'],['convergence_fan'],['sustained_arch'],['diminishing_echoes'],['reggae_layers'],['solo_and_tutti'],['pillars_and_lace','timbre_relay'],['rhythmic_canon'],['antiphonal_choirs'],['breathing_chorale'],['reggae_layers','hocket_braid'],['rotating_cantus'],['sustained_arch'],['diminishing_echoes','timbre_relay'],['solo_and_tutti'],['hocket_braid'],['antiphonal_choirs','pillars_and_lace'],['breathing_chorale'],['reggae_layers'],['sustained_arch'],['closing_apertures']]
DB=[-14,-10,-8,-5,-12,-7,-15,-11,-9,-16,-7,-10,-12,-4,-6,-13,-5,-8,-14,0,-18,-14,-10,-5,-9,-7,-3,-8,-4,-12,-16,-10,-3,-6,-2,-8,-5,-14,-22]
DESCRIPTIONS={
 'breathing_chorale':'Common long-short phrases and shared breaths; the voices articulate as one body.',
 'antiphonal_choirs':'Left and right choirs trade questions and answers, occasionally overlapping at the hinge.',
 'sustained_arch':'Long held tones enter in waves, overlap, and withdraw; short gestures appear through the held texture.',
 'reggae_layers':'Sparse bass pillars, middle-register offbeat chords, and exposed upper-register responses interlock.',
 'timbre_relay':'A line travels through changing pitch positions and instruments, over a very quiet sustained floor.',
 'pillars_and_lace':'Slow sustained pillars support sparse, individually exposed phrases.',
 'rhythmic_canon':'Four choirs pass the same rhythmic sentence at staggered quarter-note offsets.',
 'hocket_braid':'Three choirs divide one composite phrase; no one choir carries all its attacks.',
 'diminishing_echoes':'A phrase passes through four choirs with progressively quieter answers and longer final sustains.',
 'solo_and_tutti':'A few speakers ask expressive questions; the ensemble answers with short punctuation or a long assent.',
 'rotating_cantus':'A sustained foreground voice rotates among instruments while the others provide sparse responses.',
 'convergence_fan':'A one-time central accumulation: entrances spread into a full choir, unite, then fall away.',
 'closing_apertures':'A one-time coda of exposed duos and diminishing held fragments with clear spaces between them.'}

def compose():
    old=json.loads(Path('calcutta_full/score.json').read_text());pitch_source=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
    score={k:copy.deepcopy(old[k]) for k in ['bpm','duration_seconds','total_ticks','harmonies','voices','near_unison_pairs']}
    score.update(seed=SEED,form=[],notes=[],strategy_descriptions=DESCRIPTIONS)
    pending=[[] for _ in range(32)]
    for si,modes in enumerate(FORM):
        rng=random.Random(SEED+si*1009);base=si*288
        pitch0=pitch_source[score['harmonies'][si*4]['chord']]
        ranked=sorted(range(32),key=lambda v:(pitch0[v],v));spatial=sorted(range(32),key=lambda v:score['voices'][v]['pan'])
        # Rotate responsibility: repeated strategies use different speakers and choirs.
        rotation=(si*7)%32;rotated=ranked[rotation:]+ranked[:rotation]
        def add(v,t,d,vel,tag):
            t=round(t);d=round(d)
            if d<3 or t>=288 or t<0:return
            pending[v].append(dict(start=base+t,end=base+min(288,t+d),velocity=max(24,min(112,round(vel))),section=si,strategy=tag))
        def chord(group,t,d,vel,tag):
            for v in group:add(v,t,d,vel+rng.randint(-3,3),tag)
        def sentence(group,t,vel,tag,variant=0):
            # Short rhetoric ending in a sustained word; mostly quarter-note attacks.
            motif=[(0,10),(12,22),(36,34)] if variant%2==0 else [(0,22),(24,10),(36,46)]
            for off,d in motif:chord(group,t+off,d,vel+(5 if off==0 else -5 if off==36 else 0),tag)
        def steady(v):
            p=score['voices'][v]['sound'];return p['engine']!='FluidSynth' or p.get('program') in (16,19,59,68,70,71,73,74,75)
        def strategy(tag,pool):
            P=[v for v in ranked if v in pool];R=[v for v in rotated if v in pool];n=len(P)
            if not n:return
            S=[v for v in spatial if v in pool];a=S[:(n+1)//2];b=S[(n+1)//2:]
            if tag=='breathing_chorale':
                for start,vel in [(0,66),(96,79),(204,61)]:
                    chord(P,start,34,vel,tag);chord(P,start+48,34 if start<200 else 28,vel-10,tag)
            elif tag=='antiphonal_choirs':
                sentence(a,0,80,tag,0);sentence(b,72,68,tag,1);sentence(a,156,72,tag,1);sentence(b,228,82,tag,0)
                chord(P,276,10,66,tag)
            elif tag=='sustained_arch':
                for j,v in enumerate(R):
                    entry=(j%8)*6;dur=132 if steady(v) else 72
                    add(v,entry,dur,54+(j%4)*4,tag)
                    add(v,168+(j%6)*6,84-(j%3)*6,48,tag)
                for j,v in enumerate(R[::5]):sentence([v],84+(j%3)*12,72,tag,j)
            elif tag=='reggae_layers':
                low=P[:max(2,n//4)];mid=P[max(2,n//4):max(3,3*n//4)];high=P[max(3,3*n//4):]
                for bar in range(6):
                    t=bar*48;chord(low,t,21,76,tag)
                    if bar%2==0:chord(low,t+24,21,65,tag)
                    for off in (6,18,30,42):chord(mid,t+off,4 if bar%2 else 5,58+(6 if off==30 else 0),tag)
                    if high:
                        v=high[bar%len(high)];add(v,t+12,21,83,tag)
                        if bar%2:add(high[(bar+2)%len(high)],t+36,10,65,tag)
            elif tag=='timbre_relay':
                floor=[v for v in R if steady(v)][:max(2,n//8)]
                chord(floor,0,138,35,tag);chord(floor,156,126,32,tag)
                route=P+P[::-1]
                for j,t in enumerate(range(0,276,12)):
                    v=route[(j+si)%len(route)];add(v,t,10 if j%4!=3 else 22,78 if j%4==0 else 60,tag)
            elif tag=='pillars_and_lace':
                pillars=[v for v in P if steady(v)][::2] or P[::4];lace=[v for v in R if v not in pillars]
                chord(pillars,0,90,57,tag);chord(pillars,108,78,52,tag);chord(pillars,204,78,64,tag)
                for j,v in enumerate(lace):
                    t=12+(j*24)%216;add(v,t,10,72,tag);add(v,t+12,34,54,tag)
            elif tag=='rhythmic_canon':
                groups=[R[i::4] for i in range(4)]
                for cycle in (0,120):
                    for j,g in enumerate(groups):sentence(g,cycle+j*12,78-j*5,tag,j%2)
                chord(P,264,22,56,tag)
            elif tag=='hocket_braid':
                groups=[R[i::3] for i in range(3)]
                for phrase in (0,108,216):
                    for j,off in enumerate((0,12,24,48,60)):
                        g=groups[j%3];chord(g,phrase+off,10 if j<4 else 22,76 if off%24==0 else 53,tag)
            elif tag=='diminishing_echoes':
                groups=[R[i::4] for i in range(4)]
                for phrase in (0,144):
                    for j,g in enumerate(groups):
                        t=phrase+j*24;chord(g,t,10,88-j*12,tag);chord(g,t+12,34,75-j*12,tag)
            elif tag=='solo_and_tutti':
                speakers=R[:max(2,n//8)];listeners=[v for v in P if v not in speakers]
                for j,t in enumerate((0,96,192)):
                    sentence([speakers[j%len(speakers)]],t,90,tag,j)
                    chord(listeners,t+72,16 if j<2 else 22,63 if j<2 else 75,tag)
                for v in listeners[::4]:add(v,24,132,30,tag)
            elif tag=='rotating_cantus':
                singers=[v for v in R if steady(v)][:4] or R[:4]
                for j,t in enumerate((0,72,144,216)):
                    v=singers[j%len(singers)];add(v,t,64,86-j*4,tag)
                    answer=[x for x in R[j::4] if x!=v];chord(answer,t+48,16,45,tag)
            elif tag=='convergence_fan':
                for j,v in enumerate(R):
                    t=(j//4)*12;add(v,t,156-t,48+j,tag)
                chord(P,168,10,96,tag);chord(P,192,70,91,tag)
                for j,v in enumerate(R[::-1]):add(v,264+(j%4)*6,18-(j%3)*3,52-j//2,tag)
            elif tag=='closing_apertures':
                for j,t in enumerate((0,60,132,216)):
                    pair=R[j*3:j*3+2];chord(pair,t,46 if j<3 else 64,64-j*9,tag)
                for j,v in enumerate(R[12:]):add(v,12+(j%6)*36,24 if not steady(v) else 46,29,tag)
        if len(modes)==1:strategy(modes[0],list(range(32)))
        else:
            # Distinct voice ownership lets two strategies coexist without collisions.
            strategy(modes[0],ranked[::2]);strategy(modes[1],ranked[1::2])
        score['form'].append(dict(section=si+1,start_seconds=base*.05,end_seconds=(base+288)*.05,start_bar=si*6+1,bars=6,strategies=modes,dynamic_db=DB[si]))
    # Resolve rhetorical interruptions within a voice before changing its chord pitch.
    raw=[]
    for v,events in enumerate(pending):
        events.sort(key=lambda e:(e['start'], -e['velocity']))
        unique=[]
        for event in events:
            if unique and event['start']==unique[-1]['start']:continue
            unique.append(event)
        for j,e in enumerate(unique):
            stop=min(e['end'],unique[j+1]['start'] if j+1<len(unique) else score['total_ticks'])
            if stop-e['start']<3:continue
            raw.append(dict(voice=v,start=e['start'],end=stop,velocity=e['velocity'],section=e['section'],strategy=e['strategy']))
    for e in raw:
        for hi,h in enumerate(score['harmonies']):
            start=max(e['start'],h['start']);stop=min(e['end'],h['end'])
            if stop>start:score['notes'].append(dict(voice=e['voice'],start_tick=start,duration_ticks=stop-start,pitch=pitch_source[h['chord']][e['voice']],velocity=e['velocity'],section=e['section'],strategy=e['strategy'],harmony=hi))
    score['notes'].sort(key=lambda n:(n['voice'],n['start_tick']))
    score['dynamic_envelope']=dict(section_center_db=DB,interpolation='linear decibels between section centers, with final fade to -34 dB')
    score['unsplit_events']=raw
    for v in range(32):
        own=[n for n in score['notes'] if n['voice']==v];assert own
        assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
    assert len(FORM)==39 and len(DESCRIPTIONS)>=10
    assert sum('convergence_fan' in x for x in FORM)==1
    assert sum('closing_apertures' in x for x in FORM)==1
    return score
if __name__=='__main__':
    s=compose();Path('calcutta_dialogues/score.json').write_text(json.dumps(s,indent=2));print(len(s['notes']),'segments;',len(s['unsplit_events']),'attacks;',len(DESCRIPTIONS),'strategies')
