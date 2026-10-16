"""Bounded native replay for logging parity, fresh/reused objects and phase paths."""
import argparse,ctypes as ct,json,sys,os
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);args=ap.parse_args()
inputs=json.loads((E/'fixed-inputs.json').read_text());e=Backend(args.library);e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
def call(engine,x):
 try:return dict(DU=pack(engine.state('DU',x['rho'],x['u'])))
 except Exception as ex:return dict(error=str(ex),exceptionType=type(ex).__name__)
def close(engine):
 engine.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];engine.call(engine.lib.AbstractState_free,engine.handle)
rows=[]
for r in inputs:
 x=r['input']['values'];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not r['fullVLE'])
 print(json.dumps(dict(marker=r['key'],id=r['id'],fullVLE=r['fullVLE'],rho=x['rho'],u=x['u'])),file=sys.stderr,flush=True)
 reused=call(e,x);fresh=Backend(args.library);fr=call(fresh,x);close(fresh)
 rows.append(dict(key=r['key'],reused=reused,fresh=fr,equal=reused==fr))
close(e)
Path(args.output).write_text(json.dumps(dict(library=args.library,traceEnabled='B5_TRACE'in os.environ,rows=rows),indent=2)+'\n');print(len(rows),'rows;',sum(not r['equal']for r in rows),'lifecycle differences')
