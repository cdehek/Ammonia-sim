"""Independent native DT residuals and polished PH reference roots.

The reference root limits are diagnostic evaluation limits from the prior study,
not changes to any simulator tolerance. No computed correction is used by WASM.
"""
import hashlib, json, math
from pathlib import Path
import CoolProp
from CoolProp import AbstractState, CoolProp as C

B = Path(__file__).resolve().parent
E = B/'evidence'
audit = AbstractState('HEOS','Ammonia')
seed = AbstractState('HEOS','Ammonia')
cache = {}
def root(p,h):
    key=(p,h)
    if key in cache: return cache[key]
    seed.update(C.HmassP_INPUTS,h,p)
    rho,T=seed.rhomass(),seed.T()
    trace=[]
    for iteration in range(8):
        audit.update(C.DmassT_INPUTS,rho,T)
        rp,rh=audit.p()-p,audit.hmass()-h
        trace.append({'rho':rho,'T':T,'pResidual':rp,'hResidual':rh})
        if abs(rp)<1e-5 and abs(rh)<1e-8: break
        pr=audit.first_partial_deriv(C.iP,C.iDmass,C.iT)
        pt=audit.first_partial_deriv(C.iP,C.iT,C.iDmass)
        hr=audit.first_partial_deriv(C.iHmass,C.iDmass,C.iT)
        ht=audit.first_partial_deriv(C.iHmass,C.iT,C.iDmass)
        det=pr*ht-pt*hr
        rho+=(-rp*ht+pt*rh)/det
        T+=(-pr*rh+rp*hr)/det
    result={'p':audit.p(),'h':audit.hmass(),'rho':audit.rhomass(),'T':audit.T(),'u':audit.umass(),
            'trace':trace,'referenceConverged':abs(rp)<1e-5 and abs(rh)<1e-8}
    cache[key]=result
    return result

def save(path,data):
    text=json.dumps(data,indent=2,allow_nan=False)+'\n'
    if path.exists(): assert path.read_text()==text, f'Retain {path}'
    else:path.write_text(text)

summary=[]
for file in sorted(E.glob('*-*.json')):
    if not any(file.name.startswith(s) for s in ['chromium-','webkit-']): continue
    data=json.loads(file.read_text())
    if 'precision' not in data:continue
    build=data['build']
    if (build=='official72') != (CoolProp.__version__=='7.2.0'):continue
    independent=[]
    for row in data['precision']['rows']:
        if 'error' in row:continue
        p,h=row['args'];step=row['step']
        for which in ['base','perturbed']:
            sp=p+(step if which=='perturbed' and row['axis']=='P' else 0)
            sh=h+(step if which=='perturbed' and row['axis']=='H' else 0)
            s=row[which]
            ref=root(sp,sh)
            audit.update(C.DmassT_INPUTS,s['rho'],s['T'])
            independent.append({'id':row['id'],'method':row['method'],'axis':row['axis'],'step':step,'which':which,
              'args':[sp,sh],'rho':s['rho'],'T':s['T'],
              'nativeDTPressurePa':audit.p(),'nativeDTEnthalpyJkg':audit.hmass(),
              'nativePResidualPa':audit.p()-sp,'nativeHResidualJkg':audit.hmass()-sh,
              'nativeMinusWASMDTPressurePa':audit.p()-s['pEOS'],'nativeMinusWASMDTEnthalpyJkg':audit.hmass()-s['hEOS'],
              'deviationFromPolishedNative':{k:s[k]-ref[k] for k in ['rho','T']},
              'referenceConverged':ref['referenceConverged']})
    save(E/(file.stem+'-independent.json'),{'sourceFileSHA256':hashlib.sha256(file.read_bytes()).hexdigest(),
      'version':CoolProp.__version__,'git':CoolProp.__gitrevision__,'rows':independent})
    rows=data['precision']['rows']
    primary=next(r for r in rows if r['id']=='exact-saved' and r['method']==('high' if build=='official72' else 'reused') and r['axis']=='P' and r['step']==.01)
    nearby=[r for r in rows if r['id'].startswith(('p','saved-')) and r['method'] in ['reused','high-unavailable-low-level'] and 'error' not in r]
    normNoise=max(abs((r['perturbed']['rho']-r['base']['rho'])-r['analytic']*r['step'])/r['base']['rho'] for r in nearby)
    normH=max(abs(s['hResidual'])/max(1,abs(s['h']-s['p']/s['rho'])) for r in rows if 'error' not in r for s in [r['base'],r['perturbed']])
    rawref=json.loads((B.parent/'browser_eos/evidence'/('python-7.2.0.json' if build=='official72' else 'python-8.0.0.json')).read_text())['rows']
    differences={k:0 for k in ['p','h','T','rho','u']};failureChanges=[]
    for a,b in zip(data['accuracy'],rawref):
        assert a['id']==b['id']
        if ('error' in a)!=('error' in b):failureChanges.append({'id':a['id'],'browserError':a.get('error'),'historicalNativeError':b.get('error')})
        if a['region']=='invalid' or 'state' not in a or 'state' not in b:continue
        for k in differences:differences[k]=max(differences[k],abs(a['state'][k]-b['state'][k]))
    out={'file':file.name,'build':build,'browser':data['browser'],'rows':len(rows),'errors':sum('error' in r for r in rows),
      'primary':primary,'nearbyPressureDeviationsAbove1Percent':sum(abs(r['ratio']-1)>.01 for r in nearby if r['axis']=='P'),
      'nearbyEnthalpyDeviationsAbove1Percent':sum(abs(r['ratio']-1)>.01 for r in nearby if r['axis']=='H'),
      'descriptiveThresholdCaution':'1% is a descriptive count only; it is not a solver acceptance limit.',
      'maxNormalizedProbeDensityContamination':normNoise,'maxNormalizedCaloricResidual':normH,
      'independentMax':{k:max(abs(r[k]) for r in independent) for k in ['nativePResidualPa','nativeHResidualJkg','nativeMinusWASMDTPressurePa','nativeMinusWASMDTEnthalpyJkg']},
      'maxDeviationFromPolishedNative':{k:max(abs(r['deviationFromPolishedNative'][k]) for r in independent) for k in ['rho','T']},
      'referenceFailures':sum(not r['referenceConverged'] for r in independent),
      'accuracySuccesses':sum('state' in r for r in data['accuracy']),'accuracyErrors':[r for r in data['accuracy'] if 'error' in r],
      'accuracyMaxDifferenceFromHistoricalMatchingNative':differences,'accuracyFailureChanges':failureChanges}
    out['standaloneScreenPass']=out['errors']==0 and out['referenceFailures']==0 and normNoise<1e-11 and normH<1e-11 and differences['p']<10 and differences['h']<50 and differences['T']<.01 and not failureChanges
    summary.append(out)
save(E/f'precision-summary-{CoolProp.__version__}.json',summary)
save(E/f'polished-references-{CoolProp.__version__}.json',{'version':CoolProp.__version__,'git':CoolProp.__gitrevision__,
 'referenceEvaluationLimits':{'pPa':1e-5,'hJkg':1e-8},'roots':[{'args':list(k),**v} for k,v in cache.items()]})
print(json.dumps([{k:r[k] for k in ['file','standaloneScreenPass','maxNormalizedProbeDensityContamination','maxNormalizedCaloricResidual','referenceFailures']} for r in summary],indent=2))
