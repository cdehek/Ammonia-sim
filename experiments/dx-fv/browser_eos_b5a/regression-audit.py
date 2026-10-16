"""Compare rerun regressions to immutable B4C evidence without hiding errors."""
import json,os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b4c/evidence'
read=lambda p:json.loads(p.read_text())
def clean(x,drop=()):
 if isinstance(x,dict):return {k:clean(v,drop) for k,v in x.items() if k not in ('elapsedSeconds',)+drop}
 if isinstance(x,list):return [clean(v,drop) for v in x]
 return x
checks={};details={}
n=read(E/'native-candidateB.json')['rows'];old=read(H/'native-candidateB.json')['rows'];checks['all86DefaultScientificRowsExact']=clean(n)==clean(old)
f=read(E/'native-A1-full-vle.json')['rows'];oldf=read(H/'native-candidateB-full-vle.json')['rows'];checks['fullVLEPHAndSignedProbesExact']=all(clean(a['base'])==clean(b['base']) and clean(a['probes'])==clean(b['probes']) for a,b in zip(f,oldf));checks['originalFocusedAssertionsPass']=read(E/'inherited-focused-gate.json')['passOriginalFocusedRequirements']
for path,filename in [('default','shared-candidateB.json'),('full-vle','shared-candidateB-full-vle.json')]:
 a=read(E/('shared-A1-'+path+'.json'))['rows'];b=read(H/filename)['rows'];checks[path+'PHPSPUOutputsExact']=clean(a,('canonical',))==clean(b,('canonical',));checks[path+'PHPSPUFreshReused']=all(r.get('freshEqualsReused',False) for r in a);details[path+'PHPSPU']=dict(rows=len(a),propertyErrors=[r['id'] for r in a if 'error' in r],canonicalFailures=[r['id'] for r in a if not r.get('canonical',{}).get('canonicalPass',True)])
a=read(E/'lifecycle-A1.json');b=read(H/'lifecycle-candidateB.json');checks['all47LifecycleRowsExact']=a['rows']==b['rows'];checks['lifecycleCasesExact']=a['cases']==b['cases']
a=read(E/'cache-A1.json')['rows'];b=read(H/'cache-candidateB.json')['rows'];checks['all14CacheRowsExact']=a==b;checks['all14DerivativeDifferencesZero']=all(all(v==0 for v in r['derivativeDifferences'].values()) for r in a)
checks['allSharedDensityCallersExact']=read(E/'shared-density.json')['allExact'];checks['additionalAllReturnedOriginalBudgets']=read(E/'additional-eos-audit.json')['allReturnedPass']
# Explicit B4C upper-band fixtures use the original B4B failing-quality inventory.
oldb=read(H/'native-controlA.json')['rows'];upper=[r['request']['id'] for r in oldb if r['base']['PH']['values']['Q']>1];lookup={r['request']['id']:r for r in n};checks['B4COriginalUpperBandVaporPreserved']=all(lookup[k]['base']['PH']['values']['phase']==5 and lookup[k]['base']['PH']['values']['Q']<0 and lookup[k]['inventories']['C']['canonicalPass'] for k in upper)
for ident,phase in [('B1-liquid-precision',0),('approach-30298.937123458254-liquid-0.001',0),('B1-vapor-regression',5)]:
 r=lookup[ident];checks[ident]=r['base']['PH']['values']['phase']==phase and r['inventories']['C']['canonicalPass']
out=dict(checks=checks,details=details,allApplicableNativeRegressionChecksPass=all(checks.values()),B4COriginalUpperBandFixtures=upper,baseRows=86,signedProbes=344,fullVLEBaseRows=len(f),lifecycleRows=47,cacheRows=14,browserCandidateExecuted=False,nonAmmoniaQualified=False,pseudopureQualified=False)
p=E/'regression-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(out['allApplicableNativeRegressionChecksPass'],{k:v for k,v in checks.items() if not v})
