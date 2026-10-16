"""Replay saved coordinates, never regenerate or normalize inventories."""
import ctypes as ct,json,sys,os
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack
import CoolProp
H=B.parent/'browser_eos_b4c/evidence'
def capture(e,r):
 try:return dict(DU=pack(e.state('DU',r['input']['values']['rho'],r['input']['values']['u'])))
 except Exception as ex:return dict(error=str(ex),exceptionType=type(ex).__name__)
requests=[]
for i,r in enumerate(json.loads((H/'35bar-fixed-inventories.json').read_text())['rows']):
 requests.append(dict(key='native-ledger-'+str(i),origin=r['origin'],id=r['id'],fullVLE=r['fullVLE'],input=r['input'],historical=r['result']['candidateB']))
for engine in ['chromium','webkit']:
 for i,r in enumerate(json.loads((H/(engine+'-35bar-fixed-inventories.json')).read_text())['rows']):
  if r['build']!='candidateB':continue
  requests.append(dict(key=engine+'-ledger-'+str(i),origin=engine+'-'+r['origin'],id=r['id'],fullVLE=False,input=pack(r['input']),historical=dict(DU=r.get('DU'),adapterError=r.get('adapterError'))))
(E/'fixed-inputs.json').write_text(json.dumps(requests,indent=2)+'\n')
libs={'B4C':Backend('/workspace/b5-libs/candidateB.so'),'B4B':Backend('/workspace/b5-libs/controlA.so'),'wheel':Backend()}
rows=[]
for r in requests:
 result={}
 for name,e in libs.items():
  if e.lib:
   e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not r['fullVLE'])
  else:
   from CoolProp import CoolProp as C
   C.set_config_bool(C.ENABLE_SUPERANCILLARIES,not r['fullVLE'])
  a=capture(e,r)
  if 'DU'in a:a['strictSupport']=3e4<=a['DU']['values']['p']<=35e5
  result[name]=a
 hist=r['historical'];a=result['B4C']
 parity=(a.get('error')==hist.get('error') if 'error'in hist else a.get('DU')==hist.get('DU')) if r['key'].startswith('native') else None
 rows.append(dict(key=r['key'],result=result,historicalExact=parity))
out=dict(version=CoolProp.__version__,revision=CoolProp.__gitrevision__,rows=rows)
(E/'native-fixed-replay.json').write_text(json.dumps(out,indent=2)+'\n')
print('rows',len(rows),'native exact',all(r['historicalExact'] for r in rows if r['historicalExact'] is not None),'errors',sum('error'in r['result']['B4C'] for r in rows))
