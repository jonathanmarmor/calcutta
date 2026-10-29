from pathlib import Path
import json,hashlib,wave,subprocess
import numpy as np
from compose_slow import compose,envelope
r=Path('suite');p=r/'score.json';before=hashlib.sha256(p.read_bytes()).hexdigest();s=compose();assert hashlib.sha256(p.read_bytes()).hexdigest()==before;P=json.loads(Path('composition_32_voices_v3/score_and_sounds.json').read_text())['pitches']
for n in s['notes']:
 assert min(abs(n['pitch']-p) for p in P[n['source_field']])<1e-8
 assert n['start']>=0 and n['duration']>0 and n['start']+n['duration']<=840+1e-5
 assert not n.get('gliss') and not n.get('effect') and not n.get('vocal')
 if n['start']+n['duration']>558+1e-5:assert n['source_field']==39
for v in range(len(s['voices'])):
 own=[n for n in s['notes'] if n['voice']==v];assert all(a['start']+a['duration']<=b['start']+1e-5 for a,b in zip(own,own[1:]))
assert {n['source_field'] for n in s['notes']}==set(range(40))
longs=[n for n in s['notes'] if n['cloud'] is None];assert min(n['attack'] for n in longs)>15 and min(n['release'] for n in longs)>15
coverage=[]
for t in np.arange(30,800,5):
 audible=[n['pitch'] for n in longs if float(envelope(t,n['start'],n['duration'],n['attack'],n['release']))*n['gain']>.005]
 coverage.append(bool(audible) and min(audible)<51 and max(audible)>93)
assert np.mean(coverage)>.9
with wave.open('release/calcutta_slow_apertures.wav') as w:
 assert w.getframerate()==24000 and w.getnframes()==840*24000;total=0;peak=0.;energy=0.;count=0
 while b:=w.readframes(240000):
  x=np.frombuffer(b,'<i2').astype(np.float32)/32768;total+=len(b);peak=max(peak,float(max(abs(x))));energy+=float(np.dot(x,x));count+=len(x)
 assert total==840*24000*4 and peak<.76
mp3=Path('release/calcutta_slow_apertures.mp3');dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(mp3)]))['format']['duration']);assert abs(dur-840)<.12
audit=json.loads((r/'audio_audit.json').read_text());assert audit['sustained_energy_fraction']>.8 and all(v>0 for v in audit['instrument_energy'].values())
report=dict(duration=840,notes=len(s['notes']),sustained_strands=len(longs),source_sounds=len(audit['instrument_energy']),all_40_source_fields=True,minimum_sustain_attack=min(n['attack'] for n in longs),maximum_sustain_attack=max(n['attack'] for n in longs),minimum_sustain_release=min(n['release'] for n in longs),maximum_sustain_release=max(n['release'] for n in longs),full_register_coverage_fraction=float(np.mean(coverage)),only_final_field_after=558,sustained_energy_fraction=audit['sustained_energy_fraction'],peak=peak,rms=(energy/count)**.5,mp3_duration=dur,score_regeneration_identical=True,score_sha256=before,pitch_check='Each tone is a fixed exact source-field pitch; neighboring source fields overlap while fading.')
(r/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
