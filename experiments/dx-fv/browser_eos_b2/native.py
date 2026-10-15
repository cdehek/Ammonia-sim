import os
"""Matching native PH runs and independent DT evaluation of browser outputs."""
import json,struct,hashlib
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True);version=CoolProp.__version__
a=AbstractState('HEOS','Ammonia');dt=AbstractState('HEOS','Ammonia');rows=[]
for q in json.loads((B/'inputs.json').read_text()):
 p,h=q['args'];row=dict(id=q['id'],args=q['args'],inputBits=[struct.pack('>d',x).hex() for x in [p,h]],probes=[])
 def sample(p,h):
  a.update(C.HmassP_INPUTS,h,p);rho,T=a.rhomass(),a.T();dt.update(C.DmassT_INPUTS,rho,T)
  r=dict(p=p,h=h,T=T,rho=rho,Q=a.Q(),phase=int(a.phase()),pResidual=dt.p()-p,hResidual=dt.hmass()-h)
  if int(a.phase()) in [0,1,2,3,5]:r['derivatives']=dict(rhoP=dt.first_partial_deriv(C.iDmass,C.iP,C.iHmass),rhoH=dt.first_partial_deriv(C.iDmass,C.iHmass,C.iP))
  return r
 try:row['base']=sample(p,h)
 except Exception as e:row['error']=str(e);rows.append(row);continue
 for axis,step in [('P',1e-7*max(1,abs(p/1e5))*1e5),('H',1e-8*max(1,abs(h/1000))*1000)]:
  for sign in [1,-1]:
   r=dict(axis=axis,step=sign*step)
   try:
    r['output']=sample(p+(sign*step if axis=='P' else 0),h+(sign*step if axis=='H' else 0));r['crossesPhase']=r['output']['phase']!=row['base']['phase']
    r['finite']=(r['output']['rho']-row['base']['rho'])/(sign*step)
    if not r['crossesPhase'] and 'derivatives' in row['base']:r['ratio']=r['finite']/row['base']['derivatives']['rhoP' if axis=='P' else 'rhoH']
   except Exception as e:r['error']=str(e)
   row['probes'].append(r)
 rows.append(row)
audits=[]
builds=['official72'] if version.startswith('7.') else ['official8','build30','build44']
for f in sorted(E.glob('*-phase-*.json')):
 d=json.loads(f.read_text())
 if d['build'] not in builds:continue
 states=[]
 for q in d['rows']:
  for label,s in [('base',q.get('base'))]+[(f"{p['axis']}{p['step']}",p.get('output')) for p in q['probes']]:
   if not s:continue
   r=dict(id=q['id'],label=label,p=s['p'],h=s['h'],rho=s['state']['rho'],T=s['state']['T'])
   try:
    dt.update(C.DmassT_INPUTS,r['rho'],r['T']);r.update(pResidual=dt.p()-r['p'],hResidual=dt.hmass()-r['h'],nativePMinusBrowser=dt.p()-s['direct']['p'],nativeHMinusBrowser=dt.hmass()-s['direct']['h'],phase=int(dt.phase()))
   except Exception as e:r['error']=str(e)
   states.append(r)
 audits.append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),states=states))
out=dict(version=version,git=CoolProp.__gitrevision__,rows=rows,browserAudits=audits)
target=E/f'native-{version}.json';assert not target.exists(),'Use a new B2_EVIDENCE directory'
target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(version,len(rows),'native rows;',len(audits),'browser DT audits')
