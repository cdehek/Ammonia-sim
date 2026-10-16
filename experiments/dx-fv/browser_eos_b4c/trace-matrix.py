"""Exact saved base/probe inputs through diagnostic libraries, no regenerated probes."""
import argparse,json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--output',required=True);ap.add_argument('--full-vle',action='store_true');args=ap.parse_args()
e=Backend(args.library)
if args.full_vle:
 import ctypes as ct
 e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
rows=[]
for r in json.loads((E/'native-controlA.json').read_text())['rows']:
 for name,x in [('base',r['base'])]+[(q['axis']+str(q['step']),q['output']) for q in r['probes'] if 'output' in q]:
  marker=dict(id=r['request']['id'],sample=name,p=x['p'],h=x['h'],inputBits=x['inputBits']);print(json.dumps(dict(marker=marker)),file=sys.stderr,flush=True)
  try:out=dict(marker=marker,state=pack(e.state('PH',x['p'],x['h'])))
  except Exception as ex:out=dict(marker=marker,error=str(ex))
  rows.append(out)
save(Path(args.output),dict(library=args.library,fullVLE=args.full_vle,rows=rows))
