"""Validate and export Pulse and Convergence, including real primary-beat MIDI timing."""
from pathlib import Path
import json,wave,zipfile,subprocess,hashlib,importlib.metadata,sys
import numpy as np,mido
from validate_wide import validate
r=Path('suite');index=json.loads((r/'index.json').read_text());palette=json.loads((r/'palette.json').read_text());(r/'midi').mkdir(exist_ok=True)
audits=[validate(k) for k in range(1,6)];(r/'validation.json').write_text(json.dumps(audits,indent=2));elapsed=0;channels=[x for x in range(16) if x!=9]
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
album=r/'calcutta_wide_palette.wav'
if '--skip-album' not in sys.argv:
 with wave.open(str(album),'wb') as out:
  out.setnchannels(2);out.setsampwidth(2);out.setframerate(24000)
  for j,e in enumerate(index):
   with wave.open(str(r/'audio'/f"{e['number']:02}.wav")) as src:
    while block:=src.readframes(240000):out.writeframes(block)
   if j<4:out.writeframes(bytes(24000*2*2*2))
 chapter=';FFMETADATA1\ntitle=Calcutta: Wide Palette\nartist=Jonathan Marmor\n'
 for e in index:chapter+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(e['album_start']*1000)}\nEND={round((e['album_start']+e['duration'])*1000)}\ntitle={e['number']:02}. {e['title']}\n"
 (r/'chapters.ffmeta').write_text(chapter)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(album),'-i',str(r/'chapters.ffmeta'),'-map_metadata','1','-map_chapters','1','-ar','48000','-codec:a','libmp3lame','-b:a','256k','-f','mp3',str(r/'album.tmp')],check=True)
 (r/'album.tmp').replace(r/'calcutta_wide_palette.mp3')
def clock(x):return f'{int(x)//60}:{int(x)%60:02}'
text='# Calcutta: Wide Palette\n\nFive new pieces, **'+clock(sum(x['duration'] for x in index))+' of music**, with **64 instrument sounds per piece** (the previous set used 14–16). Different pools and changing section ensembles are written into the scores. The pieces begin on the 2:3 or 3:5 field, never 1:2. The fuller textures, expressive pulse and adjacent-window harmonic convergence are retained.\n\n| Album time | Piece | Duration | Final field begins | Sounds |\n|---|---|---|---|---|\n'
for e in index:text+=f"| {clock(e['album_start'])} | [{e['number']:02}. {e['title']}](audio/{e['audio']}) | {clock(e['duration'])} | {clock(e['final_chord_start'])} | 64 |\n"
text+='\n## The instrument palette\n\nThe expanded library has 97 source sounds. Each piece uses eight earlier synth colors plus a different selection of 56 sampled-source presets: pianos and electric pianos, organs, Clavinet, guitars, basses, strings, winds, brass, mallets, plucked instruments and other pitched colors. These are actual distinct source presets, not counts of octave/register changes or renamed copies. Related presets such as different pianos count as different sounds. The full names, usage counts and featured assignments are in `instrumentation.json`; every scene records its actual ensemble. Some appearances are brief, others prominent.\n\nThe earlier open-saw/resonant, Oberheim pulse/brass, TAL hollow/reed and FM glass/organ colors return in vibrato-free resynthesized form. Quieter unison components provide occasional blends, while individual instruments stay exposed. Section ensembles change rather than maintaining one fixed orchestration for the entire piece. No added room, delay, chorus, click or master ending fade is used.\n\n## Strictly no vibrato\n\nAll sustained partial frequencies are fixed throughout each note. The model builder extracts attack and body spectra from dry sources and discards their time-varying pitch trajectory; zeroing a modulation controller alone would not remove vibrato embedded in samples. The renderer uses constant-frequency harmonic wavetables or a small bank of constant-frequency inharmonic partials for struck metals. It has no pitch LFO, detuned pair, chorus or cyclic amplitude effect. Short one-way spectral settling, modeled pluck decay and faint stationary breath noise preserve instrumental differences without periodic pitch modulation.\n\nThese are sample-derived resynthesized instruments. Their attack/body color comes from the source, while their envelopes and steady pitch are reconstructed. They can sound different from the unprocessed recordings. The acoustic/electric sources are GeneralUser GS by S. Christian Collins (license included); the earlier native synth captures supply the eight synthetic models. Source rendering is 24 kHz stereo; listening files are 48 kHz / 256 kbps MP3. Note entrances and releases have short click-prevention gates.\n\n## Composition and pitch\n\nThe five pieces have fresh cells, rhythmic material and section orders. Four or more written notes remain active most of the time, with brief thin exceptions. An expressive common primary pulse supports the contrapuntal and layered phrases. Every four-bar scene changes texture and instrumentation.\n\nThe original forty fields are traversed through advancing contiguous neighborhoods, with local back-and-forth movement. At least the final third uses only the final golden-ratio field while internal chord sequences, register, rhythm and instrumentation continue moving. Structural pitches are exact field members. Rare added pitches are brief, quieter monotonic passing connections between actual same-part structural endpoints inside one field. No extra sustained pitches or held-note retuning are introduced.\n\n## Reproduce and inspect\n\nInstall the pinned Python requirements and FFmpeg, then run from the source root:\n\n```sh\npython compose_wide.py\npython render_wide.py 1\n# repeat for numbers 2 through 5\npython package_wide.py\n```\n\nSaved model coefficients suffice; no bank download or plugin installation is needed for these renders. Optional model rebuilding uses `build_models.py` with the GeneralUser SF2 path and the earlier native capture directory as arguments. The bank SHA-256 and native source metadata are preserved; complete third-party banks and plugin executables are excluded.\n\nScores preserve all notes, advancing harmonic windows, the primary beat grid, passing endpoints, instrument pools, section ensembles and featured assignments. Validation checks all 64 instruments actually sound, varying ensembles, the opening field, pitch membership, genuine passing function, final-third residence, full texture, pulse, independent lanes and complete audio duration. Model flags and the fixed-carrier renderer encode the vibrato prohibition. Occupancy and onset metrics describe the score, not subjective expressiveness.\n\nMIDI follows the actual primary tempo grid with independent ports and per-note pitch bends. Its program hints refer to the original source presets; external playback needs its own modulation controls. Use the supplied fixed-carrier renderer to preserve the no-vibrato sound. Public instructions, code and decisions are included, not hidden model reasoning.\n'
(r/'calcutta_wide_palette_guide.md').write_text(text)
(r/'playlist.m3u').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{e['duration']},{e['title']}\naudio/{e['audio']}\n" for e in index))
requirements=''.join(f'{p}=={importlib.metadata.version(p)}\n' for p in ['numpy','scipy','mido'])
files=[Path(x) for x in ['compose_wide.py','flow_base.py','pitch_core.py','build_models.py','render_wide.py','validate_wide.py','package_wide.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','calcutta/soundfont_capture.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for d in ['suite/models','suite/scores','suite/midi'] for p in Path(d).glob('*') if p.is_file()]
files += [r/'index.json',r/'palette.json',r/'BRIEF.md',r/'validation.json',r/'instrumentation.json',r/'model_provenance.json',r/'native_sources.json',r/'calcutta_wide_palette_guide.md']
if (r/'reproducibility.json').exists():files.append(r/'reproducibility.json')
destination=r/'calcutta_wide_palette_source.zip';temporary=destination.with_suffix('.tmp')
with zipfile.ZipFile(temporary,'w',zipfile.ZIP_DEFLATED) as archive:
 for p in files:archive.write(p,str(p))
 archive.writestr('README.md',text.replace('](audio/','](suite/audio/'))
 archive.writestr('requirements.txt',requirements)
with zipfile.ZipFile(temporary) as archive:assert archive.testzip() is None
temporary.replace(destination)
print('Packaged five pieces;',clock(elapsed-2),'including gaps;',sum(x['passing_notes'] for x in audits),'passing notes.',flush=True)
