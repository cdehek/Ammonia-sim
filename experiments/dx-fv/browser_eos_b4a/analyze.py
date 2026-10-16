"""Derive focused gate without suppressing known failures or support exclusions."""
import os
import json,math,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'))
sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save,root
audit=Backend();sat=Backend();primary='approach-30298.937123458254-liquid-0.001'
def read(n):return json.loads((E/n).read_text())
def phase(p,h):
 f=sat.state('PQ',p,0);g=sat.state('PQ',p,1)
 return 'liquid'if h<f['h']-1e-8 else'gas'if h>g['h']+1e-8 else'equilibrium'if f['h']+1e-8<h<g['h']-1e-8 else'endpoint-unresolved'
def canon(inv):return bool(inv and inv.get('canonicalPass'))
out=dict(primary={},native={},browser={},failures=[],knownLimitations=[],eligibleForLimitedA2=False)
nativeGate=True
for name in ['native-control44.json','native-liquid44.json','native-liquid44-full-vle.json']:
 if not(E/name).exists():nativeGate=False;out['failures'].append(dict(file=name,error='missing'));continue
 d=read(name);rows=d['rows'];r=next(x for x in rows if x['request']['id']==primary);out['primary'][name]=r
 errors=[dict(id=x['request']['id'],error=x['error'])for x in rows if'error'in x]
 invalidLiquidLever=[x['request']['id']for x in rows if'base'in x and x['base']['physicalPhase']=='liquid'and x['base']['PH']['values']['phase']==6]
 liquidCanonical=[dict(id=x['request']['id'],result=x['inventories']['C'])for x in rows if'base'in x and x['base']['physicalPhase']=='liquid'and not canon(x.get('inventories',{}).get('C'))]
 probes=[dict(id=x['request']['id'],probe=p)for x in rows for p in x['probes']if p.get('samePhysicalBranch')and x.get('base',{}).get('physicalPhase')=='liquid'and p.get('output',{}).get('supportedInput')and not p.get('nonlinearScalePass')]
 guards=[dict(id=x['request']['id'],inventory=k,recoveredP=v.get('DU',{}).get('values',{}).get('p'),error=v.get('error'))for x in rows for k,v in x.get('inventories',{}).items()if not v.get('recoveredPressureInAcceptedRange',False)]
 preservedUnsupported=[]
 for failure in liquidCanonical:
  if 'full-vle'not in name:continue
  fixed=read('full-vle-35bar-fixed-inventory-control.json')
  comparisons=[c for c in fixed['comparisons']if c['id']==failure['id']and c['inventory']in ['A','C']]
  if len(comparisons)==2 and all(c['outputEqual']and c['inputEqual']and c['error']for c in comparisons):
   preservedUnsupported.append(dict(id=failure['id'],reason='Independent physical A and repaired C DU throw identically in the unchanged control at identical fixed inventories; retained inverse limitation, never a canonical pass',comparisons=comparisons))
 unexplainedCanonical=[x for x in liquidCanonical if x['id']not in {c['id']for c in preservedUnsupported}]
 out['native'][name]=dict(rows=len(rows),baseErrors=errors,invalidLiquidLever=invalidLiquidLever,liquidCanonicalFailures=liquidCanonical,preservedIndependentDUFailures=preservedUnsupported,unexplainedLiquidCanonicalFailures=unexplainedCanonical,sameLiquidProbeFailures=probes,supportExits=guards)
 if'control'not in name:
  base=r.get('base',{});ref=base.get('reference',{});s=base.get('PH',{}).get('values',{});c=r.get('inventories',{}).get('C')
  primaryPass=bool(ref.get('converged')and all(v>0 for v in ref.get('stability',{}).values())and s.get('phase')==0 and canon(c)and abs(base['residuals']['p'])<10 and abs(base['residuals']['h'])<50 and all(p.get('nonlinearScalePass',True)for p in r['probes']))
  out['native'][name]['primaryPass']=primaryPass
  nativeGate &= primaryPass and not errors and not invalidLiquidLever and not unexplainedCanonical and not probes
browserGate=True
for engine in ['chromium','webkit']:
 name=f'{engine}-liquid44-focused.json'
 if not(E/name).exists():browserGate=False;out['failures'].append(dict(file=name,error='missing'));continue
 d=read(name);control=read(f'{engine}-control44-focused.json');references=read('native-control44.json')['rows'];items=[];newErrors=[];probeFailures=[];liquidCanonical=[];allErrors=[]
 for row in d['rows']:
  original=next(r for r in control['rows']if r['id']==row['id']);ref=next(r for r in references if r['request']['id']==row['id'])
  if'error'in row:
   allErrors.append(dict(id=row['id'],error=row['error']))
   if'error'not in original:newErrors.append(dict(id=row['id'],error=row['error']))
   continue
  b=row['base'];p,h=row['args'];physical=phase(p,h);dt=audit.state('DT',b['state']['rho'],b['state']['T']);rt=ref.get('base',{}).get('reference',{})
  item=dict(id=row['id'],physicalPhase=physical,backendPhase=b['phase'],Q=b['state']['Q'],inputBits=b['inputBits'],independentDT=pack(dt),residuals=dict(p=dt['p']-p,h=dt['h']-h),browserVersusNativeDT={k:dt[k]-b['direct'][k]for k in ['p','h','u']},probes=[])
  if physical=='liquid'and not canon(row.get('inventories',{}).get('C')):liquidCanonical.append(row['id'])
  for probe in row['probes']:
   v=dict(axis=probe['axis'],step=probe['step'],actualIncrement=probe['actualIncrement'])
   if'error'in probe:v['error']=probe['error'];item['probes'].append(v);continue
   other=probe['output'];pp,hh=other['p'],other['h'];ph=phase(pp,hh);probeDT=audit.state('DT',other['state']['rho'],other['state']['T'])
   v.update(physicalPhase=ph,inputBits=other['inputBits'],supportedInput=3e4<=pp<=35e5,backendPhase=other['phase'],Q=other['state']['Q'],independentDT=pack(probeDT),residuals=dict(p=probeDT['p']-pp,h=probeDT['h']-hh),browserVersusNativeDT={k:probeDT[k]-other['direct'][k]for k in ['p','h','u']})
   same=physical==ph and physical in ['liquid','gas'];v['samePhysicalBranch']=same
   if same and rt.get('converged'):
    analytic=rt['derivatives']['rhoP'if probe['axis']=='P'else'rhoH'];finite=(other['state']['rho']-b['state']['rho'])/probe['step'];contamination=abs(other['state']['rho']-b['state']['rho']-analytic*probe['step']);V=.003/5
    v.update(analytic=analytic,finite=finite,ratio=finite/analytic,normalizedMassProbeContamination=V*contamination/max(.01,b['state']['rho']*V),nonlinearScale=1e-11)
    M=b['state']['rho']*V;U=M*(h/1000)-p*V/1000;newU=other['state']['rho']*V*(hh/1000)-pp*V/1000
    dU=analytic*V*(h/1000)+(-V/1000 if probe['axis']=='P'else M/1000)
    v['normalizedEnergyProbeContamination']=abs(newU-U-dU*probe['step'])/max(1,abs(U))
    v['nonlinearScalePass']=v['normalizedMassProbeContamination']<=1e-11 and v['normalizedEnergyProbeContamination']<=1e-11
    if physical=='liquid'and v['supportedInput']and not v['nonlinearScalePass']:probeFailures.append(dict(id=row['id'],probe=v))
   else:v['derivativeExclusion']='Physical crossing, coexistence, or unresolved endpoint'
   item['probes'].append(v)
  items.append(item)
 r=next(r for r in d['rows']if r['id']==primary);primaryPass=r.get('base',{}).get('phase')==0 and canon(r.get('inventories',{}).get('C'))
 invalid=[r['id']for r in items if r['physicalPhase']=='liquid'and r['backendPhase']==6]
 b1=next(r for r in items if r['id']=='B1-liquid-precision')
 out['browser'][engine]=dict(browserVersion=d['browserVersion'],primaryPass=primaryPass,rows=items,allErrors=allErrors,newErrors=newErrors,invalidLiquidLever=invalid,liquidCanonicalFailures=liquidCanonical,sameLiquidProbeFailures=probeFailures,B1=b1)
 browserGate &= primaryPass and not newErrors and not invalid and not liquidCanonical and not probeFailures
 out['primary'][name]=r
out['eligibleForLimitedA2']=bool(nativeGate and browserGate)
out['nativeFocusedGate']=bool(nativeGate);out['browserFocusedGate']=bool(browserGate)
if all((E/f'{n}-liquid44-focused.json').exists()for n in ['chromium','webkit']):out['browserRowsEqual']=read('chromium-liquid44-focused.json')['rows']==read('webkit-liquid44-focused.json')['rows']
out['knownLimitations']=['Upper Q>1 band remains explicitly invalid; no vapor-classification repair.','Saved vapor PT/cache defect remains a failing physical-consistency regression.','35-bar DU/support guard observations are retained separately.','No complete A2, B2 campaign or physical iPad qualification.']
save(E/'focused-gate.json',out)
print('Native focused gate',nativeGate,'browser focused gate',browserGate,'eligible limited A2',out['eligibleForLimitedA2'])
