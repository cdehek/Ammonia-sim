"""Trace exact preserved signed probes, repeat runs, and isolated PT calls."""
import argparse,json,sys,os,ctypes as ct
from pathlib import Path
from native import Backend,bits,pack,save
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B3_EVIDENCE',B/'evidence'))
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);ap.add_argument('--disable-superanc',action='store_true')
args=ap.parse_args();eos=Backend(args.library);audit=Backend()
if args.disable_superanc:
    eos.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
    eos.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
cases=json.loads((E/'chromium-build44.json').read_text())['rows']
out=[]
for id in ['approach-30298.937123458254-liquid-0.001','B1-vapor-regression']:
    row=next(q for q in cases if q['id']==id)
    samples=[('base',row['base']['p'],row['base']['h'])]+[(q['axis']+str(q['step']),q['output']['p'],q['output']['h']) for q in row['probes']]
    for name,p,h in samples:
        for repeat in range(2):
            print(json.dumps(dict(marker=id,probe=name,repeat=repeat,args=[p,h],bits=[bits(p),bits(h)])),file=sys.stderr,flush=True)
            ph=eos.state('PH',p,h);dt=audit.state('DT',ph['rho'],ph['T'])
            out.append(dict(id=id,probe=name,repeat=repeat,inputs=pack(dict(p=p,h=h)),PH=pack(ph),independentDT=pack(dt)))
    if id=='B1-vapor-regression':
        for repeat in range(2):
            p,h=row['args']
            print(json.dumps(dict(marker='prepare-isolated-PT',repeat=repeat)),file=sys.stderr,flush=True)
            ph=eos.state('PH',p,h)
            print(json.dumps(dict(marker='isolated-PT',p=p,T=ph['T'],repeat=repeat)),file=sys.stderr,flush=True)
            pt=eos.state('PT',p,ph['T']);dt=audit.state('DT',pt['rho'],pt['T'])
            out.append(dict(id='isolated-PT',repeat=repeat,PT=pack(pt),independentDT=pack(dt)))
save(Path(args.output),dict(library=args.library,disableSuperanc=args.disable_superanc,rows=out))
