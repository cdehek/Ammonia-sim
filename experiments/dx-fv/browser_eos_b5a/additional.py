"""Replay all 21 already saved B5 independent-PH inventories; no regeneration."""
import os
import json,sys,ctypes as ct,importlib.util
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack,bits
from reference_math import homogeneous,equilibrium
spec=importlib.util.spec_from_file_location('hp',B.parent/'browser_eos_b5/high-precision.py');hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp
inputs=json.loads((B.parent/'browser_eos_b5/evidence/reference-inventory-recovery.json').read_text())['rows'];rows=[]
engines={name:Backend(lib) for name,lib in [('control','/workspace/b5-libs/candidateB.so'),('A1','/workspace/b5-libs/A1.so')]}
for e in engines.values():e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
for r in inputs:
 x=r['input'];assert all(bits(v)==r['bits'][k] for k,v in x.items());row=dict(saved=r,reference={},results={})
 try:
  hm=homogeneous(x['rho'],x['u'],r['referenceT']);eq=equilibrium(x['rho'],x['u'],r['referenceT']);d,u=mp.mpf(x['rho']),mp.mpf(x['u']);ep=hp.equilibrium(d,u,eq);T=mp.findroot(lambda T:hp.eos(d,T)['u']-u,hm['state']['values']['T'],tol=mp.mpf('1e-52'));hom=hp.eos(d,T);sel='equilibrium' if 0<=ep['Q']<=1 else 'homogeneous'
  row['reference']=dict(homogeneous=hm,equilibrium=eq,highPrecision=dict(homogeneous=hp.enc(hom),equilibrium=hp.enc(ep),selection=sel))
 except Exception as ex:row['reference']['error']=str(ex)
 for label,e in engines.items():
  row['results'][label]={}
  for full in [False,True]:
   path='fullVLE' if full else 'default';e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full);o={}
   try:
    s=e.state('DU',x['rho'],x['u']);dif=dict(p=s['p']-r['requestedP'],h=s['h']-r['requestedH'],T=s['T']-r['referenceT']);o=dict(DU=pack(s),canonicalDifferences=dif,canonicalPass=all(abs(dif[k])<=v for k,v in dict(p=.1,h=.1,T=1e-4).items()),normalizedResiduals=dict(mass=abs(s['rho']*x['V']-x['M'])/max(.01,x['M']),energy=abs((s['rho']*x['V'])*(s['u']/1000)-x['U_kJ'])/max(1,abs(x['U_kJ']))),physicalQuality=s['phase']!=6 or 0<=s['Q']<=1)
   except Exception as ex:o=dict(error=str(ex),exceptionType=type(ex).__name__)
   if label=='control':o['historicalExact']=o.get('DU')==r['results'][path].get('DU') and o.get('error')==r['results'][path].get('error')
   row['results'][label][path]=o
 rows.append(row)
p=E/'additional-inventories.json';assert not p.exists(),p
p.write_text(json.dumps(dict(rows=rows,origin='saved B5 independent-PH reference inventories, separate from fixed historical ledger',noInputsRegenerated=True),indent=2)+'\n');print('additional',len(rows),'A1 fullVLE errors',sum('error' in r['results']['A1']['fullVLE'] for r in rows))
