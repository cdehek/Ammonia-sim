"""Independent roots and saturation evidence before any B4C functional edit."""
import hashlib,json,math,subprocess,sys
from pathlib import Path
import os
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent; E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence')); S=Path('/workspace/coolprop-b4c')
sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import root,Backend,bits,pack,save
old=json.loads((B.parent/'browser_eos_b4b/evidence/source-stage-candidateB.json').read_text())['trackedSourceSHA256']
current={n:hashlib.sha256((S/n).read_bytes()).hexdigest() for n in old}
assert current==old
save(E/'source-stage-controlA.json',dict(upstream='ae81610e7d23efc57f9d051c8e70a4d66e87537f',trackedSourceSHA256=current))
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k not in ['elapsedSeconds','library','label']}
 if isinstance(x,list):return list(map(clean,x))
 return x
historical=json.loads((B.parent/'browser_eos_b4b/evidence/native-candidateB.json').read_text())
replay=json.loads((E/'native-controlA.json').read_text())
assert clean(historical)==clean(replay)
inv=json.loads((E/'original-upper-quality-inventory.json').read_text())
samples={}
for r in inv['native']['invalidSnapshots']:
 x=r['data']; key=tuple(x['inputBits']); samples[key]=x
roots=[]
for key,x in samples.items():
 p,h=x['p'],x['h'];g=x['saturation']['vapor']['values'];rt=root(p,h,'gas',(g['rho'],g['T']))
 assert rt['converged'] and all(v>0 for v in rt['stability'].values())
 roots.append(dict(inputBits=key,p=p,h=h,hMinusHg=x['hMinusHg'],physicalPhase=x['physicalPhase'],root=rt,temperatureAboveSaturation=rt['state']['T']-g['T']))
boundaries=[]
for p in sorted({r['request']['args'][0] for r in replay['rows']}):
 states={}
 for superanc in [True,False]:
  C.set_config_bool(C.ENABLE_SUPERANCILLARIES,superanc)
  f=AbstractState('HEOS','Ammonia');g=AbstractState('HEOS','Ammonia');f.update(C.PQ_INPUTS,p,0);g.update(C.PQ_INPUTS,p,1)
  states[str(superanc)]=dict(Tf=f.T(),Tg=g.T(),hf=f.hmass(),hg=g.hmass(),rhof=f.rhomass(),rhog=g.rhomass(),pressureResiduals=[f.p()-p,g.p()-p],chemicalPotentialDifference=f.gibbsmass()-g.gibbsmass())
 C.set_config_bool(C.ENABLE_SUPERANCILLARIES,True)
 a=states['True']
 for endpoint in ['hf','hg']:
  for direction in [-1,0,1]:
   h=a[endpoint] if direction==0 else math.nextafter(a[endpoint],math.inf*direction)
   rt=root(p,h,'gas' if endpoint=='hg' else 'liquid',(a['rhog' if endpoint=='hg' else 'rhof'],a['Tg' if endpoint=='hg' else 'Tf']))
   boundaries.append(dict(p=p,h=h,inputBits=[bits(p),bits(h)],endpoint=endpoint,directionULP=direction,saturationPaths=states,molarRoundTripDifference=h*.01703052- a[endpoint]*.01703052,root=rt,classification='endpoint-unresolved at original reference resolution'))
touches=inv['native']['samePhysicalVaporTouches'];supported=[q for q in touches if q['probe']['output']['supportedInput']]
save(E/'preimplementation-thermodynamics.json',dict(controlMatchesHistoricalExactlyExceptTiming=True,reference=dict(version=CoolProp.__version__,revision=CoolProp.__gitrevision__),uniqueInvalidSnapshots=roots,endpointNeighbors=boundaries,historicalSupportedVaporComparisons=len(supported),allVaporComparisons=len(touches),unsupportedVaporComparisons=[q for q in touches if not q['probe']['output']['supportedInput']],functionalB4CPatchApplied=False))
print('Verified exact B4B source and native replay; stable vapor roots',len(roots),'supported comparisons',len(supported),'endpoint neighbors',len(boundaries))
