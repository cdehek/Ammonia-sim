"""Independent same-EOS replay and exact binary64 rounding attribution.

Uses the preserved B5 evaluator unchanged. Never supplies a backend property.
"""
import csv,hashlib,importlib.util,json,struct
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';H=B.parent/'browser_eos_b5/evidence'
def read(p):return json.loads(p.read_text())
def write(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
def bits(x):return struct.pack('>d',x).hex()
def decode(x):return struct.unpack('>d',bytes.fromhex(x))[0]
spec=importlib.util.spec_from_file_location('b5hp',B.parent/'browser_eos_b5/high-precision.py');hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp
assert hashlib.sha256(hp.raw).hexdigest()==read(H/'high-precision-references.json')['ammoniaSHA256']
failures=[r for r in read(H/'original-failures.json')['rows'] if r['runtime'] in ['chromium','webkit']]
refs={r['key']:r for r in read(H/'precision-audit.json')['rows']}
attribution={r['failureKey']:r for r in read(H/'pressure-error-attribution.json')['rows']}
replays={n:read(E/(n+'-replay.json')) for n in ['chromium','webkit']}
rows=[];fixed=[];mathrefs=[]
for f in failures:
 r=next(r for r in replays[f['runtime']]['rows'] if r['id']==f['id']);x={k:decode(v) for k,v in f['fixedInput']['bits'].items()}
 assert r['key']==f['fixedKey'] and r['input']['bits']==f['fixedInput']['bits']
 assert r['raw']['bits']==f['originalRecovery']['DU']['bits']
 assert r['originatingRawPH']['values']==f['originalPH']['values']
 assert r['error']['message']==f['originalError'] and r['error']['faultKind']=='domain'
 assert [e['event'] for e in r['events']]==['EOS_call','EOS_return','table_PH_call','table_PH_pass']
 assert r['counts']['sat']==1 and r['counts']['domainGuards']==1
 assert not any(e.get('request',{}).get('mode')=='SAT' for e in r['events'])
 fixed.append(f)
 if f['runtime']=='webkit':continue
 ph=f['originalPH']['values'];p,h=f['originalPHInput'];s=r['raw']['values']
 stages=[]
 def op(name,a,b,kind):
  exact={'/':lambda:F(a)/F(b),'*':lambda:F(a)*F(b),'-':lambda:F(a)-F(b)}[kind]()
  value={'/':lambda:a/b,'*':lambda:a*b,'-':lambda:a-b}[kind]()
  error=F(value)-exact
  stages.append(dict(name=name,operation=kind,a=a,b=b,value=value,bits=bits(value),exactRoundingErrorNumerator=str(error.numerator),exactRoundingErrorDenominator=str(error.denominator)))
  return value
 V=op('V',.003,5.,'/');M=op('M',ph['rho'],V,'*');hk=op('h_kJkg',h,1000.,'/');pb=op('P_bar',p,1e5,'/')
 Mh=op('M_times_h',M,hk,'*');a=op('100_times_Pbar',100.,pb,'*');work=op('pressure_work',a,V,'*');U=op('U_kJ',Mh,work,'-');rho=op('rho_DU',M,V,'/');uk=op('u_kJkg',U,M,'/');u=op('u_DU',uk,1000.,'*')
 assert {k:bits(v) for k,v in dict(M=M,V=V,U_kJ=U,rho=rho,u=u).items()}==f['fixedInput']['bits']
 rootlist=[]
 for dps in [65,90]:
  mp.mp.dps=dps;hp.D=hp.lift(hp.data);hp.R=hp.D['gas_constant']/hp.D['molar_mass'];hp.Tc=hp.D['STATES']['reducing']['T'];hp.dc=hp.D['STATES']['reducing']['rhomolar']*hp.D['molar_mass']
  d,uu=mp.mpf(rho),mp.mpf(u);T0=mp.mpf(s['T'])
  T=mp.findroot(lambda T:hp.eos(d,T)['u']-uu,(T0-mp.mpf('.01'),T0+mp.mpf('.01')),tol=mp.mpf(10)**(-dps+15),maxsteps=15)
  hom=hp.eos(d,T);eq=hp.equilibrium(d,uu,f['independentReference']['equilibrium'])
  assert not 0<=eq['Q']<=1 # all seven browser cases independently homogeneous
  vals=dict(pMinusLimit=hom['p']-3500000,rawMinusMathematical=mp.mpf(s['p'])-hom['p'],uResidual=hom['u']-uu,PHmathP=hp.eos(mp.mpf(ph['rho']),mp.mpf(ph['T']))['p'])
  rootlist.append(dict(dps=dps,homogeneous=hp.enc(hom),excludedCoexistence=hp.enc(eq),values=hp.enc(vals)))
 ref=rootlist[-1];delta=mp.mpf(ref['values']['pMinusLimit']);saved=f['highPrecisionReference'];assert abs(delta-mp.mpf(saved['pMinusLimit']))<mp.mpf('1e-50')
 assert abs(mp.mpf(rootlist[0]['homogeneous']['p'])-mp.mpf(rootlist[1]['homogeneous']['p']))<mp.mpf('1e-50')
 rawEOS=hp.eos(mp.mpf(s['rho']),mp.mpf(s['T']));phEOS=hp.eos(mp.mpf(ph['rho']),mp.mpf(ph['T']))
 canon={k:s[k]-dict(p=p,h=h,T=ph['T'])[k] for k in ['p','h','T']}
 assert canon==f['originalRecovery']['differences']
 assert all(abs(canon[k])<=v for k,v in dict(p=.1,h=.1,T=1e-4).items())
 normalized=dict(mass=float(abs(mp.mpf(s['rho'])*mp.mpf(V)-mp.mpf(M))/max(.01,M)),energy=float(abs(mp.mpf(M)*rawEOS['u']/1000-mp.mpf(U))/max(1,abs(U))))
 assert max(normalized.values())<=1e-11
 rec=dict(key=f['fixedKey'],id=f['id'],originalPHInput=f['originalPHInput'],fixedInput=f['fixedInput'],roundingStages=stages,actualPHGetter=f['originalPH'],independentPH_EOS=hp.enc(phEOS),rawDU=r['raw'],independentRawDU_EOS=hp.enc(rawEOS),rawGetterMinusIndependentEOS=hp.enc({k:mp.mpf(s[k])-rawEOS[k] for k in ['p','h','u']}),canonicalDifferences=canon,normalizedResiduals=normalized,pressureConversion=r['pressure'],mathematical=ref,precisionRepeat=rootlist[0],phase=attribution[f['failureKey']]['phase'],inheritedDetailedAttribution=attribution[f['failureKey']],mechanism='numerical-wrong-side' if delta<0 else 'rounded-inventory-conflict',adapterAccepted=False)
 rows.append(rec);mathrefs.append(dict(key=f['fixedKey'],references=rootlist))
 # Matching WebKit values are checked above and separately retained in browser evidence.
write('fixed-inputs.json',fixed);write('seven-case-analysis.json',dict(rows=rows,coefficientSHA256=hashlib.sha256(hp.raw).hexdigest(),limitations='Same unchanged EOS mathematical signs, not physical ammonia accuracy at nanopa. Precision repetition is convergence evidence, not a rigorous interval certificate.'))
falseaccept=[]
allinputs={r['key']:r for r in read(H/'fixed-inputs.json')};allrefs={r['key']:r['reference'] for r in read(H/'high-precision-references.json')['rows']}
for r in replays['chromium']['falseAcceptance']:
 f=allinputs[r['key']];assert r['input']['bits']==f['input']['bits'] and r['raw']['values']==f['historical']['DU'] and 'adapter' in r
 assert next(q for q in replays['webkit']['falseAcceptance'] if q['key']==r['key'])['raw']['bits']==r['raw']['bits']
 x=r['input']['values'];s=r['raw']['values'];roots=[]
 for dps in [65,90]:
  mp.mp.dps=dps;hp.D=hp.lift(hp.data);hp.R=hp.D['gas_constant']/hp.D['molar_mass'];hp.Tc=hp.D['STATES']['reducing']['T'];hp.dc=hp.D['STATES']['reducing']['rhomolar']*hp.D['molar_mass']
  T=mp.findroot(lambda T:hp.eos(mp.mpf(x['rho']),T)['u']-mp.mpf(x['u']),(mp.mpf(s['T'])-mp.mpf('.01'),mp.mpf(s['T'])+mp.mpf('.01')),tol=mp.mpf(10)**(-dps+15),maxsteps=15)
  state=hp.eos(mp.mpf(x['rho']),T);roots.append(dict(dps=dps,state=hp.enc(state),pMinusLimit=mp.nstr(state['p']-3500000,60)))
 assert 0<mp.mpf(roots[-1]['pMinusLimit']) and s['p']<=3500000
 assert abs(mp.mpf(roots[-1]['pMinusLimit'])-mp.mpf(allrefs[r['key']]['pMinusLimit']))<mp.mpf('1e-50')
 assert abs(mp.mpf(roots[0]['state']['p'])-mp.mpf(roots[1]['state']['p']))<mp.mpf('1e-50')
 eq=hp.equilibrium(mp.mpf(x['rho']),mp.mpf(x['u']),failures[0]['independentReference']['equilibrium']);assert not 0<=eq['Q']<=1
 falseaccept.append(dict(key=r['key'],id=r['id'],original=f,observed=r,roots=roots,excludedCoexistence=hp.enc(eq),interpretation='Mathematical fixed-inventory false-acceptance hazard: exact same-EOS pressure outside while raw/adapter returns inside. No resolved physical excursion claim.'))
write('false-acceptance-controls.json',dict(rows=falseaccept,physicalExcursionEstablished=False))
matrix=[]
mp.mp.dps=90
for r in replays['chromium']['matrix']:
 x=r['input']['values'];s=r['raw']['values'];d,u=mp.mpf(x['rho']),mp.mpf(x['u']);seed=failures[0]['independentReference']['equilibrium']
 eq=hp.equilibrium(d,u,seed)
 if 0<=eq['Q']<=1:state=eq;branch='equilibrium'
 else:
  T0=mp.mpf(s['T']);T=mp.findroot(lambda T:hp.eos(d,T)['u']-u,(T0-mp.mpf('.01'),T0+mp.mpf('.01')),tol=mp.mpf('1e-70'),maxsteps=15);state=hp.eos(d,T);branch='homogeneous'
 # State selection uses an independently solved coexistence branch, not raw Q sentinel.
 p=mp.mpf(r['request']['values']['p']);h=mp.mpf(r['request']['values']['h'])
 if branch=='homogeneous':eos=hp.eos(mp.mpf(s['rho']),mp.mpf(s['T']))
 else:
  Traw=mp.mpf(s['T'])
  def sat_at_T(rl,rv):
   l,g=hp.eos(rl,Traw),hp.eos(rv,Traw);return ((l['p']-g['p'])/1000000,(l['g']-g['g'])/1000000)
  rl,rv=mp.findroot(sat_at_T,(eq['rhoL'],eq['rhoV']),tol=mp.mpf('1e-70'),maxsteps=15)
  l,g=hp.eos(rl,Traw),hp.eos(rv,Traw);q=mp.mpf(s['Q'])
  eos=dict(p=(l['p']+g['p'])/2,T=Traw,rho=1/((1-q)/rl+q/rv),u=(1-q)*l['u']+q*g['u'],h=(1-q)*l['h']+q*g['h'])
 normalized=dict(mass=float(abs(eos['rho']*mp.mpf(x['V'])-mp.mpf(x['M']))/max(.01,x['M'])),energy=float(abs(mp.mpf(x['M'])*eos['u']/1000-mp.mpf(x['U_kJ']))/max(1,abs(x['U_kJ']))))
 canonical=dict(p=float(mp.mpf(s['p'])-p),h=float(mp.mpf(s['h'])-h),T=s['T']-r['PH']['values']['T'])
 matrix.append(dict(id=r['id'],branch=branch,reference=hp.enc(state),excludedOrPhysicalCoexistence=hp.enc(eq),independentReturnedEOS=hp.enc(eos),getterMinusIndependentEOS=hp.enc({k:mp.mpf(s[k])-eos[k] for k in ['p','rho','u','h']}),pMinusLimit=mp.nstr(state['p']-3500000,65),rawMinusReference=mp.nstr(mp.mpf(s['p'])-state['p'],65),canonical=canonical,normalized=normalized,canonicalPass=abs(canonical['p'])<=.1 and abs(canonical['h'])<=.1 and abs(canonical['T'])<=1e-4,nonlinearPass=max(normalized.values())<=1e-11,actualAdapterAccepted='adapter' in r,requestedP=r['request']['values']['p']))
write('matrix-mathematics.json',dict(rows=matrix,precision=90,intervalCertified=False))
with (E/'fixed-inventory.csv').open('w') as stream:
 fields=['runtime','key','id','P_Pa','h_Jkg','M','V','U_kJ','rho','u','M_bits','V_bits','U_kJ_bits','rho_bits','u_bits','rawP','rawP_bits'];w=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');w.writeheader()
 for f in fixed:
  w.writerow(dict(runtime=f['runtime'],key=f['fixedKey'],id=f['id'],P_Pa=f['originalPHInput'][0],h_Jkg=f['originalPHInput'][1],**f['fixedInput']['values'],**{k+'_bits':v for k,v in f['fixedInput']['bits'].items()},rawP=f['originalRecovery']['DU']['values']['p'],rawP_bits=f['originalRecovery']['DU']['bits']['p']))
print('14 original identities verified; seven independent 65/90-digit roots; 24 diagnostic roots; all original canonical and nonlinear checks retained')
