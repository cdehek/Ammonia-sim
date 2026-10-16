"""Retains initial diagnostic failure, solves physical equations without irrelevant hom root."""
import json,os,time
from pathlib import Path
import reference as r
B=Path(__file__).resolve().parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'));mp=r.mp;hp=r.hp
refs=r.read(E/'references.json');rows=[]
for row in refs['rows']:
 out=dict(key=row['case']['key'],targets={})
 for name,t in row['targets'].items():
  if 'error'not in t and t['levels'][-1]['branch']!='equilibrium':continue
  d,u=[r.F(int(t[k]['numerator']),int(t[k]['denominator'])) for k in ['exactDensity','exactEnergyJkg']];levels=[]
  for prec in [65,90]:
   r.precision(prec);dd,uu=r.liftq(d),r.liftq(u);start=time.perf_counter();eq=hp.equilibrium(dd,uu,r.seed)
   assert 0<=eq['Q']<=1
   st={phase:r.stability(eq[dkey],eq['T']) for phase,dkey in [('liquid','rhoL'),('vapor','rhoV')]}
   assert all(x['cv']>0 and x['dp_drho_T']>0 and x['cp']>0 for x in st.values())
   levels.append(r.enc(dict(dps=prec,branch='equilibrium',selected=eq,pMinusLimit=eq['p']-3500000,endpointStability=st,seconds=time.perf_counter()-start)))
  out['targets'][name]=dict(initialFailure=t.get('error'),levels=levels,phaseEvidence='HIGH_PRECISION_DIAGNOSTIC, no certified coexistence enclosure')
 if out['targets']:rows.append(out)
p=E/'equilibrium-supplement.json';assert not p.exists();p.write_text(json.dumps(dict(initialFailuresPreserved=True,rows=rows),indent=2)+'\n')
print('physical-equation supplement',len(rows),'cases')
