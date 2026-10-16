"""Exact original probes plus fixed PT coordinates read from captured B3 execution."""
import argparse,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save,bits
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
e=Backend(args.library);audit=Backend();old=json.loads((B.parent/'browser_eos_b3/evidence/chromium-build44.json').read_text())['rows'];out=[]
for ident in ['B1-vapor-regression','approach-30298.937123458254-liquid-0.001','B1-liquid-precision']:
 row=next((r for r in old if r['id']==ident),None)
 if row is None:
  requests=[('base',30298.937123458254,94523.34612321304)]
 else:requests=[('base',*row['args'])]+[(r['axis']+str(r['step']),r['output']['p'],r['output']['h'])for r in row['probes']]
 for name,p,h in requests:
  for repeat in range(2):
   print(json.dumps(dict(marker=ident,probe=name,repeat=repeat,args=[p,h],bits=[bits(p),bits(h)])),file=sys.stderr,flush=True)
   s=e.state('PH',p,h);dt=audit.state('DT',s['rho'],s['T']);out.append(dict(id=ident,probe=name,repeat=repeat,PH=pack(s),independentDT=pack(dt)))
for version in ['30','44']:
 events=[json.loads(l)for l in (B.parent/f'browser_eos_b3/evidence/probes-trace{version}.jsonl').read_text().splitlines()]
 marker=next(r for r in events if r.get('marker')=='isolated-PT')
 for repeat in range(2):
  p,T=marker['p'],marker['T'];print(json.dumps(dict(marker='fixed-B3-PT'+version,p=p,T=T,repeat=repeat)),file=sys.stderr,flush=True)
  s=e.state('PT',p,T);dt=audit.state('DT',s['rho'],s['T']);out.append(dict(id='fixed-B3-PT'+version,repeat=repeat,requestedPT=pack(dict(p=p,T=T)),PT=pack(s),independentDT=pack(dt)))
save(Path(args.output),dict(library=args.library,rows=out))
