"""Level-1 diagnostics at three DISTINCT inventory interpretations. No properties API."""
import hashlib,importlib.util,json,os,struct,time
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'))
spec=importlib.util.spec_from_file_location('b5hp',X/'browser_eos_b5/high-precision.py')
hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp
def read(p):return json.loads(p.read_text())
def bits(x):return struct.pack('>d',x).hex()
def decode(x):return struct.unpack('>d',bytes.fromhex(x))[0]
def precision(n):
 mp.mp.dps=n;hp.D=hp.lift(hp.data);hp.R=hp.D['gas_constant']/hp.D['molar_mass'];hp.Tc=hp.D['STATES']['reducing']['T'];hp.dc=hp.D['STATES']['reducing']['rhomolar']*hp.D['molar_mass']
def enc(x):
 if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v) for v in x]
 if isinstance(x,mp.mpf):return mp.nstr(x,mp.mp.dps-5)
 return x
def rational(x):return dict(numerator=str(x.numerator),denominator=str(x.denominator))
def liftq(x):return mp.mpf(x.numerator)/x.denominator
def targets(b):
 x={k:decode(v) for k,v in b.items()};m,v,U=map(F,[x['M'],x['V'],x['U_kJ']]);w=hp.data['molar_mass']
 assert bits(x['M']/x['V'])==b['rho'] and bits((x['U_kJ']/x['M'])*1000)==b['u']
 return dict(exact_MUV=(m/v,1000*U/m),rounded_DU=(F(x['rho']),F(x['u'])),internal_molar=(F(x['rho']/w)*F(w),F(x['u']*w)/F(w)))
def stability(d,T):
 cv=mp.diff(lambda t:hp.eos(d,t)['u'],T);pr=mp.diff(lambda r:hp.eos(r,T)['p'],d);pt=mp.diff(lambda t:hp.eos(d,t)['p'],T);ur=mp.diff(lambda r:hp.eos(r,T)['u'],d)
 return dict(cv=cv,dp_drho_T=pr,cp=cv+T*pt**2/(d*d*pr),kappa=1/(d*pr),pU_rho=pt/cv,pRho_u=pr-pt*ur/cv)
seed=read(X/'browser_eos_b5/evidence/original-failures.json')['rows'][0]['independentReference']['equilibrium']
def solve(d,u,T0,offset=0):
 eq=hp.equilibrium(d,u,seed)
 T=mp.findroot(lambda t:hp.eos(d,t)['u']-u,(mp.mpf(T0)-mp.mpf('.01')+offset,mp.mpf(T0)+mp.mpf('.01')+offset),tol=mp.power(10,-mp.mp.dps+15),maxsteps=20)
 hom=hp.eos(d,T);st=stability(d,T)
 def sat(a,b):
  l,v=hp.eos(a,T),hp.eos(b,T);return (l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6
 rl,rv=mp.findroot(sat,(eq['rhoL'],eq['rhoV']),tol=mp.power(10,-mp.mp.dps+15),maxsteps=20)
 stable=bool((d>=rl or d<=rv) and st['cv']>0 and st['dp_drho_T']>0 and st['cp']>0)
 physical=bool(0<=eq['Q']<=1)
 branch='equilibrium' if physical else ('liquid' if d>=rl else 'vapor') if stable else 'UNRESOLVED'
 chosen=eq if physical else hom
 return dict(branch=branch,selected=chosen,pMinusLimit=chosen['p']-3500000,homogeneous=hom,stability=st,coexistence=eq,saturationAtHomT=dict(rhoL=rl,rhoV=rv),homogeneousStableSide=stable,phaseEvidence='HIGH_PRECISION_DIAGNOSTIC; not a branch enclosure or global stability proof',uResidual=hom['u']-u)
def cases():
 browser=read(E/'chromium-replay.json');out=[]
 for group in ['rows','falseAcceptance','matrix','endpoints']:
  for r in browser[group]:out.append(dict(key=r.get('key',r['id'] if 'id'in r else None),group=group,input=r['input'],raw=r.get('raw'),rawError=r.get('rawError'),adapter=r.get('adapter'),error=r.get('error'),request=r.get('request'),PH=r.get('PH'),requestedSupported=r.get('requestedSupported')))
 return out
def run():
 rows=[]
 for c in cases():
  start=time.perf_counter();row=dict(case=c,targets={});tt=targets(c['input']['bits'])
  for name,(d,u) in tt.items():
   out=dict(exactDensity=rational(d),exactEnergyJkg=rational(u),levels=[])
   try:
    for n in ([65,90] if name!='internal_molar' else [90]):
     precision(n);result=solve(liftq(d),liftq(u),c['raw']['values']['T']);out['levels'].append(enc(dict(dps=n,**result)))
    if len(out['levels'])==2:
     a,b=out['levels'];out['pressureRepeatDifferencePa']=mp.nstr(abs(mp.mpf(a['selected']['p'])-mp.mpf(b['selected']['p'])),70)
    if c['group'] in ['rows','falseAcceptance'] and name=='exact_MUV':
     repeated=[]
     for dt in [-1,1]:
      z=solve(liftq(d),liftq(u),c['raw']['values']['T'],mp.mpf(dt));repeated.append(enc(dict(seedOffsetK=dt,p=z['selected']['p'],branch=z['branch'])))
     out['repeatedSeeds']=repeated
   except Exception as ex:out['error']=repr(ex)
   row['targets'][name]=out
  precision(90)
  ex,du=row['targets']['exact_MUV'],row['targets']['rounded_DU']
  if 'error'not in ex and 'error'not in du:
   exr,dur=ex['levels'][-1],du['levels'][-1];s=c['raw']['values'];M=decode(c['input']['bits']['M']);V=decode(c['input']['bits']['V']);U=decode(c['input']['bits']['U_kJ'])
   row['roundedMinusExactPressurePa']=mp.nstr(mp.mpf(dur['selected']['p'])-mp.mpf(exr['selected']['p']),75)
   # Independent evaluation at raw homogeneous coordinates; equilibrium uses physical raw Q and own saturation endpoints.
   if dur['branch']!='equilibrium':evaluated=hp.eos(mp.mpf(s['rho']),mp.mpf(s['T']))
   else:
    def sat(a,b):
     l,v=hp.eos(a,mp.mpf(s['T'])),hp.eos(b,mp.mpf(s['T']));return (l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6
    rl,rv=mp.findroot(sat,(mp.mpf(dur['coexistence']['rhoL']),mp.mpf(dur['coexistence']['rhoV'])),tol=mp.mpf('1e-70'),maxsteps=20)
    l,v=hp.eos(rl,mp.mpf(s['T'])),hp.eos(rv,mp.mpf(s['T']));q=mp.mpf(s['Q']);evaluated=dict(p=l['p'],u=(1-q)*l['u']+q*v['u'],rho=1/((1-q)/rl+q/rv),h=(1-q)*l['h']+q*v['h'])
   row['independentRawEOS']=enc(evaluated)
   row['normalizedResiduals']=enc(dict(mass=abs(evaluated['rho']*mp.mpf(V)-mp.mpf(M))/max(.01,M),energy=abs(mp.mpf(M)*evaluated['u']/1000-mp.mpf(U))/max(1,abs(U))))
   row['rawMinusExactPressurePa']=mp.nstr(mp.mpf(s['p'])-mp.mpf(exr['selected']['p']),75)
  row['seconds']=time.perf_counter()-start;rows.append(row)
  print(c['key'],{k:v.get('error',v['levels'][-1]['pMinusLimit'] if v['levels'] else None) for k,v in row['targets'].items()},flush=True)
 out=dict(level='HIGH_PRECISION_DIAGNOSTIC',intervalCertified=False,mpmath=mp.__version__,coefficientsSHA256=hashlib.sha256(hp.raw).hexdigest(),rows=rows)
 p=E/'references.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
