"""First 12 bars: ensemble then 32 ascending solos, all with a quiet metronome."""
import sys,json,math,csv,wave,copy
from pathlib import Path
import numpy as np,mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from mixed_synths import Engines,RATE,save_wav
from pedalboard import load_plugin
root=Path('calcutta_full_fixed');root.mkdir(parents=True,exist_ok=True)
(root/'levels.jsonl').write_text('')
source=json.loads(Path('calcutta_full/score.json').read_text())
end_tick=source['total_ticks'];seconds=source['duration_seconds'];count=round(seconds*RATE)
notes=[dict(n,duration_ticks=min(n['duration_ticks'],end_tick-n['start_tick'])) for n in source['notes'] if n['start_tick']<end_tick]
voices=copy.deepcopy(source['voices'])
eng=Engines(Path('synth_runtime'),Path('soundfont_runtime/runtime/usr/share/sounds/sf2/TimGM6mb.sf2'));plugins={}
from instrument_sketch import SoundfontSynth
old_gm=eng.gm;rich_gm=SoundfontSynth(Path('soundfont_runtime/GeneralUser-GS.sf2'),RATE)
ensemble=np.zeros((count,2),np.float32)
def envelope(a):
    attack=min(round(.018*RATE),len(a)//4);release=min(round(.008*RATE),len(a)//4)
    a[:attack]*=(.5-.5*np.cos(np.linspace(0,np.pi,attack)))[:,None]
    a[-release:]*=(.5+.5*np.cos(np.linspace(0,np.pi,release)))[:,None]
    return a
stats_rows=[]
for v,voice in enumerate(voices):
    p=voice['sound'];name=p['engine'];plug=None
    eng.gm=rich_gm if p.get('program') in (14,26,27) and name=='FluidSynth' else old_gm
    if name!='FluidSynth':
        if name not in plugins:plugins[name]=load_plugin(str(eng.paths[name].resolve()))
        plug=plugins[name];state=Path('composition_32_voices_v3/patches')/f"{voice['patch_index']+1:02}_{name.replace(' ','_')}.vststate";plug.raw_state=state.read_bytes()
        if name=='Vital':
            plug.parameters['envelope_1_attack'].raw_value=(.018/32)**.25
        elif name=='Surge XT':
            values=plug.parameters['a_amp_eg_attack'].valid_values
            ms=[(abs(float(x[:-3])-12),x) for x in values if x.endswith(' ms')]
            plug.a_amp_eg_attack=min(ms)[1]
    own=[n for n in notes if n['voice']==v]
    # Surge loads raw patch states asynchronously. Warm it, and never convert
    # a silent calibration result into a huge gain boost.
    if plug is not None:
        import time
        for attempt in range(8):
            time.sleep(.1)
            probe=eng.note(p,plug,float(np.median([n['pitch'] for n in own])),RATE)
            if float(np.sqrt(np.mean(probe*probe)))>1e-6:break
        else:raise RuntimeError(f"Silent calibration for voice {v+1}: {p['name']}")
    gain=1.0
    stem=np.zeros((count,2),np.float32)
    if plug is not None:
        events=[]
        for n in own:
            key=round(n['pitch']);bend=round((n['pitch']-key)*8192/(3 if name=='Dexed' else 2))
            events.extend([(n['start_tick'],1,mido.Message('pitchwheel',pitch=bend)),(n['start_tick'],2,mido.Message('note_on',note=key,velocity=78)),(n['start_tick']+n['duration_ticks'],0,mido.Message('note_off',note=key))])
        msgs=[(m.bytes(),t*.05) for t,prio,m in sorted(events,key=lambda e:(e[0],e[1]))]
        track=plug(msgs,duration=seconds+1/RATE,sample_rate=RATE,buffer_size=512,reset=True).T[:count].copy()
    for n in own:
        start=round(n['start_tick']*.05*RATE);stop=round((n['start_tick']+n['duration_ticks'])*.05*RATE)
        a=eng.note(p,None,n['pitch'],stop-start) if plug is None else track[start:stop].copy()
        stem[start:stop]+=envelope(a)*gain*(n['velocity']/78)**1.7
    assert np.isfinite(stem).all()
    actual_rms=float(np.sqrt(np.mean(stem*stem)))
    if actual_rms<1e-7:raise RuntimeError(f"Silent actual stem for voice {v+1}")
    # Balance the actual performed stem with one fixed gain, preserving dynamics.
    gain=.023/actual_rms
    if gain>16:raise RuntimeError(f"Excessive stem gain for voice {v+1}: {gain}")
    stem*=gain
    stats=dict(voice=v+1,engine=name,sound=p['name'],raw_rms=actual_rms,gain=gain,balanced_rms=float(np.sqrt(np.mean(stem*stem))),peak=float(np.max(np.abs(stem))))
    stats_rows.append(stats)
    angle=(voice['pan']+1)*np.pi/4
    ensemble+=stem*np.array([np.cos(angle),np.sin(angle)],np.float32)*np.sqrt(2)
    print('Voice',v+1,name,p['name'],flush=True)
assert len(stats_rows)==32 and len({r['voice'] for r in stats_rows})==32
assert all(abs(r['balanced_rms']-.023)<1e-6 and r['gain']<=16 for r in stats_rows)
(root/'levels.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in stats_rows))
old_gm.close();rich_gm.close()


assert np.isfinite(ensemble).all()
rms=float(np.sqrt(np.mean(ensemble*ensemble)));ensemble*=.11/max(rms,1e-7)
click=np.zeros_like(ensemble)
for beat in range(source['total_ticks']//12):
    first=beat%4==0;length=round((.022 if first else .014)*RATE);t=np.arange(length)/RATE
    sig=np.sin(2*np.pi*(1800 if first else 950)*t)*np.exp(-t/(.006 if first else .004))
    sig*=np.minimum(1,t/.0015);sig*=np.linspace(1,0,length)
    start=round(beat*.6*RATE);click[start:start+length]+=sig[:,None]
click*=.0275*10**(.5)/float(np.max(np.abs(click)))
gain=.89/max(float(np.max(np.abs(ensemble+click))),float(np.max(np.abs(ensemble))))
save_wav(root/'calcutta_full_music_corrected.wav',ensemble*gain)
save_wav(root/'calcutta_full_with_click_corrected.wav',(ensemble+click)*gain)
print('COMPLETE',seconds,'seconds',flush=True)
