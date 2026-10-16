"""Independent derivative-cache snapshots at exact saved upper inputs and inherited regressions."""
import argparse,ctypes as ct,json,sys
from pathlib import Path
import os
from CoolProp import CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
e=Backend(args.library);ref=Backend();L=e.lib
L.AbstractState_first_partial_deriv.restype=ct.c_double;L.AbstractState_first_partial_deriv.argtypes=[ct.c_long]*4+[ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
requests=[r['request'] for r in json.loads((E/'native-controlA.json').read_text())['rows'] if r['base']['PH']['values']['Q']>1 or r['request']['id'] in ['B1-liquid-precision','B1-vapor-regression','approach-30298.937123458254-liquid-0.001']]
rows=[]
for q in requests:
 p,h=q['args'];s=e.state('PH',p,h);dt=ref.state('DT',s['rho'],s['T']);own={};independent={}
 for name,indices in [('pRho',('P','Dmass','T')),('hT',('Hmass','T','Dmass')),('uT',('Umass','T','Dmass')),('rhoP_h',('Dmass','P','Hmass')),('rhoH_p',('Dmass','Hmass','P'))]:
  own[name]=e.call(L.AbstractState_first_partial_deriv,e.handle,*[L.get_param_index(i.encode()) for i in indices]);independent[name]=ref.a.first_partial_deriv(*[C.get_parameter_index(i) for i in indices])
 rows.append(dict(request=q,state=pack(s),independentDT=pack(dt),derivatives=own,independentDerivatives=independent,derivativeDifferences={k:own[k]-independent[k] for k in own},getterDifferences={k:s[k]-dt[k] for k in ['p','h','u']}))
save(Path(args.output),dict(rows=rows,library=args.library,note='Differences are recorded without inventing a derivative tolerance. Original signed inventory scales are the numerical gate.'))
