"""Equilibrium checks at mean mixture density use lever rules, never homogeneous EOS."""
import json,os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));rows=[]
for runtime in ['native','chromium','webkit']:
 d=json.loads((E/('native-candidateB.json' if runtime=='native' else runtime+'-candidateB-focused.json')).read_text())['rows']
 refs=json.loads((E/'native-controlA.json').read_text())['rows']
 for r in d:
  nr=r if runtime=='native' else next(v for v in refs if v['request']['id']==r['id']);ident=nr['request']['id']
  for name,x in [('base',r['base'])]+[(q['axis']+str(q['step']),q.get('output')) for q in r['probes']]:
   if not x:continue
   s=x['PH']['values'] if runtime=='native' else x['state'];phase=s.get('phase',x.get('phase'));q=s['Q']
   if phase!=6 or not 0<=q<=1:continue
   if runtime=='native':n=x
   elif name=='base':n=nr['base']
   else:n=next(v['output'] for v in nr['probes'] if v['axis']+str(v['step'])==name)
   f=n['saturation']['liquid']['values'];g=n['saturation']['vapor']['values'];V=.003/5
   rho=1/((1-q)/f['rho']+q/g['rho']);v=dict(runtime=runtime,id=ident,sample=name,Q=q,T=s['T']-f['T'],h=s['h']-((1-q)*f['h']+q*g['h']),u=s['u']-((1-q)*f['u']+q*g['u']),normalizedLeverMass=abs(s['rho']-rho)*V/max(.01,s['rho']*V));rows.append(v)
fail=[r for r in rows if abs(r['T'])>1e-4 or abs(r['h'])>.1 or abs(r['u'])>.1 or r['normalizedLeverMass']>1e-11]
p=E/'default-equilibrium-audit.json';assert not p.exists();p.write_text(json.dumps(dict(rows=rows,failures=fail,passOriginalRequirements=not fail,maxima={k:max(abs(r[k])for r in rows)for k in ['T','h','u','normalizedLeverMass']}),indent=2)+'\n');print(len(rows),'equilibrium snapshots; failures',len(fail));assert not fail
