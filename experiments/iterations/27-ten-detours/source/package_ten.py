"""Export MIDI, listening guide, continuous album, audits and reproducible bundle."""
from pathlib import Path
import json,wave,hashlib,zipfile,subprocess,math
import numpy as np,mido
r=Path('suite');index=json.loads((r/'index.json').read_text());palette=json.loads((r/'palette.json').read_text());words=json.loads((r/'voice/texts.json').read_text())
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
channels=[x for x in range(16) if x!=9];audits=[];album_offsets=[];elapsed=0
for e in index:
 k=e['number'];s=json.loads((r/'scores'/f'{k:02}.json').read_text());a=json.loads((r/'audio'/f'{k:02}_audit.json').read_text());assert a['tremolo_events']==0 if k!=7 else a['tremolo_events']>0
 assert a['vocoded_events']==0 if k!=4 else a['vocoded_events']>0
 coverage=set()
 for n in s['notes']:
  st=n['start'];end=st+n['duration'];spans=[i for i,h in enumerate(s['harmonies']) if h['start']<end-1e-5 and h['end']>st+1e-5]
  for hi in spans:
   chord=s['harmonies'][hi]['chord'];assert min(abs(n['pitch']-p) for p in pitches[chord])<1e-9,(k,n);coverage.add(chord)
 assert len(coverage)==40,(k,len(coverage))
 for v in range(len(s['voices'])):
  own=[n for n in s['notes'] if n['voice']==v]
  assert all(x['start']+x['duration']<=y['start']+.00001 for x,y in zip(own,own[1:]))
 with wave.open(str(r/'audio'/f'{k:02}.wav')) as w:
  assert w.getframerate()==24000 and abs(w.getnframes()/24000-s['duration'])<.001
  x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768;assert max(abs(x))<.78
 a['fields_actually_sounded']=len(coverage);a['pitch_audit']='exact field members, constant pitch per note';audits.append(a)
 f=mido.MidiFile(ticks_per_beat=1000,charset='utf-8');con=mido.MidiTrack();f.tracks.append(con);con.append(mido.MetaMessage('track_name',name=s['title']));con.append(mido.MetaMessage('set_tempo',tempo=1000000));con.append(mido.MetaMessage('time_signature',numerator=4,denominator=4));last=0
 for sec in s['sections']:
  t=round(sec['start']*1000);con.append(mido.MetaMessage('marker',text=sec['name'],time=t-last));last=t
 con.append(mido.MetaMessage('end_of_track',time=round(s['duration']*1000)-last))
 for v,voice in enumerate(s['voices']):
  inst=voice['instrument'];name='Vocoder / speech formants' if inst==27 else palette[inst]['name'];tr=mido.MidiTrack();f.tracks.append(tr);ch=channels[v%15];tr.append(mido.MetaMessage('track_name',name=f'{v+1}: {name}'));tr.append(mido.MetaMessage('midi_port',port=v//15))
  for cc,val in [(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=cc,value=val))
  if inst<27 and palette[inst]['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=palette[inst]['program']))
  ev=[]
  for n in s['notes']:
   if n['voice']!=v:continue
   t=round(n['start']*1000);end=round((n['start']+n['duration'])*1000);key=round(n['pitch']);bend=round((n['pitch']-key)*4096)
   ev.extend([(t,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(t,2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),(end,0,mido.Message('note_off',channel=ch,note=key))])
   if inst==27:ev.append((t,3,mido.MetaMessage('lyrics',text=words[n['word']])))
  last=0
  for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
  tr.append(mido.MetaMessage('end_of_track',time=max(0,round(s['duration']*1000)-last)))
 dest=r/'midi'/f'{k:02}.mid';f.save(dest);assert abs(mido.MidiFile(dest).length-s['duration'])<.001
 mp3=next((r/'audio').glob(f'{k:02}_*.mp3'));e['audio']=mp3.name;e['album_start']=elapsed;album_offsets.append((elapsed,e));elapsed+=s['duration']+2
(r/'index.json').write_text(json.dumps(index,indent=2));(r/'validation.json').write_text(json.dumps(audits,indent=2))
# Exact PCM concatenation, two seconds between pieces, no crossfades or effects.
album=r/'calcutta_ten_detours.wav'
with wave.open(str(album),'wb') as out:
 out.setnchannels(2);out.setsampwidth(2);out.setframerate(24000)
 for j,e in enumerate(index):
  with wave.open(str(r/'audio'/f"{e['number']:02}.wav")) as src:
   while b:=src.readframes(240000):out.writeframes(b)
  if j<9:out.writeframes(bytes(24000*2*2*2))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(album),'-ar','48000','-codec:a','libmp3lame','-b:a','256k',str(r/'calcutta_ten_detours.mp3')],check=True)
def clock(x):return f'{int(x)//60}:{int(x)%60:02}'
text='# Calcutta: Ten Detours\n\nTen new pieces, '+clock(elapsed-2)+' including two-second inter-track gaps (50:50 of music). The complete album is `calcutta_ten_detours.mp3`. Each track is also supplied separately. Every piece uses all forty original fields as selected subsets. No pitched event leaves its active field, no octave-equivalent pitch is substituted, and no held note is retuned.\n\n## Listening order\n\n| Album time | Track | Length | Experiment |\n|---|---|---|---|\n'
for e in index:text+=f"| {clock(e['album_start'])} | {e['number']:02}. {e['title']} | {clock(e['duration'])} | {e['premise']} |\n"
text+='''
## What is different between these pieces

1. **The Wrong Intermezzo** borrows the six-region A–B–A–C–B–A mechanism described for Bartók’s Interrupted Intermezzo: a returning serenade, broader song and contrasting interruption. Its melodies, chord order and instrumentation are new. It interrupts quietly rather than making shock-volume attacks.
2. **Crossing on the Stairs** uses opposing acceleration/deceleration curves, following the formal idea of Nancarrow’s Canon X. Unlike steady pulse layers, the lines have unequal syllable lengths, rests and phrase-ending extensions. Their speakers change regularly.
3. **Pocket Gongs, Plugged In** joins nested punctuating cycles, alternation between winds, and 2+2+3-style groups. These are transformed structural ideas from several practices, not an attempt at an authentic gamelan, Andean, or Bulgarian performance.
4. **The Counting Choir** uses newly synthesized eSpeak-NG speech: Fibonacci numbers, “count again,” “the fifth is here,” “the third is sharp,” “almost the same,” “hold,” and “stop.” A few dry spoken asides remain unpitched. For the choir, a bank of speech-derived formant envelopes controls harmonic carriers at exact field pitches. Consonant/vowel rhythms become melodic material. This is an original synthetic vocal performance, not a sampled or imitated singer.
5. **One Room, Twenty Doors** is a miniature structural collage. Twenty labeled doors draw on a promenade, preludes, interlocking voices, crossing tempos, interruption, canon, additive orchestration, unequal groups, unanswered questions, departure, displacement, three-beat poise, character contrast, isolated colors, theme-and-variation, split winds, unequal bars, and two retuned public-domain tunes. It is not a mash-up of twenty commercial recordings, nor a claim that every short door reproduces an entire source work’s form.
6. **Brother Jacques at the Wrong Funeral** directly transforms public-domain Frère Jacques and Dies irae. Their rhythmic/contour identities are retained, but pitches move to the nearest actual original-field member. Some intervals compress or stretch conspicuously; that deformation is part of the point. New counterpoint surrounds the quotations.
7. **Butterfly Relays** is the **only tremolo/gating piece**. Soft amplitude curves, deep square gates, different rates, duty cycles and phases stack over long notes. Hard-gate edges are rounded by about one millisecond to prevent accidental clicks; they still shut the sound fully off. The score and audit explicitly reject tremolo DSP in the other nine pieces.
8. **Five People, One Cable** puts acoustic wind, Rhodes, fretless and DI guitar roles in close conversation with a modular lead. Shared phrase intent and small timing deviations suggest people playing together, while fixed direct panning and zero room processing keep it deliberately studio-dry. Occasional short resonant filters transplant an instrument-body-like color; they are timbral filters, not room reverberation.
9. **Take Your Cables Home** borrows the disappearing-player mechanism of Haydn’s Farewell. The cast first changes and expands; during the last part, fewer players remain. The piece gets thinner through orchestration, not a master-volume fade.
10. **Jo, Ha, Trapdoor** offers early previews, then a slow free section, an unequal pulse and a quick exit. This is a freely adapted jo–ha–kyū-inspired temporal trajectory, not a transcription of a gagaku work. Fast lines move through distinct actual pitches rather than trembling on a single held pitch.

## Sources behind the formal experiments

- Bartók, Interrupted Intermezzo: [Boston Symphony program note](https://www.bso.org/works/concerto-for-orchestra).
- Nancarrow, Study 21 / Canon X and crossing speeds: [Kyle Gann at IRCAM](https://ressources.ircam.fr/en/composer/conlon-nancarrow/workcourse).
- Gagaku free introductions, fixed/unequal meters and drawn-out time: [Japan Arts Council](https://www2.ntj.jac.go.jp/dglib/contents/learn/edc22/en/category/kangen/on3.html); [Goshōraku and its jo–ha–kyū movements](https://www2.ntj.jac.go.jp/dglib/contents/learn/edc22/en/appreciate/kangen/s3.html).
- Kecak’s interlocking voices: [Smithsonian Folkways, The Bali Sessions](https://folkways.si.edu/the-bali-sessions-living-art-sounding-spirit/world/music/album/smithsonian).
- Andean panpipe orchestral reference: [Smithsonian Folkways](https://folkways.si.edu/aerophones-panpipes/islamica-world/music/track/smithsonian).
- Unequal 2+2+3 dance grouping: [Society of Folk Dance Historians](https://sfdh.us/encyclopedia/7-8_qqs_dances.html).
- Mussorgsky, Pictures at an Exhibition and recurring promenade: [LA Phil](https://www.laphil.com/works/pictures-at-an-exhibition-modest-mussorgsky-zvxy1msw).
- Ives, The Unanswered Question and independent sonic levels: [LA Phil](https://www.laphil.com/works/the-unanswered-question).
- Haydn’s departing players: [Charlotte Symphony](https://www.charlottesymphony.org/the-story-behind-haydn-s-farewell-symphony-zpj4).
- Ravel’s orchestral repetition: [Tucson Symphony](https://www.tucsonsymphony.org/program-notes/ravel/bolero/).
- Reich’s discussion of rhythmic divisions: [composer’s lecture](https://www.redbullmusicacademy.com/lectures/steve-reich-the-music-maker/).
- Bach’s contrasting variation/canon groups: [LA Phil](https://www.laphil.com/works/goldberg-variations-bwv-988-j-s-bach).
- Satie’s spare language: [Library of Congress](https://blogs.loc.gov/nls-music-notes/2021/05/erik-satie-and-the-art-of-simplicity/).
- Schumann’s character-miniature precedent is referenced in the collage as a general suite technique, not through copied notes; Webern’s spareness: [LA Phil](https://www.laphil.com/works/six-pieces-for-orchestra-op-6).
- Indian cyclical rhythmic context: [Carnegie Hall](https://www.carnegiehall.org/Education/Programs/Music-Educators-Toolbox/5-Rhythms-from-Around-the-World/Global-Encounters-Music-of-India). The short theme/variation door is an original compositional analogy, not a quoted tabla composition.

## Sound and DSP

The eight front-line synth sounds were captured from the actual Surge XT, OB-Xf, TAL-NoiseMaker and Dexed patches used for Bright Detours. Nineteen acoustic/electric sound colors were captured from GeneralUser GS (1997–2025 S. Christian Collins; license included) through FluidSynth: Rhodes, Clavinet, three guitars, piano, harp, winds, fretless bass, steel pans, vibraphone, tubular bells, marimba, organ and muted trumpet. The resulting notes are played by a custom exact-pitch sampler. This makes acoustic and synthetic tone behave like one strange instrument family, while keeping their original attacks and natural decay/sustain differences.

Three reference registers are supplied per timbre. Upward resampling is anti-aliased; no field pitch is rounded to equal temperament. Sources are 24 kHz float16 storage, expanded to float32 for rendering; the MP3s are encoded at 48 kHz / 256 kbps. Transposition changes sampled tone color as on a sampler; these are not ten direct full-VST performances. That choice is part of this set’s hybrid sound and makes the saved render reproducible without re-installing all plugins.

All note entrances are prompt, with only brief click-prevention smoothing. Samples retain natural decay where appropriate. Gates release inside the written duration. No reverb, delay, chorus, deliberate vibrato, click track or master ending fade is added. The stereo-linked peak envelope controls exceptional peaks; it is not a periodic tremolo. Internal dynamics and transparent orchestration remain intact.

## Reproduce

The source ZIP contains all ten exact scores, MIDI, original public brief, composition/renderer/packager source, saved dry atoms and speech/formant data, synth states, source tuning matrix, and validation. Native plugin binaries and complete third-party banks are excluded. Install `numpy`, `scipy`, `mido`; then run from the archive root:

```sh
python compose_ten.py
python render_ten.py 1
# repeat render_ten.py for numbers 2 through 10
python package_ten.py
```

The saved atoms and voice envelopes suffice for all ten renders. Rebuilding the native atoms additionally requires pedalboard 0.9.26, FluidSynth, GeneralUser GS and the four documented VST3 engines; `capture_atoms.py` records the method. Rebuilding the voice phrases requires eSpeak-NG; generated speech itself is included. No original source recording of another artist is included.

MIDI uses a 60-BPM time ruler with 1000 ticks per second so expressive absolute timings remain exact. Local tempi are encoded by note placement, not separate simultaneous conductor maps. Each monophonic voice has its own channel/port and ±2-semitone bend. MIDI does not embed sampler timbres, vocal formants, speech or tremolo/body-filter DSP; it contains the underlying carrier/structural notes. Refer to the score and renderer for those sound transformations.
'''
(r/'calcutta_ten_detours_guide.md').write_text(text)
(r/'playlist.m3u').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{e['duration']},{e['number']:02}. {e['title']}\naudio/{e['audio']}\n" for e in index))
# Reusable source includes generated atoms, not native plugin executables.
with zipfile.ZipFile(r/'calcutta_ten_detours_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 files=[Path(x) for x in ['compose_ten.py','render_ten.py','package_ten.py','capture_atoms.py','make_voice.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','calcutta/mixed_synths.py','calcutta/instrument_sketch.py','composition_32_voices_v3/score_and_sounds.json']]
 files+=list(Path('calcutta').glob('*.py'))
 files+= [Path('palette_frontier/synths.json'),Path('palette_frontier/build.py')]
 files=list(dict.fromkeys(files))
 files+=list(Path('palette_frontier').glob('*.vststate'))+list(Path('palette_murmur').glob('*.vststate'))
 files += [p for d in ['suite/atoms','suite/voice','suite/scores','suite/midi'] for p in Path(d).glob('*') if p.suffix in ['.npz','.json','.mid','.wav']]
 files += [r/'index.json',r/'palette.json',r/'validation.json',r/'calcutta_ten_detours_guide.md',r/'BRIEF.md']
 for p in files:z.write(p,str(p))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nscipy\nmido\n')
print('Packaged ten pieces, album duration',elapsed-2,'seconds; exact pitches, voice monophony, exclusive tremolo and exclusive vocals verified')
