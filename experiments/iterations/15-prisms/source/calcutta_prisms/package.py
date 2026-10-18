import json,sys,inspect,zipfile
from pathlib import Path
import mido
sys.path.insert(0,str(Path('calcutta').resolve()))
from phrased_preview import midi
root=Path('calcutta_prisms');s=json.loads((root/'score.json').read_text())
fn=inspect.getsource(midi).replace("chr(65+h['chord'])","h['chord']+1").replace(".length-72", ".length-score['duration_seconds']")
namespace={'mido':mido};exec(fn,namespace);namespace['midi'](s,root/'calcutta_prisms.mid')
def clock(t):return f'{int(t)//60}:{t%60:04.1f}'
text='''# Calcutta: Prisms

A 9:21.6 piece for 32 distinct instrumental voices. Quarter note = 100, 4/4. No click, reverb, or chorus. Each voice follows its original position in the tuning ladder; no voices are merged when pitches converge.

Shared attacks have unequal instrumental balances and shaped dynamic arcs. A few timbres lead while others sit much further back. Longer sustains remain, alongside shared breaths and exposed entries.

Pitch-aware hockets connect single-note voices into little melodies. The search uses actual sounding register, choosing steps of 75–335 cents and favoring 100, 200, and 300 cents. It searches anew when the tuning changes; pitches are never snapped to equal temperament or reassigned between voices.

Exposed harmonic windows bring out the tuning's sharp-third major triads and four-note extensions. The latter use the nearest available harmonic seventh (968.826 cents) or major seventh (1088.269 cents), within 40 cents. These are approximate consonant elements, not ordinary equal-tempered or pure just-intonation chords. Early harmonies without a suitable triad expose their closest available fifth instead.

The form alternates coordinated ensembles, exposed voices, and hybrids. Recurring strategies change speakers and register. The central convergence and final apertures occur only once. Section-wide dynamics flow independently of note accents, with a large crest, a retreat, and a fading ending.

## Interaction strategies

'''
for k,v in s['strategy_descriptions'].items():
    if k not in {n['strategy'] for n in s['notes']}:continue
    text+=f"- **{k.replace('_',' ').title()}:** {v}\n"
text+='\n## Listening map\n\nTimes are section boundaries; dynamic transitions flow between sections.\n\n| Time | Bars | Texture | Dynamic target* |\n|---|---|---|---|\n'
for f in s['form']:text+=f"| {clock(f['start_seconds'])} | {f['start_bar']}–{f['start_bar']+5} | {' + '.join(x.replace('_',' ') for x in f['strategies'])} | {f['dynamic_db']:+} dB |\n"
text+='\n*Relative section-envelope targets, not measured output loudness. Instrument activity and accents also shape the result.\n\n## Reproduction\n\nThe source archive contains the deterministic composer, renderer, score, fixed calibration, pitch source, and synth states. Run from the archive root. Dependencies: Python, numpy, mido, pedalboard 0.9.26, FluidSynth, ffmpeg; install Vital, Surge XT, and Dexed VST3 plugins under `synth_runtime` using the paths in `calcutta/mixed_synths.py`. SoundFonts: TimGM6mb plus GeneralUser GS (https://schristiancollins.com/generaluser.php), placed as shown by the renderer. These third-party binaries and sample banks are not bundled. The MIDI has 32 tracks on three ports and requires independent pitch-bend channels with ±2-semitone ranges. It does not embed synth presets or the master audio dynamic envelope; the renderer/score are authoritative for the supplied recording.\n'
text+='\n## Exposed consonances\n\nThe listed intervals are octave-reduced distances from the chosen root; instruments may voice these across different octaves. Voice numbers preserve construction identity.\n\n| Time | Voices | Sonority | Intervals above root (cents) |\n|---|---|---|---|\n'
for h in s['consonance_highlights']:
    intervals=', '.join(str(x) for x in h.get('intervals_cents',[])) or f"fifth error {h['fifth_error_cents']:+} cents"
    text+=f"| {clock(h['start_tick']*.05)} | {', '.join(map(str,h['voices']))} | {h['label']} | {intervals} |\n"
text+='\nThe word “seventh” identifies a four-note extension of the triad; the exact interval in the table distinguishes its type and tuning deviation.\n'
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
print('Validated',len(s['notes']),'segments, 32 voices, pitch-aware strategies; max sustain beats',max(durations),'notes >=4 beats',sum(x>=4 for x in durations))
with zipfile.ZipFile(root/'calcutta_prisms_source.zip','w',zipfile.ZIP_DEFLATED) as z:
    paths=[Path('calcutta/prism_piece.py'),Path('calcutta/mixed_synths.py'),Path('calcutta/instrument_sketch.py'),Path('calcutta/phrased_preview.py'),Path('calcutta_full/score.json'),Path('calcutta_full_fixed/levels.jsonl'),Path('composition_32_voices_v3/score_and_sounds.json'),root/'render.py',root/'package.py',root/'score.json',root/'calcutta_prisms.mid',root/'listening_guide.md']
    paths+=list(Path('composition_32_voices_v3/patches').glob('*.vststate'))
    paths += [Path('calcutta')/name for name in ['polyphonic.py','calcutta.py','scalar_runs.py','render.py']]
    paths += [root/name for name in ['levels.jsonl','section_levels.json'] if (root/name).exists()]
    for p in paths:z.write(p,str(p))
    z.writestr('README.md',text)
