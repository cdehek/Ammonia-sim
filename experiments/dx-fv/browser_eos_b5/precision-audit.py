"""Repeat each unique independent root at higher precision; test local root seeds."""
import importlib.util,json,sys
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));spec=importlib.util.spec_from_file_location('hp',B/'high-precision.py');hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp;mp.mp.dps=90
refs=json.loads((E/'independent-fixed-references.json').read_text())['rows'];high=json.loads((E/'high-precision-references.json').read_text())['rows'];inputs=json.loads((E/'fixed-inputs.json').read_text());rows=[];cache={}
for r,ref,h in zip(inputs,refs,high):
 x=r['input']['values'];key=x['rho'],x['u'];d,u=map(mp.mpf,key)
 if key not in cache:
  seed=ref['reference']['equilibrium'];eq=hp.equilibrium(d,u,seed);hm0=mp.mpf(h['reference']['homogeneous']['T']);hmT=mp.findroot(lambda T:hp.eos(d,T)['u']-u,hm0,tol=mp.mpf('1e-75'));hom=hp.eos(d,hmT);old=h['reference'];sel=old['selection'];s=eq if sel=='equilibrium'else hom
  delta={k:mp.nstr(s[k]-mp.mpf(old[sel][k]),30)for k in ['p','T','u','h']};cache[key]=dict(precisionDelta=delta,allWithinOriginalReferenceResolution=abs(mp.mpf(delta['p']))<mp.mpf('1e-5')and abs(mp.mpf(delta['u']))<mp.mpf('1e-8'),selectedUResidual=mp.nstr(s['u']-u,30),equilibriumPressureResidual=mp.nstr(eq['pDifference'],30),equilibriumGibbsResidual=mp.nstr(eq['gDifference'],30))
 rows.append(dict(key=r['key'],**cache[key]))
# Independent local homogeneous roots from distinct temperatures. These are not
# changes to CoolProp's guesses and never count as accepted backend recoveries.
sys.path.insert(0,str(B));from references_core import local_roots
local=local_roots()
(E/'precision-audit.json').write_text(json.dumps(dict(dps=90,rows=rows,uniqueInventories=len(cache),localRoots=local),indent=2)+'\n');print('precision verified',len(cache),'unique roots')
