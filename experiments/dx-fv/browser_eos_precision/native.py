"""Matching-version native diagnostics; no coupled imports or tolerance changes."""
import json,sys,time,struct,platform
from pathlib import Path
import CoolProp
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;inputs=json.loads((B/'inputs.json').read_text())
if '--no-super' in sys.argv:C.set_config_bool(C.ENABLE_SUPERANCILLARIES,False)
if '--primary' in sys.argv:inputs['cases']=inputs['cases'][:1]
state=AbstractState('HEOS','Ammonia');audit=AbstractState('HEOS','Ammonia')
def bits(x):return struct.pack('>d',x).hex()
def sample(p,h,method):
 a=AbstractState('HEOS','Ammonia') if method=='fresh' else state
 if method.startswith('high'):
  k='P|liquid' if method=='high-liquid' else 'P'
  out={f:C.PropsSI(key,k,p,'Hmass',h,'HEOS::Ammonia') for f,key in {'p':'P','h':'Hmass','rho':'Dmass','T':'T','u':'Umass','Q':'Q'}.items()}
 else:
  if method=='after-PT':a.update(C.PT_INPUTS,350000,240)
  if method=='after-PQ':a.update(C.PQ_INPUTS,350000,.5)
  if method=='after-DU':a.update(C.DmassUmass_INPUTS,708.6710262223568,94480.59153610271)
  if method=='molar':a.update(C.HmolarP_INPUTS,h*a.molar_mass(),p)
  else:a.update(C.HmassP_INPUTS,h,p)
  out={'p':a.p(),'h':a.hmass(),'rho':a.rhomass(),'T':a.T(),'u':a.umass(),'Q':a.Q()}
 audit.update(C.DmassT_INPUTS,out['rho'],out['T'])
 out.update(pEOS=audit.p(),hEOS=audit.hmass(),cp=audit.cpmass(),cv=audit.cvmass(),kappa=audit.isothermal_compressibility(),rhoP=audit.first_partial_deriv(C.iDmass,C.iP,C.iHmass),rhoH=audit.first_partial_deriv(C.iDmass,C.iHmass,C.iP),hp=audit.first_partial_deriv(C.iHmass,C.iP,C.iT),rhoT=audit.first_partial_deriv(C.iDmass,C.iT,C.iP))
 out['pResidual']=out['pEOS']-p;out['hResidual']=out['hEOS']-h
 out['workIdentity']=out['h']-out['u']-out['p']/out['rho']
 return out
rows=[];start=time.perf_counter()
for q in inputs['cases']:
 p,h=q['args'];methods=inputs['methods'] if q.get('primary') else ['reused','high-liquid']
 for method in methods:
  probes=[('P',dp) for dp in inputs['sweep']]+[('P',-.01),('H',q['dh']),('H',-q['dh'])] if q.get('primary') else [('P',q['dp']),('H',q['dh'])]
  for axis,step in probes:
   args=[p+step,h] if axis=='P' else [p,h+step]
   try:
    if method=='reverse':pert=sample(*args,method);base=sample(p,h,method)
    else:base=sample(p,h,method);pert=sample(*args,method)
    analytic=base['rhoP' if axis=='P' else 'rhoH'];fd=(pert['rho']-base['rho'])/step
    rows.append(dict(id=q['id'],method=method,axis=axis,step=step,args=[p,h],inputBits=q['inputBits'],perturbedInputBits=list(map(bits,args)),actualStep=args[0 if axis=='P' else 1]-[p,h][0 if axis=='P' else 1],base=base,perturbed=pert,analytic=analytic,finite=fd,ratio=fd/analytic))
   except Exception as e:rows.append(dict(id=q['id'],method=method,axis=axis,step=step,error=str(e)))
out={'version':CoolProp.__version__,'git':CoolProp.__gitrevision__,'python':platform.python_version(),'configuration':json.loads(C.get_config_as_json_string()),'nativeOnlyPhaseSetter':hasattr(state,'specify_phase'),'rows':rows,'elapsedSeconds':time.perf_counter()-start,'note':'High-level P/H getters may echo input; residuals independently recomputed by DmassT. Official solver steps unchanged.'}
name=sys.argv[1];target=B/'evidence'/name
assert not target.exists(),'Retain completed evidence'
target.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print(name,len(rows),'rows',out['elapsedSeconds'],'s')
