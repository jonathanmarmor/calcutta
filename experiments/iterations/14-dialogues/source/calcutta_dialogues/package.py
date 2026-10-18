import json,sys,inspect,zipfile
from pathlib import Path
import mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from phrased_preview import midi
root=Path('calcutta_dialogues');s=json.loads((root/'score.json').read_text())
fn=inspect.getsource(midi).replace("chr(65+h['chord'])","h['chord']+1").replace(".length-72", ".length-score['duration_seconds']")
namespace={'mido':mido};exec(fn,namespace);namespace['midi'](s,root/'calcutta_dialogues.mid')
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'
text='''# Calcutta: Dialogues

A 9:21.6 piece for 32 distinct instrumental voices. Quarter note = 100, 4/4. No click, reverb, or chorus. Each voice follows its original position in the tuning ladder; no voices are merged when pitches converge.

Longer notes now sit inside shared phrases. Some instruments hold across several beats while others leave space around them. At harmonic boundaries, a held voice follows its new chord pitch. Sampled plucked/struck instruments still decay naturally; woodwinds, organs, and synths carry the longest sustained roles.

The form alternates coordinated ensembles, exposed voices, and hybrids. Recurring strategies change speakers and register. The central convergence and final apertures occur only once. Section-wide dynamics move independently of note accents, with a large crest followed by a sudden retreat and a fading ending.

## Thirteen interaction strategies

'''
for k,v in s['strategy_descriptions'].items():text+=f"- **{k.replace('_',' ').title()}:** {v}\n"
text+='\n## Listening map\n\nTimes are section boundaries; dynamic transitions flow between sections.\n\n| Time | Bars | Texture | Dynamic target* |\n|---|---|---|---|\n'
for f in s['form']:text+=f"| {clock(f['start_seconds'])} | {f['start_bar']}–{f['start_bar']+5} | {' + '.join(x.replace('_',' ') for x in f['strategies'])} | {f['dynamic_db']:+} dB |\n"
text+='\n*Relative section-envelope targets, not measured output loudness. Instrument activity and accents also shape the result.\n\n## Reproduction\n\nThe source archive contains the deterministic composer, renderer, score, fixed calibration, pitch source, and synth states. Run from the archive root. Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg; install Vital, Surge XT, and Dexed VST3 plugins under `synth_runtime` using the paths in `calcutta/mixed_synths.py`. SoundFonts: TimGM6mb plus GeneralUser GS (https://schristiancollins.com/generaluser.php), placed as shown by the renderer. These third-party binaries and sample banks are not bundled. The MIDI has 32 tracks on three ports and requires independent pitch-bend channels with ±2-semitone ranges. It does not embed synth presets or the master audio dynamic envelope; the renderer/score are authoritative for the supplied recording.\n'
(root/'listening_guide.md').write_text(text)
# Score invariants: all voices, construction pitches, boundaries, and monophony.
pitches=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
for v in range(32):
    notes=[n for n in s['notes'] if n['voice']==v];assert notes
    assert all(a['start_tick']+a['duration_ticks']<=b['start_tick'] for a,b in zip(notes,notes[1:]))
for n in s['notes']:
    h=s['harmonies'][n['harmony']];assert h['start']<=n['start_tick']<n['start_tick']+n['duration_ticks']<=h['end']
    assert n['pitch']==pitches[h['chord']][n['voice']]
durations=[(e['end']-e['start'])/12 for e in s['unsplit_events']]
print('Validated',len(s['notes']),'segments, 32 voices, 13 strategies; max sustain beats',max(durations),'notes >=4 beats',sum(x>=4 for x in durations))
with zipfile.ZipFile(root/'calcutta_dialogues_source.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths=[Path('calcutta/dialogue_piece.py'),Path('calcutta/mixed_synths.py'),Path('calcutta/instrument_sketch.py'),Path('calcutta/phrased_preview.py'),Path('calcutta_full/score.json'),Path('calcutta_full_fixed/levels.jsonl'),Path('composition_32_voices_v3/score_and_sounds.json'),root/'render.py',root/'package.py',root/'score.json',root/'calcutta_dialogues.mid',root/'listening_guide.md']
    paths+=list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
    for p in paths:z.write(p,str(p))
    z.writestr('README.md',text)
