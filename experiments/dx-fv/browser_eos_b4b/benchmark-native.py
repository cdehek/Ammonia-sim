"""Matched complete property snapshots; no timing acceptance threshold."""
import argparse,json,sys,time,resource
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,save
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
e=Backend(args.library);p,h=799999.9981754856,1624022.744737779;s=e.state('PH',p,h)
groups=[('vapor-PH','PH',p,h),('vapor-PT','PT',p,s['T']),('liquid-PH','PH',30298.937123458254,98904.56398938334),('B1-PH','PH',30298.937123458254,94523.34612321304)];rows=[]
for round_ in range(3):
 for group,mode,x,y in groups:
  t=time.perf_counter();calls=0;checksum=0;errors=[]
  while time.perf_counter()-t<.15:
   try:checksum+=e.state(mode,x,y)['rho']
   except Exception as ex:errors.append(str(ex))
   calls+=1
  rows.append(dict(round=round_,group=group,calls=calls,elapsedMS=(time.perf_counter()-t)*1000,checksum=checksum,errors=errors))
save(Path(args.output),dict(library=args.library,rows=rows,maxRSSKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,measurement='ctypes update plus seven getters; not pure kernel time'))
