"""Gentle stereo-linked peak control; no change to event attacks or release gates."""
import numpy as np

def balance(audio,rate,target=.09,ceiling=.78):
    audio*=target/max(float(np.sqrt(np.mean(audio*audio))),1e-9)
    block=round(rate*.005);n=len(audio);padded=np.pad(np.max(np.abs(audio),axis=1),(0,(-n)%block))
    peaks=np.max(padded.reshape(-1,block),axis=1)
    # A neighboring peak constrains both interpolation anchors around its block.
    protected=np.maximum.reduce([np.r_[peaks[0],peaks[:-1]],peaks,np.r_[peaks[1:],peaks[-1]]])
    required=np.minimum(1.,ceiling/np.maximum(protected,1e-9));gain=required.copy();decay=np.exp(-block/(rate*.06))
    for i in range(1,len(gain)):gain[i]=min(required[i],gain[i-1]*decay+1-decay)
    centers=(np.arange(len(gain))+.5)*block
    for start in range(0,n,rate*10):
        stop=min(n,start+rate*10);audio[start:stop]*=np.interp(np.arange(start,stop),centers,gain)[:,None]
    assert float(np.max(np.abs(audio)))<=ceiling+1e-5
    return audio,dict(minimum_peak_gain=float(min(gain)),rms=float(np.sqrt(np.mean(audio*audio))),peak=float(np.max(np.abs(audio))))
