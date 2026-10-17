"""Count the limiting chord's wide-third major triads using exact coefficients."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
data=json.loads((OUT/'analysis.json').read_text())
J=data['fifth_cents'];phi=data['golden_ratio']
positions={(p['a'],p['b']) for p in data['limiting_pitches']}
roots=sorted([(a,b) for a,b in positions if (a-1,b+1) in positions and (a+1,b) in positions],
             key=lambda v:v[0]+v[1]*phi)
assert len(roots)==7
root_values=[J*(a+b*phi) for a,b in roots]
assert all(abs(root_values[i+3]-root_values[i]-root_values[3])<1e-8 for i in range(4))
steps=[b-a for a,b in zip(root_values,root_values[1:])]
assert all(abs(a-b)<1e-8 for a,b in zip(steps,[J,J/phi,J,J,J/phi,J]))
triads=[{'root_coefficients':[a,b],'root_cents':r,
         'pitches_cents':[r,r+J/phi,r+J]} for (a,b),r in zip(roots,root_values)]
(OUT/'triad_roots.json').write_text(json.dumps({'triads':triads,'root_steps_cents':steps},indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.titlesize':14,
                     'axes.spines.top':False,'axes.spines.right':False,
                     'figure.facecolor':'white','savefig.facecolor':'white'})
fig,(ax,chain)=plt.subplots(2,1,figsize=(11,7.5),height_ratios=[3.5,1.4],layout='constrained')
colors=['#246a9b','#cc702b','#478063'];markers=['o','^','s']
for i,r in enumerate(root_values):
    y=7-i
    ax.plot([r,r+J],[y,y],color='#aab1b6',lw=1.5)
    for k,(v,c,m) in enumerate(zip([r,r+J/phi,r+J],colors,markers)):
        ax.scatter([v],[y],color=c,marker=m,s=65,zorder=3,
                   label=['Root','Wide third','Pure fifth'][k] if i==0 else None)
    ax.text(r,y+.22,f'{r:.3f}',ha='center')
ax.set(xlim=(-170,4550),ylim=(.5,8),xlabel='Cents above the lowest pitch')
ax.set_yticks(range(7,0,-1),[f'Triad {i}' for i in range(1,8)])
ax.set_xticks([0,1200,2400,3600]);ax.grid(axis='x',alpha=.15)
ax.legend(loc='upper left',ncol=3,frameon=False)
ax.set_title('Seven triads, seven roots: every triad has the same 433.832-cent third',loc='left')
chain.plot(root_values,[0]*7,color='#aab1b6',lw=1.5)
chain.scatter(root_values,[0]*7,color=colors[0],s=42,zorder=3)
for i,(a,b) in enumerate(zip(root_values,root_values[1:])):
    label='Fifth\n701.955' if i in [0,2,3,5] else 'Wide third\n433.832'
    chain.text((a+b)/2,.23,label,ha='center',va='bottom')
for i,r in enumerate(root_values):chain.text(r,-.17,f'R{i+1}',ha='center',va='top')
chain.set(xlim=(-170,4550),ylim=(-.6,.85));chain.axis('off')
chain.set_title('Each next root is a chord tone of the preceding triad',loc='left')
fig.savefig(OUT/'triad_roots.png',dpi=170);plt.close(fig)
print(json.dumps({'distinct_triads':len(roots),'roots_cents':root_values,'root_steps_cents':steps},indent=2))
