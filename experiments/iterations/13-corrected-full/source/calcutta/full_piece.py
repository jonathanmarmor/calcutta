"""Twelve bars of simpler, strongly metrical phrasing and an acoustic-heavy palette."""
import json,random,math
from pathlib import Path
import numpy as np
SEED=2026101744

def compose():
    prev=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())
    template=json.loads(Path('composition_phrases_preview/phrased_preview.json').read_text())
    oldpalette=json.loads(Path('composition_32_voices_v3/palette.json').read_text())
    gm=[('Grand piano',0,'piano'),('Bright piano',1,'piano'),('Rhodes electric piano',4,'electric keys'),('FM electric piano',5,'tine'),('Harpsichord',6,'plucked keys'),('Celesta',8,'celesta'),('Vibraphone',11,'metal'),('Tubular bells',14,'bells'),('Drawbar organ',16,'organ'),('Church organ',19,'organ'),('Nylon guitar',24,'guitar'),('Steel string guitar',25,'guitar'),('Clean jazz guitar',26,'guitar'),('Clean electric guitar',27,'guitar'),('Acoustic bass',32,'bass'),('Fingered electric bass',33,'bass'),('Flute',73,'flute'),('Recorder',74,'recorder'),('Pan pipes',75,'pan pipes'),('Clarinet',71,'reed'),('Oboe',68,'reed'),('Bassoon',70,'reed'),('Steel pans',114,'steel pans'),('Muted trumpet',59,'brass')]
    palette=[dict(engine='FluidSynth',name=name,program=program,family=family,patch_index=None,sample_based=True) for name,program,family in gm]
    for name in ['Warm transistor','Hollow square','Nasal ribbon','Sine harmonium','Liquid glass','Vowel prism','FM clarinet','Pure wooden flute']:
        i=next(i for i,p in enumerate(oldpalette) if p['name']==name);p=dict(oldpalette[i],patch_index=i,sample_based=False);palette.append(p)
    assert len(palette)==32
    rng=random.Random(SEED);order=list(range(32));rng.shuffle(order);edges=prev['near_unison_pairs'];med=np.median(np.array(prev['pitches'])[:3],axis=0)
    def cost(order):
        result=sum(120 for i,j in edges if palette[order[i]]['family']==palette[order[j]]['family'])
        for v,k in enumerate(order):
            p=palette[k];prog=p.get('program')
            if prog in (32,33,70):result+=.05*max(0,med[v]-72)**2
            if prog in (73,74,75,114):result+=.03*max(0,60-med[v])**2
        return result
    c=cost(order);best=order[:];bestc=c
    for it in range(25000):
        i,j=rng.sample(range(32),2);order[i],order[j]=order[j],order[i];n=cost(order);temp=max(.03,12*(1-it/25000))
        if n<c or rng.random()<math.exp(min(0,(c-n)/temp)):
            c=n
            if c<bestc:best,bestc=order[:],c
        else:order[i],order[j]=order[j],order[i]
    order=best;assert all(palette[order[i]]['family']!=palette[order[j]]['family'] for i,j in edges)
    harmonies=[];total=0
    for i in range(39):
        a,b=(i,i+1) if i%2==0 else (i+1,i)
        for chord,bars in [(a,2),(b,2),(a,1),(b,1)]:
            harmonies.append(dict(chord=chord,start=total,end=total+bars*48,bars=bars));total+=bars*48
    notes=[];voices=[]
    def weight(t):
        return 12 if t%48==0 else 7 if t%48==24 else 2 if t%12==0 else .25
    for v in range(32):
        vr=random.Random(SEED+v*913);floor=0;phrases=[];pid=0
        while floor<total:
            # Anchor the phrase to a quarter-note beat, especially 1 or 3.
            first=((floor+11)//12)*12
            candidates=[x for x in range(first,min(total,first+37),12)]
            if not candidates:break
            anchor=vr.choices(candidates,weights=[weight(t) for t in candidates])[0]
            phrase_end=min(total,anchor+vr.choice([24,36,48,60,72]))
            phrase_start=anchor
            if anchor-floor>=6 and vr.random()<.33:
                pickup=3 if vr.random()<.12 else 6
                t=anchor-pickup;phrase_start=t
                onset_note=(t,pickup-1,vr.randint(28,44),'pickup')
                pending=[onset_note]
            else:pending=[]
            t=anchor
            while t<phrase_end:
                remaining=phrase_end-t
                # Rhythmic units begin on quarter beats. Eighth pairs resolve to the next beat.
                motifs=[[12],[24],[6,6],[18,6],[12,6,6]]
                valid=[m for m in motifs if sum(m)<=remaining]
                if not valid:break
                priors={(12,):5.5,(24,):3.0,(6,6):.9,(18,6):.45,(12,6,6):.35}
                motif=vr.choices(valid,weights=[priors[tuple(m)] for m in valid])[0]
                for duration in motif:
                    position=(t-anchor)/max(1,phrase_end-anchor)
                    if t%12:
                        vel=vr.randint(30,52)  # subdivisions remain deliberately unstressed
                    else:
                        accent=30 if t%48==0 else 20 if t%48==24 else 0
                        vel=round(47+accent+23*math.sin(math.pi*position)+vr.uniform(-9,9))
                    final=t+duration>=phrase_end
                    if final:vel-=vr.randint(5,15)
                    vel=max(26,min(116,vel))
                    articulation=vr.choices(['tenuto','ordinary','staccato'],[7,2.5,.5])[0]
                    gate=max(2,round(duration*({'tenuto':.97,'ordinary':.86,'staccato':.65}[articulation])))
                    pending.append((t,gate,vel,articulation));t+=duration
            for onset,gate,vel,art in pending:
                for hi,h in enumerate(harmonies):
                    start=max(onset,h['start']);stop=min(onset+gate,h['end'])
                    if stop>start:notes.append(dict(voice=v,start_tick=start,duration_ticks=stop-start,pitch=prev['pitches'][h['chord']][v],velocity=vel,phrase=pid,harmony=hi,articulation=art))
            if pending:phrases.append(dict(start_tick=phrase_start,end_tick=max(t+g for t,g,vel,art in pending),anchor_tick=anchor))
            floor=phrase_end+vr.choice([6,12,18]);pid+=1
        voices.append(dict(voice=v+1,branch=prev['voices'][v]['branch'],pan=prev['voices'][v]['pan'],sound=palette[order[v]],patch_index=palette[order[v]]['patch_index'],phrases=phrases))
    repairs=0
    for v in range(32):
        for hi,h in enumerate(harmonies):
            if any(n['voice']==v and n['harmony']==hi for n in notes):continue
            notes.append(dict(voice=v,start_tick=h['start']+12,duration_ticks=10,pitch=prev['pitches'][h['chord']][v],velocity=64,phrase=-1,harmony=hi,articulation='tenuto'));repairs+=1
    notes.sort(key=lambda n:(n['voice'],n['start_tick']))
    for v in range(32):
        own=[n for n in notes if n['voice']==v]
        assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(own,own[1:]))
    return dict(seed=SEED,bpm=100,duration_seconds=total*.05,total_ticks=total,harmonies=harmonies,voices=voices,notes=notes,near_unison_pairs=edges,coverage_repairs=repairs)
if __name__=='__main__':
    s=compose()
    old=json.loads(Path('rhythm_simple/score.json').read_text())
    for v in range(32):
        for key in ['sound','patch_index','pan','branch']:s['voices'][v][key]=old['voices'][v][key]
        if s['voices'][v]['sound'].get('program') in (14,26,27):s['voices'][v]['sound']['sample_bank']='GeneralUser GS 2.0.3'
    Path('calcutta_full/score.json').write_text(json.dumps(s,indent=2));print('Generated',len(s['notes']),'notes; coverage repairs',s['coverage_repairs'])
