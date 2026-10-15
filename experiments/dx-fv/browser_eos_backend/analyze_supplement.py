"""Independent native EOS residuals for the added liquid/vapor matrix."""
import json,hashlib
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=B/'evidence';a=AbstractState('HEOS','Ammonia');summaries=[]
for f in sorted(E.glob('*-supplement-*.json')):
 d=json.loads(f.read_text())
 if (d['build']=='official72')!=(CoolProp.__version__=='7.2.0'):continue
 checks=[];rows=d['rows']
 for row in rows:
  if 'error' in row or 'exclusion' in row:continue
  for which in ['base','perturbed']:
   s=row[which];p,h=row['args'];step=row['step'] if which=='perturbed' else 0
   p+=step if row['axis']=='P' else 0;h+=step if row['axis']=='H' else 0
   a.update(C.DmassT_INPUTS,s['rho'],s['T'])
   checks.append({'id':row['id'],'region':row['region'],'method':row['method'],'axis':row['axis'],'which':which,'args':[p,h],
    'rho':s['rho'],'T':s['T'],'nativePResidual':a.p()-p,'nativeHResidual':a.hmass()-h,
    'nativeMinusWASMP':a.p()-s['pEOS'],'nativeMinusWASMH':a.hmass()-s['hEOS']})
 valid=[r for r in rows if 'ratio' in r]
 result={'file':f.name,'version':CoolProp.__version__,'git':CoolProp.__gitrevision__,'sourceSHA256':hashlib.sha256(f.read_bytes()).hexdigest(),
  'rows':checks,'errors':[r for r in rows if 'error' in r],'domainExclusions':[r for r in rows if 'exclusion' in r],
  'descriptiveRatiosAbove1Percent':sum(abs(r['ratio']-1)>.01 for r in valid),
  'ratioMin':min(r['ratio'] for r in valid),'ratioMax':max(r['ratio'] for r in valid),
  'maxIndependentPResidualPa':max(abs(r['nativePResidual']) for r in checks),
  'maxIndependentHResidualJkg':max(abs(r['nativeHResidual']) for r in checks),
  'maxNativeMinusWASMPPa':max(abs(r['nativeMinusWASMP']) for r in checks),'maxNativeMinusWASMHJkg':max(abs(r['nativeMinusWASMH']) for r in checks),
  'largestHResidual':max(checks,key=lambda r:abs(r['nativeHResidual'])),
  'caution':'Derivative agreement and absolute PH residual are separate metrics. No 1% scientific acceptance threshold is introduced.'}
 out=E/(f.stem+'-independent.json');assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
 summaries.append({k:v for k,v in result.items() if k!='rows'})
out=E/f'supplement-summary-{CoolProp.__version__}.json';assert not out.exists();out.write_text(json.dumps(summaries,indent=2)+'\n')
print([(r['file'],r['maxIndependentHResidualJkg']) for r in summaries])
