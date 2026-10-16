"""Read-only archived native comparison for the focused browser matrix."""
import importlib.util,json,os,struct,time
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'))
s=importlib.util.spec_from_file_location('c1native',B.parent/'browser_eos_b5b_c1/native.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.D=Path('/workspace/c2-native')
e=m.Native();browser=json.loads((E/'chromium-replay.json').read_text());rows=[]
for group in ['rows','falseAcceptance','matrix','endpoints']:
 for r in browser[group]:
  x={k:struct.unpack('>d',bytes.fromhex(v))[0] for k,v in r['input']['bits'].items()};out=dict(key=r.get('key',r.get('id')),group=group,input=r['input'])
  start=time.perf_counter()
  try:out['raw']=m.pack(e.state('DU',x['rho'],x['u']))
  except Exception as ex:out['error']=str(ex)
  out['seconds']=time.perf_counter()-start;rows.append(out)
gate=m.Native('GateA');endpoints=[]
for r in browser['endpoints']:
 x=r['input']['values'];out=dict(key=r['key'],qualification='Original independent phase unresolved')
 gate.L.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
 try:out['raw']=m.pack(gate.state('DU',x['rho'],x['u']))
 except Exception as ex:out['error']=str(ex)
 endpoints.append(out)
p=E/'native.json';assert not p.exists();p.write_text(json.dumps(dict(librarySHA256=e.sha,gateALibrarySHA256=gate.sha,rows=rows,gateAEndpoints=endpoints),indent=2)+'\n')
print(len(rows),'native comparisons;',len(endpoints),'Gate A unresolved endpoints')
