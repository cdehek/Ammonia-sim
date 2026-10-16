"""Prove 35-bar full-VLE DU behavior at identical physical inventories."""
import os,ctypes as ct,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B4A_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,save
source=json.loads((E/'native-liquid44-full-vle.json').read_text())['rows'];rows=[]
for label in ['control44','liquid44']:
 eos=Backend('/workspace/b4a-native-artifacts/libCoolProp-'+label+'.so');eos.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];eos.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',False)
 for r in source:
  if r['request']['args'][0]!=3500000.:continue
  for kind in ['A','C']:
   if kind not in r.get('inventories',{}):continue
   inv=r['inventories'][kind]['input']['values'];row=dict(label=label,id=r['request']['id'],inventory=kind,input=r['inventories'][kind]['input'])
   try:row['DU']=pack(eos.state('DU',inv['rho'],inv['u']))
   except Exception as exc:row['error']=str(exc)
   rows.append(row)
comparisons=[]
for a in [r for r in rows if r['label']=='control44']:
 b=next(r for r in rows if r['label']=='liquid44'and r['id']==a['id']and r['inventory']==a['inventory']);comparisons.append(dict(id=a['id'],inventory=a['inventory'],inputEqual=a['input']==b['input'],outputEqual=a.get('DU')==b.get('DU')and a.get('error')==b.get('error'),error=a.get('error')))
assert all(r['inputEqual']and r['outputEqual']for r in comparisons)
save(E/'full-vle-35bar-fixed-inventory-control.json',dict(rows=rows,comparisons=comparisons,allEqual=True))
