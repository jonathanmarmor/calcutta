"""All requested listening formats, portable source and linked movement index."""
from pathlib import Path
import json,wave,zipfile,subprocess,concurrent.futures,importlib.metadata,os
from plan import VOLUMES
r=Path('suite');out=Path('release');out.mkdir(exist_ok=True);mov=out/'movements';mov.mkdir(exist_ok=True);index=json.loads((r/'index.json').read_text());audits=json.loads((r/'validation.json').read_text())
def slug(s):return s.lower().replace(' ','_')
def clock(t):
 t=int(t);return f'{t//3600}:{(t//60)%60:02}:{t%60:02}' if t>=3600 else f'{t//60}:{t%60:02}'
for seconds in [2,4]:
 with wave.open(str(r/'audio'/f'gap{seconds}.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(24000);w.writeframes(bytes(24000*4*seconds))
for e in index:
 target=mov/e['audio']
 if not target.exists():os.link(r/'audio'/e['audio'],target)
def encode(name,lines,meta,duration,chapters,bitrate):
 concat=r/(name+'.concat');metadata=r/(name+'.ffmeta');concat.write_text('\n'.join(lines)+'\n');metadata.write_text(meta);dest=out/(name+'.mp3');temp=dest.with_suffix('.tmp')
 subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(metadata),'-map_metadata','1','-map_chapters','1','-ar','48000','-codec:a','libmp3lame','-b:a',bitrate,'-f','mp3',str(temp)],check=True)
 p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:chapter=start_time,end_time','-of','json',str(temp)]));assert abs(float(p['format']['duration'])-duration)<.12 and len(p['chapters'])==chapters;temp.replace(dest);return dict(audio=dest.name,duration=duration,encoded_duration=p['format']['duration'],chapters=chapters,bitrate=bitrate)
def assemble(v):
 title,duration,count=VOLUMES[v];own=[e for e in index if e['volume']==v+1];lines=[];meta=f';FFMETADATA1\ntitle=Calcutta {v+1}: {title}\nalbum=Seven Unequal Volumes\nartist=Jonathan Marmor\ndate=2026\n'
 for j,e in enumerate(own):
  lines.append(f"file 'audio/{e['number']:02}.wav'")
  if j<len(own)-1:lines.append("file 'audio/gap2.wav'")
  meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(e['volume_start']*1000)}\nEND={round((e['volume_start']+e['duration'])*1000)}\ntitle={e['number']:02}. {e['title']}\n"
 info=encode(f'calcutta_v{v+1:02}_{slug(title)}',lines,meta,duration,count,'256k');info.update(number=v+1,title=title,movements=count);print('Encoded volume',v+1,title,flush=True);return info
def full():
 lines=[];meta=';FFMETADATA1\ntitle=Calcutta: Seven Unequal Volumes, Complete\nalbum=Seven Unequal Volumes\nartist=Jonathan Marmor\ndate=2026\n'
 for j,e in enumerate(index):
  lines.append(f"file 'audio/{e['number']:02}.wav'")
  if j<len(index)-1:lines.append("file 'audio/gap2.wav'" if e['volume']==index[j+1]['volume'] else "file 'audio/gap4.wav'")
  meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(e['full_start']*1000)}\nEND={round((e['full_start']+e['duration'])*1000)}\ntitle=V{e['volume']} / {e['number']:02}. {e['title']}\n"
 info=encode('calcutta_seven_volumes_complete',lines,meta,16554,33,'192k');print('Encoded complete 4:35:54 master',flush=True);return info
# Only two encoders at once, including the longer master.
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 master_future=pool.submit(full);futures=[pool.submit(assemble,v) for v in range(7)];volumes=[f.result() for f in futures];master=master_future.result()
(r/'volumes.json').write_text(json.dumps(volumes,indent=2));(r/'listening_validation.json').write_text(json.dumps(dict(master=master,volumes=volumes),indent=2))
text='''# Calcutta: Seven Unequal Volumes

**33 movements · seven continuous volumes · complete master 4:35:54**

[Play the complete set](calcutta_seven_volumes_complete.mp3).

The proportions change dramatically: one volume is one continuous twenty-minute work; another has eleven movements, some lasting only seconds; another has two broad movements of 25:10 and 46:48. Movement lengths range from **0:15 to 46:48**. The seven volume files total **4:35:30**; the complete master adds four seconds between volumes. Every movement is also available separately below.

| Volume | Duration | Movements |
|---|---:|---:|
'''
for v in volumes:text+=f"| [{v['number']}. {v['title']}]({v['audio']}) | {clock(v['duration'])} | {v['movements']} |\n"
text+='''
The continuous files contain movement chapter metadata; player support varies. Times below are relative to each volume and to the complete master. Volume files have two-second gaps between movements; the full master has four seconds between volumes. Individual movement files contain no added inter-movement gaps.

## Every individual movement

| Full start | Volume / local start | Movement MP3 | Duration | Ending |
|---|---|---|---|---|
'''
for e in index:text+=f"| {clock(e['full_start'])} | {e['volume']} / {clock(e['volume_start'])} | [{e['number']:02}. {e['title']}](movements/{e['audio']}) | {clock(e['duration'])} | {e['ending']} |\n"
text+='''
## How the format changes the music

The longer works are not the short works slowed down. Each has a new theme and recurring procedural palette, with five larger acts of changing dynamics and density above the scene layer. Those acts contain changing ensembles, phrase clocks, registers and contrapuntal activity. One volume forms an extended arch; another pairs two large processes; the small-machine suite uses compressed gestures, gaps, brief counterpoint and concentrated changes. The eight-event theme for each work and all generated phrase/cue decisions are preserved in the score.

Chaconne, chorale, invention and concertino textures meet cue relays, independently phrased clocks, chord-subset paths, hocket, trills and long outer melodies over quicker inner lines. Substantial scenes/ensembles continue changing within thirty seconds, including the large works. Scene-duration metrics describe written events, not subjective surprise.

The thirty-three endings are separate event scores: answers, omissions, exchanged notes, backward unrolling, contrary motion, damped bells, incomplete thoughts, stepped withdrawals, mirrors, unequal releases, a cadenza, a ground with an extra response, separating glides, vowel-to-breath closure and others. There is no shared appended default fragment or global ending fade.

## Sound, tuning and bounded departures

The familiar dry, immediate acoustic/electric/analog/FM blend uses 97 inherited compact spectral models, plus the original formant voice identities. These are sample-derived fixed-frequency resynthesized sounds, not untouched acoustic recordings or newly loaded live plugins. Model source provenance and the GeneralUser GS license are included. No ordinary pitch LFO/vibrato, detune, chorus, reverb, click or master ending fade is added.

- **Wordless synthesized singing:** movements **7, Soft Mouths**, and **30, A Choir Across the Valley**. Harmonic excitation is shaped by vowel formants, with brief breath/consonant entrances. Movement 30 ends with explicitly unpitched breath. These are original synthetic singing-like sounds, not cloned singers or a claim of intelligible human lyrics.
- **Post effects:** movements **15, The Back of an Attack**, and **28, Echoes Against the Living**, only. The first uses reversed grains; the second finite multi-tap echoes. Effects stay inside allocated note/harmonic spans. Mirrors and retrogrades elsewhere reorder note events without reversing audio.
- **12-ET:** movement **11, An Ordinary Amen**, is a deliberate conventional tonal diversion, with a plagal F-to-C ending. Its inherited field labels are timing markers rather than Calcutta harmony.
- **Continuous glissandi:** movement **26, The Slope Is Continuous**, connects exact field endpoints through intermediate pitches, with fixed-pitch anchors and an ending that opens outward from unison. These are composed trajectories, not vibrato or retuning to follow a harmony change.
- **Trills:** movement **10, The Orchard Has No Center**, foregrounds articulated alternations at different rates, with contrasting sustained/contrapuntal passages and a final breaking-apart of the trill. It is not an amplitude-gate effect.

All other pitched notes are exact original field members, with no octave substitution or added passing tones. Movements under ninety seconds are field postcards: they select original fields 1,3,7,12,21,38,39 instead of squeezing all forty into seconds. Longer Calcutta works traverse all forty through advancing contiguous harmonic neighborhoods. All Calcutta works begin beyond the 1:2 field and spend their final 40% in the destination field. The early 1:2 visit is shortened even in the longest works. The final-field texture keeps changing rather than treating convergence as an automatic fade.

## Reproduce and inspect

Unpack the source ZIP, install FFmpeg and the pinned Python requirements, then run:

```sh
python compose_seven.py
python render_all.py
python export_seven.py
python validate_seven.py
python check_regeneration.py
python package_seven.py
```

No native synth plugins, external sound bank, paid account or singer service is required to render the saved models. `plan.py` defines volumes, durations and movement profiles; `endings.py` contains the thirty-three ending scores. `compose_seven.py` handles miniature scope and larger acts; `compose_material.py` and `compose_foundation.py` preserve reusable texture/phrase/harmony procedures. `render_seven.py` implements fixed-frequency instruments, the two vocal works, glide curves and the two effect works. Original request and public implementation instructions are in `suite/BRIEF.md`; hidden reasoning is not included.

Scores preserve each note's original part/phrase identity. MIDI uses nonoverlapping lanes for each instrument to keep the longest works within the MIDI port limit. It includes actual tempo maps and 20 ms glide pitch-bend points; audio integrates those glides continuously. Standard MIDI does not reproduce the custom voice/instrument synthesis or post effects; use the supplied renderer for those sounds.

Source audio is 24 kHz stereo. Individual and volume MP3s are 48 kHz / 256 kbps; the full master is 48 kHz / 192 kbps to keep the long single file manageable. All formats are encoded directly from PCM rather than transcoding MP3. Validation checks note/harmonic boundaries, exact pitches or declared exceptions, miniature scope, independent lanes, vocal/effect/glide confinement, ending specifications, complete WAV bytes, MP3 durations/chapters, peaks and positive energy from every scored sound. All thirty-three scores regenerate identically; representative special notes rerender identically. Metrics describe the score/files, not subjective musical quality.
'''
(out/'calcutta_seven_volumes_guide.md').write_text(text);Path('README.md').write_text(text)
for v in volumes:
 (out/f"volume_{v['number']:02}.m3u").write_text('#EXTM3U\n'+''.join(f"#EXTINF:{e['duration']},{e['title']}\nmovements/{e['audio']}\n" for e in index if e['volume']==v['number']))
Path('requirements.txt').write_text(''.join(f'{p}=={importlib.metadata.version(p)}\n' for p in ['numpy','scipy','mido']))
files=[Path(p) for p in ['README.md','requirements.txt','plan.py','endings.py','compose_seven.py','compose_material.py','compose_foundation.py','pitch_core.py','render_seven.py','render_base.py','render_all.py','export_seven.py','validate_seven.py','check_regeneration.py','package_seven.py','archive_listening.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for d in ['models','scores','midi'] for p in (r/d).glob('*') if p.is_file() and not p.name.startswith('.')]
files += [r/p for p in ['BRIEF.md','index.json','volumes.json','validation.json','score_validation.json','reproducibility.json','listening_validation.json','palette.json','native_sources.json','model_provenance.json']]
if (r/'archive_audio.json').exists():files.append(r/'archive_audio.json')
files += list((r/'audio').glob('*_audit.json'))+list(r.glob('*.ffmeta'))
dest=out/'calcutta_seven_volumes_source.zip';temp=dest.with_suffix('.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.as_posix())
with zipfile.ZipFile(temp) as z:assert z.testzip() is None
temp.replace(dest);print('Packaged master, seven volumes, thirty-three movements, source and guide.',flush=True)
