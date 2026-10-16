"""Matched bounded native C-API PH update timing, excluding output getters."""
import os
import argparse,ctypes as ct,json,resource,sys,time
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,save
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
t=time.perf_counter();eos=Backend(args.library);factory=time.perf_counter()-t;pair=eos.lib.get_input_pair_index(b'HmassP_INPUTS')
requests=[r['request']for r in json.loads((E/'native-control44.json').read_text())['rows']]
groups=[('primary',[q for q in requests if q['args']==[30298.937123458254,98904.56398938334]]),('boundary',requests[:57]),('B1',[q for q in requests if q['id']=='B1-liquid-precision'])]
rows=[]
for repeat in range(3):
 for name,inputs in groups:
  start=time.perf_counter();calls=0;errors=[]
  for _ in range(25):
   for q in inputs:
    p,h=q['args']
    try:eos.call(eos.lib.AbstractState_update,eos.handle,pair,h,p)
    except Exception as exc:errors.append(str(exc))
    calls+=1
  rows.append(dict(group=name,round=repeat,calls=calls,elapsedSeconds=time.perf_counter()-start,errors=errors))
save(Path(args.output),dict(library=args.library,firstFactorySeconds=factory,rows=rows,maxRSSKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,timing='C API AbstractState_update only, including ctypes and error-buffer overhead; output getters excluded'))
