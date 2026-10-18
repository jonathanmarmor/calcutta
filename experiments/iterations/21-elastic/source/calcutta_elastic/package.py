from pathlib import Path
import json,zipfile,sys,math
import numpy as np,mido
root=Path('calcutta_elastic');s=json.loads((root/'score.json').read_text())
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
f.save(root/'calcutta_elastic.mid')
actual=mido.MidiFile(root/'calcutta_elastic.mid').length;assert abs(actual-s['duration_seconds'])<.005,(actual,s['duration_seconds'])
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'
text='''# Calcutta: Elastic Weather

9:08.7. A wholly new score made from the same 40 original tuning fields and a reused sound palette. No previous note sequences, motifs, rhythms, harmonic itinerary, or form were imported. The repeated dense short-short-long chord gesture has been removed. Complete fields still receive one soft, protected exposure each, without recurring chordal stabs.

The opening is sparse and starts in the 3:5 field. Neighboring early fields converse; the 1:2 field appears briefly rather than anchoring the piece. All 40 original harmonies are heard in full somewhere. Every other sounding pitch is also an actual endpoint of its current original field; no new tuning or octave-transposed pitch has been added.

## Time and expression

The conductor changes tempo continuously in eighth-of-a-beat steps, with breath-shaped acceleration, hesitation, and cadential slowing. Nominal scene tempos range from 36 to 116 quarter notes per minute; the expressive conductor momentarily spans approximately 24–145. Instrumental lines may run independently of that conductor.

Rubato sentences use unequal note spacing, shaped dynamics, 35 ms anticipation or 65 ms delay, and smaller continuous timing inflections. Tuplet scenes include thirds and fifths, with slight expressive deviations. Pulse clouds have six to thirteen neighboring but genuinely independent clocks, with slow rate drift and changing entrances/density; they do not consist of a backing pulse plus one different-tempo solo.

Two rhetorical suspensions work backward from a future downbeat. Four lines use periods of 0.37, 0.79, 0.53, and 1.13 seconds, approaching that common landing from different tempos. Their final attacks align to the millisecond score. Held notes follow their construction positions when crossing a harmonic change.

The larger form alternates these timing behaviors with transparent long-breathed music. There is no click, delay, reverb, chorus, or deliberate vibrato. Attacks/releases are smoothed inside the written gates.

## Listening map

| Time | Scene | Nominal conductor BPM | Texture |
|---|---|---|---|
'''
for scene in s['form']:text+=f"| {clock(scene['start_seconds'])} | {scene['name']} | {scene['nominal_bpm'][0]} → {scene['nominal_bpm'][1]} | {scene['strategies'][0].replace('_',' ')} |\n"
text+='\n## Planned landings\n\n'
for land in s['rhythmic_landings']:text+=f"- **{clock(land['seconds'])}:** four independent lines arrive together, inside scene {land['section']}.\n"
text+='''
## Sounds and research

The palette retains dry OB-Xf, Surge XT, Dexed, winds, guitars, keyboards, basses, and plucked sounds. A marimba attack plus a quieter sustaining sax sample is a new programming experiment inspired by Larry Fast's description of the technique behind “Shock the Monkey,” using our own sample bank rather than his Fairlight files or melody. It is not presented as an exact patch recreation.

See `synth_configurations.md` for documented configurations and performance/programming details from Stevie Wonder, Ozric Tentacles, Peter Gabriel/Larry Fast, and Kate Bush. Historical effects chains are described there but not copied into this dry render. Exact patch claims are distinguished from practical inferences and modern reconstructions.

## Reproduce

Run from the archive root:

```sh
python calcutta/elastic_piece.py
python calcutta_elastic/render.py
python calcutta_elastic/package.py
```

Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, OB-Xf 1.0.3, Surge XT with patch-format 31 support, and Dexed. SoundFonts: TimGM6mb and GeneralUser GS (https://schristiancollins.com/generaluser.php). Third-party binaries/sample banks are not bundled; configure their paths as shown by the renderer. Fixed instrument calibration and saved synth states are included.

The composer reads only the voice palette from `calcutta_motifs/score.json`, and the original endpoint matrix from `composition_32_voices_v3/score_and_sounds.json`. It creates all musical events and the form afresh. `seconds_per_tick` is 0.001: note timing is stored in milliseconds, unlike earlier scores.

The MIDI includes the performed microtiming and a dense real tempo map at PPQ 960, with 53 instrumental tracks on four ports and independent ±2-semitone pitch bends. It is checked to agree with the audio duration within 5 ms. It does not embed plugin states or the rendered master-volume envelope. The JSON/renderer remain authoritative for the supplied audio.
'''
(root/'calcutta_elastic_guide.md').write_text(text)
for n in s['notes']:
 h=s['harmonies'][n['harmony']];assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end']
for landing in s['rhythmic_landings']:
 tick=round(landing['seconds']*1000);assert len([n for n in s['notes'] if abs(n['start_tick']-tick)<=1 and n['role']=='rhythmic suspension'])>=4
with zipfile.ZipFile(root/'calcutta_elastic_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 files=[Path('calcutta')/name for name in ['elastic_piece.py','mixed_synths.py','instrument_sketch.py','polyphonic.py','calcutta.py','scalar_runs.py','render.py']]
 files += [Path('COMPOSITION_GUIDELINES.md'),Path('calcutta_motifs/score.json'),Path('calcutta_full_fixed/levels.jsonl'),Path('composition_32_voices_v3/score_and_sounds.json')]
 files+=list(Path('motif_patches').glob('*'))+list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
 files += [root/name for name in ['score.json','render.py','package.py','calcutta_elastic.mid','calcutta_elastic_guide.md','synth_configurations.md','levels.jsonl','section_levels.json'] if (root/name).exists()]
 for path in files:z.write(path,str(path))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nmido\npedalboard==0.9.26\n')
print('Performed MIDI duration',actual,'seconds; real tempo map, field bounds, and simultaneous landings verified')
