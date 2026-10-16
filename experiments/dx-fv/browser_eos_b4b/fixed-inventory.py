"""Cross-evaluate old and new exact 35-bar inventories without changing guards."""
import ctypes as ct,json,sys,os
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4B_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save
rows=[]
for full in [False,True]:
 libs={label:Backend('/workspace/b4b-native-artifacts/libCoolProp-'+label+'.so')for label in ['controlA','candidateB']}
 for e in libs.values():
  e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full)
 for origin in ['controlA','candidateB']:
  source=json.loads((E/f'native-{origin}{"-full-vle"if full else ""}.json').read_text())['rows']
  for r in source:
   if r['request']['args'][0]!=3500000.:continue
   for kind in ['A','C']:
    if kind not in r.get('inventories',{}):continue
    inv=r['inventories'][kind]['input'];x=inv['values'];result={}
    for label,e in libs.items():
     try:
      s=e.state('DU',x['rho'],x['u']);result[label]=dict(DU=pack(s),strictSupport=3e4<=s['p']<=35e5)
     except Exception as ex:result[label]=dict(error=str(ex))
    rows.append(dict(fullVLE=full,origin=origin,id=r['request']['id'],inventory=kind,input=inv,result=result,outputsEqual=result['controlA']==result['candidateB']))
save(E/'35bar-fixed-inventories.json',dict(rows=rows,allEqual=all(r['outputsEqual']for r in rows),note='Changed PH outputs create different inventories. No historical inventory is substituted or normalized. Strict support guard is unchanged.'))
print(len(rows),'fixed 35-bar inventories; equal',all(r['outputsEqual']for r in rows))
