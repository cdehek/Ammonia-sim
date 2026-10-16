"""Bounded serial native DU timing; exceptions are counted, never timed as passes."""
import os
import ctypes as ct,json,time,sys,statistics,resource
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'));from native import Backend
inputs=json.loads((E/'fixed-inputs.json').read_text());groups={}
for label,key in [('resolved-liquid','native-ledger-146'),('vapor-endpoint','native-ledger-148')]:groups[label]=next(r for r in inputs if r['key']==key)
for label,match in [('mixture','mixture'),('stable-vapor','stable-vapor')]:groups[label]=next(r for r in inputs if match in r['id'] and '3500000' in r['id'])
rows=[]
progress=(E/'native-performance-progress.jsonl').open('x')
for name,lib in [('control','/workspace/b5-libs/rebuilt-control.so'),('A1','/workspace/b5-libs/A1.so')]:
 t=time.perf_counter();e=Backend(lib);init=time.perf_counter()-t;e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
 for full in [False,True]:
  e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full)
  for label,r in groups.items():
   x=r['input']['values'];rounds=[];errors=0;calls=0;err=None
   for _ in range(5):
    start=time.perf_counter();n=0
    while time.perf_counter()-start<.15:
     try:e.state('DU',x['rho'],x['u'])
     except Exception as ex:errors+=1;err=str(ex)
     n+=1
    rounds.append((time.perf_counter()-start)/n*1e6);calls+=n
   rows.append(dict(build=name,group=label,key=r['key'],fullVLE=full,medianMicroseconds=statistics.median(rounds),roundMicroseconds=rounds,calls=calls,exceptions=errors,lastException=err,initializationSeconds=init,maxRSSKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
   progress.write(json.dumps(rows[-1])+'\n');progress.flush()
progress.close()
p=E/'native-performance.json';assert not p.exists(),p
p.write_text(json.dumps(dict(rows=rows,interface='complete C API update plus p/T/rho/h/u/Q/phase getters via ctypes',matchedWorkloads=True,serial=True,rounds=5,roundDurationSeconds=.15,WASM=None,worker=None,note='Descriptive Linux host timings. Error-path cost is not successful recovery cost. No simulator or iPad performance claim.'),indent=2)+'\n')
print([(r['build'],r['group'],r['fullVLE'],round(r['medianMicroseconds'],2),r['exceptions']) for r in rows])
