"""Exact saved PH inputs, separately labeled newly formed canonical inventories."""
import argparse,ctypes as ct,json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b4c/evidence';sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,inventory
import CoolProp
from CoolProp import CoolProp as C
ap=argparse.ArgumentParser();ap.add_argument('--historical72',action='store_true');a=ap.parse_args()
requests=[]
for f in ['native-candidateB.json','native-candidateB-full-vle.json','chromium-candidateB-focused.json','webkit-candidateB-focused.json']:
 for r in json.loads((H/f).read_text())['rows']:
  q=r.get('request',r)
  if q['args'][0]==3500000:requests.append(dict(origin=f,id=q['id'],args=q['args'],fullVLE='full-vle'in f,historicalPH=r['base'].get('PH',{}).get('values',r['base'].get('state'))))
engines={'wheel':Backend()}
if not a.historical72:engines.update(B4C=Backend('/workspace/b5-libs/candidateB.so'),B4B=Backend('/workspace/b5-libs/controlA.so'))
rows=[]
for r in requests:
 result={};p,h=r['args']
 for name,e in engines.items():
  if e.lib:e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not r['fullVLE'])
  else:C.set_config_bool(C.ENABLE_SUPERANCILLARIES,not r['fullVLE'])
  try:
   s=e.state('PH',p,h);ref=Backend().state('DT',s['rho'],s['T']);out=dict(PH=pack(s),independentDT=pack(ref),newCanonicalInventory=inventory(e,p,h,s['rho'],s['T']))
   if name=='B4C'and r['origin'].startswith('native'):out['historicalExact']=s==r['historicalPH']
  except Exception as ex:out=dict(error=str(ex),exceptionType=type(ex).__name__)
  result[name]=out
 rows.append(dict(request=r,result=result))
(E/('PH-native72.json'if a.historical72 else'PH-native8.json')).write_text(json.dumps(dict(version=CoolProp.__version__,revision=CoolProp.__gitrevision__,rows=rows,note='newCanonicalInventory is never substituted for fixed-inputs.json'),indent=2)+'\n');print('PH',CoolProp.__version__,len(rows),'requests')
