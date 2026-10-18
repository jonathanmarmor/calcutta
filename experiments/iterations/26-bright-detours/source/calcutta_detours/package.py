from pathlib import Path
import json,zipfile,sys,math
import numpy as np,mido
root=Path('calcutta_detours');s=json.loads((root/'score.json').read_text())
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
f.save(root/'calcutta_detours.mid')
actual=mido.MidiFile(root/'calcutta_detours.mid').length;assert abs(actual-s['duration_seconds'])<.01,(actual,s['duration_seconds'])
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'


text='# Calcutta: Bright Detours\n\n8:14; 46 short episodes, twenty texture types. Every episode lasts 7–14 seconds (mean 10.74). The opening offers an exposed analog lead, a slow FM melody, rapid resonant bursts, a suspended brass/wind sonority, and Rhodes/Clavinet dialogue within 42 seconds.\n\n## Synths at the front\n\nEight new unblended lead patches have their own parts: Surge XT open ladder-filter saw and resonant sequencer lead; OB-Xf silver pulse and touch brass; TAL-NoiseMaker bright hollow lead and rubber reed; Dexed FM glass and harmonic organ. They lead, answer, sustain and trade foreground roles. These are original patches using documented analog/FM techniques, not recovered artist presets or exact Pro-One/CS-80/Fairlight emulations. The previous research is preserved in the archive.\n\nTONTO-inspired open-filter monophonic lines and Ozric-inspired resonant note sequences are exposed rather than hidden underneath samples. Gabriel/Fast-inspired independent cycle lengths shape actual phrases. Two occasional acoustic/FM blends explore attack-and-body orchestration, while most parts remain individual instruments. No historical audio or artist melodies are copied.\n\n## Rhythm and form\n\nFast phrases use unequal short durations, rests, long final syllables and small mutations. Slow passages sustain separate melodic notes for several seconds, with sparse answers. Five-against-seven sentences, rapid unequal cycles, very slow canons, accumulating counterpoint, a fast foreground that suddenly withdraws, and accelerating chord-stack sequences provide different kinds of multi-tempo texture. Independent tempi are expressed by per-line timing; they are not simplified into steady MIDI clock pulses. The conductor has only half a BPM of drift.\n\nAll forty original fields occur, using selected subsets. This version prioritizes distinct inventions and clear leads rather than restating all 32 construction endpoints of every field. Every note is an exact member of its active original field. There are no passing tones, octave transpositions, glides, or mid-note retunings. Structural triads retain the tuning’s sharp thirds and fifths; available seventh extensions are used where present. The score keeps near-unison steps out of scalar paths.\n\nForeground attacks are prompt and dry. No click, reverb, delay, chorus, deliberate vibrato, or master fade. A single fixed FM tone remains after the final phrase is interrupted, then stops at its written gate. The same light stereo-linked peak control as the preceding version preserves a louder average level without forcing large chord attacks.\n\n## Listening map\n\n| Time | Idea | Original field |\n|---|---|---|\n'
for x in s['form']:text+='| '+clock(x['start_seconds'])+' | '+x['name']+' | '+str(x['harmony']+1)+' |\n'
text+='\n## Instruments\n\n'
for c in s['composites']:text+='- **'+c['name']+'**: '+', '.join(x['name']+' × '+str(x['gain']) for x in c['components'])+'.\n'
text+='\n## Reproduce\n\nRun `python calcutta/detour_piece.py`, `python calcutta_detours/render.py`, then `python calcutta_detours/package.py` from this archive’s root. The saved lead states are already included; `palette_frontier/build.py` documents how they were programmed. Python dependencies: numpy, mido, pedalboard 0.9.26. External dependencies: FluidSynth, ffmpeg, Surge XT supporting patch-format 31, OB-Xf 1.0.3, TAL-NoiseMaker 5.0.6, Dexed, GeneralUser GS and TimGM6mb. Configure paths in the renderer and FluidSynth environment variables as in earlier iterations. Native binaries and banks are not bundled. The seed is 2026101758. Exact score regeneration is distinct from byte-identical native audio. MIDI has separate monophonic pitch-bend tracks and a performed tempo map; it does not embed the sounds or the audio master envelope.\n'
(root/'calcutta_detours_guide.md').write_text(text)
with zipfile.ZipFile(root/'calcutta_detours_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 files=list(Path('calcutta').glob('*.py'))+list(Path('palette_frontier').glob('*.vststate'))+[Path('palette_frontier/build.py'),Path('palette_frontier/synths.json')]
 files+=list(Path('palette_murmur').glob('*.vststate'))
 files+=list(Path('motif_patches').glob('*.vststate'))+list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
 files += [Path('calcutta_motifs/score.json'),Path('composition_32_voices_v3/score_and_sounds.json'),Path('calcutta_full_fixed/levels.jsonl'),Path('calcutta_elastic/synth_configurations.md')]
 files += [p for p in root.iterdir() if p.suffix in ['.py','.json','.jsonl','.md','.mid']]
 for p in files:z.write(p,str(p))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nmido\npedalboard==0.9.26\n')
print('Performed MIDI verified',actual)
