"""Historical matching 7.2 wheel, exact saved DU coordinates; no internal trace."""
import sys,json
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'));from native import Backend,pack
import CoolProp
assert CoolProp.__version__=='7.2.0'
inputs=json.loads((E/'fixed-inputs.json').read_text());e=Backend();rows=[]
for r in inputs:
 x=r['input']['values'];out=dict(key=r['key'])
 try:out['DU']=pack(e.state('DU',x['rho'],x['u']))
 except Exception as ex:out.update(error=str(ex),exceptionType=type(ex).__name__)
 rows.append(out)
(E/'native72-fixed-replay.json').write_text(json.dumps(dict(version=CoolProp.__version__,revision=CoolProp.__gitrevision__,rows=rows),indent=2)+'\n');print(CoolProp.__version__,len(rows),'errors',sum('error'in r for r in rows))
