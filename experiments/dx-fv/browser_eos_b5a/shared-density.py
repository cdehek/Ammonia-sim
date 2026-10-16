"""New bounded shared saturation-D caller checks; original fixtures stay separate."""
import os
import json,sys,ctypes as ct
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'));from native import Backend,FIELDS,pack,bits
engines={name:Backend(lib) for name,lib in [('control','/workspace/b5-libs/candidateB.so'),('A1','/workspace/b5-libs/A1.so')]}
a=AbstractState('HEOS','Ammonia');fixtures=[]
for p in [30298.937123458254,350000.,799999.9981754856,3500000.]:
 a.update(C.PQ_INPUTS,p,0);hf=a.hmass();a.update(C.PQ_INPUTS,p,1);hg=a.hmass()
 for name,mode,value in [('liquid','PH',hf-1000),('hf','PQ',0),('mixture','PQ',.4),('hg','PQ',1),('vapor','PH',hg+10000)]:
  a.update(C.HmassP_INPUTS,value,p) if mode=='PH' else a.update(C.PQ_INPUTS,p,value)
  fixtures.append(dict(id=f'{p}-{name}',p=p,rho=a.rhomass(),h=a.hmass(),s=a.smass()))
rows=[]
for full in [False,True]:
 for fixture in fixtures:
  for mode,pair,key in [('DH','DmassHmass_INPUTS','h'),('DS','DmassSmass_INPUTS','s'),('DP','DmassP_INPUTS','p')]:
   x,y=fixture['rho'],fixture[key];r=dict(fixture=fixture,mode=mode,fullVLE=full,input=[x,y],inputBits=[bits(x),bits(y)],result={})
   for label,e in engines.items():
    e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full)
    try:
     e.call(e.lib.AbstractState_update,e.handle,e.lib.get_input_pair_index(pair.encode()),x,y)
     s={k:e.call(e.lib.AbstractState_keyed_output,e.handle,e.lib.get_param_index(v.encode())) for k,v in FIELDS.items()};r['result'][label]=dict(state=pack(s))
    except Exception as ex:r['result'][label]=dict(error=str(ex),exceptionType=type(ex).__name__)
   r['exact']=r['result']['control']==r['result']['A1'];rows.append(r)
out=dict(rows=rows,allExact=all(r['exact'] for r in rows),controlErrors=sum('error' in r['result']['control'] for r in rows),candidateErrors=sum('error' in r['result']['A1'] for r in rows),note='New shared-caller diagnostics; existing errors remain explicit failures. Non-ammonia and pseudopure unqualified.')
p=E/'shared-density.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(len(rows),'shared-density cases; exact',out['allExact'],'errors',out['controlErrors'],out['candidateErrors'])
