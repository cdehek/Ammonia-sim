"""Fresh EOS consistency, stability, canonical and nonlinear gates on raw DU."""
import json,sys
from pathlib import Path
import os
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b4c/evidence';sys.path.insert(0,str(B.parent/'browser_eos_b3'))
from native import pack
def read(f):return json.loads((E/f).read_text())
inputs={r['key']:r for r in read('fixed-inputs.json')};rows=[]
metadata={}
for file in ['native-candidateB.json','native-candidateB-full-vle.json']:
 for r in json.loads((H/file).read_text())['rows']:metadata[(r['request']['id'],'full-vle'in file)]=r
for engine in ['native','native72','chromium','webkit']:
 data=read('native-fixed-replay.json'if engine=='native'else 'native72-fixed-replay.json'if engine=='native72'else engine+'-fixed-replay.json')['rows']
 for r in data:
  q=inputs[r['key']];x=q['input']['values'];results=r['result']if engine=='native'else {'wheel72':r}if engine=='native72'else {r['build']:r}
  for build,result in results.items():
   raw=result.get('DU');s=raw.get('values',raw)if raw else None
   if not s:rows.append(dict(runtime=engine,build=build,key=r['key'],error=result.get('error',result.get('rawError'))));continue
   a=AbstractState('HEOS','Ammonia');Q=s['Q']
   if 0<=Q<=1:a.update(C.QT_INPUTS,Q,s['T']);kind='equilibrium at returned T,Q'
   else:a.specify_phase(C.iphase_liquid if s['rho']>225 else C.iphase_gas);a.update(C.DmassT_INPUTS,s['rho'],s['T']);kind='homogeneous at returned rho,T'
   audit={k:getattr(a,f)()for k,f in dict(p='p',h='hmass',u='umass',rho='rhomass',T='T').items()}
   d={k:audit[k]-s[k]for k in audit};U=x['U_kJ'];M=x['M'];meta=metadata[(q['id'],q['fullVLE'])];p,h=meta['request']['args'];T=meta['base']['PH']['values']['T']
   # For browser-origin inventories compare with the browser's own originating T.
   if q['origin'].startswith(('chromium-','webkit-')):
    browser,origin=q['origin'].split('-',1)
    saved=json.loads((H/(browser+'-'+origin+'-focused.json')).read_text())['rows'];orig=next(z for z in saved if z['id']==q['id']);T=orig['base']['state']['T'];p,h=orig['args']
   diff=dict(p=s['p']-p,h=s['h']-h,T=s['T']-T)
   nr=dict(mass=abs((audit['rho']-x['rho'])*x['V'])/max(.01,M),energy=abs(M*audit['u']/1000-U)/max(1,abs(U)))
   rows.append(dict(runtime=engine,build=build,key=r['key'],referenceKind=kind,independentEOS=pack(audit),getterMinusIndependent={k:-v for k,v in d.items()},canonicalDifferences=diff,canonicalPass=abs(diff['p'])<=.1 and abs(diff['h'])<=.1 and abs(diff['T'])<=1e-4,normalizedResiduals=nr,nonlinearPass=max(nr.values())<=1e-11,strictPressurePa=3e4<=s['p']<=35e5,strictPressureBar=.3<=s['p']/1e5<=35,adapterError=result.get('adapterError')))
(E/'raw-DU-eos-audit.json').write_text(json.dumps(dict(rows=rows),indent=2)+'\n');print('raw EOS audits',len(rows),'exceptions',sum('error'in r for r in rows),'canonical failures',sum(r.get('canonicalPass')is False for r in rows),'nonlinear failures',sum(r.get('nonlinearPass')is False for r in rows))
