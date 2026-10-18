"""32 branch-preserving voices: independent random note/rest rhythms."""
import argparse, csv, json, math, random, wave
from pathlib import Path
import numpy as np
import mido
from calcutta import Calcutta
from instrument_sketch import SoundfontSynth

# Zero-based General MIDI programs; category differences drive convergence contrast.
PALETTE = [
 ('Grand piano',0,'keys'),('Electric piano',4,'electric'),
 ('Harpsichord',6,'plucked'),('Celesta',8,'bell'),('Glockenspiel',9,'bell'),
 ('Vibraphone',11,'metal'),('Marimba',12,'wood'),('Xylophone',13,'wood'),
 ('Tubular bells',14,'bell'),('Drawbar organ',16,'organ'),('Church organ',19,'organ'),
 ('Accordion',21,'free reed'),('Harmonica',22,'free reed'),
 ('Nylon guitar',24,'guitar'),('Jazz guitar',26,'guitar'),('Muted guitar',28,'guitar'),
 ('Acoustic bass',32,'bass'),('Slap bass',36,'bass'),('Synth bass',38,'synth'),
 ('Violin',40,'bowed'),('Cello',42,'bowed'),('Pizzicato strings',45,'plucked strings'),
 ('Harp',46,'harp'),('Trumpet',56,'brass'),('Trombone',57,'brass'),('French horn',60,'brass'),
 ('Alto sax',65,'reed'),('Oboe',68,'reed'),('Bassoon',70,'reed'),('Clarinet',71,'reed'),
 ('Flute',73,'flute'),('Pan flute',75,'flute')]


def compose(seed=20261017):
    model=Calcutta()
    pitches=np.array([[p/100 for pair in s[-1] for p in pair] for s in model.structures])
    assert pitches.shape==(40,32)
    assert np.allclose(np.sort(pitches,axis=1),model.harmonies)
    distance=np.min(np.abs(pitches[:,:,None]-pitches[:,None,:]),axis=0)*100
    edges=[(i,j) for i in range(32) for j in range(i+1,32) if distance[i,j]<30]
    rng=random.Random(seed)
    order=list(range(32));rng.shuffle(order)
    med=np.median(pitches,axis=0)
    def cost(order):
        c=sum(100 for i,j in edges if PALETTE[order[i]][2]==PALETTE[order[j]][2])
        # Keep bass and low winds in the lower voices, without octave displacement.
        for v,k in enumerate(order):
            program=PALETTE[k][1]
            low,high=(36,70) if program in (32,36,38,70) else (48,84) if program in (42,57,60) else (55,96) if program in (65,68,71,73,75) else (40,100)
            c+=.025*(max(0,low-med[v])**2+max(0,med[v]-high)**2)
        return c
    best=order[:];bestc=c=cost(order)
    for n in range(40000):
        i,j=rng.sample(range(32),2);order[i],order[j]=order[j],order[i]
        new=cost(order);temp=max(.02,8*(1-n/40000))
        if new<c or rng.random()<math.exp(min(0,(c-new)/temp)):
            c=new
            if c<bestc:best,bestc=order[:],c
        else:order[i],order[j]=order[j],order[i]
    order=best
    assert not [(i,j) for i,j in edges if PALETTE[order[i]][2]==PALETTE[order[j]][2]]
    pans=list(np.linspace(-.85,.85,32));rng.shuffle(pans)
    voices=[];notes=[];total=40*16
    for v,k in enumerate(order):
        name,program,family=PALETTE[k]
        voice=dict(voice=v+1,branch=f'{v//2:04b}:'+('upper' if v%2 else 'lower'),instrument=name,program=program,family=family,pan=pans[v],events=[])
        vr=random.Random(seed+1000+v);t=0;playing=bool(vr.getrandbits(1))
        while t<total:
            drawn=vr.randint(1,8);length=min(drawn,total-t)
            voice['events'].append(dict(start=t,duration=length,drawn_duration=drawn,note=playing))
            if playing:
                end=t+length;pos=t
                while pos<end:
                    chord=pos//16;stop=min(end,(chord+1)*16)
                    notes.append(dict(voice=v,start=pos,duration=stop-pos,pitch=float(pitches[chord,v]),velocity=78,chord=chord))
                    pos=stop
            t+=length;playing=not playing
        voices.append(voice)
    return dict(seed=seed,bpm=100,meter='4/4',bars_per_harmony=2,harmony_order=list(range(40)),seconds_per_eighth=.3,total_eighths=total,duration_seconds=192,voices=voices,pitches=pitches.tolist(),notes=notes,near_unison_pairs=edges)


def write_midi(piece,path):
    midi=mido.MidiFile(ticks_per_beat=480)
    conductor=mido.MidiTrack();midi.tracks.append(conductor)
    conductor.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(piece['bpm'])))
    conductor.append(mido.MetaMessage('time_signature',numerator=4,denominator=4))
    last=0
    for h in range(40):
        t=h*3840;conductor.append(mido.MetaMessage('marker',text=f'Harmony {h+1}',time=t-last));last=t
    conductor.append(mido.MetaMessage('end_of_track',time=piece['total_eighths']*240-last))
    channels=[i for i in range(16) if i!=9]
    for v,voice in enumerate(piece['voices']):
        ch=channels[v%15];tr=mido.MidiTrack();midi.tracks.append(tr)
        tr.append(mido.MetaMessage('track_name',name=f"{v+1:02} {voice['branch']} {voice['instrument']}"))
        tr.append(mido.MetaMessage('midi_port',port=v//15))
        tr.append(mido.Message('program_change',channel=ch,program=voice['program']))
        for control,value in [(101,0),(100,0),(6,2),(38,0),(101,127),(100,127),(10,round((voice['pan']+1)*63.5))]:
            tr.append(mido.Message('control_change',channel=ch,control=control,value=value))
        events=[]
        for n in piece['notes']:
            if n['voice']!=v:continue
            key=round(n['pitch']);bend=round((n['pitch']-key)*4096)
            assert abs(key+bend/4096-n['pitch'])*100<.013
            events.extend([(n['start']*240,1,mido.Message('pitchwheel',channel=ch,pitch=bend)),(n['start']*240,2,mido.Message('note_on',channel=ch,note=key,velocity=n['velocity'])),((n['start']+n['duration'])*240,0,mido.Message('note_off',channel=ch,note=key))])
        last=0
        for tick,_,message in sorted(events,key=lambda e:(e[0],e[1])):
            tr.append(message.copy(time=tick-last));last=tick
        tr.append(mido.MetaMessage('end_of_track',time=piece['total_eighths']*240-last))
    midi.save(path)
    # Verify encoded timing and microtonal pitch against the actual MIDI.
    actual=[]
    for v,tr in enumerate(mido.MidiFile(path).tracks[1:]):
        t=0;bend=0;active=None
        for m in tr:
            t+=m.time
            if m.type=='pitchwheel':bend=m.pitch
            elif m.type=='note_on' and m.velocity:active=(t,m.note+bend/4096)
            elif m.type=='note_off':
                start,pitch=active;actual.append((v,start//240,(t-start)//240,pitch));active=None
        assert active is None
    expected=[(n['voice'],n['start'],n['duration'],n['pitch']) for n in piece['notes']]
    for a,b in zip(sorted(actual),sorted(expected)):
        assert a[:3]==b[:3] and abs(a[3]-b[3])*100<.013
    assert len(actual)==len(expected)


def render(piece,soundfont,path,rate=44100):
    synth=SoundfontSynth(soundfont,rate)
    audio=np.zeros((round(piece['duration_seconds']*rate),2),np.float32)
    try:
        for v,voice in enumerate(piece['voices']):
            ref=synth.note(float(np.median(np.array(piece['pitches'])[:,v])),78,voice['program'],rate)
            rms=float(np.sqrt(np.mean(ref**2)));assert rms>1e-6
            gain=min(5,max(.15,.045/rms));voice['render_gain']=gain
            angle=(voice['pan']+1)*np.pi/4
            pan=np.array([np.cos(angle),np.sin(angle)],np.float32)*np.sqrt(2)
            for n in piece['notes']:
                if n['voice']!=v:continue
                start=round(n['start']*.3*rate);end=round((n['start']+n['duration'])*.3*rate)
                sound=synth.note(n['pitch'],n['velocity'],voice['program'],end-start)
                audio[start:end]+=sound*gain*pan
            print(f"Rendered voice {v+1}: {voice['instrument']}",flush=True)
    finally:synth.close()
    assert np.isfinite(audio).all()
    peak=float(np.max(np.abs(audio)));assert peak>0
    audio*=.89/peak
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes((audio*32767).astype('<i2').tobytes())
    piece['render']=dict(sample_rate=rate,soundfont=Path(soundfont).name,normalization=.89/peak,reverb=False,chorus=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--soundfont',required=True,type=Path)
    parser.add_argument('--output',type=Path,default=Path('output/rhythmic_voices'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    piece=compose();write_midi(piece,args.output/'calcutta_32_voices.mid')
    render(piece,args.soundfont,args.output/'calcutta_32_voices.wav')
    (args.output/'calcutta_32_voices.json').write_text(json.dumps(piece,indent=2)+'\n')
    with (args.output/'voice_instruments.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['voice','construction_branch','instrument','GM_program_1_based','pan'])
        for v in piece['voices']:writer.writerow([v['voice'],v['branch'],v['instrument'],v['program']+1,v['pan']])
    print(json.dumps(dict(duration=piece['duration_seconds'],voices=32,notes=len(piece['notes']),near_unison_pairs=len(piece['near_unison_pairs']),same_family_near_unisons=0)))
if __name__=='__main__':main()
