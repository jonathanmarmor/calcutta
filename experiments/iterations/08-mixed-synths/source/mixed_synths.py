"""Render the saved v2 score with real Surge XT, Vital, Dexed, and FluidSynth."""
import argparse,json,math,csv,wave,random
from pathlib import Path
import numpy as np
import mido
from pedalboard import load_plugin
from instrument_sketch import SoundfontSynth
RATE=44100

def save_wav(path,a):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE)
        w.writeframes((np.clip(a,-.999,.999)*32767).astype('<i2').tobytes())

def patch(engine,name,family,**params):return dict(engine=engine,name=name,family=family,parameters=params)

def palette():
    patches=[]
    for name,family,shape,width,cutoff,typ in [
      ('Warm transistor','analog',-65,50,1800,'Classic'),
      ('Narrow pulse reed','reed',65,18,3800,'Classic'),
      ('Rounded triangle','round',-95,50,6000,'Classic'),
      ('Bright saw brass','brass',-20,50,5200,'Modern'),
      ('Hollow square','hollow',85,50,3200,'Classic'),
      ('Nasal ribbon','nasal',45,32,2200,'Modern'),
      ('Sine harmonium','organ',30,50,10000,'Sine'),
      ('Digital wire','digital',70,50,7400,'Sine'),
      ('Soft electric wind','wind',-40,65,2700,'Modern')]:
        patches.append(patch('Surge XT',name,family,a_osc_1_type=typ,a_osc_1_shape=shape,a_osc_1_width_1=width,a_filter_1_type='LP 12 dB',a_filter_1_cutoff=cutoff,a_filter_1_resonance=8))
    for name,family,dist,amount,frame,cutoff in [
      ('Liquid glass','glass','Bend',26,0,9000),('Digital oboe','reed','Pulse',58,0,5000),
      ('Soft folded ribbon','round','Squeeze',22,0,2400),('Vowel prism','vowel','Formant',32,0,7500),
      ('Silver edge','metal','Sync',17,0,11000),('Warm chip pulse','chip','Pulse',32,0,6000),
      ('Hollow porcelain','hollow','Bend',76,0,6200),('Bright folded brass','brass','Squeeze',68,0,4800),
      ('Fine spectral thread','digital','Formant',64,0,10000)]:
        patches.append(patch('Vital',name,family,oscillator_1_distortion_type=dist,oscillator_1_distortion_amount=amount,oscillator_1_wave_frame=frame,filter_1_switch=True,filter_1_cutoff__raw=(12*math.log2(cutoff/261.625565)+52)/128,filter_1_resonance=12))
    for name,family,algorithm,ratios,levels in [
      ('FM clarinet','reed',5,[1,2,1,4,1,6],[94,60,75,40,0,0]),
      ('Held electric tine','tine',5,[1,3,1,7,1,2],[93,65,74,48,0,0]),
      ('Copper FM horn','brass',5,[1,1,1,2,1,3],[93,75,68,42,0,0]),
      ('Pure wooden flute','wind',5,[1,1,1,2,1,3],[95,38,60,25,0,0]),
      ('Sustained celeste','glass',5,[1,4,1,9,1,2],[94,70,72,56,0,0]),
      ('Rubber FM bass','round',5,[1,1,1,3,1,2],[96,65,60,37,0,0]),
      ('Crystalline organ','organ',32,[1,2,3,4,5,8],[91,79,71,62,48,40]),
      ('Bronze harmonic cloud','metal',5,[1,5,1,8,1,3],[94,73,67,51,0,0])]:
        d=dict(algorithm=algorithm,feedback=0)
        for i in range(1,7):d.update({f'op{i}_f_coarse':ratios[i-1],f'op{i}_output_level':levels[i-1]})
        patches.append(patch('Dexed',name,family,**d))
    for name,program,family in [('MIDI piano',0,'piano'),('MIDI vibraphone',11,'vibes'),('MIDI tubular bells',14,'bells'),('MIDI church organ',19,'organ'),('MIDI accordion',21,'accordion'),('MIDI clarinet',71,'reed')]:
        patches.append(dict(engine='FluidSynth',name=name,family=family,program=program,parameters={}))
    assert len(patches)==32
    return patches

class Engines:
    def __init__(self,root,soundfont):
        self.paths={'Surge XT':root/'surge/usr/lib/vst3/Surge XT.vst3','Vital':next((root/'vital').rglob('Vital.vst3')),'Dexed':root/'dexed/Dexed.vst3'}
        self.gm=SoundfontSynth(soundfont,RATE)
    def load(self,p):
        if p['engine']=='FluidSynth':return None
        plug=load_plugin(str(self.paths[p['engine']].resolve()))
        engine=p['engine']
        if engine=='Surge XT':
            plug.fx_chain_bypass='All FX Off';plug.a_osc_drift=0
            plug.a_amp_eg_sustain=100;plug.a_amp_eg_release='0.0 ms';plug.a_amp_eg_attack='3.9 ms'
            for i in range(1,4):setattr(plug,f'a_osc_{i}_unison_detune','0.00 cents')
        elif engine=='Vital':
            for key in list(plug.parameters):
                if key.endswith('_switch') and key.split('_')[0] in ['reverb','delay','chorus','phaser','flanger','distortion','compressor','equalizer']:setattr(plug,key,False)
            plug.envelope_1_sustain=1;plug.envelope_1_release='0 secs'
            plug.oscillator_1_unison_detune=0;plug.oscillator_1_phase_randomization=0
            plug.oscillator_1_destination='FILTER 1'
        else:
            plug.lfo_pm_depth=0;plug.lfo_am_depth=0;plug.p_mode_sens=0
            for i in range(1,7):
                for j in range(1,5):
                    setattr(plug,f'op{i}_eg_rate_{j}',99)
                    setattr(plug,f'op{i}_eg_level_{j}',99 if j<4 else 0)
                setattr(plug,f'op{i}_osc_detune',0)
        for key,value in p['parameters'].items():
            if key.endswith('__raw'):plug.parameters[key[:-5]].raw_value=value
            else:setattr(plug,key,value)
        return plug
    def note(self,p,plug,pitch,count):
        key=round(pitch);bend=round((pitch-key)*8192/(3 if p['engine']=='Dexed' else 2))
        if plug is None:
            s=self.gm;s.lib.fluid_synth_all_sounds_off(s.synth,0);s.samples(128)
            s.lib.fluid_synth_program_select(s.synth,0,s.sfid,0,p['program'])
            s.lib.fluid_synth_cc(s.synth,0,1,0);s.lib.fluid_synth_cc(s.synth,0,77,0)
            s.lib.fluid_synth_pitch_bend(s.synth,0,8192+bend)
            s.lib.fluid_synth_noteon(s.synth,0,key,78);a=s.samples(count)
            s.lib.fluid_synth_all_sounds_off(s.synth,0)
        else:
            a=plug([(mido.Message('pitchwheel',pitch=bend).bytes(),0.),(mido.Message('note_on',note=key,velocity=78).bytes(),0.)],duration=(count+1)/RATE,sample_rate=RATE,buffer_size=512,reset=True).T[:count].copy()
        # Sub-millisecond edge rounding is inside the gate; absolutely no release tail.
        fade=min(32,count//4);a[:fade]*=np.linspace(0,1,fade)[:,None];a[-fade:]*=np.linspace(1,0,fade)[:,None]
        return a

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--soundfont',type=Path,required=True);ap.add_argument('--score',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);(args.output/'patches').mkdir(exist_ok=True)
    score=json.loads(args.score.read_text());patches=palette();eng=Engines(args.runtime,args.soundfont)
    probes=[];features=[];sustains=[]
    for i,p in enumerate(patches):
        cache=args.output/'patches'/f'probe_{i+1:02}.npy'
        if cache.exists():a=np.load(cache);plug=None
        else:
            plug=eng.load(p);a=eng.note(p,plug,69,round(2.4*RATE));np.save(cache,a)
        rms=float(np.sqrt(np.mean(a*a)));assert rms>1e-5,(p['name'],rms)
        p['probe_rms']=rms
        sustain=float(np.sqrt(np.mean(a[int(1.8*RATE):int(2.2*RATE)]**2))/np.sqrt(np.mean(a[int(.2*RATE):int(.6*RATE)]**2)))
        p['sustain_ratio']=sustain;sustains.append(sustain)
        mono=a[int(.3*RATE):int(1.3*RATE)].mean(axis=1);spec=np.abs(np.fft.rfft(mono*np.hanning(len(mono))))
        feat=np.array([np.sum(spec[max(0,int(440*h)-4):int(440*h)+5]**2) for h in range(1,30)])**.25
        feat/=max(np.linalg.norm(feat),1e-9);features.append(feat)
        probes.append(a*.12/rms)
        if plug is not None:(args.output/'patches'/f'{i+1:02}_{p["engine"].replace(" ","_")}.vststate').write_bytes(plug.raw_state)
        print('Probe',i+1,p['engine'],p['name'],'sustain',round(sustain,3),flush=True)
        del plug
    features=np.array(features);similarity=features@features.T
    edges=score['near_unison_pairs'];rng=random.Random(7017);order=list(range(32));rng.shuffle(order)
    def cost(order):
        return sum(12*(patches[order[i]]['family']==patches[order[j]]['family'])+similarity[order[i],order[j]]**4 for i,j in edges)
    c=cost(order);best=order[:];bestc=c
    for it in range(20000):
        i,j=rng.sample(range(32),2);order[i],order[j]=order[j],order[i];n=cost(order);temp=max(.003,.6*(1-it/20000))
        if n<c or rng.random()<math.exp(min(0,(c-n)/temp)):
            c=n
            if c<bestc:best,bestc=order[:],c
        else:order[i],order[j]=order[j],order[i]
    order=best;assert all(patches[order[i]]['family']!=patches[order[j]]['family'] for i,j in edges)
    audio=np.zeros((192*RATE,2),np.float32)
    for v,voice in enumerate(score['voices']):
        p=patches[order[v]];plug=eng.load(p);voice['sound']=p
        ref=eng.note(p,plug,float(np.median(np.array(score['pitches'])[:,v])),RATE)
        rms=float(np.sqrt(np.mean(ref*ref)));gain=.035/max(rms,1e-5);voice['render_gain']=gain
        angle=(voice['pan']+1)*np.pi/4;pan=np.array([np.cos(angle),np.sin(angle)])*np.sqrt(2)
        notes=[n for n in score['notes'] if n['voice']==v]
        if plug is not None:
            events=[]
            for n in notes:
                start=round(n['start']*.3*RATE);end=round((n['start']+n['duration'])*.3*RATE)
                key=round(n['pitch']);bend=round((n['pitch']-key)*8192/(3 if p['engine']=='Dexed' else 2))
                events.extend([(start,1,mido.Message('pitchwheel',pitch=bend)),(start,2,mido.Message('note_on',note=key,velocity=78)),(end,0,mido.Message('note_off',note=key))])
            messages=[(m.bytes(),t/RATE) for t,priority,m in sorted(events,key=lambda x:(x[0],x[1]))]
            track=plug(messages,duration=192+1/RATE,sample_rate=RATE,buffer_size=512,reset=True).T[:192*RATE].copy()
        for n in notes:
            start=round(n['start']*.3*RATE);end=round((n['start']+n['duration'])*.3*RATE)
            if plug is None:a=eng.note(p,plug,n['pitch'],end-start)
            else:
                a=track[start:end].copy()
                a[:32]*=np.linspace(0,1,32)[:,None];a[-32:]*=np.linspace(1,0,32)[:,None]
            assert a.shape==(end-start,2)
            audio[start:end]+=a*gain*pan
        print('Voice',v+1,p['engine'],p['name'],flush=True);del plug
    eng.gm.close();assert np.isfinite(audio).all();audio*=.89/np.max(np.abs(audio))
    save_wav(args.output/'calcutta_mixed_synths.wav',audio)
    audition=[]
    for a in probes:audition.extend([a,np.zeros((round(.35*RATE),2),np.float32)])
    preview=np.concatenate(audition);preview*=.85/max(.85,float(np.max(np.abs(preview))))
    save_wav(args.output/'palette_audition.wav',preview)
    score['render']=dict(engines=['Surge XT','Vital','Dexed','FluidSynth'],reverb=False,vibrato=False,release_tail_samples=0,edge_rounding_samples=32)
    (args.output/'score_and_sounds.json').write_text(json.dumps(score,indent=2))
    (args.output/'palette.json').write_text(json.dumps(patches,indent=2))
    with (args.output/'voice_sounds.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['voice','branch','engine','sound','family'])
        for v in score['voices']:w.writerow([v['voice'],v['branch'],v['sound']['engine'],v['sound']['name'],v['sound']['family']])
    print('COMPLETE',flush=True)
if __name__=='__main__':main()
