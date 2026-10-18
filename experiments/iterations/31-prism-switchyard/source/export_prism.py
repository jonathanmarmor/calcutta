"""Validate and export Pulse and Convergence, including real primary-beat MIDI timing."""
from pathlib import Path
import json,wave,zipfile,subprocess,hashlib,importlib.metadata,sys
import numpy as np,mido
from validate_prism import validate
r=Path('suite');index=json.loads((r/'index.json').read_text());palette=json.loads((r/'palette.json').read_text());(r/'midi').mkdir(exist_ok=True)
audits=[validate(k) for k in [1]];(r/'validation.json').write_text(json.dumps(audits,indent=2));elapsed=0;channels=[x for x in range(16) if x!=9]
for e in index:
 k=e['number'];s=json.loads((r/'scores'/f'{k:02}.json').read_text());grid=np.array(s['metric_grid']);ticks=np.arange(len(grid))*1000
 def tick(t):return round(float(np.interp(t,grid,ticks)) if t<=grid[-1] else ticks[-1]+(t-grid[-1])/(grid[-1]-grid[-2])*1000)
 f=mido.MidiFile(ticks_per_beat=1000,charset='utf-8');con=mido.MidiTrack();f.tracks.append(con);con.append(mido.MetaMessage('track_name',name=s['title']));con.append(mido.MetaMessage('time_signature',numerator=4,denominator=4));ev=[]
 for j in range(len(grid)-1):ev.append((j*1000,0,mido.MetaMessage('set_tempo',tempo=round((grid[j+1]-grid[j])*1e6))))
 for sec in s['sections']:ev.append((tick(sec['start']),1,mido.MetaMessage('marker',text=sec['texture'])))
 ev.append((tick(s['final_chord_start']),1,mido.MetaMessage('marker',text='Final golden-ratio field: no later harmonic fields')));last=0
 for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):con.append(msg.copy(time=t-last));last=t
 con.append(mido.MetaMessage('end_of_track',time=tick(s['duration'])-last))
 for v,voice in enumerate(s['voices']):
  inst=voice['instrument'];tr=mido.MidiTrack();f.tracks.append(tr);ch=channels[v%15];tr.append(mido.MetaMessage('track_name',name=f"{voice['part']}: {palette[inst]['name']}"));tr.append(mido.MetaMessage('midi_port',port=v//15))
  for cc,val in [(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=cc,value=val))
  if palette[inst]['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=palette[inst]['program']))
  ev=[]
  for n in s['notes']:
   if n['voice']!=v:continue
   t=tick(n['start']);end=tick(n['start']+n['duration']);key=round(n['pitch']);bend=round((n['pitch']-key)*4096)
   ev.extend([(t,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(t,2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),(end,0,mido.Message('note_off',channel=ch,note=key))])
  last=0
  for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
  tr.append(mido.MetaMessage('end_of_track',time=max(0,tick(s['duration'])-last)))
 dest=r/'midi'/f'{k:02}.mid';f.save(dest);assert abs(mido.MidiFile(dest).length-s['duration'])<.003
 e['audio']=next((r/'audio').glob(f'{k:02}_*.mp3')).name;e['album_start']=elapsed;elapsed+=e['duration']+2
(r/'index.json').write_text(json.dumps(index,indent=2))
