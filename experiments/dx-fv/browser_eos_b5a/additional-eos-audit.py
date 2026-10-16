"""Fresh EOS mass/energy checks for every returned additional inventory."""
import json,os
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));a=AbstractState('HEOS','Ammonia');rows=[]
for r in json.loads((E/'additional-inventories.json').read_text())['rows']:
 x=r['saved']['input']
 for build,paths in r['results'].items():
  for path,o in paths.items():
   v=dict(failureKey=r['saved']['failureKey'],build=build,path=path)
   if 'error' in o:v['error']=o['error']
   else:
    s=o['DU']['values']
    if s['phase']==6:a.unspecify_phase();a.update(C.QT_INPUTS,s['Q'],s['T'])
    else:a.specify_phase(C.iphase_liquid if s['rho']>225 else C.iphase_gas);a.update(C.DmassT_INPUTS,s['rho'],s['T'])
    nr=dict(mass=abs((a.rhomass()-x['rho'])*x['V'])/max(.01,x['M']),energy=abs(x['M']*a.umass()/1000-x['U_kJ'])/max(1,abs(x['U_kJ'])))
    v.update(freshEOS=dict(p=a.p(),rho=a.rhomass(),h=a.hmass(),u=a.umass()),normalizedResiduals=nr,nonlinearPass=max(nr.values())<=1e-11,canonicalPass=o['canonicalPass'],physicalQuality=o['physicalQuality'])
   rows.append(v)
out=dict(rows=rows,allReturnedPass=all(r.get('nonlinearPass',True) and r.get('canonicalPass',True) and r.get('physicalQuality',True) for r in rows),endpointPhysicalQualification=False)
p=E/'additional-eos-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'additional EOS rows; all returned original budgets',out['allReturnedPass'])
