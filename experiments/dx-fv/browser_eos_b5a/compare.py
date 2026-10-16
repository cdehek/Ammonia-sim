"""Exact fixed-inventory comparison, independent physics, original budgets.

Never reconstruct a historical input from an output. Every record and its input
bits are retained, plus all 73 unique inventories on both recovery paths.
"""
import os
import argparse,ctypes as ct,json,sys,struct,time
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import Backend,pack
from CoolProp import AbstractState,CoolProp as C
ap=argparse.ArgumentParser();ap.add_argument('--library',required=True);ap.add_argument('--label',required=True);args=ap.parse_args()
inputs=json.loads((E/'fixed-inputs.json').read_text());refs={r['key']:r for r in json.loads((E/'independent-fixed-references.json').read_text())['rows']};hp={r['key']:r['reference'] for r in json.loads((E/'high-precision-references.json').read_text())['rows']}
metadata={}
H=B.parent/'browser_eos_b4c/evidence'
for full in [False,True]:
 for z in json.loads((H/('native-candidateB'+('-full-vle' if full else '')+'.json')).read_text())['rows']:
  metadata[(z['request']['id'],full)]=z
browserMeta={}
for engine in ['chromium','webkit']:
 for origin in ['controlA','candidateB']:
  browserMeta[(engine,origin)]={r['id']:r for r in json.loads((H/(engine+'-'+origin+'-focused.json')).read_text())['rows']}
e=Backend(args.library);e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool];a=AbstractState('HEOS','Ammonia')
def call(r,full):
 x=r['input']['values'];assert all(struct.pack('>d',v).hex()==r['input']['bits'][k] for k,v in x.items())
 assert x['rho']==x['M']/x['V'] and x['u']==(x['U_kJ']/x['M'])*1000
 e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full);out=dict(key=r['key'],id=r['id'],fullVLE=full,input=r['input'])
 try:
  s=e.state('DU',x['rho'],x['u']);out['DU']=pack(s);h=hp[r['key']];selection=h['selection'];ref={k:float(v) for k,v in h[selection].items()}
  out['mathematicalReferenceBranch']=selection
  out['differences']={k:s[k]-ref[k] for k in ['p','h','T','rho','u']}
  out['referencePass']=all(abs(out['differences'][k])<=lim for k,lim in [('p',.1),('h',.1),('T',1e-4)])
  meta=metadata[(r['id'],r['fullVLE'])];p,h=meta['request']['args'];T=meta['base']['PH']['values']['T']
  if r['origin'].startswith(('chromium-','webkit-')):
   browser,origin=r['origin'].split('-',1);m=browserMeta[(browser,origin)][r['id']];p,h=m['args'];T=m['base']['state']['T']
  out['canonicalDifferences']=dict(p=s['p']-p,h=s['h']-h,T=s['T']-T)
  out['canonicalPass']=all(abs(out['canonicalDifferences'][k])<=v for k,v in dict(p=.1,h=.1,T=1e-4).items())
  out['standalonePass']=all(abs(out['differences'][k])<lim for k,lim in [('p',10),('h',50),('T',.01)])
  if s['phase']==6:
   a.unspecify_phase();a.update(C.QT_INPUTS,s['Q'],s['T'])
  else:
   a.specify_phase(C.iphase_liquid if s['rho']>225 else C.iphase_gas);a.update(C.DmassT_INPUTS,s['rho'],s['T'])
  audit=dict(p=a.p(),rho=a.rhomass(),h=a.hmass(),u=a.umass())
  out['independentInventoryEOS']=audit
  # Original accepted M/U scales and operation ordering, using fresh EOS values.
  out['normalizedResiduals']=dict(mass=abs((audit['rho']-x['rho'])*x['V'])/max(.01,x['M']),energy=abs(x['M']*audit['u']/1000-x['U_kJ'])/max(1,abs(x['U_kJ'])))
  out['nonlinearPass']=all(v<=1e-11 for v in out['normalizedResiduals'].values())
  out['physicalQuality']=s['phase']!=6 or 0<=s['Q']<=1
  out['strictSupport']=3e4<=s['p']<=35e5
  if s['phase']!=6:
   a.specify_phase(C.iphase_liquid if s['rho']>225 else C.iphase_gas);a.update(C.DmassT_INPUTS,s['rho'],s['T'])
   out['independentEOS']={k:getattr(a,k)() for k in ['p','hmass','umass','cpmass','cvmass','isothermal_compressibility']}
   out['pRho']=a.first_partial_deriv(C.iP,C.iDmass,C.iT)
   out['getterDifferences']=dict(p=s['p']-a.p(),h=s['h']-a.hmass(),u=s['u']-a.umass())
  else:
   L=refs[r['key']]['reference']['equilibrium']
   out['equilibriumReference']=dict(state=L['state'],lastResidual=L['trace'][-1],liquidStability=L['liquidStability'],vaporStability=L['vaporStability'])
 except Exception as ex:out.update(error=str(ex),exceptionType=type(ex).__name__)
 return out
rows=[call(r,r['fullVLE']) for r in inputs]
unique={tuple(r['input']['bits'][k] for k in ['rho','u']):r for r in inputs}
cross=[call(r,full) for r in unique.values() for full in [False,True]]
out=dict(label=args.label,library=args.library,rows=rows,crossPath=cross,budgets=dict(canonical=dict(p=.1,h=.1,T=1e-4),nonlinear=1e-11,standalone=dict(p=10,h=50,T=.01),independentResolution=dict(p=1e-5,caloric=1e-8)),note='Math reference signs do not upgrade original unresolved endpoint phase classification.')
p=E/(args.label+'-comparison.json');assert not p.exists(),p
p.write_text(json.dumps(out,indent=2)+'\n')
print(args.label,'ledger errors',sum('error' in r for r in rows),'cross errors',sum('error' in r for r in cross),'returned gates',all(r['canonicalPass'] and r['nonlinearPass'] and r['physicalQuality'] for r in rows+cross if 'DU' in r))
