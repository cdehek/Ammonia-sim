"""Same-EOS independent DT audits; preserved inputs and explicit new diagnostics."""
import argparse, ctypes as ct, json, sys
from pathlib import Path
from CoolProp import CoolProp as C
from CoolProp import AbstractState
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend, pack, save, bits, inventory
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
audit=Backend();a=AbstractState('HEOS','Ammonia')
saved=json.loads((B.parent/'browser_eos_b4a/inputs.json').read_text())
old=json.loads((B.parent/'browser_eos_b3/evidence/chromium-build44.json').read_text())['rows']
cases=[q for q in saved if q['id'] in ['B1-vapor-regression','B1-liquid-precision','approach-30298.937123458254-liquid-0.001'] or ('focused-' in q['id'])]
v=next(r for r in old if r['id']=='B1-vapor-regression')
cases += [dict(id='saved-vapor-'+p['axis']+str(p['step']),args=[p['output']['p'],p['output']['h']],origin='exact B3 signed probe') for p in v['probes']]
for p in [30298.937123458254,350000.,799999.9981754856,3500000.]:
 for q in [0,1]:
  s=audit.state('PQ',p,q);cases.append(dict(id=f'endpoint-{p}-{q}',args=[p,s['h']],origin='new diagnostic native PQ endpoint'))
 for dT in [-.01,-.001,.001,.01,10.]:
  s=audit.state('PQ',p,0);a.specify_phase(C.iphase_liquid if dT<0 else C.iphase_gas)
  a.update(C.PT_INPUTS,p,s['T']+dT)
  cases.append(dict(id=f'offset-{p}-{dT}',args=[p,a.hmass()],origin='new diagnostic temperature offset converted by unmodified EOS'))

def extras(e):
 if e.lib:
  L=e.lib;out={}
  for name in ['dalphar_dtau_constdelta','dalphar_ddelta_consttau','dalpha0_dtau_constdelta']:
   out[name]=e.call(L.AbstractState_keyed_output,e.handle,L.get_param_index(name.encode()))
  L.AbstractState_first_partial_deriv.restype=ct.c_double
  L.AbstractState_first_partial_deriv.argtypes=[ct.c_long]*4+[ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
  for name,indices in [('pRho',('P','Dmass','T')),('hT',('Hmass','T','Dmass')),('uT',('Umass','T','Dmass'))]:
   out[name]=e.call(L.AbstractState_first_partial_deriv,e.handle,*[L.get_param_index(i.encode()) for i in indices])
  return out
 x=e.a
 return dict(dalphar_dtau_constdelta=x.dalphar_dTau(),dalphar_ddelta_consttau=x.dalphar_dDelta(),dalpha0_dtau_constdelta=x.dalpha0_dTau(),pRho=x.first_partial_deriv(C.iP,C.iDmass,C.iT),hT=x.first_partial_deriv(C.iHmass,C.iT,C.iDmass),uT=x.first_partial_deriv(C.iUmass,C.iT,C.iDmass))

def snapshot(e,mode,x,y):
 s=e.state(mode,x,y);dt=audit.state('DT',s['rho'],s['T']);out=dict(mode=mode,input=[x,y],inputBits=[bits(x),bits(y)],state=pack(s),independentDT=pack(dt))
 if s['phase']!=6:
  own=extras(e);ref=extras(audit);out.update(derivatives=own,independentDerivatives=ref,derivativeDifferences={k:own[k]-ref[k] for k in own},getterDifferences={k:s[k]-dt[k] for k in ['p','h','u']})
  V=.003/5;M=s['rho']*V;U=M*(s['h']/1000)-100*(s['p']/1e5)*V
  out['normalizedEnergyInconsistency']=abs(M*(s['u']-dt['u'])/1000)/max(1,abs(U))
 else:
  f=audit.state('PQ',s['p'],0);g=audit.state('PQ',s['p'],1);q=s['Q']
  out['equilibrium']=dict(validQuality=0<=q<=1,temperatureResidual=s['T']-f['T'],rhoResidual=s['rho']-1/((1-q)/f['rho']+q/g['rho']),hResidual=s['h']-((1-q)*f['h']+q*g['h']),uResidual=s['u']-((1-q)*f['u']+q*g['u']))
 return out

rows=[]
for q in cases:
 p,h=q['args'];e=Backend(args.library);row=dict(request=q,sequences=[])
 try:
  base=snapshot(e,'PH',p,h);s=base['state']['values'];row['base']=base
  row['inventory']=inventory(e,p,h,s['rho'],s['T'])
  # PH->PT->PH and repeated PT/PH; all calls go to the same object.
  actions=[('PH',p,h),('PH',p,h)]
  if s['phase']!=6:actions=[('PT',p,s['T']),('PT',p,s['T']),('PH',p,h),('PH',p,h),('DU',s['rho'],s['u']),('PT',p,s['T']),('PH',p,h)]
  for mode,x,y in actions:
   try:row['sequences'].append(snapshot(e,mode,x,y))
   except Exception as ex:row['sequences'].append(dict(mode=mode,error=str(ex)))
  if s['phase']!=6:
   fresh=Backend(args.library)
   try:row['freshPT']=snapshot(fresh,'PT',p,s['T'])
   except Exception as ex:row['freshPTError']=str(ex)
   fresh.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];fresh.call(fresh.lib.AbstractState_free,fresh.handle)
 except Exception as ex:row['error']=str(ex)
 finally:
  e.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];e.call(e.lib.AbstractState_free,e.handle)
 rows.append(row)
save(Path(args.output),dict(library=args.library,cases=cases,rows=rows,reference='unmodified CoolProp 8.0.0 independent state DT and derivatives',nonlinearScale=1e-11))
print(len(rows),'lifecycle cases',sum('error'in r for r in rows),'base errors')
