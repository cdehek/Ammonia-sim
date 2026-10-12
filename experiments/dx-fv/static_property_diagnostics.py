"""Additional independent checks and original-surface comparison; static only."""
import ast
import json
import sys
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
from CoolProp import AbstractState, PQ_INPUTS, HmassP_INPUTS
from static_property_reconstruction import ROOT,DATA,P,X,Z,SAT,F,VALID,candidates

E=Path(sys.argv[1]).resolve();assert not E.is_relative_to(ROOT)
MODE=sys.argv[2] if len(sys.argv)>2 else 'all';assert MODE in ['all','probes']
save=lambda name,obj:(E/name).write_text(json.dumps(obj,indent=2,allow_nan=False,
                                                   default=lambda v:v.item())+'\n')
def stats(a):
    a=np.array(a);return dict(count=len(a),maximumAbsolute=float(max(abs(a))),rms=float(np.sqrt(np.mean(a*a))),
                             minimum=float(min(a)),maximum=float(max(a)))
source=ROOT/'experiments/dx-fv/joint_property_analysis.py'
tree=ast.parse(source.read_text());prefix=[]
for node in tree.body:
    if isinstance(node,ast.If) and ast.unparse(node.test)=="MODE == 'prepare'":break
    prefix.append(node)
else:raise AssertionError('Original diagnostic definition boundary missing')
argv=sys.argv;sys.argv=[str(source),'analyze',str(E)];ns={'__file__':str(source)}
exec(compile(ast.Module(body=prefix,type_ignores=[]),str(source),'exec'),ns);sys.argv=argv
old=ns['surface'];models=candidates();ts_pchip=PchipInterpolator(X,SAT[:,0]+273.15,extrapolate=False)
if MODE=='all':
    interior=json.loads((E/'interior.json').read_text());baseline=[]
    for row in interior['rows']:
        p=row['p'];truth=row['EOS'];z=old.saturation(p)['T']+273.15-truth['T']
        i,w=old.bracket(p);axis,hc,rc=old.curves(p,'liquid')
        if not 0<=z<=axis[-1]:baseline.append(dict(p=p,z=z,failure='Original PT liquid offset unsupported'));continue
        j=min(len(axis)-2,int(z));b=(z-axis[j])/(axis[j+1]-axis[j]);a0=F[i];a1=F[i+1]
        h=float(np.interp(z,axis,hc));rho=float(np.exp(np.interp(z,axis,rc)))
        hx=(a1[j,0]*(1-b)+a1[j+1,0]*b-a0[j,0]*(1-b)-a0[j+1,0]*b)/(X[i+1]-X[i])
        hz=(hc[j+1]-hc[j])/(axis[j+1]-axis[j])
        rx=((1-b)*np.log(a1[j,2])+b*np.log(a1[j+1,2])-(1-b)*np.log(a0[j,2])-b*np.log(a0[j+1,2]))/(X[i+1]-X[i])
        rz=(rc[j+1]-rc[j])/(axis[j+1]-axis[j]);tx=(SAT[i+1,0]-SAT[i,0])/(X[i+1]-X[i])
        rp=rho*(rx+rz*tx)/p;rt=-rho*rz;hp=(hx+hz*tx)/p
        baseline.append(dict(p=p,z=z,errors=dict(h=h-truth['h'],rho=rho-truth['rho'],u=h-100*p/rho-truth['u']),
                             kappa=rp/rho,cp=-hz,maxwell=hp-100*(1/rho+truth['T']*rt/rho**2)))
    valid=[r for r in baseline if 'failure' not in r]
    summary=dict(count=len(baseline),failures=len(baseline)-len(valid),
                 errors={k:stats([r['errors'][k] for r in valid]) for k in ['h','rho','u']},
                 kappa=stats([r['kappa'] for r in valid]),cp=stats([r['cp'] for r in valid]),
                 maxwell=stats([r['maxwell'] for r in valid]),negativeCompressibility=sum(r['kappa']<=0 for r in valid))
    save('baseline.json',dict(summary=summary,rows=baseline))
    print('Original constitutive surface compared at same PT',flush=True)

    # Original and saturation-only PCHIP PH comparators at all PH requests.
    ph=[]
    for row in json.loads((E/'ph.json').read_text())['rows']:
        p=row['p'];truth=row['EOS']
        try:
            a=old.from_ph(p,truth['h']);a['T']+=273.15
            b=dict(a,T=float(ts_pchip(np.log(p)))-a['offsetK'])
            f=ns['du'](a['rho'],a['u'])
            ph.append(dict(p=p,z=row['z'],original=a,pchipTemperatureOnly=b,
                           originalErrors={k:a[k]-truth[k] for k in ['p','T','h','rho','u']},
                           pchipErrors={k:b[k]-truth[k] for k in ['p','T','h','rho','u']},
                           pressureConstitutiveErrorBar=p-f['p']))
        except (ValueError,AssertionError) as exc:ph.append(dict(p=p,z=row['z'],failure=str(exc)))

# Exact previously reported PH probes, including the 0.033-bar trajectory endpoint
# reused as a STATIC target. No trajectory replay or candidate integration.
if MODE=='probes':ph=json.loads((E/'baseline-ph.json').read_text())['rows']
previous=json.loads((ROOT/'../ammonia-joint-property-evidence/properties.json').read_text())['points']
names=['liquid-p0.3029893712344606-sc1.0','saved-five-linear-0','saved-five-linear-1']
names.append(max((v['name'] for v in previous if v['name'].startswith('saved-five-linear-')),
                 key=lambda name:int(name.rsplit('-',1)[1])))
saved=[]
for name in names:
    r=next(v for v in previous if v['name']==name);p=r['p'];h=r['h']
    eos=AbstractState('HEOS','Ammonia');eos.update(HmassP_INPUTS,h*1000,p*1e5)
    truth=dict(p=p,h=h,T=eos.T(),rho=eos.rhomass(),u=eos.umass()/1000)
    a=old.from_ph(p,h);a['T']+=273.15;f=ns['du'](a['rho'],a['u'])
    row=dict(name=name,p=p,h=h,EOS=truth,original=a,
             originalPressureErrorBar=p-f['p'],candidates={})
    for method,c in models.items():
        try:
            state=c.ph(p,h);flash=ns['du'](state['rho'],state['u'])
            row['candidates'][method]=dict(state=state,errors={k:state[k]-truth[k] for k in truth},
                                         pressureConstitutiveErrorBar=p-flash['p'])
        except (ValueError,FloatingPointError) as exc:row['candidates'][method]=dict(failure=str(exc))
    saved.append(row)
save('baseline-ph.json',dict(rows=ph,savedProbes=saved))
print('Previously reported liquid probes evaluated statically',flush=True)

# Coordinate saturation scan: EOS convergence-independent algebraic evaluations;
# dense boundaries also test monotonicity/no overshoot and Clapeyron/coexistence.
if MODE=='all':
    sat=AbstractState('HEOS','Ammonia');saturation=[]
    for i in range(len(P)-1):
        for a in np.linspace(0,1,17):
            p=min(35.,float(np.exp(X[i]+a*(X[i+1]-X[i]))))
            sat.update(PQ_INPUTS,p*1e5,0);T=sat.T();hf=sat.hmass()/1000;sf=sat.smass()/1000;rf=sat.rhomass()
            sat.update(PQ_INPUTS,p*1e5,1);hg=sat.hmass()/1000;sg=sat.smass()/1000;rg=sat.rhomass()
            row=dict(p=p,temperatureErrorK=models['joint-pchip'].temperature(p,0)-T,
                     coordinateSlopeKBar=float(models['joint-pchip'].ts(np.log(p),1))/p,
                     inKnotTemperatureRange=bool(SAT[i,0]+273.15-1e-12<=models['joint-pchip'].temperature(p,0)<=SAT[i+1,0]+273.15+1e-12),candidates={})
            for name,c in models.items():
                try:
                    f=c.at(p,0,derivatives=False);Tk=f['T'];g=f['h']-Tk*f['s']
                    # Unchanged vapor fields are only boundary comparators. No vapor
                    # reconstruction is claimed. The direct EOS vapor is independent.
                    v=old.saturation(p)
                    vg=v['hg']-Tk*v['sg']
                    latent=v['hg']-f['h'];dv=1/v['rhog']-1/f['rho']
                    clapeyron=100*Tk*dv/latent
                    row['candidates'][name]=dict(hErrorKJkg=f['h']-hf,rhoErrorKgM3=f['rho']-rf,
                            liquidGMinusUnchangedVaporGKJkg=g-vg,
                            liquidGMinusEOSVaporGKJkg=g-(hg-Tk*sg),
                            clapeyronMismatchKBar=row['coordinateSlopeKBar']-clapeyron)
                except (ValueError,FloatingPointError) as exc:row['candidates'][name]=dict(failure=str(exc))
            saturation.append(row)
    save('saturation.json',dict(count=len(saturation),rows=saturation))
    print('Saturation consistency boundaries scanned',flush=True)

# Independent finite-difference checks of potential thermodynamic derivatives.
derivatives=[]
for p,z in [(.3029893712344606,1.),(1.,.1),(3.5,10.),(32.65314902038559,.1)]:
    for name,c in models.items():
        center=c.at(p,z)
        for relative in [1e-6,3e-7]:
            dp=p*relative;dt=1e-5;T=center['T']
            pm=c.at(p-dp,c.temperature(p-dp,0)-T,derivatives=False)
            pp=c.at(p+dp,c.temperature(p+dp,0)-T,derivatives=False)
            tm=c.at(p,z+dt,derivatives=False);tp=c.at(p,z-dt,derivatives=False)
            gp=((pp['h']-T*pp['s'])-(pm['h']-T*pm['s']))/(2*dp)
            gt=((tp['h']-tp['T']*tp['s'])-(tm['h']-tm['T']*tm['s']))/(2*dt)
            rp=(pp['rho']-pm['rho'])/(2*dp);rt=(tp['rho']-tm['rho'])/(2*dt)
            hp=(pp['h']-pm['h'])/(2*dp)
            derivatives.append(dict(method=name,p=p,z=z,relativePressureStep=relative,
              potentialVolumeIdentityErrorKJkgBar=gp-100/center['rho'],potentialEntropyIdentityError=gt+center['s'],
              rhoPAnalytical=center['rhoP'],rhoPFinite=rp,rhoTAnalytical=center['rhoT'],rhoTFinite=rt,
              finiteMaxwellMismatchKJkgBar=hp-100*(1/center['rho']+T*rt/center['rho']**2)))
save('derivatives.json',derivatives)

# Independent half-grid check of the problematic two inventory root scans.
if MODE=='all':
    roots=json.loads((E/'roots.json').read_text());refined=[]
    probes=sorted(set(roots['searchPressuresBar']+list(np.linspace(.3,.34,3201))))
    for row in roots['lowPressure']:
        q=dict(coordinates=row['coordinates'],candidates={})
        for name,c in models.items():
            found=c.roots(row['rho'],row['u'],probes)
            q['candidates'][name]=dict(rootsBar=found,bracketChecks=c.last_root_checks,
                energyResidualsKJkg=[c.at_density(p,row['rho'])['u']-row['u'] for p in found])
        refined.append(q)
        print('Refined low-pressure root scan',row['coordinates'],flush=True)
    save('roots-refined.json',dict(rows=refined,searchPressuresBar=probes))

# Comparable pure-Python original constitutive PT workload and five warm pairs.
workload=json.loads((E/'performance.json').read_text())['workload']
def original_at(p,z):
    i,w=old.bracket(p);axis,hc,rc=old.curves(p,'liquid')
    a=dict(h=float(np.interp(z,axis,hc)),rho=float(np.exp(np.interp(z,axis,rc))))
    a.update(p=p,T=old.saturation(p)['T']+273.15-z,
        s=float(np.interp(z,axis,(1-w)*F[i,:len(axis),1]+w*F[i+1,:len(axis),1])))
    a['u']=a['h']-100*p/a['rho'];return a
for p,z in workload:original_at(p,z)
timings=[]
for pair in range(5):
    order=['original','joint-pchip','gibbs-rounded-projection']
    if pair%2:order.reverse()
    for name in order:
        t=time.perf_counter();checksum=0.
        for repeat in range(10):
            for p,z in workload:
                # Identical physical PT inputs and identical six output fields.
                T=models['joint-pchip'].temperature(p,z)
                a=original_at(p,old.saturation(p)['T']+273.15-T) if name=='original' else models[name].at(p,z,derivatives=False)
                checksum+=a['rho']
        timings.append(dict(pair=pair,method=name,seconds=time.perf_counter()-t,
                            evaluations=300,checksum=checksum))
save('baseline-performance.json',dict(staticOnly=True,
       warning='Python prototype comparison; not Node solver or coupled performance.',timings=timings))
print('Additional static checks completed',flush=True)
