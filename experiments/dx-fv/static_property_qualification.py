"""Independent static EOS comparisons, never a coupled integration.

All candidate construction precedes EOS evaluation and consumes frozen data only.
Reproduction: pinned Python static_property_qualification.py /outside/repo/evidence
"""
import ast
import hashlib
import json
import math
import platform
import resource
import sys
import time
from pathlib import Path
import numpy as np
import scipy
import CoolProp
from CoolProp import AbstractState, PT_INPUTS, PQ_INPUTS, DmassUmass_INPUTS, DmassT_INPUTS, iphase_liquid
from scipy.optimize import brentq
from static_property_reconstruction import ROOT, DATA, P, X, Z, SAT, F, VALID, candidates

E=Path(sys.argv[1]).resolve();assert not E.is_relative_to(ROOT);E.mkdir(exist_ok=True,parents=True)
assert CoolProp.__version__=='7.2.0'
def save(name,data):
    (E/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def clean(obj):
    if isinstance(obj,dict):return {k:clean(v) for k,v in obj.items()}
    if isinstance(obj,list):return [clean(v) for v in obj]
    if isinstance(obj,(float,np.floating)):return float(obj) if np.isfinite(obj) else None
    if isinstance(obj,(int,np.integer)):return int(obj)
    return obj
def stats(values):
    a=np.array(values);a=a[np.isfinite(a)]
    return dict(count=len(a),maximumAbsolute=float(np.max(abs(a))),rms=float(np.sqrt(np.mean(a*a))),
                minimum=float(min(a)),maximum=float(max(a))) if len(a) else dict(count=0)
models={};construction={}
for name,model in candidates().items():models[name]=model
# Separate construction timings: equivalent rebuilds, no EOS calls.
from static_property_reconstruction import JointPchip,GibbsHermite
for name,ctor in [('joint-pchip',JointPchip),('gibbs-bicubic',lambda:GibbsHermite(order=1)),
                  ('gibbs-biquintic',GibbsHermite),('gibbs-rounded-projection',lambda:GibbsHermite(projected=True))]:
    t=time.perf_counter();c=ctor();construction[name]=dict(seconds=time.perf_counter()-t,
          polynomialArrayBytes=sum(a.nbytes for a in getattr(c,'coefficients',{}).values()),
          projection=getattr(c,'projection',None))
    del c
print('Candidates constructed; frozen data only',flush=True)
eos=AbstractState('HEOS','Ammonia');sat=AbstractState('HEOS','Ammonia')
def snapshot():return dict(p=eos.p()/1e5,T=eos.T(),h=eos.hmass()/1000,
                           s=eos.smass()/1000,rho=eos.rhomass(),u=eos.umass()/1000)
def reference(p,z):
    sat.update(PQ_INPUTS,p*1e5,0);T=sat.T()-z
    if z==0:
        eos.unspecify_phase();eos.update(PQ_INPUTS,p*1e5,0)
    else:
        # Stable liquid is known from T<Tsat. Explicit phase selection bypasses
        # CoolProp's near-saturation PT ambiguity check; no metastable samples.
        eos.specify_phase(iphase_liquid);eos.update(PT_INPUTS,p*1e5,T)
    return snapshot()
def flash(rho,u):
    eos.unspecify_phase()
    try:eos.update(DmassUmass_INPUTS,rho,u*1000);fallback=False
    except ValueError as exc:
        if 'Input vapor quality' not in str(exc):raise
        def f(T):eos.update(DmassT_INPUTS,rho,T);return eos.umass()/1000-u
        T=brentq(f,200,600,xtol=1e-10);eos.update(DmassT_INPUTS,rho,T);fallback=True
    return dict(**snapshot(),DTFallback=fallback)

# Full original-liquid-knot audit, including all reconstructed deviations.
knots=[];knotstats={};source={k:[] for k in ['T','h','s','rho']}
for i,p in enumerate(P):
    for j,z in enumerate(Z):
        if not VALID[i,j]:continue
        truth=reference(float(p),float(z));values={}
        original=dict(T=SAT[i,0]+273.15-z,h=F[i,j,0],s=F[i,j,1],rho=F[i,j,2])
        for k in source:source[k].append(original[k]-truth[k])
        for name,c in models.items():
            a=c.at(min(float(p),35.),float(z),derivatives=False)
            delta={k:a[k]-original[k] for k in original}
            values[name]=dict(deviations=delta,eosErrors={k:a[k]-truth[k] for k in truth})
        knots.append(dict(i=i,j=j,p=float(p),z=float(z),original=original,candidates=values))
for name in models:
    knotstats[name]={k:stats([row['candidates'][name]['deviations'][k] for row in knots])
                     for k in ['T','h','s','rho']}
save('knots.json',clean(dict(count=len(knots),sourceRoundingAgainstEOS={k:stats(v) for k,v in source.items()},
                           summary=knotstats,knots=knots)))
print('All liquid knots recorded',len(knots),flush=True)

# 2x2 interior quadrature-style sampling of every supported original liquid cell,
# plus a near-saturation pressure-midpoint sweep. These are finite tests, not proof.
samples=[]
for i in range(len(P)-1):
    zm=float(Z[np.flatnonzero(VALID[i]&VALID[i+1])[-1]])
    for a in [.25,.75]:
        p=float(np.exp(X[i]+a*(X[i+1]-X[i])))
        for j in range(int(zm)):
            for b in [.25,.75]:samples.append((p,j+b,'interior'))
    for z in [1e-6,.001,.01,.1,.5,1.,5.,15.,29.5]:
        if z<zm:samples.append((float(np.exp((X[i]+X[i+1])/2)),z,'near-boundary'))
for p in [.3,.3029893712344606,1.,3.5,32.65314902038559,35.]:
    for z in [.01,.1,1.,5.,15.]:
        if z<models['joint-pchip'].bounds(p)[1]:samples.append((p,z,'explicit'))
summary={name:dict(errors={k:[] for k in ['h','rho','u','s']},kappa=[],cp=[],cv=[],
                  maxwell=[],condition=[],failures=[],unstable=[]) for name in models}
rows=[];ts_errors=[]
for index,(p,z,kind) in enumerate(samples):
    truth=reference(p,z);row=dict(p=p,z=z,kind=kind,EOS=truth,candidates={})
    for name,c in models.items():
        # Same physical PT, not simply the same native offset.
        zz=c.temperature(p,0)-truth['T']
        try:
            if zz<0:raise ValueError('Near-saturation physical state lies outside candidate liquid boundary')
            a=c.at(p,zz)
            for k in summary[name]['errors']:summary[name]['errors'][k].append(a[k]-truth[k])
            for src,dst in [('kappa','kappa'),('cp','cp'),('cv','cv'),('maxwell','maxwell'),
                            ('scaledRecoveryCondition','condition')]:
                if src in a:summary[name][dst].append(a[src])
            if a['kappa']<=0 or a['cp']<=0 or a.get('cv',1)<=0:
                summary[name]['unstable'].append(dict(index=index,p=p,z=z,kappa=a['kappa'],cp=a['cp'],cv=a.get('cv')))
            row['candidates'][name]=a
        except (ValueError,FloatingPointError) as exc:
            failure=dict(index=index,p=p,z=z,error=str(exc));summary[name]['failures'].append(failure)
            row['candidates'][name]=dict(failure=str(exc))
    ts_errors.append(models['joint-pchip'].temperature(p,0)-(truth['T']+z));rows.append(row)
    if index and index%5000==0:print('Static EOS interior comparisons',index,flush=True)
for name,s in summary.items():
    s['errors']={k:stats(v) for k,v in s['errors'].items()}
    for k in ['kappa','cp','cv','maxwell','condition']:s[k]=stats(s[k])
    s['unstableCount']=len(s['unstable']);s['failureCount']=len(s['failures'])
save('interior.json',clean(dict(count=len(samples),coordinateTemperatureErrorK=stats(ts_errors),
                              summary=summary,rows=rows)))
print('Interior comparison completed',len(samples),flush=True)

# Property-coordinate recovery: EOS PH inputs; independently invert candidate;
# then EOS DU of candidate inventory isolates constitutive pressure error.
# Rejected raw-potential candidates get a bounded representative subset only.
phrows=[]
for p in [.3,.3029893712344606,.5,1.,2.5,3.5,8.,16.,32.65314902038559,35.]:
    for z in [.001,.01,.1,.5,1.,5.,15.,29.5]:
        if z>models['joint-pchip'].bounds(p)[1]:continue
        truth=reference(p,z);record=dict(p=p,z=z,EOS=truth,candidates={})
        for name,c in models.items():
            try:
                a=c.ph(p,truth['h']);f=flash(a['rho'],a['u'])
                record['candidates'][name]=dict(state=a,PHerrors={k:a[k]-truth[k] for k in truth},
                       EOSAtCandidateDU=f,pressureConstitutiveErrorBar=p-f['p'])
            except (ValueError,FloatingPointError) as exc:record['candidates'][name]=dict(failure=str(exc))
        phrows.append(record)
save('ph.json',clean(dict(count=len(phrows),rows=phrows)))
print('PH/independent DU comparisons completed',len(phrows),flush=True)

# Replay exact low-pressure common inventory from preserved evidence, and EOS
# inventory at the originally reported physical state. No new coupled execution.
old=json.loads((ROOT/'../ammonia-joint-property-evidence/conditioning.json').read_text())['points'][0]
low=dict(p=.3029893712344606,z=1.)
truth=reference(low['p'],low['z'])
pressures=sorted(set([.3,35.,low['p']]+[float(p) for p in P if p<=35]+
                    list(np.linspace(.3,.34,1601))))
root_rows=[]
for coordinates,rho,u in [('original-inventory',old['densityKgM3'],old['UKJkg']),
                           ('direct-EOS-inventory',truth['rho'],truth['u'])]:
    record=dict(coordinates=coordinates,rho=rho,u=u,EOSRecovery=flash(rho,u),candidates={})
    for name,c in models.items():
        roots=c.roots(rho,u,pressures)
        record['candidates'][name]=dict(rootsBar=roots,states=[c.at_density(p,rho) for p in roots])
    root_rows.append(record)
    print('Low-pressure root scan',coordinates,flush=True)

# PH -> M/U/V -> PH roundtrips at same candidate physical states. Root enumeration
# has finite brackets; dense local refinement at low pressure checks detection.
roundtrips=[]
for p,z in [(low['p'],1.),(.5,5.),(1.,.1),(3.5,15.),(8.,.5),(16.,5.),(32.65314902038559,.1)]:
    row=dict(p=p,z=z,candidates={})
    for name,c in models.items():
        a=c.at(p,z,derivatives=False)
        local=[q for q in np.linspace(max(.3,p*.97),min(35,p*1.03),201)]
        probes=sorted(set(pressures+local+[p]))
        roots=c.roots(a['rho'],a['u'],probes)
        phstate=c.ph(p,a['h'])
        row['candidates'][name]=dict(rootsBar=roots,rootStates=[c.at_density(q,a['rho']) for q in roots],
             PHroundtrip={k:phstate[k]-a[k] for k in ['p','T','h','rho','u']})
    roundtrips.append(row)
    print('Canonical uniqueness scan',p,z,flush=True)
save('roots.json',clean(dict(lowPressureEOS=truth,originalSurfaceRootsBar=old['tableRootsBar'],
                            lowPressure=root_rows,roundtrips=roundtrips,
                            searchPressuresBar=pressures)))

# Continuity across original grid interfaces in physical states and derivatives;
# potential C2 is structural for quintic patches, C1 for cubic, PCHIP C1 in each axis.
interfaces=[]
for i in [1,2,60,120,180,239]:
    p=float(P[i])
    for z in [.1,1.,5.5,15.]:
        row=dict(i=i,p=p,z=z,candidates={})
        for name,c in models.items():
            sides=[]
            for delta in [-1e-10,1e-10]:
                try:sides.append(c.at(p*np.exp(delta),z))
                except ValueError:sides.append(None)
            if all(sides):row['candidates'][name]={k:sides[1].get(k,0)-sides[0].get(k,0)
                  for k in ['T','h','rho','u','cp','kappa']}
        interfaces.append(row)
save('continuity.json',clean(interfaces))

# Equivalent static PT workload; build and EOS costs excluded. Warm-up and five
# interleaved rounds, alternating order. This is Python prototype performance.
workload=[(float(np.exp(X[i]+.4*(X[i+1]-X[i]))),float(z))
          for i in [1,60,120,180,239] for z in [.1,.5,1.,5.,10.,15.]]
for c in models.values():
    for p,z in workload:c.at(p,z,derivatives=False)
timings=[]
for pair in range(5):
    names=list(models)
    if pair%2:names.reverse()
    for name in names:
        t=time.perf_counter();checksum=0.
        for repeat in range(10):
            for p,z in workload:checksum+=models[name].at(p,z,derivatives=False)['rho']
        timings.append(dict(pair=pair,method=name,seconds=time.perf_counter()-t,
                            evaluations=10*len(workload),checksum=checksum))
save('performance.json',clean(dict(construction=construction,staticTimings=timings,
                         workload=workload,peakProcessRSSKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)))
save('summary.json',clean(dict(completed=True,staticOnly=True,candidateQualified=False,
      versions=dict(Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__,
                    CoolProp=CoolProp.__version__,platform=platform.platform()),
      sourceHash=hashlib.sha256((ROOT/'properties.json').read_bytes()).hexdigest(),
      counts=dict(knots=len(knots),interior=len(rows),PH=len(phrows)),
      knotStats=knotstats,interiorSummary=summary,
      saturationCoordinateErrorK=stats(ts_errors),lowPressure=root_rows)))
print('STATIC ONLY completed; candidates remain unqualified',flush=True)
