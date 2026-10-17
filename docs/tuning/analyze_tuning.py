"""Reproduce README figures and numerical checks from the tuning generator.

Run from any directory with Python, numpy and matplotlib installed.
"""
from collections import Counter
import json
import math
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from calcutta import Calcutta,build_structure

OUT=Path(__file__).resolve().parent
piece=Calcutta()
phi=(1+math.sqrt(5))/2
fifth=1200*math.log2(3/2)
span=piece.outer_interval
third=fifth/phi
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,
                     'axes.titlesize':14,'axes.labelsize':11,'figure.facecolor':'white',
                     'axes.spines.top':False,'axes.spines.right':False,
                     'savefig.facecolor':'white'})
BLUE='#246a9b';ORANGE='#cc702b';GRAY='#67747d'

# Exact symbolic arithmetic in Z[phi], normalized to the pure fifth.
# Four possible branch shifts: phi^2, phi, 1, phi^-1.
starts=[(0,0)]
for da,db in [(1,1),(0,1),(1,0),(-1,1)]:
    starts=starts+[(a+da,b+db) for a,b in starts]
counts=Counter(starts+[(a+1,b) for a,b in starts])
limit=sorted([(fifth*(a+b*phi),n,a,b) for (a,b),n in counts.items()])
assert len(counts)==16 and sum(counts.values())==32
limit_expanded=sorted([v for v,n,_,_ in limit for _ in range(n)])
assert max(abs(v-(p*100-4800)) for v,p in zip(limit_expanded,piece.harmonies[-1]))<1e-8

raw=[]
for _,_,ratio in piece.ratios:
    raw.append([point for pair in build_structure(0,span,ratio)[-1] for point in pair])
raw=np.array(raw)
raw_limit=np.array([point for pair in build_structure(0,span,phi)[-1] for point in pair])
errors=[max(abs(v-w) for v,w in zip(sorted(row),limit_expanded)) for row in raw]

fig,axes=plt.subplots(3,1,figsize=(10,7.7),sharex=True,layout='constrained')
for ax,(name,r) in zip(axes,[('First chord: child = 1/2 of parent',2),
                            ('Second chord: child = 2/3 of parent',1.5),
                            ('Limit: child = 1/phi of parent',phi)]):
    c=1/r
    ax.plot([0,1],[2,2],color=GRAY,lw=5,solid_capstyle='butt')
    ax.plot([0,c],[1,1],color=BLUE,lw=8,solid_capstyle='butt')
    ax.plot([1-c,1],[0,0],color=ORANGE,lw=8,solid_capstyle='butt')
    ax.axvspan(1-c,c,color=BLUE,alpha=.07)
    for x,y in [(0,2),(1,2),(0,1),(c,1),(1-c,0),(1,0)]:
        ax.scatter([x],[y],s=25,color=GRAY if y==2 else BLUE if y==1 else ORANGE,zorder=4)
    ax.set_yticks([0,1,2],['Upper child','Lower child','Parent'])
    ax.set_ylim(-.5,2.7);ax.set_xlim(-.02,1.02)
    ax.set_title(name,loc='left',pad=2)
    ax.spines[['left','bottom']].set_visible(False)
    ax.tick_params(axis='y',length=0)
axes[-1].set_xticks([0,.25,.5,.75,1],['0','25%','50%','75%','100%'])
axes[-1].set_xlabel('Position within the parent interval, measured in cents')
fig.savefig(OUT/'overlapping_intervals.png',dpi=170);plt.close(fig)

fig,(ax,zoom)=plt.subplots(2,1,figsize=(10,8),height_ratios=[2.2,1],layout='constrained')
x=np.arange(1,13)
for p in range(32):ax.plot(x,raw[:12,p],color=BLUE,alpha=.42,lw=1.1)
for v,_,_,_ in limit:ax.axhline(v,color=GRAY,alpha=.2,lw=.7)
ax.set(xlim=(1,12),ylim=(-100,span+100),xlabel='Chord number',ylabel='Cents above the lowest pitch')
ax.set_xticks(range(1,13));ax.set_yticks([0,1200,2400,3600,4800])
ax.grid(axis='x',alpha=.12)
ax.set_title('Large rearrangements become small tuning adjustments',loc='left')
target=fifth*(1+phi)
indices=np.where(abs(raw_limit-target)<1e-7)[0]
assert len(indices)==4
for i in indices:zoom.plot(x[3:],raw[3:12,i]-target,color=BLUE,lw=1.6,alpha=.7)
zoom.axhline(0,color=GRAY,lw=1)
zoom.set(xlim=(4,12),xlabel='Chord number',ylabel='Deviation (cents)')
zoom.set_xticks(range(4,13))
zoom.set_title('Close-up: four endpoints converge at 1837.742 cents',loc='left')
fig.savefig(OUT/'pitch_convergence.png',dpi=170);plt.close(fig)

fig,ax=plt.subplots(figsize=(10,4.7),layout='constrained')
ax.semilogy(range(1,21),errors[:20],'-o',color=BLUE,markersize=4)
ax.axhline(1,color=GRAY,lw=.9,linestyle='--')
ax.text(19.7,1.3,'1 cent (scale reference)',ha='right',color=GRAY)
for n in [1,4,6,8,10]:
    ax.annotate(f'{errors[n-1]:.3g}',(n,errors[n-1]),xytext=(5,9),textcoords='offset points')
ax.set(xlim=(.5,20.5),xlabel='Chord number',ylabel='Maximum pitch error (cents, logarithmic scale)')
ax.set_xticks([1,4,8,12,16,20]);ax.grid(alpha=.15)
ax.set_title('Distance from the limiting chord falls rapidly',loc='left')
fig.savefig(OUT/'convergence_error.png',dpi=170);plt.close(fig)

fig,(ax,lower)=plt.subplots(2,1,figsize=(11,7.2),height_ratios=[1.3,1],layout='constrained')
parent=fifth*phi
for a,b,y,color in [(0,fifth,1.5,BLUE),(third,parent,.9,ORANGE)]:
    ax.plot([a,b],[y,y],color=color,lw=7,solid_capstyle='butt')
    ax.scatter([a,b],[y,y],color=color,s=30,zorder=3)
ax.text(fifth/2,1.67,'701.955 cents: pure 3:2 fifth',ha='center',color=BLUE)
ax.text((third+parent)/2,1.07,'701.955 cents: another pure fifth',ha='center',color=ORANGE)
points=[0,third,fifth,parent]
ax.scatter(points,[.25]*4,color=BLUE,s=45)
for v,label in zip(points,['Root\n0','Sharp major third\n433.832','Fifth\n701.955','Upper endpoint\n1135.787']):
    ax.text(v,.05,label,ha='center',va='top')
ax.set(xlim=(-130,parent+150),ylim=(-.55,2.1))
ax.axis('off');ax.set_title('A final sibling pair contains the 0–433.832–701.955 triad',loc='left')
vals=[v for v,_,_,_ in limit];mult=[n for _,n,_,_ in limit]
lower.scatter(vals,[1]*16,s=[45*n for n in mult],color=BLUE,alpha=.8)
for v,n in zip(vals,mult):lower.text(v,1.19,f'×{n}',ha='center')
lower.set(xlim=(-100,span+100),ylim=(.7,1.5),xlabel='Cents above the lowest pitch')
lower.set_xticks([0,1200,2400,3600,4800]);lower.set_yticks([])
lower.spines[['left','bottom']].set_visible(False)
lower.set_title('32 endpoints converge to 16 distinct pitches; labels show multiplicity',loc='left')
fig.savefig(OUT/'limiting_chord.png',dpi=170);plt.close(fig)

data={'outer_interval_cents':span,'golden_ratio':phi,'fifth_cents':fifth,
      'third_cents':third,'third_above_12tet_cents':third-400,
      'third_above_just_cents':third-1200*math.log2(5/4),
      'limiting_pitches':[{'cents':v,'multiplicity':n,'a':a,'b':b} for v,n,a,b in limit],
      'chords':[{'number':i+1,'ratio':f'{b}/{a}','child_fraction':f'{a}/{b}',
                 'max_sorted_error_cents':errors[i]} for i,(a,b,_) in enumerate(piece.ratios)]}
(OUT/'analysis.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({k:v for k,v in data.items() if k not in ['limiting_pitches','chords']},indent=2))
