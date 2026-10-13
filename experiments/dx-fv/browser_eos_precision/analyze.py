"""Reproducible arithmetic attribution, conditioning and evidence summaries."""
import json,math,hashlib
from pathlib import Path
from decimal import Decimal,localcontext
import numpy as np
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(name):return json.loads((E/name).read_text())
def save(name,value):
 p=E/name;text=json.dumps(value,indent=2,allow_nan=False)+'\n'
 if p.exists():assert p.read_text()==text,'Retain completed evidence'
 else:p.write_text(text)
def primary(q,method='reused'):return next(r for r in q['rows'] if r.get('id')=='exact-saved' and r.get('method')==method and r.get('axis')=='P' and r.get('step')==.01)
q=read('chromium-8.0.0.json');r=primary(q);a,b=r['base'],r['perturbed'];dp=r['step']
noise=a['rhoH']*(b['hResidual']-a['hResidual'])+a['rhoP']*(b['pResidual']-a['pResidual'])
observed=b['rho']-a['rho']-a['rhoP']*dp
with localcontext() as c:
 c.prec=60;exactDifference=Decimal.from_float(b['rho'])-Decimal.from_float(a['rho']);decimalFinite=exactDifference/Decimal.from_float(dp)
root={'mechanism':'Input-dependent caloric PH residual becomes density error through the EOS derivative, contaminating the unchanged finite difference. No unstable EOS branch is required.',
 'inputs':r['args'],'inputBits':r['inputBits'],'perturbedInputBits':r['perturbedInputBits'],'acceptedStepPa':dp,'actualBinary64StepPa':r['actualStep'],
 'analyticRhoPAtH':a['rhoP'],'finiteRhoPAtH':r['finite'],'ratio':r['ratio'],'base':a,'perturbed':b,
 'densityPhysicalIncrement':a['rhoP']*dp,'densityArtefactObserved':observed,'densityArtefactPredicted':noise,'attributionRelativeResidual':(noise-observed)/observed,
 'caloricTemperatureErrorEstimateK':(b['hResidual']-a['hResidual'])/a['cp'],
 'decimal60ExactDifferenceOfBinary64Outputs':str(exactDifference),'decimal60Finite':str(decimalFinite),
 'densityULP':math.ulp(a['rho']),'twoULPDensityFDRepresentationalScale':2*math.ulp(a['rho'])/dp,
 'representationCaution':'This is the representation scale for two density outputs, not a certificate that an EOS evaluation is correctly rounded. Close positive binary64 density subtraction is exact by Sterbenz; input-evaluation errors remain.',
 'sourceStoppingRules':{'oldBits':44,'currentBits':30,'oldRelativeBracketTolerance':2**(1-44),'currentRelativeBracketTolerance':2**(1-30),'relaxationFactor':2**14,'possibleCurrentBracketWidthK':a['T']*2**(1-30),'possibleMidpointCaloricErrorJkg':a['cp']*a['T']*2**(1-30)/2,
 'limitations':'Envelope implied by pinned source and Boost header, not an observed final WASM bracket. Internal iteration/bracket instrumentation is not exported. The source comment 2^(1-30)=9.31e-10 is arithmetically incorrect; Boost actually computes 1.862645149230957e-9.'},
 'backendInterfaceResolution':'None demonstrated. Public phase-imposed PropsSI, molar inputs and state lifecycle changes retain the failure. Native-only configuration experiments change which nearby inputs fail, without curing all probes.'}
root['scaledInventoryContamination']=[]
for n in [5,9]:
 V=.003/n;M=V*a['rho'];U=V*(a['rho']*a['h']-a['p'])/1000;scales=np.array([max(.01,M),max(1,abs(U))]);
 J=np.array([[V*a['rhoP']*1e5,V*a['rhoH']*1000],[V*(a['h']*a['rhoP']-1)*100,V*(a['rho']+a['h']*a['rhoH'])]])/scales[:,None]
 root['scaledInventoryContamination'].append({'sections':n,'volumeM3':V,'massKg':M,'energyKJ':U,'densityArtefactMassKg':noise*V,'scaledMassResidual':noise*V/scales[0],'scaledInputEnthalpyEnergyResidual':noise*V*a['h']/1000/scales[1],'nonlinearTolerance':1e-11,'inventoryAnalyticJacobianPHbarKJkg':J.tolist(),'determinant':float(np.linalg.det(J)),'condition2':float(np.linalg.cond(J)),'conditionWithRelativeCoordinateScaling':float(np.linalg.cond(J@np.diag([max(1,r['args'][0]/1e5),max(1,r['args'][1]/1000)]))),'note':'Local liquid inventory Jacobian only. Does not prove global inversion uniqueness or full coupled conditioning.'})
save('root-cause.json',root)
summary={'classification':'Official 8.0.0 shipped PH interface remains incompatible with demonstrated unchanged small-probe requirements; no migration authorized. Internal stopping-rule attribution strongly supported, final WASM branch/bracket uninstrumented.','comparisons':[],'staticSynthetic':[],'ipad':[]}
for name in ['native-8.0.0.json','chromium-8.0.0.json','webkit-8.0.0.json','native-7.2.0.json','chromium-7.2.0.json','webkit-7.2.0.json','native-8.0.0-cached-path.json','native-8.0.0-no-super.json']:
 t=read(name);method='high' if '7.2' in name and not name.startswith('native') else 'reused';pr=primary(t,method)
 nearby=[r for r in t['rows'] if r.get('id','').startswith(('p','saved-')) and r.get('method') in ['reused','high-unavailable-low-level']]
 summary['comparisons'].append({'file':name,'rows':len(t['rows']),'errors':sum('error'in r for r in t['rows']),'saved':{k:pr[k]for k in ['analytic','finite','ratio']},'basePResidual':pr['base']['pResidual'],'perturbedPResidual':pr['perturbed']['pResidual'],'baseHResidual':pr['base']['hResidual'],'perturbedHResidual':pr['perturbed']['hResidual'],'nearbyStates':len(nearby)//2,'pressureRatiosMoreThan1PercentFromUnity':sum(abs(r['ratio']-1)>.01 for r in nearby if r['axis']=='P'),'enthalpyRatiosMoreThan1PercentFromUnity':sum(abs(r['ratio']-1)>.01 for r in nearby if r['axis']=='H'),'countCaution':'1% is a descriptive diagnostic threshold, not an added or altered solver acceptance contract. 57 source liquid states include the exact saved point.'})
for name in ['chromium','webkit']:
 for v in ['8.0.0','7.2.0']:
  t=read(f'{name}-synthetic-{v}.json');summary['staticSynthetic'].append({'browser':name,'version':v,'cases':len(t['rows']),'converged':sum(r['converged'] for r in t['rows']),'failures':[{'n':r['n'],'target':r['target'],'accounting':r['accounting'],'error':r['error'],'nonlinearResidual':r['nonlinearResidual']}for r in t['rows'] if not r['converged']],'elapsedMSMin':min(r['elapsedMS']for r in t['rows']),'elapsedMSMax':max(r['elapsedMS']for r in t['rows']),'newtonIterationsMax':max(r['work']['iterations']for r in t['rows'])})
cross=read('native-contract.json')['crossEOSChecks'];summary['matching8DirectEOSCrossCheck']={'states':len(cross),'maxPressurePa':max(abs(r['nativeMinusWASM']['pEOS'])for r in cross),'maxEnthalpyJkg':max(abs(r['nativeMinusWASM']['hEOS'])for r in cross),'note':'Independent native build at identical returned D/T coordinates; formulation agreement, not experimental ammonia validation.'}
t=read('ipad-smoke-v2.json')
for r in t['results']:
 for mode,z in [('online',z)for z in r['online']]+[('origin-disabled-fresh-page',r['offlineRestart']['record'])]:
  o=z.get('result',{});summary['ipad'].append({'desktopBrowser':r['browser'],'actualPhysicalIPad':False,'requestedVersion':z['requestedVersion'],'mode':mode,'startupMS':o.get('init',{}).get('totalMS'),'linearMemory':o.get('linearMemory'),'workerMaxTimerGapMS':z.get('workerResponsiveness',{}).get('maxGapMS'),'errors':z['errors'],'throughput':[{'mode':m,'callsPerSecond':sum(x['calls']for x in o['throughput']if x['mode']==m)/sum(x['elapsedMS']for x in o['throughput']if x['mode']==m)*1000,'failures':sum(x['failures']for x in o['throughput']if x['mode']==m)}for m in ['PH','DU']],'stress':o.get('stress')})
save('summary.json',summary);print(summary['classification'])
