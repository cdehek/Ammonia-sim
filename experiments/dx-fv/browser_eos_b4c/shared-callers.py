"""Explicitly new H/S/U-pressure lifecycle diagnostics, never replacement fixtures."""
import argparse,ctypes as ct,json,math,sys
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,FIELDS,bits,pack,save,inventory,root
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);ap.add_argument('--full-vle',action='store_true');args=ap.parse_args()
class Caloric(Backend):
 def __init__(self):
  super().__init__(args.library)
  if args.full_vle:
   self.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];self.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
 def query(self,mode,p,y):
  pair,x,z={'PH':('HmassP_INPUTS',y,p),'PS':('PSmass_INPUTS',p,y),'PU':('PUmass_INPUTS',p,y)}[mode]
  self.call(self.lib.AbstractState_update,self.handle,self.lib.get_input_pair_index(pair.encode()),x,z)
  return {k:self.call(self.lib.AbstractState_keyed_output,self.handle,self.lib.get_param_index(v.encode())) for k,v in dict(FIELDS,s='Smass').items()}
 def close(self):
  self.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];self.call(self.lib.AbstractState_free,self.handle)
e=Caloric();ref=AbstractState('HEOS','Ammonia');sat=Backend();rows=[]
try:
 for p in [30298.937123458254,350000.,799999.9981754856,3500000.]:
  f=sat.state('PQ',p,0);g=sat.state('PQ',p,1)
  for mode,key,param in [('PH','h',C.iHmass),('PS','s',C.iSmass),('PU','u',C.iUmass)]:
   endpoints=[]
   for q in [0,1]:
    ref.unspecify_phase();ref.update(C.PQ_INPUTS,p,q);endpoints.append(ref.keyed_output(param))
   lo,hi=endpoints;delta=hi-lo
   for label,y in [('liquid',lo-.001*delta),('hf',lo),('mixture',lo+.4*delta),('hg',hi),('hg-minus-ULP',math.nextafter(hi,-math.inf)),('hg-plus-ULP',math.nextafter(hi,math.inf)),('upper-band',hi+.99e-9*delta),('outside-band',hi+1.01e-9*delta)]:
    row=dict(id=f'{mode}-{p}-{label}',mode=mode,input=[p,y],inputBits=[bits(p),bits(y)],endpointValues=endpoints,rawQuality=(y-lo)/delta)
    fresh=Caloric()
    try:
     s=e.query(mode,p,y);s2=fresh.query(mode,p,y);row.update(state=pack(s),freshState=pack(s2),freshEqualsReused=s==s2)
     ref.unspecify_phase();ref.update(C.DmassT_INPUTS,s['rho'],s['T']);dt={k:ref.keyed_output(C.get_parameter_index(v)) for k,v in dict(FIELDS,s='Smass').items()};row['independentDT']=pack(dt)
     if s['phase']!=6:
      row.update(requestedResiduals=dict(p=dt['p']-p,caloric=dt[key]-y),getterDifferences={k:s[k]-dt[k] for k in ['p','h','u','s']},stability=dict(cp=ref.cpmass(),cv=ref.cvmass(),kappa=ref.isothermal_compressibility(),hT_p=ref.first_partial_deriv(C.iHmass,C.iT,C.iP),sT_p=ref.first_partial_deriv(C.iSmass,C.iT,C.iP),uT_p=ref.first_partial_deriv(C.iUmass,C.iT,C.iP)),canonical=inventory(e,p,s['h'],s['rho'],s['T']))
     else:
      q=s['Q'];row['equilibrium']=dict(validQuality=0<=q<=1,TResidual=s['T']-f['T'],hResidual=s['h']-((1-q)*f['h']+q*g['h']),rhoResidual=s['rho']-1/((1-q)/f['rho']+q/g['rho']))
    except Exception as ex:row['error']=str(ex)
    finally:fresh.close()
    rows.append(row)
finally:e.close()
save(Path(args.output),dict(library=args.library,fullVLE=args.full_vle,rows=rows,origin='new shared-caller diagnostics, original saved PH matrix remains authoritative'))
print(len(rows),'shared caller diagnostics',sum('error' in r for r in rows),'errors')
