"""Validated LOCAL homogeneous u(rho,T) root enclosure, NOT phase certification.

All EOS operations use FLINT/Arb balls, including powers/exp/log. Exact rationals
are constructed before ball conversion. A seed is only a proposed bracket centre.
The public diagnostic ALWAYS returns UNRESOLVED absent a validated physical
branch. It never emits a thermodynamic property state for a simulator.
"""
import hashlib,json,os,time
from fractions import Fraction as F
from pathlib import Path
from flint import arb,fmpq,ctx
B=Path(__file__).resolve().parent;E=Path(os.environ.get('C2_EVIDENCE',B/'evidence'))
DATA=json.loads((B/'evidence/Ammonia.json').read_text())['EOS'][0]
def ball(x):
 if isinstance(x,arb):return x
 q=F(x);return arb(fmpq(q.numerator,q.denominator))
def lift(x):
 if isinstance(x,(float,int)):return ball(x)
 if isinstance(x,list):return [lift(v) for v in x]
 if isinstance(x,dict):return {k:lift(v) for k,v in x.items()}
 return x
def eos(d,T):
 D=lift(DATA);R=D['gas_constant']/D['molar_mass'];Tc=D['STATES']['reducing']['T'];dc=D['STATES']['reducing']['rhomolar']*D['molar_mass'];delta,tau=d/dc,Tc/T
 art,artt,ard=arb(0),arb(0),arb(0)
 for group in D['alphar']:
  for i,n in enumerate(group['n']):
   di,ti=group['d'][i],group['t'][i];v=n*delta**di*tau**ti;lt=ti/tau;ltt=-ti/tau**2;ld=di/delta
   if group['type']=='ResidualHelmholtzPower':
    le=group['l'][i]
    if not le.is_zero():v*=(-delta**le).exp();ld-=le*delta**(le-1)
   elif group['type']=='ResidualHelmholtzGaussian':
    eta,beta,eps,gamma=[group[k][i] for k in ['eta','beta','epsilon','gamma']]
    v*=(-eta*(delta-eps)**2-beta*(tau-gamma)**2).exp();ld-=2*eta*(delta-eps);lt-=2*beta*(tau-gamma);ltt-=2*beta
   elif group['type']=='ResidualHelmholtzGaoB':
    eta,beta,eps,gamma,b=[group[k][i] for k in ['eta','beta','epsilon','gamma','b']];z=b+beta*(tau-gamma)**2
    if z.contains(0):raise ArithmeticError('GaoB denominator interval includes zero')
    v*=(eta*(delta-eps)**2+1/z).exp();ld+=2*eta*(delta-eps);lt-=2*beta*(tau-gamma)/z**2;ltt+=-2*beta/z**2+8*beta**2*(tau-gamma)**2/z**3
   else:raise ValueError(group['type'])
   art+=v*lt;artt+=v*(lt**2+ltt);ard+=v*ld
 lead,log,planck=D['alpha0'];a0t=lead['a2']+log['a']/tau;a0tt=-log['a']/tau**2
 for n,t in zip(planck['n'],planck['t']):
  em=(t*tau).expm1();a0t+=n*t/em;a0tt-=n*t**2*(t*tau).exp()/em**2
 return dict(p=d*R*T*(1+delta*ard),u=R*Tc*(a0t+art),cv=-R*tau**2*(a0tt+artt))
def serialize(x):
 # Exact rational endpoints of outward dyadic lower/upper bounds. Decimal is display only.
 lo,hi=x.lower().fmpq(),x.upper().fmpq()
 return dict(lower=str(lo),upper=str(hi),display=x.str(65,radius=True))
def enclose(density,energy,seed,precision=256,radius='1e-30'):
 ctx.prec=precision;d,u=ball(density),ball(energy);c=ball(F(seed));rad=F(radius)
 if not (d>0 and rad>0 and ball(F(seed)-rad)>0 and u.is_finite()):raise ArithmeticError('invalid density, temperature, radius or energy')
 # Independent rational endpoints, no floating-point interval endpoint construction.
 a,b=F(seed)-rad,F(seed)+rad;T=ball(a).union(ball(b))
 ea,eb,whole=eos(d,ball(a)),eos(d,ball(b)),eos(d,T)
 fa,fb=ea['u']-u,eb['u']-u
 if not all(x.is_finite() for x in [fa,fb,whole['cv'],whole['p']]):raise ArithmeticError('nonfinite ball')
 if not (fa<0 and fb>0):raise ArithmeticError('strict endpoint signs not established')
 if not whole['cv']>0:raise ArithmeticError('cv positivity not established over bracket')
 # Continuity on positive rho/T and finite nonzero denominators + IVT gives
 # existence. cv>0 on the entire interval gives uniqueness at this density.
 p=whole['p'];delta=p-3500000
 side='OUTSIDE' if delta>0 else 'INSIDE' if delta<=0 else 'STRADDLES'
 return dict(status='UNRESOLVED',reason='Physical branch and competing-phase exclusion are not validated',
  method='Arb homogeneous sign bracket + interval cv, C2-local/1',precisionBits=precision,
  localRootExistence=True,localRootUnique=True,physicalBranchCertified=False,fullInventoryCertified=False,
  localPressureSide=side,temperature=serialize(T),pressurePa=serialize(p),pMinusLimitPa=serialize(delta),
  cv=serialize(whole['cv']),lowerEnergyResidual=serialize(fa),upperEnergyResidual=serialize(fb),eosEvaluations=3)
def run():
 refs=json.loads((E/'references.json').read_text());rows=[]
 for row in refs['rows']:
  c=row['case'];out=dict(key=c['key'],inputBits=c['input']['bits'],status='UNRESOLVED',targets={})
  for name,target in row['targets'].items():
   if 'error'in target:out['targets'][name]=dict(status='NUMERICAL_FAILURE',reason=target['error']);continue
   z=target['levels'][-1]
   if z['branch']=='equilibrium':
    out['targets'][name]=dict(status='UNRESOLVED',reason='Equilibrium branch requires coupled validated coexistence enclosure; homogeneous certificate deliberately withheld');continue
   d,u=[F(int(target[k]['numerator']),int(target[k]['denominator'])) for k in ['exactDensity','exactEnergyJkg']]
   trials=[]
   for prec in [192,256]:
    start=time.perf_counter()
    try:result=enclose(d,u,z['homogeneous']['T'],prec)
    except Exception as ex:result=dict(status='NUMERICAL_FAILURE',reason=repr(ex))
    result['seconds']=time.perf_counter()-start;trials.append(result)
   out['targets'][name]=dict(status=trials[-1]['status'],trials=trials)
  rows.append(out)
 p=E/'local-enclosures.json';assert not p.exists()
 p.write_text(json.dumps(dict(schema='C2-local/1',arithmetic='python-flint 0.8.0 / FLINT 3.3.1 Arb balls',scope='LOCAL homogeneous root only, not complete phase/support certification',rows=rows),indent=2)+'\n')
 print('rows',len(rows),'local enclosures',sum('trials'in t and t['trials'][-1].get('localRootExistence',False) for r in rows for t in r['targets'].values()))
if __name__=='__main__':
 import argparse,struct
 parser=argparse.ArgumentParser();parser.add_argument('--inventory',help='JSON containing exact M,V,U_kJ binary64 hex bits');parser.add_argument('--seed',help='rational/decimal temperature bracket centre, never trusted as proof');parser.add_argument('--radius',default='1e-30');args=parser.parse_args()
 if not args.inventory:run()
 else:
  try:
   b=json.loads(Path(args.inventory).read_text());x={k:struct.unpack('>d',bytes.fromhex(b[k]))[0] for k in ['M','V','U_kJ']};m,v,U=map(F,[x['M'],x['V'],x['U_kJ']])
   if not (m>0 and v>0):raise ValueError('nonpositive M/V')
   result=enclose(m/v,1000*U/m,args.seed,radius=args.radius);result['inventoryBits']=b;result['target']='exact_MUV'
  except Exception as ex:result=dict(status='NUMERICAL_FAILURE',reason=repr(ex))
  print(json.dumps(result,indent=2))
