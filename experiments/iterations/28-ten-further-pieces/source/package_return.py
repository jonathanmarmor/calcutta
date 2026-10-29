"""Validate, export MIDI, concatenate the album and preserve this exact generation."""
from pathlib import Path
import json,wave,zipfile,subprocess,hashlib
import mido
from validate_return import validate
r=Path('suite');index=json.loads((r/'index.json').read_text());palette=json.loads((r/'palette.json').read_text());(r/'midi').mkdir(exist_ok=True)
audits=[validate(k) for k in range(1,11)];(r/'validation.json').write_text(json.dumps(audits,indent=2));elapsed=0;channels=[x for x in range(16) if x!=9]
for e in index:
 k=e['number'];s=json.loads((r/'scores'/f'{k:02}.json').read_text());f=mido.MidiFile(ticks_per_beat=1000,charset='utf-8');con=mido.MidiTrack();f.tracks.append(con);con.append(mido.MetaMessage('track_name',name=s['title']));con.append(mido.MetaMessage('set_tempo',tempo=1000000));last=0
 for sec in s['sections']:
  t=round(sec['start']*1000);con.append(mido.MetaMessage('marker',text=sec['texture'],time=t-last));last=t
 con.append(mido.MetaMessage('end_of_track',time=round(s['duration']*1000)-last))
 for v,voice in enumerate(s['voices']):
  inst=voice['instrument'];tr=mido.MidiTrack();f.tracks.append(tr);ch=channels[v%15];tr.append(mido.MetaMessage('track_name',name=f"{voice['part']}: {palette[inst]['name']}"));tr.append(mido.MetaMessage('midi_port',port=v//15))
  for cc,val in [(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=cc,value=val))
  if palette[inst]['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=palette[inst]['program']))
  ev=[]
  for n in s['notes']:
   if n['voice']!=v:continue
   t=round(n['start']*1000);end=round((n['start']+n['duration'])*1000);key=round(n['pitch']);bend=round((n['pitch']-key)*4096)
   ev.extend([(t,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(t,2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),(end,0,mido.Message('note_off',channel=ch,note=key))])
  last=0
  for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
  tr.append(mido.MetaMessage('end_of_track',time=max(0,round(s['duration']*1000)-last)))
 dest=r/'midi'/f'{k:02}.mid';f.save(dest);assert abs(mido.MidiFile(dest).length-s['duration'])<.001
 e['audio']=next((r/'audio').glob(f'{k:02}_*.mp3')).name;e['album_start']=elapsed;elapsed+=e['duration']+2
(r/'index.json').write_text(json.dumps(index,indent=2))
album=r/'calcutta_ten_further_pieces.wav'
with wave.open(str(album),'wb') as out:
 out.setnchannels(2);out.setsampwidth(2);out.setframerate(24000)
 for j,e in enumerate(index):
  with wave.open(str(r/'audio'/f"{e['number']:02}.wav")) as src:
   while block:=src.readframes(240000):out.writeframes(block)
  if j<9:out.writeframes(bytes(24000*2*2*2))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(album),'-ar','48000','-codec:a','libmp3lame','-b:a','256k',str(r/'calcutta_ten_further_pieces.mp3')],check=True)
def clock(x):return f'{int(x)//60}:{int(x)%60:02}'
premises=[
 'Guitar, Rhodes and reeds carry intersecting melodies; chord-stack sequences become dialogue and then exposed lines.',
 'Broad piano/cello/woodwind spacing opens into interlock and quicker counterpoint, then lets individual tones stand alone.',
 'Clavinet, marimba, reeds and strings keep distinct expressive clocks; several slow layers and faster lines exchange roles.',
 'Small wind/brass choirs answer each other; solos emerge between coordinated phrases and woven responses.',
 'Plucked and mallet attacks hand a melody between colors, opening into long winds and then measured contrapuntal detail.',
 'English horn, cello, guitar and piano sustain longer melodic sentences, with occasional genuine passing connections and quieter inner activity.',
 'Acoustic lines overlap in a close, brisk weave, broken by bare solos, slow frames and passages of generous space.',
 'Triads and sevenths are revoiced and sequenced inside the fields; quiet dissonance, single lines and synth/sample blends interrupt their continuity.',
 'Slow bass and accompaniment move beneath quicker expressive parts, then the tempo relationships and foreground instruments change.',
 'Short exposed ideas grow into layered counterpoint, break apart, and return in altered registers and timbres without a recurring borrowed form.'
]
text='# Calcutta: Ten Further Pieces\n\nTen new pieces, **56:24 of music**, or **56:42** in the continuous listening file with two-second gaps. This returns to the techniques developed before Ten Detours, with no new composition research, external formal models, quotations, vocals or tremolo/gating study. All melodic material is newly generated.\n\n## Listening order\n\n| Album time | Track | Length | Character |\n|---|---|---|---|\n'
for e,p in zip(index,premises):text+=f"| {clock(e['album_start'])} | [{e['number']:02}. {e['title']}](audio/{e['audio']}) | {clock(e['duration'])} | {p} |\n"
text+='''
## Musical constraints

The original forty Calcutta fields remain the harmonic source. Structural notes are actual pitches in the active field, not octave-equivalent substitutions. The pieces move locally between neighboring fields, with some reversals, differing dwell times and later convergence. None opens on the 1:2 field. Every field is heard, usually through subsets; these are not exhaustive 32-voice statements of every field.

Additional pitches are rare, brief passing tones. Each lies strictly between two structural notes in the same melodic part and same field, moves in their direction, sounds more quietly than its originating note, and lasts at most 440 milliseconds. The score records the actual endpoint note IDs. Connectors without a real destination are rejected. No extra sustained chord tones, neighbor-note ornaments, octave folding, moving held pitches, fast ornamental runs or glissandi are introduced. Structural notes end before a field changes.

Each piece has a new motif, rhythm, ensemble and explicitly chosen sequence of textures. Techniques include chord-root sequences, mutation, opposing melodic contours, small coordinated choirs, several independent expressive tempi, timbral hocket, sustained quiet dissonance, solo plus accompaniment, and transparent counterpoint. Strongly voiced chord stabs and the recurring short-short-long gesture are not the basis of this set. The scenes last roughly 10–18 seconds, always under thirty. Each piece contains one/two-line passages as well as five-to-seven-layer passages. The endings are individually written and dry; there is no master fade.

## Instruments and sound

Approximately nine in ten attacks use sampled instruments. Piano, Rhodes, Clavinet, acoustic and electric guitars, harp, mallets, reeds, flute, cello, viola, violin and acoustic/fretless bass share the foreground with analog/FM colors. Synths also appear as inner voices, restrained layers, occasional leads and small unison components. The instrumental assignments change through a piece instead of remaining attached to one pitch.

The source is a custom exact-pitch sampler using three dry reference registers per timbre. Eight synth sources were previously captured from Surge XT, OB-Xf, TAL-NoiseMaker and Dexed; sampled acoustic/electric sources use GeneralUser GS through FluidSynth. Nine additional sampled colors were captured for this set. GeneralUser GS is by S. Christian Collins (1997–2025); its license is included. These are sampler-based performances, not new full-plugin renders or recordings of a live ensemble. They retain the source instruments' natural attack/decay differences. Sampling/transposition changes tone color and captured sustains have finite lengths.

No reverb, delay, chorus, click, periodic gating or deliberate vibrato is added. Note edges receive only brief click-prevention smoothing and an eight-millisecond release gate. Stereo-linked peak control sets a moderate listening level while retaining internal dynamics. The source renders use 24 kHz stereo audio; listening copies are 48 kHz / 256 kbps MP3.

## Reproduce and inspect

The source bundle includes the original pitch lists, all ten deterministic composers/form plans, score decisions, exact passing-tone endpoints, MIDI, saved dry sound atoms, palette, validation, public request/brief and renderer. Saved atoms suffice; no plugin installation or network access is needed to render them. Install Python dependencies from `requirements.txt` and FFmpeg, then run from the source root:

```sh
python compose_return.py
python render_return.py 1
# render numbers 2 through 10 in the same way
python package_return.py
```

For a single piece, `python compose_return.py 3` regenerates score 03. The renderer never silently selects a new seed. Scores contain absolute timings for the independently paced lines. MIDI uses a fixed 60-BPM time ruler with 1000 ticks per second, independent channels/ports and per-note pitch bend; its tempo map is not a separate conductor for every line. A DAW must honor the MIDI ports and pitch-bend range. MIDI does not embed the sampler tones; use the included renderer for the supplied audio.

`validate_return.py` verifies every structural pitch, genuine passing endpoints, constant pitch, harmonic boundaries, independent voice lanes, field coverage, frequent changes, sparse/dense passages, duration and output peak. The public `suite/BRIEF.md` and code expose the generation specification; they are not a model's hidden reasoning transcript. Complete third-party sound banks and plugin executables are excluded.
'''
(r/'calcutta_ten_further_pieces_guide.md').write_text(text)
(r/'playlist.m3u').write_text('#EXTM3U\n'+''.join(f"#EXTINF:{e['duration']},{e['title']}\naudio/{e['audio']}\n" for e in index))
files=[Path(x) for x in ['compose_return.py','render_return.py','validate_return.py','package_return.py','capture_more.py','GENERALUSER-LICENSE.txt','calcutta/peak_balance.py','calcutta/soundfont_capture.py','composition_32_voices_v3/score_and_sounds.json']]
files += [p for d in ['suite/atoms','suite/scores','suite/midi','native_states'] for p in Path(d).glob('*') if p.is_file()]
files += [r/'index.json',r/'palette.json',r/'BRIEF.md',r/'validation.json',r/'calcutta_ten_further_pieces_guide.md']
with zipfile.ZipFile(r/'calcutta_ten_further_pieces_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,str(p))
 z.writestr('README.md',text.replace('](audio/','](suite/audio/'));z.writestr('requirements.txt','numpy==2.3.5\nscipy==1.17.0\nmido==1.3.3\n')
print('Packaged ten pieces;',clock(elapsed-2),'with gaps;',sum(x['passing_notes'] for x in audits),'validated passing notes.',flush=True)
