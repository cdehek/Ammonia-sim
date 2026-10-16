"""Small explicitly labeled boundary, cross-path and perturbation diagnostics."""
import ctypes as ct,json,math,sys,struct
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack
e=Backend('/workspace/b5-libs/candidateB.so');e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
def config(full):e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full)
def du(x):
 try:return dict(DU=pack(e.state('DU',x['rho'],x['u'])))
 except Exception as ex:return dict(error=str(ex),exceptionType=type(ex).__name__)
def inv(p,h,rho):
 V=.003/5;M=rho*V;U=M*(h/1000)-100*(p/1e5)*V
 return dict(M=M,U_kJ=U,V=V,rho=M/V,u=(U/M)*1000)
def canonical(out,p,h,T):
 if 'DU'not in out:return dict(pass_=False)
 s=out['DU']['values'];diff=dict(p=s['p']-p,h=s['h']-h,T=s['T']-T)
 return dict(differences=diff,pass_=abs(diff['p'])<=.1 and abs(diff['h'])<=.1 and abs(diff['T'])<=1e-4,strictSupport=3e4<=s['p']<=35e5)
inputs=json.loads((E/'fixed-inputs.json').read_text());unique={tuple(r['input']['bits'][k] for k in ['rho','u']):r for r in inputs};cross=[]
for r in unique.values():
 row=dict(key=r['key'],input=r['input'],paths={})
 for full in [False,True]:config(full);row['paths']['fullVLE'if full else'default']=du(r['input']['values'])
 cross.append(row)
(E/'cross-path.json').write_text(json.dumps(dict(rows=cross),indent=2)+'\n')
references=[]
for r in json.loads((E/'reference-inventories.json').read_text()):
 row=dict(**r,results={})
 for full in [False,True]:
  config(full);out=du(r['input']);row['results']['fullVLE'if full else'default']=dict(**out,canonical=canonical(out,r['requestedP'],r['requestedH'],r['referenceT']))
 references.append(row)
(E/'reference-inventory-recovery.json').write_text(json.dumps(dict(rows=references),indent=2)+'\n')
fail=json.loads((E/'original-failures.json').read_text())['rows'];perturb=[]
for r in [next(r for r in fail if r['runtime']=='native-full-VLE'and'liquid-0.001'in r['id']),next(r for r in fail if r['runtime']=='native-full-VLE'and r['id']=='approach-3500000.0-vapor-0.0'),next(r for r in fail if r['runtime']=='chromium'and'liquid-0.001'in r['id'])]:
 original=r['fixedInput']['values']
 for field in ['rho','u']:
  for sign in [-1,1]:
   for n in [1,16]:
    x=dict(original);v=x[field]
    for _ in range(n):v=math.nextafter(v,math.inf if sign>0 else-math.inf)
    x[field]=v;row=dict(failureKey=r['failureKey'],label='diagnostic DU-coordinate perturbation, not a new canonical inventory',field=field,ulps=sign*n,increment=v-original[field],input=pack(x),paths={})
    for full in [False,True]:config(full);row['paths']['fullVLE'if full else'default']=du(x)
    perturb.append(row)
(E/'inventory-sensitivity.json').write_text(json.dumps(dict(rows=perturb),indent=2)+'\n')
# Preserve the saved inward pressure probe verbatim, rather than a rounded label.
saved=json.loads((B.parent/'browser_eos_b4c/evidence/native-candidateB.json').read_text())['rows']
sample=next(r for r in saved if r['request']['id']=='focused-3500000.0-stable-vapor')
near=next(q['output']['p']for q in sample['probes']if q['axis']=='P'and q['step']<0)
pressures=list(dict.fromkeys([3500000.,math.nextafter(3500000.,-math.inf),math.nextafter(3500000.,math.inf),near,3499990.,3490000.,3400000.]))
sweep=[]
for p in pressures:
 config(False);sf=e.state('PQ',p,0);sg=e.state('PQ',p,1)
 for label,h in [('liquid',sf['h']-.001),('mixture',(sf['h']+sg['h'])/2),('vapor',sg['h']+.001)]:
  row=dict(label='new diagnostic pressure sweep',region=label,p=p,h=h,inputBits=pack(dict(p=p,h=h)),pBar=p/1e5,pBarBits=struct.pack('>d',p/1e5).hex(),PaAfterBarRoundTrip=(p/1e5)*1e5,requestedSupported=3e4<=p<=35e5,paths={})
  for full in [False,True]:
   config(full)
   try:
    ph=e.state('PH',p,h);x=inv(p,h,ph['rho']);out=du(x);row['paths']['fullVLE'if full else'default']=dict(PH=pack(ph),input=pack(x),**out,canonical=canonical(out,p,h,ph['T']))
   except Exception as ex:row['paths']['fullVLE'if full else'default']=dict(error=str(ex))
  sweep.append(row)
(E/'boundary-sweep.json').write_text(json.dumps(dict(rows=sweep,note='Diagnostic h values are constructed at each explicitly listed pressure; they never replace saved inputs or original finite differences.'),indent=2)+'\n')
print('cross-path',len(cross),'reference inventories',len(references),'perturbations',len(perturb),'boundary states',len(sweep))
