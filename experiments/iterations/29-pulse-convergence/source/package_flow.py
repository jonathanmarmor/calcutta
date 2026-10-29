"""Validate and export Pulse and Convergence, including real primary-beat MIDI timing."""
from pathlib import Path
import json,wave,zipfile,subprocess,hashlib,importlib.metadata,sys
import numpy as np,mido
from validate_flow import validate
r=Path('suite');index=json.loads((r/'index.json').read_text());palette=json.loads((r/'palette.json').read_text());(r/'midi').mkdir(exist_ok=True)
audits=[validate(k) for k in range(1,11)];(r/'validation.json').write_text(json.dumps(audits,indent=2));elapsed=0;channels=[x for x in range(16) if x!=9]
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
album=r/'calcutta_pulse_and_convergence.wav'
if '--skip-album' not in sys.argv:
 with wave.open(str(album),'wb') as out:
  out.setnchannels(2);out.setsampwidth(2);out.setframerate(24000)
  for j,e in enumerate(index):
   with wave.open(str(r/'audio'/f"{e['number']:02}.wav")) as src:
    while block:=src.readframes(240000):out.writeframes(block)
   if j<9:out.writeframes(bytes(24000*2*2*2))
 chapter=';FFMETADATA1\ntitle=Calcutta: Pulse and Convergence\nartist=Jonathan Marmor\n'
 for e in index:chapter+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(e['album_start']*1000)}\nEND={round((e['album_start']+e['duration'])*1000)}\ntitle={e['number']:02}. {e['title']}\n"
 (r/'chapters.ffmeta').write_text(chapter)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(album),'-i',str(r/'chapters.ffmeta'),'-map_metadata','1','-map_chapters','1','-ar','48000','-codec:a','libmp3lame','-b:a','256k',str(r/'calcutta_pulse_and_convergence.mp3')],check=True)
def clock(x):return f'{int(x)//60}:{int(x)%60:02}'
text='# Calcutta: Pulse and Convergence\n\nTen new pieces, **'+clock(sum(x['duration'] for x in index))+' of music**; **'+clock(elapsed-2)+'** in the continuous album with two-second gaps. The primary changes are fuller texture, a sustained expressive pulse, and a left-to-right harmonic journey that reaches the final golden-ratio field for at least the last third. No new compositional research or borrowed tunes/forms were used.\n\n## Listening order\n\n| Album time | Piece | Duration | Final field begins within piece | Final-field share |\n|---|---|---|---|---|\n'
for e in index:text+=f"| {clock(e['album_start'])} | [{e['number']:02}. {e['title']}](audio/{e['audio']}) | {clock(e['duration'])} | {clock(e['final_chord_start'])} | {100*e['final_chord_fraction']:.1f}% |\n"
text+='''
## How the progression works

Each piece advances through contiguous windows of the original forty fields. A typical route uses A–C, then B–F, then F/G, one field alone, a wider next neighborhood, and so on. Within a window, it can move back and forth. The window's lower and upper bounds never move backward. All forty fields are heard. The last window contains only field 39, the final finite golden-ratio approximation, and lasts about 37–42% of the piece. The full schedules are in `areas` and `harmonies` in each score.

This final residence is not a long static pad. Four-bar episodes continue to change the melodic cells, triad/seventh-root sequences, registers, leading instruments, instrumental choirs, timbral relays, inner lines, phrasing and dynamics. The harmonic field stays fixed while its contents keep moving. The final field is the original saved pitch set, not a newly calculated limiting tuning or an octave-repeating scale.

## Fuller texture and an expressive pulse

Four or more written notes are active during roughly 91–92% of every piece, with averages around six and peaks of ten to thirteen. One- or two-note passages occupy only about 3–4%, including breaths and endings. These are score occupancy measures, not a perceptual estimate of how many instruments the listener can distinguish. Quiet inner voices, a distributed instrumental pulse and several moving foreground lines usually coexist.

The shared 4/4 pulse is supplied by changing bass and upper instrumental activity, not drums or a metronome. Mild common tempo breathing, small timing offsets, metrical accents, varied durations and shaped velocities prevent identical mechanical attacks. The moving lines include eighths, dotted figures and occasional subsidiary clock relationships, but the primary pulse remains present. Textures change about every four bars, always inside thirty seconds. No recurring violent tutti attack is used as the formal engine.

The pieces have separate melodic contours, rhythms, orchestral palettes, tempi, section orders and short endings. Sampled piano, Rhodes, Clavinet, guitars, harp, winds, strings, basses and mallets remain prominent, with analog/FM sounds taking changing foreground and background roles. There are no vocals, tremolo/gating studies, click track or master fade in this set.

## Pitch policy

Structural notes are exact members of the active original harmony. No octave-equivalent pitches are invented. Rare added notes are genuine passing tones: brief, quieter, monotonic connectors between actual same-part structural endpoints in the same harmonic span. Their endpoint IDs are recorded and checked. No new sustained chord tones or neighboring-note ornaments are introduced. Structural notes end before incompatible changes; no held pitch is retuned. The golden-field residence permits these same rare passing connections but no other harmonic fields.

## Sound method

The custom exact-pitch sampler uses saved dry atoms captured in three registers per instrument. Synth sources come from previously configured Surge XT, OB-Xf, TAL-NoiseMaker and Dexed. Acoustic/electric colors were captured through FluidSynth from GeneralUser GS, by S. Christian Collins (1997–2025; license included). These are sampled performances, not new full-plugin performances or recordings of a live ensemble. Natural source attacks and decays remain, sampled sustains are finite, and transposition affects tone color.

No reverb, delay, chorus, deliberate vibrato or periodic amplitude DSP is added. Brief edge smoothing and an eight-millisecond release gate prevent accidental clicks without a lingering release. Stereo-linked peak control preserves the internal dynamic shapes. Source audio is 24 kHz stereo; listening files are 48 kHz / 256 kbps MP3. The continuous album has track chapters where supported.

## Reproduce and inspect

The source bundle preserves the public request and generation brief, ten explicit forms/seeds, exact note and harmony decisions, beat times, instrument palette, passing endpoints, saved sound atoms, MIDI and validation. No network or plugin installation is required to render these saved sources. Install the pinned Python requirements and FFmpeg, then run from the source root:

```sh
python compose_flow.py
python render_flow.py 1
# render numbers 2 through 10 in the same way
python package_flow.py
```

`compose_flow.py 4` regenerates only score 04. `pitch_core.py` supplies the pitch-selection and voice-allocation primitives. `validate_flow.py` checks the advancing adjacent-field route, final residence, every structural pitch and passing connector, constant pitch per note, independent voice lanes, actual density, nearby musical attacks on the primary beat grid, scene lengths, duration and output peaks. It does not pretend to judge musical expressiveness by those numerical checks.

MIDI encodes the real primary beat grid using a tempo event per quarter note. Note positions retain the small performance offsets; the independently paced secondary parts share that time axis. Each independent lane gets its own channel/port and pitch-bend sensitivity. A DAW must honor separate ports and bend range; MIDI does not embed the sampled instruments. Use the supplied renderer for the exact timbral arrangement. Public instructions and code are preserved, not a model's hidden reasoning transcript. Complete third-party banks and plugin binaries are excluded.
'''
(r/'calcutta_pulse_and_convergence_guide.md').write_text(text)
(r/'playlist.m3u').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{e['duration']},{e['title']}\naudio/{e['audio']}\n" for e in index))
requirements=''.join(f'{p}=={importlib.metadata.version(p)}\n' for p in ['numpy','scipy','mido'])
files=[Path(x) for x in ['compose_flow.py','pitch_core.py','render_flow.py','validate_flow.py','package_flow.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for d in ['suite/atoms','suite/scores','suite/midi','native_states'] for p in Path(d).glob('*') if p.is_file()]
files += [r/'index.json',r/'palette.json',r/'BRIEF.md',r/'validation.json',r/'calcutta_pulse_and_convergence_guide.md']
if (r/'reproducibility_flow.json').exists():files.append(r/'reproducibility_flow.json')
destination=r/'calcutta_pulse_and_convergence_source.zip';temporary=destination.with_suffix('.tmp')
with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
 for p in files:archive.write(p,str(p))
 archive.writestr('README.md',text.replace('](audio/','](suite/audio/'))
 archive.writestr('requirements.txt',requirements)
with zipfile.ZipFile(temporary) as archive:assert archive.testzip() is None
temporary.replace(destination)
print('Packaged ten pieces;',clock(elapsed-2),'including gaps;',sum(x['passing_notes'] for x in audits),'passing notes.',flush=True)
