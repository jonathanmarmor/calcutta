import ctypes as ct
import ctypes.util
import os
import numpy as np
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

