from pathlib import Path
import os,json
B=Path(__file__).resolve().parent;os.environ['MPLCONFIGDIR']=str(B/'.runtime/mpl');os.environ['XDG_CACHE_HOME']=str(B/'.runtime/cache');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
x=json.loads((B/'evidence/performance-analysis.json').read_text());D=B/'figures';D.mkdir(exist_ok=True)
fig,axes=plt.subplots(2,2,figsize=(10,7),constrained_layout=True)
for ax,(k,v) in zip(axes.flat,x['statistics'].items()):
 for p in v['pairs']:ax.plot([0,1],[p['controlWallMS'],p['candidateWallMS']],marker='o',alpha=.7,label='pair '+str(p['pair']))
 ax.set_xticks([0,1],['Original','Candidate']);ax.set_ylabel('Wall time (ms)');ax.set_title(k+'; six pairs');ax.grid(axis='y',alpha=.2)
fig.suptitle('B15 Node measurements — all samples, including vapor outlier');fig.savefig(D/'paired-wall-times.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(8,3.5),constrained_layout=True)
for i,f in enumerate(['cold','warm']):
 c=json.loads((B/'evidence/integrated-work-counts.json').read_text())['fixtures'][f];ax.bar(i-.17,c['control']['advanceCounts']['pressureBrackets'],.34,color='#46566b',label='Original'if i==0 else None);ax.bar(i+.17,c['candidate']['advanceCounts']['pressureBrackets'],.34,color='#2a9d8f',label='Candidate'if i==0 else None)
ax.set_xticks([0,1],['Cold','Warm']);ax.set_ylabel('Pressure brackets per advance through 0.01 s');ax.set_title('Detached counts: unchanged bisections and interpolation');ax.legend();fig.savefig(D/'pressure-search-counts.png',dpi=160)
