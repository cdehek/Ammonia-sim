"""Plots only actual retained pairs/counts; no estimates or outlier trimming."""
from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parent/'.runtime/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parent;F=B/'figures';F.mkdir(exist_ok=True)
A=json.loads((B/'evidence/analysis.json').read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(11,4.8),sharey=True)
labels=['Cold, fresh','Warm, fresh','Cold, 2 warmups','Warm, 2 warmups']
for ax,(runtime,key,metric)in zip(axes,[('Node 24','node','wallMS'),('Chromium Worker 154','worker','computeMS')]):
 for i,(w,f)in enumerate((w,f)for w in [0,2]for f in ['cold','warm']):
  row=A[key][f'{f}-warmups{w}-{metric}'];values=[p['improvementPercent']for p in row['pairs']]
  ax.scatter(values,[i+(j-2.5)*.035 for j in range(6)],s=35,color='#176b82',zorder=3)
  ax.plot([row['improvementPercent']['median']]*2,[i-.22,i+.22],color='#dc6334',lw=3)
 ax.axvline(0,color='#333',lw=1);ax.set_yticks(range(4),labels);ax.set_title(runtime);ax.set_xlabel('Paired improvement % (positive = faster)');ax.grid(axis='x',alpha=.2)
axes[0].invert_yaxis();fig.suptitle('B16: all six pairs per case; orange = median paired result')
fig.text(.5,.015,'One Linux cloud host · 0.01 s bounded solves · >0.001 s UNQUALIFIED RESEARCH · no owner-device qualification',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.05,1,.94));fig.savefig(F/'paired-performance.png',dpi=160);plt.close(fig)
C=json.loads((B/'evidence/context-counts.json').read_text())
fig,ax=plt.subplots(figsize=(7,4));positions=[0,1];original=[];candidate=[]
for f in ['cold','warm']:
 original.append(next(r for r in C['rows']if r['fixture']==f and r['variant']=='control')['advanceCounts']['pressureBrackets'])
 candidate.append(next(r for r in C['rows']if r['fixture']==f and r['variant']=='candidate')['advanceCounts']['pressureBrackets'])
ax.bar([p-.18 for p in positions],original,width=.36,label='Original',color='#176b82');ax.bar([p+.18 for p in positions],candidate,width=.36,label='B15 candidate',color='#dc6334');ax.set_xticks(positions,['Cold','Warm']);ax.set_ylabel('Pressure bracket operations during advance');ax.set_title('Exact work counts; original Node schedule');ax.legend();fig.tight_layout();fig.savefig(F/'pressure-work.png',dpi=160);plt.close(fig)
print('Wrote two figures from actual pairs and counted source operations')
