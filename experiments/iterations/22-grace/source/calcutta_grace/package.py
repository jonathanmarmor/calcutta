from pathlib import Path
import json,zipfile,sys,math
import numpy as np,mido
root=Path('calcutta_grace');s=json.loads((root/'score.json').read_text())
PPQ=960;grid=s['conductor_grid'];beats=np.array(grid['beats']);seconds=np.array(grid['seconds'])
def miditick(ms):return round(float(np.interp(ms/1000,seconds,beats))*PPQ)
f=mido.MidiFile(ticks_per_beat=PPQ);conductor=mido.MidiTrack();f.tracks.append(conductor)
events=[(0,0,mido.MetaMessage('time_signature',numerator=4,denominator=4))]
for t in s['tempo_map']:events.append((round(t['beat']*PPQ),1,mido.MetaMessage('set_tempo',tempo=round(60000000/t['bpm']))))
for scene in s['form']:events.append((miditick(scene['start_seconds']*1000),2,mido.MetaMessage('marker',text=scene['name'])))
for hi,h in enumerate(s['harmonies']):events.append((miditick(h['start']),3,mido.MetaMessage('marker',text=f"Field {h['chord']+1}")))
last=0
for t,_,msg in sorted(events,key=lambda x:(x[0],x[1])):conductor.append(msg.copy(time=t-last));last=t
end=round(beats[-1]*PPQ);conductor.append(mido.MetaMessage('end_of_track',time=end-last))
channels=[x for x in range(16) if x!=9]
for v,voice in enumerate(s['voices']):
 tr=mido.MidiTrack();f.tracks.append(tr);ch=channels[v%15]
 tr.append(mido.MetaMessage('track_name',name=f"{v+1}: {voice['sound']['name']}"));tr.append(mido.MetaMessage('midi_port',port=v//15))
 for control,value in [(101,0),(100,0),(6,2),(38,0),(101,127),(100,127)]:tr.append(mido.Message('control_change',channel=ch,control=control,value=value))
 if voice['sound']['engine']=='FluidSynth':tr.append(mido.Message('program_change',channel=ch,program=voice['sound']['program']))
 ev=[]
 for n in s['notes']:
  if n['voice']!=v:continue
  start=miditick(n['start_tick']);stop=miditick(n['start_tick']+n['duration_ticks']);key=round(n['pitch']);bend=round((n['pitch']-key)*4096)
  ev.extend([(start,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(start,2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),(stop,0,mido.Message('note_off',channel=ch,note=key))])
 last=0
 for t,_,msg in sorted(ev,key=lambda x:(x[0],x[1])):tr.append(msg.copy(time=t-last));last=t
 tr.append(mido.MetaMessage('end_of_track',time=end-last))
f.save(root/'calcutta_grace.mid')
actual=mido.MidiFile(root/'calcutta_grace.mid').length;assert abs(actual-s['duration_seconds'])<.005,(actual,s['duration_seconds'])
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'
text='''# Calcutta: Grace and Grain

8:46.7. New themes, a new seventeen-scene form, and a different harmonic itinerary, using the original 40 fields and the established dry instrumental palette.

## Permission for this recording only

Passing tones, grace notes, and melodic ornaments may leave the original pitch collections in this version. Structural notes and full-field presentations remain exact original pitches. No new global harmonies are defined. The exception does not carry forward to subsequent generations unless requested again.

The score tags every added ornament with `is_ornament`. It contains 946 ornament notes: 843 lie outside the active original field, while others use existing endpoints. They are mostly short and softer than their target notes. Their patterns include chromatic-like approaches, uneven diatonic-like flourishes, pentatonic-sized sweeps, small microtonal turns, and original-endpoint runs. Runs are compressed into the space before a target, with varied internal timing, rather than imposed as a constant fast subdivision.

## No sustained retuning

Every rendered note has one fixed pitch for its complete duration. A note can cross a harmony boundary only if that unchanged pitch is genuinely present in every field it crosses. The score has 71 verified common-tone bridges.

Other phrases end before the boundary with a breath. Some answer after a roughly 110 ms gap with a new, nearby pitch and a fresh attack. No pitch-wheel adjustment occurs while a note remains held. This replaces the former practice of splitting a branch sustain at a boundary and immediately sounding its shifted continuation.

Three bass-pedal passages deliberately carry an unchanged common tone through changing fields. Protected whole-field listening windows may interrupt those pedals, after which they return on the same pitch. Structural material is checked against each field it actually sounds through; passing ornaments are kept inside one field's time span and released before its change.

## Form and timing

The piece retains continuous conductor rubato, intentional anticipation/delay, tuplets, independent nearby pulses, and back-calculated rhythmic suspensions that land together. Sound releases remain immediate and smoothed; no click, delay, reverb, chorus, or deliberate vibrato is added.

| Time | Scene | Nominal conductor BPM | Texture |
|---|---|---|---|
'''
for scene in s['form']:text+=f"| {clock(scene['start_seconds'])} | {scene['name']} | {scene['nominal_bpm'][0]} → {scene['nominal_bpm'][1]} | {scene['strategies'][0].replace('_',' ')} |\n"
text+='\n## Rhythmic landings\n\n'
for landing in s['rhythmic_landings']:text+=f"- **{clock(landing['seconds'])}:** four lines approach at different local tempos and resolve together.\n"
text+='''
## Reproduce

Run from the archive root:

```sh
python calcutta/grace_piece.py
python calcutta_grace/render.py
python calcutta_grace/package.py
```

Python dependencies: numpy, mido, pedalboard 0.9.26. Other dependencies: FluidSynth, ffmpeg, OB-Xf 1.0.3, Surge XT with patch-format 31 support, Dexed, TimGM6mb, and GeneralUser GS. Plugin/sample-bank binaries are not bundled. Configure paths as shown in the renderer. The archive includes source, score, tuning matrix, sound palette, instrument calibration, and saved synth states.

The composer reads only the previous voice palette and original endpoint matrix; it does not import previous notes or form. Millisecond score timing is exported to MIDI with a dense real tempo map. The 52 monophonic instrumental tracks use four ports with independent ±2-semitone pitch bends. MIDI does not embed plugin states or the rendered master-volume envelope.
'''
(root/'calcutta_grace_guide.md').write_text(text)
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
for n in s['notes']:
 spans=[i for i,h in enumerate(s['harmonies']) if h['start']<n['start_tick']+n['duration_ticks'] and h['end']>n['start_tick']]
 assert spans==n['harmony_spans']
 if not n['is_ornament']:
  assert all(min(abs(p-n['pitch']) for p in pitches[s['harmonies'][i]['chord']])<1e-10 for i in spans)
 if len(spans)>1:assert not n['is_ornament']
for c in s['complete_presentations']:
 mid=round((c['start_seconds']+c['end_seconds'])/2*1000)
 assert {n['pitch_index'] for n in s['notes'] if n['start_tick']<=mid<n['start_tick']+n['duration_ticks']}==set(range(32))
with zipfile.ZipFile(root/'calcutta_grace_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 files=[Path('calcutta')/name for name in ['grace_piece.py','mixed_synths.py','instrument_sketch.py','polyphonic.py','calcutta.py','scalar_runs.py','render.py']]
 files += [Path('COMPOSITION_GUIDELINES.md'),Path('calcutta_motifs/score.json'),Path('calcutta_full_fixed/levels.jsonl'),Path('composition_32_voices_v3/score_and_sounds.json')]
 files += list(Path('motif_patches').glob('*'))+list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
 files += [root/name for name in ['score.json','render.py','package.py','calcutta_grace.mid','calcutta_grace_guide.md','levels.jsonl','section_levels.json'] if (root/name).exists()]
 for path in files:z.write(path,str(path))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nmido\npedalboard==0.9.26\n')
print('Performed MIDI duration',actual,'seconds; ornament tags, fixed-pitch bridges, and full fields verified')
