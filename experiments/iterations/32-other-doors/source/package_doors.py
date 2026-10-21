"""Assemble chaptered continuous album, individual listening ZIP and portable source."""
from pathlib import Path
import json,wave,zipfile,subprocess,shutil,hashlib,importlib.metadata
r=Path('suite');out=Path('release');out.mkdir(exist_ok=True);index=json.loads((r/'index.json').read_text());audits=json.loads((r/'validation.json').read_text())
def clock(t):return f'{int(t)//60}:{int(t)%60:02}'
# Concatenate PCM to avoid inter-track encoder padding; encode the album just once.
gap=r/'audio/gap.wav'
with wave.open(str(gap),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(24000);w.writeframes(bytes(24000*4*2))
concat=[];meta=';FFMETADATA1\ntitle=Other Doors\nalbum=Calcutta: Other Doors\nartist=Jonathan Marmor\ndate=2026\n'
for j,e in enumerate(index):
 concat.append(f"file 'audio/{e['number']:02}.wav'")
 if j<11:concat.append("file 'audio/gap.wav'")
 meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(e['album_start']*1000)}\nEND={round((e['album_start']+e['duration'])*1000)}\ntitle={e['number']:02}. {e['title']}\n"
(r/'concat.txt').write_text('\n'.join(concat)+'\n');(r/'chapters.ffmeta').write_text(meta);dest=out/'calcutta_other_doors.mp3';temp=dest.with_suffix('.tmp')
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(r/'concat.txt'),'-i',str(r/'chapters.ffmeta'),'-map_metadata','1','-map_chapters','1','-ar','48000','-codec:a','libmp3lame','-b:a','256k','-f','mp3',str(temp)],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:chapter=start_time,end_time','-of','json',str(temp)]));assert abs(float(probe['format']['duration'])-3600)<.12 and len(probe['chapters'])==12;temp.replace(dest)
text='''# Calcutta: Other Doors

**Twelve new pieces · 60:00 including gaps · 59:38 of music**

An uneven album: three works around ten minutes, medium-length inventions, and miniatures down to 41 seconds. Different pieces have different generating engines and formal trajectories, rather than the same accompaniment underneath new presets. The dry, immediate, vibrato-free sound and the original Calcutta pitch fields remain the common ground.

[Play the continuous album](calcutta_other_doors.mp3). It contains chapter metadata; chapter support depends on the player. The separate-track listening ZIP includes all twelve MP3s, this guide and a playlist.

| Album start | Track | Duration | What to listen for |
|---|---|---|---|
'''
for e in index:text+=f"| {clock(e['album_start'])} | [{e['number']:02}. {e['title']}](audio/{e['audio']}) | {clock(e['duration'])} | {e['description']} |\n"
text+='''
## What changes from piece to piece

**Three Unequal Rivers**, **Rooms in a Long House**, and **An Unfinished Atlas** carry the large forms. The first repeatedly changes the relationships between three phrase clocks, with slower and faster material moving together. The second returns to contrasting rooms—dialogue, graph-based harmony, quiet chamber music, cue relays and moving registers—in changed harmonic surroundings. The last builds and subtracts layers, relocates registers, clears space and interrupts its own momentum. Shorter tracks provide different kinds of contrast rather than compressed copies of those forms.

**Fifths Under Glass** treats the internal triads and sevenths as a graph: shared pitches and voice-leading cost influence which subset follows which. **Orchard of Circuits** uses a queue of phrase cues: one player's cell schedules a transformed response from another player, so the network generates later entries. **A Very Short Parade** and **Thirty-Two Small Clocks** work directly with the original construction-tree endpoint identities. **The Stair Remembers** foregrounds recognizable rising/falling chord sequences.

**The Switches Are Singing** is the only track with amplitude-gate DSP. Sustained layers use different rates, phases and duties, with ungated islands and melodies. All other tracks omit gates and tremolo. The 41-second **One Window Left Open** is an intimate, near-still destination-field miniature—a deliberate exception to both the fuller textures and the full harmonic journey.

Every piece changes its substantial texture or ensemble within 25 seconds. Density and speed vary inside works: long outer melodies can sit over fast inner parts, independent clocks can become coordinated dialogue, and dense ensembles can open into chamber passages. These are written event/ensemble changes; the timing limit is not a claim about subjective surprise.

## Sound and tuning

All 97 inherited source models are heard across the album. Individual tracks use 11–90 actual sounds, with different inventories and changing ensembles; related presets count as distinct sounds, not distinct instrument families. Reed/keyboard colors are foregrounded in the second track, while acoustic, electric and synthetic colors share the larger works. Instrumentation counts and note-level assignments are in the scores and validation report.

These are the fixed-frequency, sample-derived resynthesized colors developed in Wide Palette and Prism Switchyard, not newly installed plugins or untouched acoustic samples. Attack/body spectra, short spectral settling, modeled pluck decay and faint stationary breath noise provide instrumental distinctions while discarding source pitch modulation. GeneralUser GS source provenance and license are included; eight earlier analog/FM colors remain available. There is no vibrato, added chorus/detune, reverb, delay, click or master ending fade. Notes have prompt entrances and short click-prevention releases. Individual dry endings replace a shared fade or loud final cadence.

Eleven tracks traverse all forty original harmonies through advancing contiguous neighborhoods, start on 2:3, and spend the last 40% entirely in the final golden-ratio field. Track 7 stays in that final field throughout. Early 1:2 visits are brief and occur after the opening. Every written note is an exact field member: no passing tones were needed on this album, and no octave substitutes or held-note retuning are used. Instruments move among actual field pitches. The harmonic/inharmonic partials of a timbre are distinct from the written MIDI pitches.

## Reproduce and inspect

Unpack the source ZIP, install FFmpeg and the pinned requirements, then run:

```sh
python compose_doors.py
python render_album.py
python validate_doors.py
python export_doors.py
python check_regeneration.py
python package_doors.py
```

The 97 compact saved models suffice for rendering; external banks and native plugins are not required. `suite/BRIEF.md` preserves the original request and public composition specification. The twelve scores record notes, construction identities, phrase sequences, relay cues, changing ensembles, beat grids, harmonic windows and gate parameters. The renderer and model provenance make the timbral process inspectable. Public instructions and decisions are included, not hidden reasoning.

MIDI uses independent bend lanes/ports and actual primary tempo maps. It supplies source program hints, but does not encode the resynthesized timbres or amplitude gates. The supplied renderer is authoritative for those sounds. Source audio is 24 kHz stereo, encoded to 48 kHz / 256 kbps MP3. The continuous album is encoded from concatenated PCM, with eleven two-second gaps and twelve chapter markers.

Validation checks exact pitches and harmonic boundaries, advancing windows, final-field residence, independent monophonic MIDI lanes, gate confinement, complete WAV bytes, output peaks, MP3 duration and positive audio energy from every scored instrument. All twelve scores regenerate identically; a representative gated note also rerenders identically. Render and occupancy metrics describe the actual files and score, not subjective musical quality.
'''
(out/'calcutta_other_doors_guide.md').write_text(text)
(r/'playlist.m3u').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{e['duration']},{e['title']}\naudio/{e['audio']}\n" for e in index))
def archive(dest,files):
 temp=dest.with_suffix('.tmp')
 with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
  for local,name in files:z.write(local,name)
 with zipfile.ZipFile(temp) as z:assert z.testzip() is None
 temp.replace(dest)
files=[(r/'audio'/e['audio'],'audio/'+e['audio']) for e in index]+[(out/'calcutta_other_doors_guide.md','README.md'),(r/'playlist.m3u','playlist.m3u')]
archive(out/'calcutta_other_doors_tracks.zip',files)
Path('README.md').write_text(text);Path('requirements.txt').write_text(''.join(f'{p}=={importlib.metadata.version(p)}\n' for p in ['numpy','scipy','mido']))
files=[Path(x) for x in ['compose_doors.py','render_doors.py','render_album.py','validate_doors.py','export_doors.py','check_regeneration.py','package_doors.py','pitch_core.py','README.md','requirements.txt','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for folder in ['models','scores','midi'] for p in (r/folder).glob('*') if p.is_file()]
files += [r/x for x in ['BRIEF.md','palette.json','native_sources.json','model_provenance.json','validation.json','score_validation.json','reproducibility.json','index.json','chapters.ffmeta']]
files+=list((r/'audio').glob('*_audit.json'))
archive(out/'calcutta_other_doors_source.zip',[(p,p.as_posix()) for p in files]);(r/'album_validation.json').write_text(json.dumps(dict(duration=probe['format']['duration'],chapters=12,total_music_seconds=sum(e['duration'] for e in index),gap_seconds=22),indent=2));print('Packaged Other Doors: 12 tracks, 60:00 album, source and guide',flush=True)
