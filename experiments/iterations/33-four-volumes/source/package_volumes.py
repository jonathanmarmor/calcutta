"""Four chaptered large volumes, explanatory guide and portable source bundle."""
from pathlib import Path
import json,wave,zipfile,subprocess,concurrent.futures,importlib.metadata
from plan import VOLUMES
r=Path('suite');out=Path('release');out.mkdir(exist_ok=True);index=json.loads((r/'index.json').read_text());audits=json.loads((r/'validation.json').read_text())
def slug(s):return s.lower().replace(' ','_')
def clock(t):return f'{int(t)//60}:{int(t)%60:02}'
gap=r/'audio/gap.wav'
with wave.open(str(gap),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(24000);w.writeframes(bytes(24000*4*2))
def assemble(v):
 title,duration=VOLUMES[v];items=index[v*4:v*4+4];lines=[];meta=f';FFMETADATA1\ntitle=Calcutta Volume {v+1}: {title}\nalbum=Calcutta: Four Volumes\nartist=Jonathan Marmor\ndate=2026\n'
 for j,e in enumerate(items):
  lines.append(f"file 'audio/{e['number']:02}.wav'")
  if j<3:lines.append("file 'audio/gap.wav'")
  meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(e['volume_start']*1000)}\nEND={round((e['volume_start']+e['duration'])*1000)}\ntitle={e['number']:02}. {e['title']}\n"
 (r/f'volume{v+1}.concat').write_text('\n'.join(lines)+'\n');(r/f'volume{v+1}.ffmeta').write_text(meta);name=f'calcutta_volume_{v+1}_{slug(title)}.mp3';dest=out/name;temp=dest.with_suffix('.tmp')
 subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(r/f'volume{v+1}.concat'),'-i',str(r/f'volume{v+1}.ffmeta'),'-map_metadata','1','-map_chapters','1','-ar','48000','-codec:a','libmp3lame','-b:a','256k','-f','mp3',str(temp)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:chapter=start_time,end_time','-of','json',str(temp)]));assert abs(float(probe['format']['duration'])-duration)<.12 and len(probe['chapters'])==4;temp.replace(dest);print('Assembled volume',v+1,title,flush=True);return dict(number=v+1,title=title,duration=duration,audio=name,chapters=4,encoded_duration=probe['format']['duration'])
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:volumes=list(pool.map(assemble,range(4)))
(r/'volumes.json').write_text(json.dumps(volumes,indent=2))
text='''# Calcutta: Four Volumes

**Four continuous volumes · 16 movements · 2 hours**

A larger format than the previous album: four linked volumes of 24, 28, 32 and 36 minutes. Each has four movement chapters and its own balance of textures. The original Calcutta tuning remains the center, with two explicitly marked departures. Endings are individually composed rather than selected from one default cadence or fade.

| Volume | Length | Character |
|---|---|---|
'''
characters=['Instrumental conversations, a chaconne and changing contrapuntal ensembles.','Two wordless synthetic-vocal works, one echo work and an extended trill study.','A tonal 12-ET detour, continuous glissandi, an unanswered dialogue and reversed-grain color.','Longer processes, reorchestrated returns, spreading time, concertino and a phrase that folds backward.']
for v,ch in zip(volumes,characters):text+=f"| [{v['number']}. {v['title']}]({v['audio']}) | {clock(v['duration'])} | {ch} |\n"
text+='\nEach file contains four chapter markers. Support for displaying chapters depends on the player. Times below are relative to that volume, not the complete two-hour set. There are three two-second gaps inside each volume.\n\n## Movements and endings\n\n| Volume / time | Movement | Length | Ending |\n|---|---|---|---|\n'
for e in index:text+=f"| {e['volume']} / {clock(e['volume_start'])} | {e['number']:02}. {e['title']} | {clock(e['duration'])} | {e['ending']} |\n"
text+='''
## The planned departures

**Singing voices — movements 5 and 8 only.** Mouths of Light and A Sentence Interrupted use an original wordless formant ensemble: harmonic excitation shaped into vowel spectra, with brief breath/consonant entrances. Fundamental frequency stays fixed, with no vibrato. This is explicitly synthetic singing-like sound, not cloned singers, recorded vocals or a claim of intelligible human lyrics. Solo and canonic entries meet reeds, electric keys and the earlier analog/FM colors.

**Effects — movements 6 and 12 only.** Echoes Have Their Own Meter uses finite multi-tap repeats, including an ending where excitation stops before the echoes. The Reversible Room uses reversed grains and a final reverse-envelope resonance. Effects stay within allocated note spans and harmonic boundaries. The remaining fourteen movements have no added delay, reverb, chorus, audio reversal or other post effects. Ordinary synthesis, note-edge smoothing and the continuous glides are separate processes. The final movement's retrograde reverses event order; it does not reverse audio.

**Tuning — two exceptions.** An Ordinary Sky (9) is genuinely 12-tone equal temperament, in a conventional diatonic/tonal setting with an explicit G7-to-C cadence. Its inherited field labels are timing markers, not a claim that it plays Calcutta harmony. Continuous Ground (10) slides continuously between exact Calcutta field endpoints while fixed-pitch anchors remain; interior pitches deliberately leave the discrete fields. The other fourteen movements use only exact original field members, without passing tones or octave substitutes. Fifteen works preserve the advancing Calcutta field route, as written notes or glide anchors; their last 40% stays in the final field. No note is retuned merely to follow a new harmony.

**Trills — movement 7.** The Trill Orchard treats articulated alternating field pitches as foreground, accompaniment and counterpoint, with different rates and slower contrasting layers. It ends by slowing the alternation and settling on the lower neighbor. These are discrete note events, not vibrato.

## Familiar textures, unfamiliar pitches

The new chaconne, chorale, invention and concertino procedures bring recurring bass patterns, imitative parts, chordal phrases and clear solo/accompaniment relationships into the Calcutta fields. Other passages use cue-driven relays, multiple phrase clocks, moving chord subsets, hocket and changing registers. Materials, seeds, instrumentation and section plans are new. Most substantial scene changes happen sooner than 24 seconds, and no scene exceeds 30 seconds, including the endings.

The 97 inherited instrumental models preserve the dry, immediate sampled-source/acoustic/electric/analog/FM blend. Four new formant voice identities appear in the two vocal works. Instruments are sample-derived fixed-frequency reconstructions, not untouched samples or newly loaded live plugins. GeneralUser GS source provenance and license are included. Except for composed glissandi, there is no pitch modulation; no detune, chorus, click or master ending fade is added. Short note-edge smoothing controls accidental clicks while keeping attacks prompt. Effects exceptions are identified above.

Quiet sustained dissonance and internal fifth/triad/seventh subsets remain important. The endings try different rhetorical functions: answer, withdrawal, an unfinished upper thought, evaporation of players, humming closure, echo continuation, settling trill, interrupted singing, tonal cadence, convergence, missing response, reverse resonance, remembered opening, expanded time, ensemble answer and event retrograde. Some finish with silence or an intentionally unresolved thought. None uses a global ending fade.

## Reproduce and inspect

Unpack the source ZIP, install FFmpeg and the pinned Python requirements, then run:

```sh
python compose_volumes.py
python render_all.py
python export_volumes.py
python validate_volumes.py
python check_regeneration.py
python package_volumes.py
```

The compact saved models suffice; no native plugins, external sample bank, paid account or singer service is required. `plan.py` records the volume and movement form. `compose_volumes.py` contains new textures and each ending; `compose_foundation.py` preserves the earlier harmonic/phrase primitives with new seeds. `render_volumes.py` implements continuous pitch integration, formant singing and the two bounded effect types. Public request and implementation instructions are in `suite/BRIEF.md`. These are public generation decisions, not hidden reasoning.

Scores store every note, voice, harmonic span, phrase/cue decision, instrument assignment, glide endpoint/curve, vocal vowel, effect parameter, ending and primary tempo grid. MIDI uses separate pitch-bend lanes/ports and actual tempo maps. Glides have 20 ms pitch-bend control points with a wider bend range; audio integrates their pitch continuously. MIDI does not reproduce the custom voice/timbre synthesis or post effects. The provided renderer is authoritative for sound.

Validation checks harmonic boundaries, exact pitch membership or the two declared pitch exceptions, gate/effect/vocal confinement, sixteen different ending specifications, independent voice lanes, complete WAV bytes, MP3 duration, output peaks and positive energy from scored instruments. All sixteen scores regenerate identically; representative voice, glissando and DSP notes rerender identically. Volume files are encoded once from concatenated PCM, with four chapter markers each. Source audio is 24 kHz stereo; listening copies are 48 kHz / 256 kbps MP3. Metrics describe the score and files, not subjective realism or musical quality.
'''
(out/'calcutta_four_volumes_guide.md').write_text(text);Path('README.md').write_text(text)
Path('requirements.txt').write_text(''.join(f'{p}=={importlib.metadata.version(p)}\n' for p in ['numpy','scipy','mido']))
files=[Path(p) for p in ['README.md','requirements.txt','plan.py','compose_volumes.py','compose_foundation.py','pitch_core.py','render_volumes.py','render_base.py','render_all.py','export_volumes.py','validate_volumes.py','check_regeneration.py','package_volumes.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for d in ['models','scores','midi'] for p in (r/d).glob('*') if p.is_file() and not p.name.startswith('.')]
files += [r/p for p in ['BRIEF.md','index.json','volumes.json','validation.json','score_validation.json','reproducibility.json','palette.json','native_sources.json','model_provenance.json']]
files += list((r/'audio').glob('*_audit.json'))+list(r.glob('volume*.ffmeta'))
dest=out/'calcutta_four_volumes_source.zip';temp=dest.with_suffix('.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,p.as_posix())
with zipfile.ZipFile(temp) as z:assert z.testzip() is None
temp.replace(dest);print('Packaged four volumes, guide and portable source.',flush=True)
