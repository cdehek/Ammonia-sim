"""Unchanged exact historical 35-bar inventories and separately labeled new PH inventories."""
import ctypes as ct,json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4C_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save
libs={k:Backend('/workspace/b4c-libs/'+k+'.so') for k in ['controlA','candidateB']}
requests=[dict(origin='historical-B4B-fixed-ledger',fullVLE=r['fullVLE'],id=r['id'],input=r['input']) for r in json.loads((B.parent/'browser_eos_b4b/evidence/35bar-fixed-inventories.json').read_text())['rows']]
for full in [False,True]:
 for r in json.loads((E/('native-candidateB'+('-full-vle' if full else '')+'.json')).read_text())['rows']:
  if r['request']['args'][0]==3500000. and 'C' in r.get('inventories',{}):requests.append(dict(origin='B4C-current-PH',fullVLE=full,id=r['request']['id'],input=r['inventories']['C']['input']))
rows=[]
for r in requests:
 result={};x=r['input']['values']
 for label,e in libs.items():
  e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not r['fullVLE'])
  try:
   s=e.state('DU',x['rho'],x['u']);result[label]=dict(DU=pack(s),strictSupport=3e4<=s['p']<=35e5)
  except Exception as ex:result[label]=dict(error=str(ex))
 rows.append(dict(**r,result=result,outputsEqual=result['controlA']==result['candidateB']))
save(E/'35bar-fixed-inventories.json',dict(rows=rows,allEqual=all(r['outputsEqual'] for r in rows),note='The same binary64 inventory is sent to both backends. A recovery overshoot does not demonstrate physical domain exit.'))
print(len(rows),'fixed inventories; equal',all(r['outputsEqual'] for r in rows))
