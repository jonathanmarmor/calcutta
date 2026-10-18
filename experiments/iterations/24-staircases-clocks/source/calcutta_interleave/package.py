from pathlib import Path
import json,zipfile,sys,math
import numpy as np,mido
root=Path('calcutta_interleave');s=json.loads((root/'score.json').read_text())
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
f.save(root/'calcutta_interleave.mid')
actual=mido.MidiFile(root/'calcutta_interleave.mid').length;assert abs(actual-s['duration_seconds'])<.01,(actual,s['duration_seconds'])
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'

text = '# Calcutta: Staircases and Clocks\n\n8:20. Thirteen new scenes with twelve unison blends and eight exposed individual instruments; prompt dry foreground attacks with a louder overall mix; slower entrances reserved for a few background notes. No click, reverb, delay, chorus, deliberate vibrato, or retuning of held notes.\n\n## Listening\n\nQuiet mosaics unfold all 32 construction pitches of every original field across time, rather than returning to full-ensemble attacks. In the foreground, short contours recur with stable rhythmic identities, shift through field degrees, and change their spacing. The score searches each original field for sharp-third triads and fifths, then fourth-note extensions near harmonic or major sevenths. Recurring contours climb and descend those root-ordered stacks, with a small fourth-repeat mutation. Separate lines maintain independent pulse periods (roughly 37–78 BPM), often with skipped attacks and longer holds. Conductor rubato is under 1 BPM. A light stereo-linked peak envelope raises average loudness while keeping dry, prompt attacks; it adds no ambience. This version uses only exact original-field pitches. The twelve composite instruments alternate with eight exposed single instruments. The ensemble stops before a short, unanswered solo Clavinet ending: no master fade. Each note ends before a harmony boundary.\n\nThe synthesizer palette includes twelve new TAL-NoiseMaker, OB-Xf, and Surge XT patches, plus Dexed FM and GeneralUser GS / TimGM samples. They evoke single-oscillator analog, Oberheim, ladder-filter, and FM approaches from the earlier research; these are new patches, not claimed reconstructions of particular records. All layered components play the same exact pitch, with independent fixed balance gains.\n\n## Blended instruments\n\n'
for c in s['composites']:
 text += '- **'+c['name']+'**: '+', '.join(x['name']+' × '+str(x['gain']) for x in c['components'])+'.\n'
text += '\n## Form\n\n| Time | Scene |\n|---|---|\n'
for x in s['form']:text+='| '+clock(x['start_seconds'])+' | '+x['name']+' |\n'
text += '\n## Reproduce\n\nRun `python calcutta/interleave_piece.py`, `python calcutta_interleave/render.py`, and `python calcutta_interleave/package.py` from the archive root. Install numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg, TAL-NoiseMaker 5.0.6, OB-Xf 1.0.3, Surge XT with patch-format 31 support, Dexed, GeneralUser GS and TimGM6mb. Configure the native-library and plugin paths as shown in the renderer. Plugin binaries and sample banks are not bundled. Synth states, the original tuning matrix, source, fixed sound calibration results, and the complete millisecond score are included. MIDI carries independent pitch-bend tracks and the performed tempo map; it does not contain plugin states or the audio master envelope.\n'
(root/'calcutta_interleave_guide.md').write_text(text)
with zipfile.ZipFile(root/'calcutta_interleave_source.zip','w',zipfile.ZIP_DEFLATED) as z:
 files=list(Path('calcutta').glob('*.py'))+list(Path('palette_murmur').glob('*.vststate'))+[Path('palette_murmur/build.py'),Path('palette_murmur/synths.json'),Path('calcutta_murmur/score.json')]
 files+=list(Path('motif_patches').glob('*.vststate'))+list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
 files += [Path('calcutta_motifs/score.json'),Path('composition_32_voices_v3/score_and_sounds.json'),Path('calcutta_full_fixed/levels.jsonl')]
 files += [p for p in root.iterdir() if p.suffix in ['.py','.json','.jsonl','.md','.mid']]
 for p in files:z.write(p,str(p))
 z.writestr('README.md',text);z.writestr('requirements.txt','numpy\nmido\npedalboard==0.9.26\n')
print('Performed MIDI verified',actual)
