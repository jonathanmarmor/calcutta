"""Meter-aware, independently phrased 32-voice Calcutta preview."""
import argparse,json,math,random,csv
from pathlib import Path
import numpy as np
import mido
from pedalboard import load_plugin
from mixed_synths import Engines,RATE,save_wav
TICKS=12  # per quarter: sixteenths=3, eighth-triplets=4
SECONDS=.6/TICKS

def strength(t,mode='four'):
    bar=t%48
    base=5.5 if bar==0 else 3.4 if bar==24 else 2.4 if bar%12==0 else 1.1 if bar%6==0 else .42 if bar%3==0 else .3
    if mode=='three-three-two':base+=3.5 if bar%48 in (0,18,36) else 0
    elif mode=='triplet':base+=1.2 if bar%4==0 else 0
    elif mode=='cross-three':base+=2.5 if t%36==0 else 0
    return base

def compose(previous,seed=2026101716):
    rng=random.Random(seed);sounds=previous['voices'];patches=json.loads(Path('composition_32_voices_v3/palette.json').read_text())
    order=[next(i for i,p in enumerate(patches) if p['name']==v['sound']['name'] and p['engine']==v['sound']['engine']) for v in sounds]
    edges=previous['near_unison_pairs'];used=set();swaps=[]
    for _ in range(4000):
        if len(swaps)==8:break
        a,b=rng.sample(range(32),2)
        if a in used or b in used:continue
        order[a],order[b]=order[b],order[a]
        if all(patches[order[i]]['family']!=patches[order[j]]['family'] for i,j in edges):used.update([a,b]);swaps.append([a,b])
        else:order[a],order[b]=order[b],order[a]
    assert len(swaps)==8
    harmonies=[];t=0
    for i in range(5):
        a,b=(i,i+1) if i%2==0 else (i+1,i)
        for chord,bars in [(a,2),(b,2),(a,1),(b,1)]:
            harmonies.append(dict(chord=chord,start=t,end=t+bars*48,bars=bars));t+=bars*48
    total=t;notes=[];voices=[]
    modes=['four','three-three-two','triplet','cross-three','four']
    for v in range(32):
        vr=random.Random(seed+v*271);t=vr.choice([0,3,6,9,12,18,24]);phrases=[];phrase_id=0
        while t<total:
            # Each voice chooses its own phrase onset and extent.
            start=t;length=vr.choice([24,30,36,42,48,60,72]);end=min(total,start+length)
            mode=modes[min(start//288,4)] if vr.random()<.75 else 'four'
            triplet=mode=='triplet' and vr.random()<.7
            phrase_notes=[]
            while t<end:
                remaining=end-t
                options=[4,8,12,16,24] if triplet else [3,6,9,12,18,24]
                options=[x for x in options if x<=remaining]
                if not options:break
                prior={3:1.2,4:1.4,6:3.2,8:3.0,9:1.0,12:3.5,16:1.0,18:.8,24:.6}
                duration=vr.choices(options,weights=[prior[x]*(.5+strength(t+x,mode)) for x in options])[0]
                final=t+duration>=end-3
                position=(t-start)/max(1,end-start)
                arc=math.sin(math.pi*position)
                vel=round(58+16*arc+4.0*strength(t,mode)+vr.uniform(-5,5))
                vel=max(45,min(103,vel))
                articulation=vr.choices(['tenuto','ordinary','staccato'],weights=[5,4,1])[0]
                if final:articulation='tenuto';vel=max(48,vel-8)
                gate=max(2,round(duration*({'tenuto':.97,'ordinary':.84,'staccato':.57}[articulation])))
                # A line crosses a harmonic boundary by following its branch pitch.
                for hi,h in enumerate(harmonies):
                    onset=max(t,h['start']);stop=min(t+gate,h['end'])
                    if stop>onset:
                        n=dict(voice=v,start_tick=onset,duration_ticks=stop-onset,pitch=previous['pitches'][h['chord']][v],velocity=vel,phrase=phrase_id,harmony=hi,articulation=articulation,mode=mode)
                        notes.append(n);phrase_notes.append(n)
                t+=duration
                # A brief consonant-like break inside a mostly continuous phrase.
                if not final and vr.random()<.07:t+=min(3,end-t)
            if phrase_notes:phrases.append(dict(id=phrase_id,start_tick=start,end_tick=max(n['start_tick']+n['duration_ticks'] for n in phrase_notes),mode=mode))
            phrase_id+=1
            # Weighted breathing spaces: prefer re-entry on a metrical support.
            gap_options=[9,12,15,18,21,24,27,30]
            gap=vr.choices(gap_options,weights=[strength(end+x,mode) for x in gap_options])[0]
            t=end+gap
        voice=dict(voice=v+1,branch=sounds[v]['branch'],pan=sounds[v]['pan'],sound=patches[order[v]],patch_index=order[v],phrases=phrases)
        voices.append(voice)
    # Every branch must sound in every harmony, including the one-bar changes.
    repairs=0
    for v in range(32):
        for hi,h in enumerate(harmonies):
            if any(n['voice']==v and n['harmony']==hi for n in notes):continue
            onset=h['start']+12;stop=min(onset+9,h['end'])
            assert not any(n['voice']==v and n['start_tick']<stop and n['start_tick']+n['duration_ticks']>onset for n in notes)
            notes.append(dict(voice=v,start_tick=onset,duration_ticks=stop-onset,pitch=previous['pitches'][h['chord']][v],velocity=66,phrase=-1,harmony=hi,articulation='tenuto',mode='four'));repairs+=1
    notes.sort(key=lambda n:(n['voice'],n['start_tick']))
    score=dict(seed=seed,bpm=100,meter='4/4',ticks_per_quarter=12,seconds_per_tick=SECONDS,duration_seconds=total*SECONDS,total_ticks=total,harmonies=harmonies,voices=voices,notes=notes,near_unison_pairs=edges,sound_swaps=swaps,coverage_repairs=repairs)
    for v in range(32):
        last=0
        for n in [n for n in notes if n['voice']==v]:
            assert n['start_tick']>=last
            h=harmonies[n['harmony']];assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end']
            last=n['start_tick']+n['duration_ticks']
    assert total==1440 and abs(score['duration_seconds']-72)<1e-8
    return score

def midi(score,path):
    f=mido.MidiFile(ticks_per_beat=480);tr=mido.MidiTrack();f.tracks.append(tr)
    tr.append(mido.MetaMessage('set_tempo',tempo=600000));tr.append(mido.MetaMessage('time_signature',numerator=4,denominator=4))
    last=0
    for h in score['harmonies']:
        tick=h['start']*40;tr.append(mido.MetaMessage('marker',text=f"Harmony {chr(65+h['chord'])}",time=tick-last));last=tick
    tr.append(mido.MetaMessage('end_of_track',time=score['total_ticks']*40-last))
    channels=[i for i in range(16) if i!=9]
    for v,voice in enumerate(score['voices']):
        tr=mido.MidiTrack();f.tracks.append(tr);ch=channels[v%15]
        tr.append(mido.MetaMessage('track_name',name=f"{v+1}: {voice['sound']['engine']} / {voice['sound']['name']}"));tr.append(mido.MetaMessage('midi_port',port=v//15))
        for c,value in [(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=c,value=value))
        if voice['sound']['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=voice['sound']['program']))
        events=[]
        for n in score['notes']:
            if n['voice']!=v:continue
            key=round(n['pitch']);bend=round((n['pitch']-key)*4096)
            for t,prio,msg in [(n['start_tick'],1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(n['start_tick'],2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),(n['start_tick']+n['duration_ticks'],0,mido.Message('note_off',channel=ch,note=key))]:events.append((t*40,prio,msg))
        last=0
        for t,prio,msg in sorted(events,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
        tr.append(mido.MetaMessage('end_of_track',time=score['total_ticks']*40-last))
    f.save(path)
    assert abs(mido.MidiFile(path).length-72)<1e-6

def render(score,runtime,soundfont,patchdir,output):
    eng=Engines(runtime,soundfont);plugins={};audio=np.zeros((round(score['duration_seconds']*RATE),2),np.float32)
    for v,voice in enumerate(score['voices']):
        p=voice['sound'];engine=p['engine'];plug=None
        if engine!='FluidSynth':
            if engine not in plugins:plugins[engine]=load_plugin(str(eng.paths[engine].resolve()))
            plug=plugins[engine];state=patchdir/f"{voice['patch_index']+1:02}_{engine.replace(' ','_')}.vststate";plug.raw_state=state.read_bytes()
        own=[n for n in score['notes'] if n['voice']==v]
        ref=eng.note(p,plug,float(np.median([n['pitch'] for n in own])),RATE)
        gain=.032/max(1e-5,float(np.sqrt(np.mean(ref*ref))))
        angle=(voice['pan']+1)*np.pi/4;pan=np.array([np.cos(angle),np.sin(angle)])*np.sqrt(2)
        if plug is not None:
            events=[]
            for n in own:
                key=round(n['pitch']);bend=round((n['pitch']-key)*8192/(3 if engine=='Dexed' else 2))
                events.extend([(n['start_tick'],1,mido.Message('pitchwheel',pitch=bend)),(n['start_tick'],2,mido.Message('note_on',note=key,velocity=78)),(n['start_tick']+n['duration_ticks'],0,mido.Message('note_off',note=key))])
            msgs=[(m.bytes(),t*SECONDS) for t,prio,m in sorted(events,key=lambda x:(x[0],x[1]))]
            track=plug(msgs,duration=score['duration_seconds']+1/RATE,sample_rate=RATE,buffer_size=512,reset=True).T[:len(audio)].copy()
        for n in own:
            start=round(n['start_tick']*SECONDS*RATE);stop=round((n['start_tick']+n['duration_ticks'])*SECONDS*RATE)
            a=eng.note(p,None,n['pitch'],stop-start) if plug is None else track[start:stop].copy()
            a[:32]*=np.linspace(0,1,32)[:,None];a[-32:]*=np.linspace(1,0,32)[:,None]
            audio[start:stop]+=a*gain*pan*(n['velocity']/78)**1.4
        print('Voice',v+1,engine,p['name'],flush=True)
    eng.gm.close();assert np.isfinite(audio).all();audio*=.89/float(np.max(np.abs(audio)));save_wav(output,audio)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--previous',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--soundfont',type=Path,required=True);ap.add_argument('--patches',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(exist_ok=True,parents=True)
    score=compose(json.loads(args.previous.read_text()));(args.output/'phrased_preview.json').write_text(json.dumps(score,indent=2))
    midi(score,args.output/'phrased_preview.mid');print('Score',len(score['notes']),'notes; repairs',score['coverage_repairs'],flush=True)
    render(score,args.runtime,args.soundfont,args.patches,args.output/'phrased_preview.wav')
    with (args.output/'voice_sounds.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['voice','branch','engine','sound']);w.writerows([v['voice'],v['branch'],v['sound']['engine'],v['sound']['name']] for v in score['voices'])
    print('COMPLETE',flush=True)
if __name__=='__main__':main()
