"""Explicit original component budgets and endpoint continuity from raw results."""
import json,os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'));primary='approach-30298.937123458254-liquid-0.001'
def read(n):return json.loads((E/n).read_text())
def compare(errors,limits,strict=False):return {k:dict(residual=v,limit=limits[k],passOriginalBudget=abs(v)<limits[k]if strict else abs(v)<=limits[k])for k,v in errors.items()}
def save(n,d):
 p=E/n;data=json.dumps(d,indent=2)+'\n'
 if p.exists():assert p.read_text()==data
 else:p.write_text(data)
out={};gate=read('focused-gate.json')
for filename in ['native-control44.json','native-liquid44.json','native-liquid44-full-vle.json']:
 r=next(r for r in read(filename)['rows']if r['request']['id']==primary);b=r['base'];ref=b['reference'];state=b['PH']['values'];errors={**b['residuals'],'T':state['T']-ref['state']['T']}
 inv={}
 for name,v in r['inventories'].items():
  inv[name]=dict(input=v['input'],canonical=compare(v['canonicalDifferences'],dict(p=.1,h=.1,T=1e-4))if'canonicalDifferences'in v else None,error=v.get('error'),independentEOSResiduals=v.get('independentDUResiduals'),canonicalPass=v['canonicalPass'])
 out[filename]=dict(request=r['request'],returned=b['PH'],independentDT=b['independentDT'],standalone=compare(errors,dict(p=10,h=50,T=.01),True),referenceRoot=compare(dict(p=ref['trace'][-1]['pResidual'],h=ref['trace'][-1]['hResidual']),dict(p=1e-5,h=1e-8),True),inventories=inv,stability=ref['stability'],probes=r['probes'])
for engine in ['chromium','webkit']:
 for build in ['control44','liquid44']:
  filename=f'{engine}-{build}-focused.json';r=next(r for r in read(filename)['rows']if r['id']==primary);b=r['base'];ref=out['native-control44.json']['referenceRoot'];reference=next(x for x in read('native-control44.json')['rows']if x['request']['id']==primary)['base']['reference']['state']
  inv={name:dict(input=v['input'],canonical=compare(v['differences'],dict(p=.1,h=.1,T=1e-4))if'differences'in v else None,error=v.get('error'),independentDT=v.get('independentDT'),canonicalPass=v['canonicalPass'],acceptedAdapterError=v.get('acceptedAdapterError'))for name,v in r['inventories'].items()}
  C=r['inventories']['C']['input']['values'];physicalU=C['M']*b['direct']['u']/1000;caloric=abs(physicalU-C['U_kJ'])/max(1,abs(C['U_kJ']))
  out[filename]=dict(requestedPH=r['args'],inputBits=b['inputBits'],returned=b['state'],selectedPhase=b['phase'],independentDT=b['direct'],standalone=compare(dict(p=b['pResidual'],h=b['hResidual'],T=b['state']['T']-reference['T']),dict(p=10,h=50,T=.01),True),inventories=inv,PHinventoryEOSMismatch=dict(energyKJ=physicalU-C['U_kJ'],normalizedEnergyMismatch=caloric,originalNonlinearScale=1e-11,passLocalScale=caloric<=1e-11),stability=b.get('derivatives'),probes=next(x for x in gate['browser'][engine]['rows']if x['id']==primary)['probes']if build=='liquid44'else r['probes'])
save('original-budget-ledger.json',out)
continuity=[]
for engine in ['chromium','webkit']:
 rows=read(f'{engine}-liquid44-focused.json')['rows']
 for p in sorted({r['args'][0]for r in rows}):
  for name,tag in [('hf','liquid'),('hg','vapor')]:
   base=next(r for r in rows if r['args'][0]==p and r['id'].endswith(f'-{tag}-0.0'));neighbors=[r for r in rows if r['args'][0]==p and r['id'].startswith('ULP-')and f'-{name}-'in r['id']];rho=base['base']['state']['rho'];T=base['base']['state']['T'];M=rho*(.003/5)
   samples=[]
   for r in neighbors:
    dr=r['base']['state']['rho']-rho;dT=r['base']['state']['T']-T;norm=abs(dr*(.003/5))/max(.01,M)
    samples.append(dict(id=r['id'],requestedPH=r['args'],dRho=dr,dT=dT,normalizedMassChange=norm,originalNonlinearScale=1e-11,withinOriginalScale=norm<=1e-11,selectedPhase=r['base']['phase'],Q=r['base']['state']['Q'],canonicalPass=r['inventories']['C']['canonicalPass']))
   continuity.append(dict(engine=engine,p=p,endpoint=name,baseRequestedPH=base['args'],basePhase=base['base']['phase'],baseQ=base['base']['state']['Q'],neighbors=samples))
assert all(n['withinOriginalScale']for r in continuity for n in r['neighbors'])
save('endpoint-continuity.json',dict(rows=continuity,note='Unresolved endpoint labels can change between liquid and two-phase at representable neighbors; density continuity is evaluated with the original normalized mass scale, not an invented quality tolerance. Upper Q>1 neighbors remain explicitly invalid.'))
print('All original primary budget comparisons retained; ULP endpoint mass continuity within original scale')
