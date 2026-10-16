"""Check observed outputs and unchanged scientific requirements, never override them."""
import hashlib,json,struct
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';H=B.parent/'browser_eos_b5/evidence'
def read(p):return json.loads(p.read_text())
def bits(x):return struct.pack('>d',x).hex()
seven=read(E/'seven-case-analysis.json')['rows'];matrix=read(E/'matrix-mathematics.json')['rows'];checks={};engines={n:read(E/(n+'-replay.json')) for n in ['chromium','webkit']}
for name,d in engines.items():
    original=[r for r in read(H/'original-failures.json')['rows'] if r['runtime']==name]
    checks[name+'SevenBitExact']=len(d['rows'])==len(original)==7 and all(r['key']==f['fixedKey'] and r['raw']['bits']==f['originalRecovery']['DU']['bits'] and r['input']['bits']==f['fixedInput']['bits'] for r,f in zip(d['rows'],original))
    checks[name+'OriginPHBitExact']=all(all(bits(v)==bits(f['originalPH']['values'][k]) for k,v in r['originatingRawPH']['values'].items()) and 'originatingAdapterPH' in r for r,f in zip(d['rows'],original))
    checks[name+'RawThenGuard']=all(r['error']['faultKind']=='domain' and 'adapter.mjs:8:' in r['error']['stack'] and [e['event'] for e in r['events']]==['EOS_call','EOS_return','table_PH_call','table_PH_pass'] and r['counts']['sat']==1 for r in d['rows'])
    old=read(H/(name+'-diagnostics.json'))['boundary']
    checks[name+'Inherited21SweepExact']=all(r['PH']['values']==o['PH'] and r['raw']['values']==o['DU'] and r['input']['values']==o['inventory'] and r.get('error',{}).get('message')==o.get('adapterDUError') for r,o in zip(d['matrix'][:21],old))
    checks[name+'StrictPressureGuards']=all(g['EOSCalls']==0 and g['error']['faultKind']=='domain' for g in d['guards'] if g['kind']=='sat-pressure' and (g['p']<.3 or g['p']>35))
    checks[name+'TemperatureGuardIsolation']=all(g.get('error',{}).get('faultKind')=='domain' for g in d['guards'] if g['kind']=='synthetic-temperature-guard')
checks['BothEngineMatrixBitsIdentical']=all(a['raw']['bits']==b['raw']['bits'] and a['input']['bits']==b['input']['bits'] and a['request']['bits']==b['request']['bits'] for a,b in zip(engines['chromium']['matrix'],engines['webkit']['matrix']))
checks['TwoMathematicalFalseAcceptanceControls']=all(len(engines[n]['falseAcceptance'])==2 and all('adapter' in r and r['raw']['values']['p']<=3500000 for r in engines[n]['falseAcceptance']) for n in engines) and len(read(E/'false-acceptance-controls.json')['rows'])==2
checks['OriginalCanonicalAndNonlinear']=all(all(abs(r['canonicalDifferences'][k])<=limit for k,limit in dict(p=.1,h=.1,T=1e-4).items()) and max(r['normalizedResiduals'].values())<=1e-11 for r in seven)
checks['MatrixCanonicalAndNonlinear']=all(r['canonicalPass'] and r['nonlinearPass'] for r in matrix)
checks['OriginalTwoMathematicallyInFiveOut']=sum(r['mechanism']=='numerical-wrong-side' for r in seven)==2 and sum(r['mechanism']=='rounded-inventory-conflict' for r in seven)==5
checks['IndependentOriginalStandalone']=all(abs(float(r['rawDU']['values']['p'])-float(r['mathematical']['homogeneous']['p']))<10 and abs(float(r['rawDU']['values']['h'])-float(r['mathematical']['homogeneous']['h']))<50 and abs(float(r['rawDU']['values']['T'])-float(r['mathematical']['homogeneous']['T']))<.01 for r in seven)
checks['ProposedFailureNeverBecomesPropertyState']=read(E/'prototype-results.json')['propertyStatesReturned']==0
assert all(checks.values()),checks
facts=dict(canonicalMax={k:max(abs(r['canonicalDifferences'][k]) for r in seven) for k in ['p','h','T']},originalNormalizedMax={k:max(r['normalizedResiduals'][k] for r in seven) for k in ['mass','energy']},matrixNormalizedMax={k:max(r['normalized'][k] for r in matrix) for k in ['mass','energy']},observedOriginalRejections=14,observedMatrixPerBrowser=24,proposedClasses=read(E/'prototype-results.json')['counts'],physicalTrajectoryProofsObserved=0,fullA2Qualification=False,newNativeExecution=False,intervalCertification=False)
budgets=dict(canonical=dict(pPa=.1,hJkg=.1,TK=1e-4),nonlinearMassEnergy=1e-11,independentReferenceResolution=dict(pPa=1e-5,caloricJkg=1e-8),standaloneStrict=dict(pPa=10,hJkg=50,TK=.01),sectionAndAggregateStrict=dict(massKg=1e-8,energyKJ=1e-6),support=dict(pBar=[.3,35],TminK=195.495,subcoolK=30,superheatK=250,thermalDomainK=[200,400]),newtonIterations=30,thermalClosureK=1e-12,minimumStepSeconds=1e-9,maximumAttempts=100000,FD='unchanged signed pressure 1e-7*max(1,abs(pbar)), enthalpy 1e-8*max(1,abs(hkJkg)), thermal capacity*1e-6; +1,-1, 12 shrink levels',TRBDF2='unchanged gamma=2-sqrt(2), full versus two half steps /3; commit two half steps')
(E/'scientific-audit.json').write_text(json.dumps(dict(checks=checks,facts=facts,originalBudgets=budgets,allPass=True,scope='Focused diagnostic arithmetic checks only; refusal, unresolved phase, and backend qualification remain separate.'),indent=2)+'\n')
print(json.dumps(facts,indent=2))
