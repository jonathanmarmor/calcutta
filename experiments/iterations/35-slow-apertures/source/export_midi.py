"""Fixed pitch-bend lanes with expression curves for slow note and texture envelopes."""
from pathlib import Path
import json,collections
import numpy as np,mido
from compose_slow import envelope
r=Path('suite');s=json.loads((r/'score.json').read_text());pal=json.loads((r/'palette.json').read_text());f=mido.MidiFile(ticks_per_beat=1000);con=mido.MidiTrack();f.tracks.append(con);con.extend([mido.MetaMessage('track_name',name='Slow Apertures: seconds-based timing'),mido.MetaMessage('set_tempo',tempo=1000000)]);ev=[]
for c in s['clouds']:ev.append((round(c['start']*1000),mido.MetaMessage('marker',text=c['kind'])))
ev.append((558000,mido.MetaMessage('marker',text='Only the final field remains')));last=0
for t,msg in sorted(ev,key=lambda x:x[0]):con.append(msg.copy(time=t-last));last=t
con.append(mido.MetaMessage('end_of_track',time=840000-last));own=collections.defaultdict(list)
for n in s['notes']:own[n['voice']].append(n)
channels=[i for i in range(16) if i!=9]
for vi,v in enumerate(s['voices']):
 inst=v['instrument'];ch=channels[vi%15];tr=mido.MidiTrack();f.tracks.append(tr);tr.extend([mido.MetaMessage('track_name',name=pal[inst]['name']+' lane '+str(v['lane'])),mido.MetaMessage('midi_port',port=vi//15)])
 for cc,val in [(1,0),(91,0),(93,0),(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=cc,value=val))
 if pal[inst]['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=pal[inst]['program']))
 events=[]
 for n in own[vi]:
  start=round(n['start']*1000);end=round((n['start']+n['duration'])*1000);key=round(n['pitch']);bend=round((n['pitch']-key)*4096);events.extend([(start,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(start,3,mido.Message('note_on',channel=ch,note=key,velocity=64)),(end,0,mido.Message('note_off',channel=ch,note=key)),(end,1,mido.Message('control_change',channel=ch,control=11,value=0))])
  times=np.r_[0,np.arange(.25,n['duration'],.25),n['duration']]
  for dt in times:
   gain=float(envelope(dt,0,n['duration'],n['attack'],n['release']))*n['gain']
   if n['cloud'] is not None:
    c=s['clouds'][n['cloud']];gain*=float(envelope(dt+n['start'],c['start'],c['duration'],c['attack'],c['release']))
   val=round(np.clip(gain*7,0,1)*127);events.append((start+round(dt*1000),2,mido.Message('control_change',channel=ch,control=11,value=val)))
 last=0
 for t,_,msg in sorted(events,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
 tr.append(mido.MetaMessage('end_of_track',time=max(0,840000-last)))
f.save(r/'slow_apertures.mid');assert abs(mido.MidiFile(r/'slow_apertures.mid').length-840)<.001;print('Exported MIDI with slow expression curves.')
