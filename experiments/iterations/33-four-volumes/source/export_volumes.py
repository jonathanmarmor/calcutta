"""Independent bend lanes, actual timing, and explicit continuous glissando data."""
from pathlib import Path
import json,collections,math
import numpy as np,mido
from plan import VOLUMES
r=Path('suite');index=json.loads((r/'index.json').read_text());palette=json.loads((r/'palette.json').read_text())+[{'name':f'Original formant voice {j+1}','engine':'Formant','program':54} for j in range(4)];(r/'midi').mkdir(exist_ok=True);channels=[x for x in range(16) if x!=9]
for e in index:
 k=e['number'];s=json.loads((r/'scores'/f'{k:02}.json').read_text());grid=np.array(s['metric_grid']);ticks=np.arange(len(grid))*1000
 def tick(t):return round(float(np.interp(t,grid,ticks)) if t<=grid[-1] else ticks[-1]+(t-grid[-1])/(grid[-1]-grid[-2])*1000)
 f=mido.MidiFile(ticks_per_beat=1000,charset='utf-8');con=mido.MidiTrack();f.tracks.append(con);con.append(mido.MetaMessage('track_name',name=s['title']));con.append(mido.MetaMessage('time_signature',numerator=4,denominator=4));ev=[]
 for j in range(len(grid)-1):ev.append((j*1000,0,mido.MetaMessage('set_tempo',tempo=round((grid[j+1]-grid[j])*1e6))))
 for sec in s['sections']:ev.append((tick(sec['start']),1,mido.MetaMessage('marker',text=sec['texture'])))
 last=0
 for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):con.append(msg.copy(time=t-last));last=t
 con.append(mido.MetaMessage('end_of_track',time=tick(s['duration'])-last));own=collections.defaultdict(list)
 for n in s['notes']:own[n['voice']].append(n)
 for v,voice in enumerate(s['voices']):
  inst=voice['instrument'];tr=mido.MidiTrack();f.tracks.append(tr);ch=channels[v%15];tr.append(mido.MetaMessage('track_name',name=f"{voice['part']}: {palette[inst]['name']}"));tr.append(mido.MetaMessage('midi_port',port=v//15));bendrange=24 if any('gliss' in n for n in own[v]) else 2
  for cc,val in [(101,0),(100,0),(6,bendrange),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=cc,value=val))
  if palette[inst]['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=palette[inst]['program']))
  ev=[]
  for n in own[v]:
   t=tick(n['start']);end=tick(n['start']+n['duration']);key=round(n['pitch']);bend=round((n['pitch']-key)*8192/bendrange);ev.extend([(t,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(t,2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),(end,0,mido.Message('note_off',channel=ch,note=key))])
   if n.get('gliss'):
    g=n['gliss'];arrive=g.get('arrive_fraction',1.)
    for dt in np.arange(.02,n['duration'],.02):
     u=min(1,dt/(n['duration']*arrive));u=u*u*(3-2*u);p=n['pitch']+(g['to_pitch']-n['pitch'])*u;bend=round((p-key)*8192/bendrange);assert -8192<=bend<=8191;ev.append((tick(n['start']+dt),1,mido.Message('pitchwheel',channel=ch,pitch=bend)))
  last=0
  for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
  tr.append(mido.MetaMessage('end_of_track',time=max(0,tick(s['duration'])-last)))
 dest=r/'midi'/f'{k:02}.mid';f.save(dest);assert abs(mido.MidiFile(dest).length-s['duration'])<.004
 e['audio']=f"{k:02}_{s['slug']}.mp3"
for v,(_,duration) in enumerate(VOLUMES):
 elapsed=0
 for e in index[v*4:v*4+4]:e['volume_start']=elapsed;elapsed+=e['duration']+2
 assert elapsed-2==duration
(r/'index.json').write_text(json.dumps(index,indent=2));print('Exported 16 MIDI files, including continuous pitch-bend curves and all four volume maps.')
