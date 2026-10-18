"""Render Dialogues with fixed instrument calibration and sectional dynamics."""
import sys,json,math,csv,wave,copy
from pathlib import Path
import numpy as np,mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from mixed_synths import Engines,RATE,save_wav
from pedalboard import load_plugin
root=Path('calcutta_archipelago');root.mkdir(parents=True,exist_ok=True)
(root/'levels.jsonl').write_text('')
source=json.loads(Path('calcutta_archipelago/score.json').read_text())
end_tick=source['total_ticks'];seconds=source['duration_seconds'];count=round(seconds*RATE)
notes=[dict(n,duration_ticks=min(n['duration_ticks'],end_tick-n['start_tick'])) for n in source['notes'] if n['start_tick']<end_tick]
voices=copy.deepcopy(source['voices'])
eng=Engines(Path('synth_runtime'),Path('soundfont_runtime/runtime/usr/share/sounds/sf2/TimGM6mb.sf2'));plugins={}
eng.paths['Surge XT']=next(Path('synth_runtime/surge_current').rglob('Surge XT.vst3'))
from instrument_sketch import SoundfontSynth
old_gm=eng.gm;rich_gm=SoundfontSynth(Path('soundfont_runtime/GeneralUser-GS.sf2'),RATE)
ensemble=np.zeros((count,2),np.float32)
def envelope(a):
    attack=min(round(.018*RATE),len(a)//4);release=min(round(.008*RATE),len(a)//4)
    a[:attack]*=(.5-.5*np.cos(np.linspace(0,np.pi,attack)))[:,None]
    a[-release:]*=(.5+.5*np.cos(np.linspace(0,np.pi,release)))[:,None]
    return a
calibration=[json.loads(line) for line in Path('calcutta_full_fixed/levels.jsonl').read_text().splitlines()]
assert len(calibration)==32
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
    gain=calibration[v]['gain']
    if voice.get('new_calibration'):
        probe=eng.note(p,None,float(np.median([n['pitch'] for n in own])),RATE*2)
        probe_rms=float(np.sqrt(np.mean(probe*probe)))
        if probe_rms<1e-6:raise RuntimeError('Silent new acoustic color')
        gain=.045/probe_rms
    if gain>16:raise RuntimeError(f"Excessive stem gain for voice {v+1}: {gain}")
    stem*=gain
    stats=dict(voice=v+1,engine=name,sound=p['name'],raw_rms=actual_rms,gain=gain,balanced_rms=float(np.sqrt(np.mean(stem*stem))),peak=float(np.max(np.abs(stem))))
    stats_rows.append(stats)
    angle=(voice['pan']+1)*np.pi/4
    ensemble+=stem*np.array([np.cos(angle),np.sin(angle)],np.float32)*np.sqrt(2)
    print('Voice',v+1,name,p['name'],flush=True)
assert len(stats_rows)==32 and len({r['voice'] for r in stats_rows})==32
assert all(r['balanced_rms']>1e-7 and 0<r['gain']<=16 for r in stats_rows)
(root/'levels.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in stats_rows))
old_gm.close();rich_gm.close()


assert np.isfinite(ensemble).all()
centers=[0]+[(s['start_seconds']+s['end_seconds'])/2 for s in source['form']]+[seconds]
db=[-18]+source['dynamic_envelope']['section_center_db']+[-34]
for start in range(0,count,RATE*10):
    stop=min(count,start+RATE*10)
    envelope_db=np.interp(np.arange(start,stop)/RATE,centers,db)
    ensemble[start:stop]*=(10**(envelope_db/20))[:,None]
peak=float(np.max(np.abs(ensemble)));gain=.89/peak
ensemble*=gain
save_wav(root/'calcutta_archipelago.wav',ensemble)
section_levels=[]
for section in source['form']:
    a=ensemble[round(section['start_seconds']*RATE):round(section['end_seconds']*RATE)]
    section_levels.append(dict(section=section['section'],rms_dbfs=20*math.log10(max(1e-9,float(np.sqrt(np.mean(a*a)))))))
(root/'section_levels.json').write_text(json.dumps(section_levels,indent=2))
print('COMPLETE',seconds,'seconds; no click; peak',float(np.max(np.abs(ensemble))),flush=True)
