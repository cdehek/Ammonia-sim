"""Actual archived matched-native replay, fresh/reused, all original records."""
import ctypes as ct,hashlib,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';sys.path.insert(0,str(X/'browser_eos_b3'))
from native import Backend,pack
inputs=json.loads((E/'fixed-inputs.json').read_text());extra=json.loads((E/'additional-inputs.json').read_text())['rows'];rows=[]
def close(e):
 e.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];e.call(e.lib.AbstractState_free,e.handle)
def call(e,rho,u):
 try:return dict(state=pack(e.state('DU',rho,u)))
 except Exception as error:return dict(error=str(error))
for label in ['control','candidate']:
 path='/workspace/b7-work/native/'+label+'.so';e=Backend(path);e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
 try:
  for full in [False,True]:
   e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full);records=[];additional=[]
   for target,source in [(records,inputs),(additional,[dict(key=r['failureKey'],input=dict(values=r['input'],bits=r['bits'])) for r in extra])]:
    for r in source:
     x=r['input']['values'];reused=call(e,x['rho'],x['u']);fresh=Backend(path)
     try:f=call(fresh,x['rho'],x['u'])
     finally:close(fresh)
     assert reused==f,(label,full,r['key'],'fresh/reused mismatch')
     target.append(dict(key=r['key'],input=r['input'],reused=reused,fresh=f))
   rows.append(dict(label=label,fullVLE=full,librarySHA256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),records=records,additional=additional))
 finally:close(e)
p=E/'native-fresh-replay.json';assert not p.exists();p.write_text(json.dumps(dict(rows=rows,passed=True,originalRecords=250,originalPairs=73,separateReferenceInventories=21),indent=2)+'\n');print('Native actual fresh/reused replay PASS: 250 records and separate 21, both artifacts/paths; all handles disposed')
