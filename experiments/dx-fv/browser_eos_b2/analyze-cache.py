import os
"""First-order cache-consistency attribution; diagnostic, never a property fix."""
import json
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
d=json.loads((E/'forensics-8.0.0-default.json').read_text());r=d['rows'][0];s=r['PH'];a=AbstractState('HEOS','Ammonia');a.update(C.DmassT_INPUTS,s['rho'],s['T'])
pr=a.first_partial_deriv(C.iP,C.iDmass,C.iT);hr=a.first_partial_deriv(C.iHmass,C.iDmass,C.iT)
dp=s['p']-r['independentDT']['p'];dr=dp/pr
# calc_hmolar sets final delta but can consume old cached Helmholtz derivatives.
# Remove the explicit delta-prefactor derivative from the full EOS h_rho.
explicitDelta=(a.p()/s['rho']-a.gas_constant()/a.molar_mass()*s['T'])/s['rho']
sensitivity=hr-explicitDelta;observed=s['h']-r['independentDT']['h'];pred=sensitivity*dr
out=dict(dpdrho=pr,dhdrhoAtT=hr,explicitDeltaPrefactorDerivative=explicitDelta,staleDerivativeSensitivity=sensitivity,cachedPressureMinusDT=dp,inferredLastEvaluatedDensityMinusReturned=dr,predictedCachedHMinusDT=pred,observedCachedHMinusDT=observed,relativeAttributionError=(pred-observed)/observed,PHminusTarget=s['h']-d['inputs'][1],DTminusTarget=r['independentDT']['h']-d['inputs'][1],normalizedPhysicalEnergyDefectAtFiveSectionV=abs(s['rho']*.0006*(r['independentDT']['h']-d['inputs'][1])/1000),nonlinearBudget=1e-11,referenceOnly=True,limitation='First-order numerical attribution plus source inspection, not an instrumented WASM internal trace.')
(E/'cache-attribution-refined.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
