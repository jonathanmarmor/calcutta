"""Smaller repository copies only where the GitHub blob API rejects large inputs."""
from pathlib import Path
import json,subprocess,os,concurrent.futures,hashlib
r=Path('suite');dest=r/'archive_audio';dest.mkdir(exist_ok=True);index=json.loads((r/'index.json').read_text())
def make(e):
 source=r/'audio'/e['audio'];target=dest/e['audio'];smaller=source.stat().st_size>40000000
 bitrate='96k' if e['duration']*16000>38000000 else '128k'
 if smaller:
  temp=target.with_suffix('.tmp');subprocess.run(['ffmpeg','-v','error','-y','-i',str(r/'audio'/f"{e['number']:02}.wav"),'-ar','48000','-codec:a','libmp3lame','-b:a',bitrate,'-metadata','title='+e['title'],'-metadata','artist=Jonathan Marmor','-f','mp3',str(temp)],check=True);temp.replace(target)
 elif not target.exists():os.link(source,target)
 d=float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(target)]))['format']['duration']);assert abs(d-e['duration'])<.12
 return dict(number=e['number'],audio=e['audio'],archive_bitrate=bitrate if smaller else '256k',archive_bytes=target.stat().st_size,archive_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),delivered_bitrate='256k',delivered_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:report=list(pool.map(make,index))
(r/'archive_audio.json').write_text(json.dumps(report,indent=2));print('Prepared repository copies; main delivered files remain 256 kbps.')
