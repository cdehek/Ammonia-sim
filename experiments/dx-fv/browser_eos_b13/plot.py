"""Standalone diagnostic figures; requires matplotlib, never executes science."""
import os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/b13-matplotlib")
from pathlib import Path
import json,gzip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
B=Path(__file__).resolve().parent;E=B/'evidence';F=B/'figures';F.mkdir(exist_ok=True)
fig,axes=plt.subplots(2,1,figsize=(9,7),sharex=True,layout='constrained')
for fixture,ax in zip(['cold','warm'],axes):
 rows=[json.loads(l) for l in gzip.open(E/f'canonical-{fixture}-010-r1.jsonl.gz','rt')];r=[r for r in rows if r['type']=='checkpoint'][-1];s=r['science']['state'];attempts=r['attempts']
 accepted=s['trace'];rejected=[a for a in attempts if a['failure'] or a['rejectionReason']]
 ax.semilogy([x['startSeconds'] for x in accepted],[x['trialSeconds'] for x in accepted],'-o',ms=3,label='accepted adaptive trial (two half substeps)')
 ax.scatter([x['startSeconds'] for x in rejected],[x['trialSeconds'] for x in rejected],marker='x',c='firebrick',label='rejected accuracy trial',zorder=3)
 for event in s['events']:ax.axvline(event['seconds'],ls='--',c='purple',label='estimated vapor-boundary crossing')
 ax.set(title=fixture.capitalize()+' fixture — UNQUALIFIED RESEARCH',ylabel='Trial duration (s)');ax.grid(True,alpha=.25);ax.legend(fontsize=8)
axes[-1].set_xlabel('Accepted physical time at trial start (s)')
fig.suptitle('B13-A0: measured adaptive step evolution (Node 24)')
fig.savefig(F/'adaptive-steps.svg');fig.savefig(F/'adaptive-steps.png',dpi=160);plt.close(fig)
a=json.loads((E/'analysis.json').read_text());fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
labels=['Jacobian\n(includes residuals)','All residuals\n(includes properties)','Public properties','Linear solve']
for fixture,ax in zip(['cold','warm'],axes):
 ms=a['results'][fixture]['observed']['profile']['ms'];values=[ms['jacobian'],ms['residual'],sum(v for k,v in ms.items() if k.startswith('property.')),ms['linear']]
 ax.bar(range(4),values,color=['#375e97','#4c9f70','#b36a3c','#8d79a8']);ax.set_xticks(range(4),labels,fontsize=8);ax.set(title=fixture.capitalize(),ylabel='Instrumented inclusive wall time (ms)');ax.grid(axis='y',alpha=.2)
fig.suptitle('B13-A0: nested component timings — bars overlap; do not add')
fig.savefig(F/'component-profile.svg');fig.savefig(F/'component-profile.png',dpi=160)

for svg in F.glob('*.svg'):svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
