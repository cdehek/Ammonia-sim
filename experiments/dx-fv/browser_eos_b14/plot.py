"""Evidence plots, no interpolated state is represented as accepted."""
import os,json
from pathlib import Path
B=Path(__file__).resolve().parent;os.environ['MPLCONFIGDIR']=str(B/'.runtime/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
E=B/'evidence';F=B/'figures';F.mkdir(exist_ok=True)
def read(n):return json.loads((E/(n+'.json')).read_text())
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False})
a=read('accepted-warm');t=read('temporal-warm');event=read('transition-bracket')['event'];sel=[r for r in a if .005<=r['seconds']<=.0056]
fig,axes=plt.subplots(3,1,figsize=(8,8),sharex=True,layout='constrained')
x=[r['seconds']*1000 for r in sel]
axes[0].plot(x,[r['sections'][0]['derived']['hMinusHgKJkg']for r in sel],'o-',ms=3);axes[0].axhline(0,color='0.5',lw=.8);axes[0].set_ylabel('Section 0 h − hg (kJ/kg)')
axes[0].axvspan(event['bracketStartSeconds']*1000,event['bracketEndSeconds']*1000,color='0.8',label='Accepted phase bracket');axes[0].legend()
for label,key in [('accepted',True),('rejected',False)]:
 r=[v for v in t if .005<=v['startSeconds']<=.0056 and v['accepted']==key];axes[1].scatter([v['startSeconds']*1000 for v in r],[v['originalError']for v in r],marker='o'if key else'x',label=label,s=25)
axes[1].axhline(1,color='0.5',lw=.8);axes[1].set_yscale('log');axes[1].set_ylabel('Original temporal maximum');axes[1].legend()
axes[2].plot(x,[r['endpoint']['faces'][1]['massKgS']for r in sel],'o-',ms=3);axes[2].axhline(0,color='0.5',lw=.8);axes[2].set_ylabel('Face 1 flow (kg/s)');axes[2].set_xlabel('Accepted time / trial start (ms)')
fig.suptitle('Warm phase bracket, error trials and hydraulic reversal\nMarkers are actual accepted endpoints or attempted trial starts')
fig.savefig(F/'warm-transition.png',dpi=160);fig.savefig(F/'warm-transition.svg');plt.close(fig)
a=read('analysis');fig,axes=plt.subplots(2,1,figsize=(9,7),layout='constrained')
for ax,f in zip(axes,['cold','warm']):
 vals=a['timing'][f]['observed'];col=a['fixtures'][f]['columnTotals'];means=[];lo=[];hi=[]
 for k in range(21):
  x=sorted(v['columnMS'][k]for v in vals);means.append(x[1]);lo.append(x[1]-x[0]);hi.append(x[-1]-x[1])
 ax.bar(range(21),means,color=['#356a91']*10+['#aa7755']*11);ax.errorbar(range(21),means,yerr=[lo,hi],fmt='none',ecolor='black',capsize=2,lw=.7);ax.set_xticks(range(21),[v['label']for v in col],rotation=55,ha='right');ax.set_ylabel('Inclusive column total (ms)');ax.set_title(f.capitalize()+' — median and range, 3 diagnostic processes')
fig.suptitle('Jacobian column timing includes residual/property work\nDiagnostic overhead is substantial; these are not uninstrumented exclusive costs')
fig.savefig(F/'jacobian-columns.png',dpi=160);fig.savefig(F/'jacobian-columns.svg');plt.close(fig)

# SVG path-data newlines remain separators after trailing-space normalization.
for p in F.glob('*.svg'):
 p.write_text('\n'.join(line.rstrip()for line in p.read_text().splitlines())+'\n')
