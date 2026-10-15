"""Physical-branch analysis of invalid backend Q-band outputs.

Independent native DT roots supply homogeneous derivatives for valid liquid or
vapor inputs that the backend calls two-phase. Original WASM finite differences
are reused verbatim; no root/correction is passed back to the browser model.
"""
import os,json
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'))
a=AbstractState('HEOS','Ammonia');sat=AbstractState('HEOS','Ammonia');roots={};saturations={};results=[]
def saturation(p):
 if p not in saturations:
  sat.update(C.PQ_INPUTS,p,0);hf,T=sat.hmass(),sat.T();sat.update(C.PQ_INPUTS,p,1);saturations[p]=dict(hf=hf,hg=sat.hmass(),T=T)
 return saturations[p]
def physical(p,h):
 s=saturation(p)
 if min(abs(h-s['hf']),abs(h-s['hg']))<=1e-8:return 'endpoint within native reference resolution'
 return 'liquid' if h<s['hf'] else 'vapor' if h>s['hg'] else 'two-phase'
def root(p,h,branch,rho,T):
 key=(p,h,branch)
 if key in roots:return roots[key]
 a.specify_phase(C.iphase_liquid if branch=='liquid' else C.iphase_gas);trace=[]
 for _ in range(12):
  a.update(C.DmassT_INPUTS,rho,T);rp,rh=a.p()-p,a.hmass()-h
  trace.append(dict(rho=rho,T=T,pResidual=rp,hResidual=rh))
  if abs(rp)<1e-5 and abs(rh)<1e-8:break
  pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT);pt=a.first_partial_deriv(C.iP,C.iT,C.iDmass);hr=a.first_partial_deriv(C.iHmass,C.iDmass,C.iT);ht=a.first_partial_deriv(C.iHmass,C.iT,C.iDmass);det=pr*ht-pt*hr
  rho+=(-rp*ht+pt*rh)/det;T+=(-pr*rh+hr*rp)/det
 last=trace[-1];r=dict(branch=branch,trace=trace,referenceConverged=abs(last['pResidual'])<1e-5 and abs(last['hResidual'])<1e-8,rhoP=a.first_partial_deriv(C.iDmass,C.iP,C.iHmass),rhoH=a.first_partial_deriv(C.iDmass,C.iHmass,C.iP),cp=a.cpmass(),cv=a.cvmass(),kappa=a.isothermal_compressibility(),TMinusSaturation=a.T()-saturation(p)['T']);roots[key]=r;return r
for f in sorted(E.glob('*-phase-*.json')):
 d=json.loads(f.read_text());build=d['build']
 if (build=='official72')!=(CoolProp.__version__=='7.2.0'):continue
 for q in d['rows']:
  s=q.get('base')
  if not s or s['phase']!=6 or 0<=s['state']['Q']<=1:continue
  p,h=q['args'];branch=physical(p,h);endpoint=branch.startswith('endpoint')
  limit='liquid' if s['state']['Q']<0 else 'vapor'
  r=root(p,h,limit,s['state']['rho'],s['state']['T'])
  item=dict(file=f.name,id=q['id'],args=q['args'],inputBits=q['inputBits'],backendPhase=s['phase'],backendQuality=s['state']['Q'],physicalPhase=branch,homogeneousReference=r,probes=[])
  for probe in q['probes']:
   row=dict(axis=probe['axis'],step=probe['step'],actualIncrement=probe['actualIncrement'])
   if 'error' in probe:row['error']=probe['error'];item['probes'].append(row);continue
   out=probe['output'];other=physical(out['p'],out['h']);row.update(physicalProbePhase=other,backendProbePhase=out['phase'],backendProbeQuality=out['state']['Q'],finite=probe['finite'],inputBits=out['inputBits'])
   if not endpoint and branch==other and branch in ['liquid','vapor']:
    analytic=r['rhoP' if probe['axis']=='P' else 'rhoH'];contamination=abs((out['state']['rho']-s['state']['rho'])-analytic*probe['step']);volume=.003/5
    row.update(analyticAtIndependentPhysicalRoot=analytic,ratio=probe['finite']/analytic,physicalPhaseCrossing=False,relativeDensityProbeContamination=contamination/s['state']['rho'],normalizedMassProbeContamination=volume*contamination/max(.01,s['state']['rho']*volume))
   else:row.update(physicalPhaseCrossing=branch!=other,exclusion='Physical phase crossing or endpoint: homogeneous smoothness not required')
   item['probes'].append(row)
  results.append(item)
out=dict(version=CoolProp.__version__,git=CoolProp.__gitrevision__,referenceOnly=True,rootLimits=dict(pressurePa=1e-5,enthalpyJkg=1e-8),nonlinearScaleForLocalDiagnostic=1e-11,rows=results)
target=E/f'boundary-derivatives-native-{CoolProp.__version__}.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
comparisons=[p for r in results for p in r['probes'] if 'ratio' in p]
print(CoolProp.__version__,len(results),'boundary rows;',len(comparisons),'same physical branch probes; ratio range',min(p['ratio'] for p in comparisons),max(p['ratio'] for p in comparisons))
