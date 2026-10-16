"""Small shared H/S/U caller and property-domain regression; retain errors."""
import argparse,ctypes as ct,json,sys
from pathlib import Path
from CoolProp import CoolProp as C,AbstractState
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,root,pack,save,inventory
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
eos=Backend(args.library);audit=Backend();a=AbstractState('HEOS','Ammonia');rows=[]
for p in [30298.937123458254,350000.,799999.9981754856,3500000.]:
 f=audit.state('PQ',p,0);g=audit.state('PQ',p,1)
 for name,h in [('liquid',f['h']-.001),('mixture',f['h']+.4*(g['h']-f['h'])),('vapor',g['h']+10000)]:
  if name=='mixture':a.update(C.HmassP_INPUTS,h,p)
  else:
   rt=root(p,h,'liquid'if name=='liquid'else'gas',(f['rho']if name=='liquid'else g['rho'],f['T']));a.specify_phase(C.iphase_liquid if name=='liquid'else C.iphase_gas);a.update(C.DmassT_INPUTS,rt['state']['rho'],rt['state']['T']);a.unspecify_phase()
  for pair,value in [('PSmass_INPUTS',a.smass()),('PUmass_INPUTS',a.umass())]:
   row=dict(p=p,hReference=h,phaseReference=name,pair=pair,value=value)
   try:
    eos.call(eos.lib.AbstractState_update,eos.handle,eos.lib.get_input_pair_index(pair.encode()),p,value)
    s={k:eos.call(eos.lib.AbstractState_keyed_output,eos.handle,eos.lib.get_param_index(v.encode()))for k,v in {'p':'P','h':'Hmass','rho':'Dmass','T':'T','Q':'Q','phase':'Phase'}.items()};dt=audit.state('DT',s['rho'],s['T']);row.update(state=pack(s),independentDT=pack(dt),eosResiduals=dict(p=dt['p']-p,h=dt['h']-h),inventory=inventory(eos,p,h,s['rho'],s['T']))
   except Exception as exc:row['error']=str(exc)
   rows.append(row)
for mode,x,y,label in [('PQ',350000,-.0001,'negative-quality'),('PQ',350000,1.0001,'quality-above-one'),('PH',30298.937123458254,-1e8,'invalid-enthalpy'),('PH',0,98904.56398938334,'zero-pressure'),('PH',-1,98904.56398938334,'negative-pressure'),('PH',float('nan'),98904.56398938334,'nan-pressure'),('PQ',1e8,0,'above-critical-saturation'),('PT',350000,190,'below-fluid-temperature'),('PH',30000,100000,'adapter-low-pressure-boundary'),('PH',3500000,600000,'adapter-high-pressure-boundary')]:
 row=dict(mode=mode,args=[x if x==x else 'NaN',y],label=label)
 try:row['state']=pack(eos.state(mode,x,y))
 except Exception as exc:row['error']=str(exc)
 rows.append(row)
save(Path(args.output),dict(library=args.library,rows=rows))
