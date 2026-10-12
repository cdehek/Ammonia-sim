"""Holdout direct EOS audit. Never calls fit; verifies frozen candidate hash first."""
import ast,hashlib,json,math,platform,resource,time
from pathlib import Path
import numpy as np
import scipy
import mpmath as mp
from scipy.optimize import brentq
from model import BASE,ROOT,TERMS,load

E=BASE/'evidence';candidate=E/'candidate.json'
expected=(E/'candidate.sha256').read_text().split()[0]
assert hashlib.sha256(candidate.read_bytes()).hexdigest()==expected
assert not (E/'validation.json').exists(), 'Use a separate evidence copy for replay; retain first holdout result'
freeze=dict(candidateSHA256=expected,codeSHA256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.glob('*.py')},
    validationStartUnix=time.time(),holdoutDesign='Each cell: pressure fractions .07,.25,.5,.75,.93; offsets 1e-6,.001,.01,.1,.25,.5,.75,.99,1,1.25,1.5,1.75,1.999999 as supported; row interfaces and boundaries; both saved high PH states and low inventories.',
    fitNotRetunedAfterEOS=True,limits=dict(pressurePaStrict=10,temperatureKStrict=.01,enthalpyKJkgStrict=.05))
(E/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
# First EOS import occurs only after coefficients and the freeze manifest exist.
import CoolProp
from CoolProp import AbstractState,PT_INPUTS,PQ_INPUTS,DmassUmass_INPUTS,DmassT_INPUTS,HmassP_INPUTS,iphase_liquid,iDmass,iP,iT,iHmass
assert CoolProp.__version__=='7.2.0'
models=load();D=json.loads((ROOT/'properties.json').read_text());mp.mp.dps=70

def clean(v):
    if isinstance(v,dict):return {k:clean(w) for k,w in v.items()}
    if isinstance(v,(list,tuple)):return [clean(w) for w in v]
    if isinstance(v,(np.integer,)):return int(v)
    if isinstance(v,(float,np.floating)):return float(v) if np.isfinite(v) else None
    return v

def save(name,obj):(E/name).write_text(json.dumps(clean(obj),indent=2,allow_nan=False)+'\n')
def state(a):
    return dict(p=a.p()/1e5,T=a.T(),h=a.hmass()/1000,s=a.smass()/1000,rho=a.rhomass(),u=a.umass()/1000,cp=a.cpmass()/1000,cv=a.cvmass()/1000,
                kappa=1e5*a.isothermal_compressibility(),rhoP=1e5*a.first_partial_deriv(iDmass,iP,iT),rhoT=a.first_partial_deriv(iDmass,iT,iP))
eos=AbstractState('HEOS','Ammonia');sat=AbstractState('HEOS','Ammonia');alt=AbstractState('HEOS','Ammonia');flash=AbstractState('HEOS','Ammonia')
def ref(p,z=None,h=None):
    sat.update(PQ_INPUTS,p*1e5,0);Ts=sat.T()
    if h is not None:
        eos.unspecify_phase();eos.update(HmassP_INPUTS,h*1000,p*1e5)
    elif z==0:eos.unspecify_phase();eos.update(PQ_INPUTS,p*1e5,0)
    else:eos.specify_phase(iphase_liquid);eos.update(PT_INPUTS,p*1e5,Ts-z)
    q=state(eos);q['TsEOS']=Ts;q['inputPressureBar']=p
    return q

def mp_at(c,p,T):
    p=mp.mpf(p);T=mp.mpf(T);x=(p-mp.mpf(c.pc))/mp.mpf(c.ps);y=(T-mp.mpf(c.tc))/mp.mpf(c.ts)
    def der(a,b):return mp.fsum(mp.mpf(v)*math.factorial(i)/math.factorial(i-a)*math.factorial(j)/math.factorial(j-b)*x**(i-a)*y**(j-b)/mp.mpf(c.ps)**a/mp.mpf(c.ts)**b for (i,j),v in zip(TERMS,c.c) if i>=a and j>=b)
    g=der(0,0);gp=der(1,0);gt=der(0,1);pp=der(2,0);pt=der(1,1);tt=der(0,2);h=g-T*gt
    return dict(p=p,T=T,h=h,s=-gt,rho=100/gp,u=h-p*gp,g=g,gp=gp,gpp=pp,gpt=pt,gtt=tt,cp=-T*tt,cv=-T*(tt-pt*pt/pp),kappa=-pp/gp)
def mp_sat(c,p):
    x=(mp.mpf(p)-mp.mpf(c.pc))/mp.mpf(c.ps)
    return mp.fsum(mp.mpf(a)*x**i for i,a in enumerate(c.satc))

# Every source interval, independently in high precision using decimal source
# centers. Temperature perturbation is shared by ALL offsets in a pressure row.
exact=json.loads((ROOT/'properties.json').read_text(),parse_float=mp.mpf)
knots=[]
for name,c in models.items():
    for i in c.d['rows']:
        p=D['p'][i];T0=mp_sat(c,p);Tsource=exact['sat'][i][0]+mp.mpf('273.15')
        for z in range(c.zmax+1):
            q=mp_at(c,p,T0-z);h,s,r=exact['liquid'][i][z]
            delta={k:float(q[k]-v) for k,v in [('h',h),('s',s),('rho',r)]};delta['T']=float(T0-Tsource)
            truth=ref(p,z);num=c.at_z(p,z)
            knots.append(dict(patch=name,row=i,z=z,deviations=delta,withinActualIntervals=all(abs(v)<=(5e-9 if k=='T' else 5e-8) for k,v in delta.items()),
                sourceEOSErrors={k:float(v-mp.mpf(truth[k])) for k,v in [('h',h),('s',s),('rho',r),('T',Tsource-z)]},
                evaluationErrors={k:float(mp.mpf(num[k])-q[k]) for k in q if k in num}))
        f=mp_at(c,p,T0);x=(mp.mpf(p)-mp.mpf(c.pc))/mp.mpf(c.ps);sv=mp.fsum(mp.mpf(a)*x**i for i,a in enumerate(c.svc))
        sp=mp.fsum(i*mp.mpf(a)*x**(i-1)/mp.mpf(c.ps) for i,a in enumerate(c.satc) if i)
        hv=f['g']+T0*sv;rv=100/(f['gp']+sp*(sv-f['s']))
        delta={k:float(v-exact['sat'][i][j]) for k,v,j in [('h',hv,4),('s',sv,5),('rho',rv,6)]}
        knots.append(dict(patch=name,row=i,z=0,phase='vapor-boundary',deviations=delta,withinActualIntervals=all(abs(v)<=5e-8 for v in delta.values())))
save('knots.json',dict(liquidCount=16,vaporBoundaryCount=6,allIntervalsPass=all(q['withinActualIntervals'] for q in knots),rows=knots))

rows=[];reference_checks=[];mp_checks=[];satrows=[];interfaces=[]
for name,c in models.items():
    P=[D['p'][i] for i in c.d['rows']]
    pts=[]
    offsets=[1e-6,.001,.01,.1,.25,.5,.75,.99,1.,1.25,1.5,1.75,1.999999]
    offsets=[z for z in offsets if z<c.zmax]+[c.zmax-1e-6]
    for a,b in zip(P[:-1],P[1:]):
        for f in [.07,.25,.5,.75,.93]:
            for z in sorted(set(offsets)):pts.append((a+f*(b-a),z,'interior-or-saturation-approach'))
    for p in P:
        for z in [1e-6,.1,.5,c.zmax-1e-6]:pts.append((p,z,'pressure-row-interface-or-edge'))
    for index,(p,z,kind) in enumerate(pts):
        truth=ref(p,z);row=dict(patch=name,p=p,zEOS=z,kind=kind,EOS=truth)
        try:
            a=c.at(p,truth['T']);row['candidatePT']=a;row['PTerrors']={k:a[k]-truth[k] for k in ['h','rho','u','s','cp','cv','kappa']}
            row['stable']=a['v']>0 and a['kappa']>0 and a['cp']>0 and a['cv']>0
        except ValueError as exc:row['PTfailure']=str(exc)
        try:
            # Explicit canonical inventory with fixed volume. Intensive rho/u
            # equivalence is exact; no trajectory or heat transfer is run.
            V=.003;M=truth['rho']*V;U=M*truth['u'];a=c.recover(M/V,U/M)
            row['inventory']=dict(Mkg=M,UkJ=U,Vm3=V);row['recovered']=a
            row['recoveryErrors']=dict(pressurePa=(a['p']-p)*1e5,T=a['T']-truth['T'],h=a['h']-truth['h'])
        except ValueError as exc:row['recoveryFailure']=str(exc)
        rows.append(row)
        if index%17==0:
            # Numerical reference check: independent input pairs/algorithms in
            # the SAME HEOS model, not an independent physical EOS uncertainty.
            alt.specify_phase(iphase_liquid);alt.update(DmassT_INPUTS,truth['rho'],truth['T']);r=state(alt)
            nr=dict(patch=name,p=p,z=z,DTminusPT={k:r[k]-truth[k] for k in ['p','T','h','u','rho','cp','cv']},prescribedPressureResidualPa=(truth['p']-p)*1e5)
            try:
                flash.unspecify_phase();flash.update(DmassUmass_INPUTS,truth['rho'],truth['u']*1000);q=state(flash)
                nr['DUminusPT']={k:q[k]-truth[k] for k in ['p','T','h','u','rho']}
            except ValueError as exc:nr['DUfailure']=str(exc)
            hp=100*eos.first_partial_deriv(iHmass,iP,iT)
            nr['maxwell']=hp-100*(1/truth['rho']+truth['T']*truth['rhoT']/truth['rho']**2)
            reference_checks.append(nr)
            if 'candidatePT' in row:
                q=mp_at(c,p,truth['T']);mp_checks.append(dict(patch=name,p=p,z=z,evaluationErrors={k:float(mp.mpf(row['candidatePT'][k])-q[k]) for k in q if k in row['candidatePT']}))
            if 'recovered' in row:
                a=row['recovered'];rr=mp.mpf(M/V);uu=mp.mpf(U/M)
                def residual(pp,TT):
                    q=mp_at(c,pp,TT);return q['rho']-rr,q['u']-uu
                pp,TT=mp.findroot(residual,(mp.mpf(a['p']),mp.mpf(a['T'])),tol=mp.mpf('1e-55'))
                q=mp_at(c,pp,TT)
                mp_checks.append(dict(patch=name,p=p,z=z,recoveryNumericalErrors=dict(pressurePa=float((mp.mpf(a['p'])-pp)*1e5),T=float(mp.mpf(a['T'])-TT),h=float(mp.mpf(a['h'])-q['h']))))
    # Saturation compatibility all along boundary, independent vapor EOS too.
    for p in np.linspace(P[0],P[-1],41):
        f=c.at_z(float(p),0);v=c.vapor(float(p));sat.update(PQ_INPUTS,p*1e5,0);ef=state(sat);sat.update(PQ_INPUTS,p*1e5,1);ev=state(sat)
        satrows.append(dict(patch=name,p=p,temperatureErrorK=f['T']-ef['T'],liquidErrors={k:f[k]-ef[k] for k in ['h','s','rho','g'] if k in ef},
            vaporErrors={k:v[k]-ev[k] for k in ['h','s','rho']},gibbsMismatch=v['g']-f['g'],latentMismatch=(v['h']-f['h'])-f['T']*(v['s']-f['s']),
            clapeyronMismatch=c.saturation(p,1)-100*f['T']*(v['v']-f['v'])/(v['h']-f['h']),latentH=v['h']-f['h']))
    # One polynomial has no internal interface branches. Numerical side probes
    # at physical T distinguish O(epsilon) variation from a finite jump.
    for p in P[1:-1]:
        for z in [.25,1.,1.75]:
            for eps in [1e-7,1e-9]:
                T=c.saturation(p)-z;a=c.at(p-eps,T);b=c.at(p+eps,T)
                interfaces.append(dict(patch=name,p=p,z=z,epsilonBar=eps,sideDifferences={k:b[k]-a[k] for k in ['g','h','s','rho','u','cp','cv','kappa']}))
    if c.zmax==2:
        for f in [.2,.5,.8]:
            p=P[0]+f*(P[-1]-P[0]);T=c.saturation(p)-1
            for eps in [1e-7,1e-9]:
                a=c.at(p,T-eps);b=c.at(p,T+eps)
                interfaces.append(dict(patch=name,p=p,z=1,epsilonK=eps,sideDifferences={k:b[k]-a[k] for k in ['g','h','s','rho','u','cp','cv','kappa']}))
    print('EOS holdout completed',name,len(pts),flush=True)
save('holdouts.json',dict(rows=rows));save('saturation.json',dict(rows=satrows));save('numerical-uncertainty.json',dict(referenceChecks=reference_checks,highPrecisionCandidateChecks=mp_checks,mpDigits=mp.mp.dps,physicalEOSModelUncertainty='Not supplied by CoolProp; no independent experimental uncertainty is claimed.'));save('continuity.json',dict(structural='single physical polynomial C-infinity inside each assembly; disconnected patches not joined',rows=interfaces))

# Reuse original mathematical surface by parsing only its class definition.
# Historical source remains byte-identical; no old script side effects/EOS fit.
source=ROOT/'experiments/dx-fv/joint_property_analysis.py';tree=ast.parse(source.read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ExistingSurface')
ns=dict(np=np,math=math,DATA=D,brentq=brentq);exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns);old=ns['ExistingSurface']()
def scan_original(rho,u,lo,hi):
    roots=[];last=None
    for p in np.linspace(lo,hi,4001):
        try:a=old.from_density(float(p),rho);f=a['u']-u
        except AssertionError:last=None;continue
        if last and f*last[1]<0:
            p0=brentq(lambda q:old.from_density(q,rho)['u']-u,last[0],float(p),xtol=5e-15,rtol=1e-15);r=old.from_density(p0,rho)
            if abs(r['u']-u)<1e-7 and abs(r['rho']-rho)<1e-7 and all(abs(p0-q['p'])>1e-8 for q in roots):roots.append(r)
        last=(float(p),f)
    return roots
probes=[]
lowp=.3029893712344606;q=ref(lowp,1)
for label,rho,u in [('original-multiple-root-inventory',708.6710262223568,94.48059153610271),('matching-independent-EOS-inventory',q['rho'],q['u'])]:
    row=dict(name=label,patch='low',rho=rho,u=u,originalRoots=scan_original(rho,u,.3,.3183890254214986))
    flash.unspecify_phase();flash.update(DmassUmass_INPUTS,rho,u*1000);truth=state(flash);row['EOS']=truth
    try:
        a=models['low'].recover(rho,u);row['candidate']=a;row['errors']=dict(pressurePa=(a['p']-truth['p'])*1e5,T=a['T']-truth['T'],h=a['h']-truth['h'])
    except ValueError as exc:row['failure']=str(exc)
    probes.append(row)
# Both saved high-pressure problematic states: initial and 0.1-s endpoint,
# evaluated statically at PH and at unchanged original inventories.
for label,p,h in [('saved-high-initial',32.65314902038559,686.779725665),('saved-high-endpoint',32.80473738460169,686.845872427996)]:
    truth=ref(p,h=h);ori=old.from_ph(p,h);row=dict(name=label,patch='high',p=p,h=h,EOSAtPH=truth,original=ori)
    try:
        a=models['high'].ph(p,h);flash.unspecify_phase();flash.update(DmassUmass_INPUTS,a['rho'],a['u']*1000);rt=state(flash)
        row.update(candidatePH=a,EOSAtCandidateInventory=rt,inventoryEquivalentPressureErrorPa=(p-rt['p'])*1e5)
        b=models['high'].recover(truth['rho'],truth['u']);row['candidateAtEOSInventory']=b;row['forwardErrors']=dict(pressurePa=(b['p']-p)*1e5,T=b['T']-truth['T'],h=b['h']-truth['h'])
        flash.unspecify_phase();flash.update(DmassUmass_INPUTS,ori['rho'],ori['u']*1000);rt=state(flash);b=models['high'].recover(ori['rho'],ori['u'])
        row['originalInventoryComparison']=dict(candidate=b,EOS=rt,errors=dict(pressurePa=(b['p']-rt['p'])*1e5,T=b['T']-rt['T'],h=b['h']-rt['h']))
    except ValueError as exc:row['failure']=str(exc)
    probes.append(row)
save('probes.json',dict(rows=probes,rootUniqueness='candidate injectivity follows only where certificate succeeds; original finite scans establish multiple roots, not exhaustiveness'))

# Repeated same workload, no EOS in timed path. Single process Python prototype.
timings=[]
for name,c in models.items():
    work=[(r['p'],r['EOS']['T']) for r in rows if r['patch']==name and 'candidatePT' in r][:100]
    for _ in range(5):
        t=time.perf_counter();checksum=sum(c.at(p,T)['rho'] for p,T in work)
        timings.append(dict(patch=name,evaluations=len(work),seconds=time.perf_counter()-t,checksum=checksum))
summary={}
for name in models:
    rr=[r for r in rows if r['patch']==name];valid=[r for r in rr if 'recoveryErrors' in r]
    maxrec={k:max(abs(r['recoveryErrors'][k]) for r in valid) for k in ['pressurePa','T','h']}
    summary[name]=dict(holdoutCount=len(rr),recoverySuccess=len(valid),recoveryFailures=len(rr)-len(valid),maxRecoveryErrors=maxrec,
        maxPTerrors={k:max(abs(r['PTerrors'][k]) for r in rr if 'PTerrors' in r) for k in ['h','rho','u','s','cp','cv','kappa']},
        pressureGatePass=maxrec['pressurePa']<10,temperatureGatePass=maxrec['T']<.01,enthalpyGatePass=maxrec['h']<.05,
        sampledStabilityFailures=sum(not r.get('stable',False) for r in rr),maxCondition=max(r['candidatePT']['condition'] for r in rr if 'candidatePT' in r))
save('performance.json',dict(timings=timings,coefficientBytes={n:c.c.nbytes+c.satc.nbytes+c.svc.nbytes for n,c in models.items()},peakRSSKiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
save('validation.json',dict(candidateSHA256=expected,summary=summary,classification='Chosen construction rejected' if any(not r['pressureGatePass'] or not r['temperatureGatePass'] or not r['enthalpyGatePass'] or r['sampledStabilityFailures'] for r in summary.values()) else 'Inconclusive pending full audit',qualified=False,
    versions=dict(Python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,CoolProp=CoolProp.__version__,mpmath=mp.__version__),strictLimits=freeze['limits'],noCoupledTrajectoryQualification=True))
print(json.dumps(summary,indent=2),flush=True)
