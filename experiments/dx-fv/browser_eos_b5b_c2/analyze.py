"""Evidence joins, exact arithmetic stages, scientific budgets and measured costs."""
import hashlib,json,os,statistics,struct
from fractions import Fraction as F
from pathlib import Path
import reference as r
B=Path(__file__).resolve().parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'));X=B.parent
def read(p):return json.loads(p.read_text())
def write(n,x):
 p=E/n;assert not p.exists();p.write_text(json.dumps(x,indent=2)+'\n')
refs=read(E/'references.json');loc={x['key']:x for x in read(E/'local-enclosures.json')['rows']};sup={x['key']:x for x in read(E/'equilibrium-supplement.json')['rows']};native={x['key']:x for x in read(E/'native.json')['rows']}
origins={x['key']:x for x in read(E/'chromium-origins.json')['rows']}
failures={x['fixedKey']:x for x in read(X/'browser_eos_b5/evidence/original-failures.json')['rows'] if x['runtime']=='chromium'}
browser={n:read(E/(n+'-replay.json')) for n in ['chromium','webkit']}
stages=[];matrix=[]
for row in refs['rows']:
 c=row['case'];key=c['key'];x=c['input']['values'];request=c.get('request');PH=c.get('PH');raw=c['raw']['values'];source=None
 if key in failures:
  f=failures[key];request=dict(values=dict(zip(['p','h'],f['originalPHInput'])));PH=f['originalPH'];source='B5 original-failures.json, saved bits'
 elif key in origins:
  request=origins[key]['request'];PH=origins[key]['raw'];source='B4C webkit-candidateB-focused.json inputBits; newly replayed in both engines'
 canonical=None
 if request and PH:
  q=request['values'];canonical=dict(p=raw['p']-q['p'],h=raw['h']-q['h'],T=raw['T']-PH['values']['T'])
  assert all(abs(canonical[k])<=z for k,z in dict(p=.1,h=.1,T=1e-4).items())
  if key in failures or key in origins:
   operations=[]
   def op(name,a,b,kind):
    exact={'/':lambda:F(a)/F(b),'*':lambda:F(a)*F(b),'-':lambda:F(a)-F(b)}[kind]();value={'/':lambda:a/b,'*':lambda:a*b,'-':lambda:a-b}[kind]();error=F(value)-exact
    operations.append(dict(name=name,operation=kind,aBits=r.bits(a),bBits=r.bits(b),resultBits=r.bits(value),resultExactRational=r.rational(F(value)),roundingError=r.rational(error)));return value
   V=op('V',.003,5.,'/');M=op('M',PH['values']['rho'],V,'*');hk=op('h_kJkg',q['h'],1000.,'/');pb=op('P_bar',q['p'],100000.,'/');mh=op('M_h',M,hk,'*');a=op('100_Pbar',100.,pb,'*');work=op('pressureWork',a,V,'*');U=op('U_kJ',mh,work,'-');d=op('rho_DU',M,V,'/');uk=op('u_kJkg',U,M,'/');u=op('u_DU',uk,1000.,'*')
   assert {k:r.bits(v) for k,v in dict(M=M,V=V,U_kJ=U,rho=d,u=u).items()}==c['input']['bits']
   w=r.hp.data['molar_mass'];internal=dict(rhomolar=d/w,umolar=u*w)
   stages.append(dict(key=key,origin=source,requestedPH=request,actualPH=PH,input=c['input'],storedRationals={k:r.rational(F(v)) for k,v in x.items()},operations=operations,internalMolar=dict(values=internal,bits={k:r.bits(v) for k,v in internal.items()}),targetRationals={k:{a:v[a] for a in ['exactDensity','exactEnergyJkg']} for k,v in row['targets'].items()}))
 targets={}
 for name,t in row['targets'].items():
  z=(sup[key]['targets'][name]['levels'][-1] if 'error'in t else t['levels'][-1])
  local=loc[key]['targets'][name];cert=local.get('trials',[{}])[-1]
  targets[name]=dict(branchDiagnostic=z['branch'],pressureMinusLimitPaDiagnostic=z['pMinusLimit'],highPrecisionReference=z,
   localRootEnclosure=cert if cert else None,certificateStatus='UNRESOLVED',physicalBranchCertified=False,initialDiagnosticFailure=t.get('error'))
 residual=row.get('normalizedResiduals')
 if residual is None and key in sup:
  r.precision(90);z=sup[key]['targets']['rounded_DU']['levels'][-1]['selected'];mp=r.mp;hp=r.hp;T=mp.mpf(raw['T'])
  def sat(a,b):
   l,v=hp.eos(a,T),hp.eos(b,T);return (l['p']-v['p'])/10**6,(l['g']-v['g'])/10**6
  rl,rv=mp.findroot(sat,(mp.mpf(z['rhoL']),mp.mpf(z['rhoV'])),tol=mp.mpf('1e-70'),maxsteps=20);l,v=hp.eos(rl,T),hp.eos(rv,T);q=mp.mpf(raw['Q']);den=1/((1-q)/rl+q/rv);uu=(1-q)*l['u']+q*v['u']
  residual=r.enc(dict(mass=abs(den*mp.mpf(x['V'])-mp.mpf(x['M']))/max(.01,x['M']),energy=abs(mp.mpf(x['M'])*uu/1000-mp.mpf(x['U_kJ']))/max(1,abs(x['U_kJ']))))
 if residual:assert max(float(v) for v in residual.values())<=1e-11
 observed={}
 for name,b in browser.items():
  if c['group']=='rows':
   identity=next(y['id'] for y in browser['chromium']['rows'] if y['key']==key)
   rr=next(z for z in b['rows'] if z['id']==identity)
  else:rr=next(z for z in b[c['group']] if z.get('key',z.get('id'))==key)
  observed[name]=dict(input=rr['input'],raw=rr.get('raw'),rawError=rr.get('rawError'),adapter=rr.get('adapter'),error=rr.get('error'),adapterPH=rr.get('adapterPH'),adapterPHError=rr.get('adapterPHError'))
 # No new full standalone/A2/phase qualification is inferred from these diagnostics.
 qualification='Original Gate B independent phase unresolved' if c['group']=='endpoints' else 'Exact-boundary qualification blocked' if c['group'] in ['rows','falseAcceptance'] else 'Inherited finite standalone controls; C2 rechecks canonical/local residuals where applicable; no full backend/A2 qualification'
 matrix.append(dict(key=key,group=c['group'],exactInput=c['input'],requestedPH=request,PHInputSupported=(30000<=request['values']['p']<=3500000) if request else 'unknown',originalPH=PH,actual=observed,nativeRaw=native[key],canonicalDifferences=canonical,canonicalPass=True if canonical else 'unmeasured in C2',normalizedResiduals=residual,targets=targets,certificateStatus='UNRESOLVED',originalScientificQualification=qualification,physicalTrajectoryExit='unproved'))
write('inventory-arithmetic.json',dict(operationOrder='accepted binary64 sequence, no algebraic simplification or FMA',rows=stages))
write('matrix.json',dict(evidenceLevels=['HIGH_PRECISION_DIAGNOSTIC','validated LOCAL homogeneous enclosure, no phase certificate','original scientific qualification separate'],rows=matrix))
times={}
for prec in [192,256]:
 a=[t['seconds'] for x in loc.values() for v in x['targets'].values() for t in v.get('trials',[]) if t.get('precisionBits')==prec];times[str(prec)]=dict(n=len(a),medianSeconds=statistics.median(a),maxSeconds=max(a),minSeconds=min(a),eosEvaluationsPerAttempt=3)
write('performance.json',dict(localHomogeneousEnclosure=times,referenceCaseTotalSeconds=dict(n=len(refs['rows']),median=statistics.median(x['seconds'] for x in refs['rows']),max=max(x['seconds'] for x in refs['rows'])),excluded=['high-precision root search before local enclosure','validated saturation/physical branch proof','global competing-root exclusion','initialization/imports','browser transfer/worker startup','all original simulator validation'],browserCertificateMeasured=False,physicalIPadMeasured=False))
table=['# Focused exact-inventory matrix','', 'All complete certificate outcomes are **UNRESOLVED**. Signed numbers below are Level-1 diagnostics; homogeneous local pressure bounds are separately retained in `evidence/local-enclosures.json`. PH input support is a separate fact.','', '| Case | PH input supported | Raw p−max (Pa) | Exact M/U/V p−max (Pa) | Rounded DU p−max (Pa) | Branch diagnostic | Historical MVU |','|---|---|---:|---:|---:|---|---|']
for x in matrix:
 t=x['targets'];raw=x['actual']['chromium']['raw']['values']['p']-3500000
 table.append(f"| {x['key']} | {x['PHInputSupported']} | {raw:+.12g} | {float(t['exact_MUV']['pressureMinusLimitPaDiagnostic']):+.12g} | {float(t['rounded_DU']['pressureMinusLimitPaDiagnostic']):+.12g} | {t['exact_MUV']['branchDiagnostic']} | {'return' if x['actual']['chromium']['adapter'] else 'refuse'} |")
(E/'MATRIX.md' if os.environ.get('C2_EVIDENCE') else B/'MATRIX.md').write_text('\n'.join(table)+'\n\nThe first seven contain one exact-M/U/V inside sign and six outside signs; their historical rounded-DU split remains two inside/five outside. No historical file or classification wrapper changes. Gate B endpoint rows remain unqualified. B5-sweep-19 retains its initial algebraic diagnostic failure and successful physical-equation supplement.\n')
print('9 original construction audits;',len(matrix),'full matrix rows;',times)
