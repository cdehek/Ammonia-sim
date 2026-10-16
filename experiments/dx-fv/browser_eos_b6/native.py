"""Bounded preserved native control; no rebuild, coefficients or source changes."""
import importlib.util,json,sys,ctypes as ct,hashlib,lzma,os
from pathlib import Path
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence'
spec=importlib.util.spec_from_file_location('c1_native',X/'browser_eos_b5b_c1/native.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.D=Path('/workspace/b6-native')
e=m.Native();e.L.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long]
old=json.loads((X/'browser_eos_b4c/evidence/native-candidateB.json').read_text())
ids=['B1-liquid-precision','B1-vapor-regression','approach-30298.937123458254-liquid-0.001','diagnostic-quality-band-799999.9981754856-hg-9.9e-10']
rows=[]
try:
 for r in old['rows']:
  if r['request']['id'] not in ids:continue
  for label,z in [('base',r['base'])]+[(p['axis']+':'+str(p['step']),p['output']) for p in r['probes']]:
   a,b=r['request']['args'] if label=='base' else (z['p'],z['h'])
   state=e.state('PH',a,b);expected=z['PH']['values']
   assert all(state[k]==v for k,v in expected.items()),(r['request']['id'],label,state,expected)
   rows.append(dict(id=r['request']['id'],sample=label,request=dict(mode='PH',args=[a,b],bits=[m.bits(a),m.bits(b)]),state=m.pack(state),historicalExact=True))
 refusal=[]
 fs=json.loads((E/'historical-rejected-pt.json').read_text())
 for f in fs:
  if f['engine']!='chromium' or f['sequence']!=0:continue
  pre=e.state('PH',*f['fixture']['args']);error=None
  try:e.state('PT',*f['request']['args'])
  except ValueError as ex:error=str(ex)
  assert error,'native PT must refuse'
  recovered=e.state('PH',*f['fixture']['args']);assert pre==recovered
  refusal.append(dict(fixture=f['fixture']['id'],request=f['request'],inputBits=f['inputBits'],error=error,recovered=m.pack(recovered),freshBefore=m.pack(pre),CABIExceptionHandledInternally=True))
 out=dict(passed=True,librarySHA256=e.sha,rows=rows,refusals=refusal,nativeIsHistoricalScientificControl=True,notCandidateNativeRepair=True)
finally:e.call(e.L.AbstractState_free,e.handle)
target=Path(os.environ.get('B6_NATIVE_OUTPUT',E/'native-controls.json'));assert not target.exists(),target
target.write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'native scientific samples exact;',len(refusal),'native PT refusals recovered; handle freed')
