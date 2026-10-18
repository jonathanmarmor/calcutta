"""16-bar metered sketch rendered with sampled General MIDI instruments."""
import argparse
import ctypes as ct
import ctypes.util
import json
import math
import os
from pathlib import Path
import wave

import numpy as np

from polyphonic import compose, read_midi, validate, write_midi

INSTRUMENTS = [
    ('flute',73), ('nylon guitar',24), ('clarinet',71), ('marimba',12),
    ('cello',42), ('harp',46), ('oboe',68), ('piano',0),
    ('bassoon',70), ('vibraphone',11), ('violin',40),
]


class SoundfontSynth:
    def __init__(self, soundfont, rate):
        name = os.environ.get('FLUIDSYNTH_LIBRARY') or ctypes.util.find_library('fluidsynth')
        if not name:
            raise RuntimeError('Install libfluidsynth and a General MIDI soundfont')
        self.lib = ct.CDLL(name)
        declarations = {
            'new_fluid_settings': (ct.c_void_p, []),
            'fluid_settings_setnum': (ct.c_int,[ct.c_void_p,ct.c_char_p,ct.c_double]),
            'fluid_settings_setint': (ct.c_int,[ct.c_void_p,ct.c_char_p,ct.c_int]),
            'new_fluid_synth': (ct.c_void_p,[ct.c_void_p]),
            'fluid_synth_sfload': (ct.c_int,[ct.c_void_p,ct.c_char_p,ct.c_int]),
            'fluid_synth_program_select': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_int,ct.c_int,ct.c_int]),
            'fluid_synth_pitch_bend': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_int]),
            'fluid_synth_pitch_wheel_sens': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_int]),
            'fluid_synth_cc': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_int,ct.c_int]),
            'fluid_synth_noteon': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_int,ct.c_int]),
            'fluid_synth_noteoff': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_int]),
            'fluid_synth_all_sounds_off': (ct.c_int,[ct.c_void_p,ct.c_int]),
            'fluid_synth_write_float': (ct.c_int,[ct.c_void_p,ct.c_int,ct.c_void_p,ct.c_int,ct.c_int,
                                               ct.c_void_p,ct.c_int,ct.c_int]),
            'delete_fluid_synth': (None,[ct.c_void_p]),
            'delete_fluid_settings': (None,[ct.c_void_p]),
        }
        for function,(restype,argtypes) in declarations.items():
            fn=getattr(self.lib,function)
            fn.restype,fn.argtypes=restype,argtypes
        self.settings=self.lib.new_fluid_settings()
        self.lib.fluid_settings_setnum(self.settings,b'synth.sample-rate',float(rate))
        self.lib.fluid_settings_setnum(self.settings,b'synth.gain',.7)
        self.lib.fluid_settings_setint(self.settings,b'synth.reverb.active',0)
        self.lib.fluid_settings_setint(self.settings,b'synth.chorus.active',0)
        self.synth=self.lib.new_fluid_synth(self.settings)
        self.sfid=self.lib.fluid_synth_sfload(self.synth,str(soundfont).encode(),1)
        if self.sfid < 0: raise RuntimeError('Could not load soundfont')
        self.lib.fluid_synth_pitch_wheel_sens(self.synth,0,2)
        self.rate=rate

    def samples(self,count):
        left=np.empty(count,dtype=np.float32)
        right=np.empty(count,dtype=np.float32)
        result=self.lib.fluid_synth_write_float(self.synth,count,left.ctypes.data,0,1,
                                                right.ctypes.data,0,1)
        assert result == 0
        return np.stack([left,right],axis=1)

    def note(self,pitch,velocity,program,count):
        self.lib.fluid_synth_all_sounds_off(self.synth,0)
        # Flush FluidSynth's internal block buffer before starting a new note.
        self.samples(128)
        assert self.lib.fluid_synth_program_select(self.synth,0,self.sfid,0,program)==0
        self.lib.fluid_synth_cc(self.synth,0,10,64)
        key=round(pitch)
        bend=8192+round((pitch-key)/2*8192)
        self.lib.fluid_synth_pitch_bend(self.synth,0,bend)
        assert self.lib.fluid_synth_noteon(self.synth,0,key,velocity)==0
        release=min(round(.025*self.rate),count//4)
        body=self.samples(count-release)
        self.lib.fluid_synth_noteoff(self.synth,0,key)
        tail=self.samples(release)
        sound=np.concatenate([body,tail])
        fade=min(round(.012*self.rate),count//4)
        sound[-fade:] *= np.linspace(1,0,fade,dtype=np.float32)[:,None]
        self.lib.fluid_synth_all_sounds_off(self.synth,0)
        return sound

    def close(self):
        self.lib.delete_fluid_synth(self.synth)
        self.lib.delete_fluid_settings(self.settings)


def render(piece,notes,soundfont,path,rate=44100):
    seconds=piece['seconds_per_step']
    audio=np.zeros((math.ceil(len(piece['bars'])*16*seconds*rate),2),dtype=np.float32)
    synth=SoundfontSynth(soundfont,rate)
    # Instrument-specific balance avoids sampled piano/guitar masking winds.
    gains={0:.85,11:1.05,12:1.2,24:1.25,40:.72,42:1.0,46:1.25,68:.8,70:1.0,71:.95,73:1.25}
    try:
        for note in notes:
            cell=piece['cells'][note['cell']]
            instr=piece['instruments'][cell['instrument']]
            start=round(note['start_step']*seconds*rate)
            end=round((note['start_step']+note['duration_steps'])*seconds*rate)
            sound=synth.note(note['pitch'],note['velocity'],instr['program'],end-start)
            angle=(instr['pan']+1)*np.pi/4
            sound[:,0] *= np.cos(angle)*math.sqrt(2)
            sound[:,1] *= np.sin(angle)*math.sqrt(2)
            audio[start:end] += sound*gains[instr['program']]
    finally: synth.close()
    assert np.isfinite(audio).all() and np.max(np.abs(audio))>0
    audio *= .88/np.max(np.abs(audio))
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate)
        w.writeframes((audio*32767).astype('<i2').tobytes())
    return len(audio)/rate


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--soundfont',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('output/instrument_sketch'))
    p.add_argument('--seed',type=int,default=20261011)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    piece=compose(seed=args.seed,whole_bpm=12.5,bar_count=16,metered=True)
    for i,instr in enumerate(piece['instruments']):
        name,program=INSTRUMENTS[i%len(INSTRUMENTS)]
        instr['family'],instr['program']=name,program
    piece['quarter_notes_per_minute']=50
    piece['soundfont']=args.soundfont.name
    midi=args.output/'calcutta_16_bars_q50.mid'
    write_midi(piece,midi)
    actual=read_midi(midi)
    validate(piece,actual)
    assert piece['bars']==[0,1]*4+[2,1]*4
    assert abs(piece['seconds_per_step']-.3)<1e-10
    piece['stats']['duration_seconds']=render(piece,actual,args.soundfont,args.output/'calcutta_16_bars_q50.wav')
    starts=[c['start_step']%16 for c in piece['cells']]
    piece['stats']['cell_start_positions']={str(i):starts.count(i) for i in range(16)}
    piece['stats']['instrument_families']=sorted(set(i['family'] for i in piece['instruments']))
    (args.output/'calcutta_16_bars_q50.json').write_text(json.dumps(piece,indent=2)+'\n')
    print(json.dumps(piece['stats'],indent=2))


if __name__=='__main__': main()
