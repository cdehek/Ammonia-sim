"""Audit scientific evidence against saved inputs and original budgets.

Passing this audit means evidence integrity, not backend qualification. Original
exceptions and adapter rejections remain failures of the accepted backend.
"""
import json,struct,math,csv,hashlib
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b4c/evidence'
def read(f):return json.loads((E/f).read_text())
def bits(x):return struct.pack('>d',float(x)).hex()
inputs=read('fixed-inputs.json');native=read('native-fixed-replay.json')['rows'];refs=read('independent-fixed-references.json')['rows'];mp=read('high-precision-references.json')['rows'];fail=read('original-failures.json');trace=read('trace-audit.json');precision=read('precision-audit.json');eos=read('raw-DU-eos-audit.json')['rows'];checks={}
checks['binary64InventoryAndOperationOrder']=all(all(bits(v)==r['input']['bits'][k]for k,v in r['input']['values'].items())and r['input']['values']['rho']==r['input']['values']['M']/r['input']['values']['V']and r['input']['values']['u']==(r['input']['values']['U_kJ']/r['input']['values']['M'])*1000 for r in inputs)
checks['allNativeHistoricalRowsExact']=all(r['historicalExact']for r in native if r['historicalExact']is not None)
checks['instrumentedUninstrumentedParity']=trace['loggingParity']and trace['archivalParity']
checks['nativeFreshReused']=trace['freshReusedEqual']
checks['sourceAndArtifactsPreserved']=read('preservation-verification.json')['allPass']
checks['allDoubleReferencesConverged']=all(r['reference']['homogeneous']['converged']and r['reference']['equilibrium']['converged']for r in refs)
checks['allMPReferencesPresent']=all('error'not in r['reference']for r in mp)
checks['precisionRepeat']=all(r['allWithinOriginalReferenceResolution']for r in precision['rows'])
checks['stableReferences']=True
for r,h in zip(refs,mp):
 a=r['reference'];s=h['reference'];which=s['selection'];v=a['homogeneous']['stability']if which=='homogeneous'else None
 if v:checks['stableReferences']&=all(v[k]>0 for k in ['cp','cv','kappa','pRho'])
 else:checks['stableReferences']&=all(a['equilibrium'][p][k]>0 for p in ['liquidStability','vaporStability']for k in ['cp','cv','kappa','pRho'])and 0<=float(s['equilibrium']['Q'])<=1
 checks['stableReferences']&=float(s[which]['rho'])>0
checks['allReturnedCanonicalBudgets']=all(r['canonicalPass']for r in eos if'canonicalPass'in r)
checks['allReturnedNonlinearBudgets']=all(r['nonlinearPass']for r in eos if'nonlinearPass'in r)
browserFacts={}
for engine in ['chromium','webkit']:
 b=read(engine+'-fixed-replay.json');d=read(engine+'-diagnostics.json');old=json.loads((H/(engine+'-35bar-fixed-inventories.json')).read_text())['rows'];lookup={(engine+'-ledger-'+str(i)):r for i,r in enumerate(old)if r['build']=='candidateB'}
 own=[r for r in b['rows']if r['build']=='candidateB'and r['key']in lookup]
 checks[engine+'HistoricalExact']=all(r.get('DU')==lookup[r['key']].get('DU')and r.get('adapterError')==lookup[r['key']].get('adapterError')and r.get('rawError')==lookup[r['key']].get('rawError')for r in own)
 checks[engine+'PHExact']=all(r['PH']==r['historical']for r in b['phRows']if r['build']=='candidateB')
 checks[engine+'FreshReused']=all(r['fresh']==r['reused']for r in d['lifecycle'])
 checks[engine+'GuardPath']=all('originatingAdapterPH'in r and r.get('faultKind')=='domain'and [x['event']for x in r['events']]==['EOS_call','table_guard_call','table_guard_pass']and r['counts']['sat']==1 and 'adapter.mjs:8:'in r['stack']for r in d['guardTraces'])
 n={r['key']:r['result']['B4C'].get('DU',{}).get('values')for r in native};rows=[r for r in b['rows']if r['build']=='candidateB'];diff={k:max(abs(n[r['key']][k]-r['DU'][k])for r in rows)for k in ['p','h','u','T','rho','Q']}
 browserFacts[engine]=dict(version=b['version'],fixedRows=len(b['rows']),ownHistoricalInventories=len(own),sharedNativeBrowserMaxDifferences=diff,sharedNativeBrowserGuardDisagreements=[r['key']for r in rows if(n[r['key']]['p']<=35e5)!=(r['DU']['p']<=35e5)],scalarVsStateDifferences={k:max(abs(r['scalar'][k]-r['reused'][k])for r in d['lifecycle'])for k in ['p','h','T','rho','u','Q']},boundaryAdapterRejections=sum('adapterDUError'in r for r in d['boundary']))
for r in fail['rows']:
 if r['runtime']=='native-full-VLE':
  t=next(x for x in trace['rows']if x['fixedKey']==r['fixedKey']);checks['trace-'+r['fixedKey']]=any(x['event']=='Brent_stop_scaled_residual'for x in t['events'])and(t['twoPhaseReturn']['c']<0 or t['twoPhaseReturn']['c']>1)
successful=[r for r in eos if'canonicalPass'in r];cur=[r for r in fail['rows']if r['runtime']=='chromium'];attr=read('pressure-error-attribution.json')['rows'];n72=read('native72-fixed-replay.json')['rows'];n72unique={tuple(inputs[i]['input']['bits'][k]for k in ['rho','u'])for i,r in enumerate(n72)if'error'in r}
facts=dict(failureCounts=fail['counts'],fixedRows=len(inputs),uniqueInventories=read('independent-fixed-references.json')['uniqueInventories'],nativeDefaultCrossPathExceptions=sum('error'in r['paths']['default']for r in read('cross-path.json')['rows']),nativeFullVLECrossPathExceptions=sum('error'in r['paths']['fullVLE']for r in read('cross-path.json')['rows']),native72Exceptions=len([r for r in n72 if'error'in r]),native72UniqueExceptionInventories=len(n72unique),rawEOSAuditRows=len(eos),rawExceptions=sum('error'in r for r in eos),successfulCanonicalMax={k:max(abs(r['canonicalDifferences'][k])for r in successful)for k in ['p','h','T']},successfulNonlinearMax={k:max(r['normalizedResiduals'][k]for r in successful)for k in ['mass','energy']},originalBrowserCanonicalMax={k:max(abs(r['originalRecovery']['differences'][k])for r in cur)for k in ['p','h','T']},originalBrowserFixedReferenceBelowLimit=sum(float(r['highPrecisionReference']['pMinusLimit'])<0 for r in cur),originalBrowserFixedReferenceAboveLimit=sum(float(r['highPrecisionReference']['pMinusLimit'])>0 for r in cur),maxPHInventoryEnergyMismatch=max(r['normalizedPHInventoryEnergyMismatch']for r in attr),browser=browserFacts,retainedBudgets=dict(canonical=dict(p=.1,h=.1,T=1e-4),nonlinear=1e-11,independentResolution=dict(p=1e-5,caloric=1e-8),standalone=dict(p=10,h=50,T=.01),massLedger=1e-8,energyLedger=1e-6),fullA2Qualification=False)
out=dict(assessment='ROOT CAUSE CONFIRMED',checks=checks,evidenceAuditPass=all(checks.values()),facts=facts,backendQualified=False,allOriginalFailuresRetained=True,functionalRepairImplemented=False)
(E/'scientific-audit.json').write_text(json.dumps(out,indent=2)+'\n')
# Reviewable exact input inventory with binary64 columns.
with(E/'fixed-inventory.csv').open('w',newline='')as f:
 fields=['key','origin','id','fullVLE']+[k+s for k in ['M','V','U_kJ','rho','u']for s in ['','_bits']];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for r in inputs:w.writerow(dict(**{k:r[k]for k in ['key','origin','id','fullVLE']},**{k+s:r['input']['values'if s==''else'bits'][k]for k in ['M','V','U_kJ','rho','u']for s in ['','_bits']}))
print('evidence audit',out['evidenceAuditPass'],{k:v for k,v in checks.items()if not v});assert out['evidenceAuditPass']
