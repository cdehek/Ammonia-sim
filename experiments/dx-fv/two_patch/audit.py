"""Independent evidence audit; PASS here does not qualify the rejected model."""
import hashlib,json,math,subprocess,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
import mpmath as mp
from model import BASE,ROOT,TERMS,load
from certify import Q
E=BASE/'evidence';mp.mp.dps=65
read=lambda f:json.loads((E/f).read_text())
save=lambda f,d:(E/f).write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
models=load();D=json.loads((ROOT/'properties.json').read_text());DEC=json.loads((ROOT/'properties.json').read_text(),parse_float=F)
start=time.perf_counter();prov=read('provenance.json')
for p,h in prov['preservedFiles'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
assert subprocess.check_output(['git','merge-base','5318173b49719e263c2adda214a222a9c0533a47','HEAD'],cwd=ROOT,text=True).strip()=='5318173b49719e263c2adda214a222a9c0533a47'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='research/gibbs-two-patch-feasibility-20261012'
for ref,want in [('origin/main','0473d32f62db992fde0f581d116e1bd0c8e7d8ed'),('origin/v0.5.5-stage-1','d4422425750a1d3c4e432cc103ac42ead40b7cc6'),('origin/experimental/dx-fv-stage-3','be9eb35a4ddf5098e685182f8104685127c6a6ee'),('origin/wip/dx-fv-stage2b-property-research-20261012','5318173b49719e263c2adda214a222a9c0533a47')]:
    assert subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip()==want
h=hashlib.sha256((E/'candidate.json').read_bytes()).hexdigest()
assert h==read('freeze.json')['candidateSHA256']==read('certificate.json')['candidateSHA256']==read('validation.json')['candidateSHA256']
assert h==(E/'candidate.sha256').read_text().split()[0]
for f in ['fit.py','model.py','validate.py']:
    assert hashlib.sha256((BASE/f).read_bytes()).hexdigest()==read('freeze.json')['codeSHA256'][f],f
# certify.py only received an added conservative product-roundoff term after
# first validation. Candidate, fitter, model and holdout code remain frozen.
assert all(r['stabilityCertified'] and r['uniqueCanonicalRecoveryOnImage'] for r in read('certificate.json')['patches'].values())

# Exact rational interval audit independent of numerical optimizer tolerances.
def exact_state(c,p,T):
    x=(p-Q(c.pc))/Q(c.ps);y=(T-Q(c.tc))/Q(c.ts)
    def der(a,b):return sum(Q(v)*F(math.factorial(i),math.factorial(i-a))*F(math.factorial(j),math.factorial(j-b))*x**(i-a)*y**(j-b)/Q(c.ps)**a/Q(c.ts)**b for (i,j),v in zip(TERMS,c.c) if i>=a and j>=b)
    g=der(0,0);gt=der(0,1);gp=der(1,0)
    return dict(g=g,h=g-T*gt,s=-gt,rho=100/gp,gp=gp)
exact_knots=[]
for n,c in models.items():
    for i in c.d['rows']:
        p=Q(D['p'][i]);x=(p-Q(c.pc))/Q(c.ps);T=sum(Q(v)*x**k for k,v in enumerate(c.satc));Tsource=DEC['sat'][i][0]+F(27315,100)
        for z in range(c.zmax+1):
            a=exact_state(c,p,T-z);diff=dict(T=T-Tsource,**{k:a[k]-v for k,v in zip(['h','s','rho'],DEC['liquid'][i][z])})
            inside=all(abs(v)<=(F(5,10**9) if k=='T' else F(5,10**8)) for k,v in diff.items());assert inside,(n,i,z)
            exact_knots.append(dict(patch=n,row=i,z=z,phase='liquid',deviations={k:float(v) for k,v in diff.items()},exactRationalIntervalsPass=inside))
        a=exact_state(c,p,T);sv=sum(Q(v)*x**k for k,v in enumerate(c.svc));sp=sum(k*Q(v)*x**(k-1)/Q(c.ps) for k,v in enumerate(c.satc) if k)
        values=[a['g']+T*sv,sv,100/(a['gp']+sp*(sv-a['s']))]
        diff={k:v-source for k,v,source in zip(['h','s','rho'],values,DEC['sat'][i][4:7])};assert all(abs(v)<=F(5,10**8) for v in diff.values())
        exact_knots.append(dict(patch=n,row=i,phase='vapor-boundary',deviations={k:float(v) for k,v in diff.items()},exactRationalIntervalsPass=True))
save('exact-interval-audit.json',dict(arithmetic='fractions.Fraction; exact for exported binary64 model and decimal source rounding intervals',rows=exact_knots,allPass=True))

# Independent high-precision recovery. Certified monotonicity makes endpoint
# signs conclusive on the canonical image; successful local Newton is not used
# as a uniqueness proof. No value, coefficient or constraint is refitted.
def mstate(c,p,T):
    x=(p-mp.mpf(c.pc))/mp.mpf(c.ps);y=(T-mp.mpf(c.tc))/mp.mpf(c.ts)
    g=mp.mpf(0);gp=mp.mpf(0);gt=mp.mpf(0)
    for (i,j),v in zip(TERMS,c.c):
        a=mp.mpf(v);g+=a*x**i*y**j
        if i:gp+=i*a*x**(i-1)*y**j/mp.mpf(c.ps)
        if j:gt+=j*a*x**i*y**(j-1)/mp.mpf(c.ts)
    return dict(rho=100/gp,u=g-T*gt-p*gp,h=g-T*gt,T=T,p=p)
def msat(c,p):
    x=(p-mp.mpf(c.pc))/mp.mpf(c.ps)
    return mp.fsum(mp.mpf(v)*x**i for i,v in enumerate(c.satc))
def mp_recovery(c,rho,u):
    rho=mp.mpf(rho);u=mp.mpf(u);lo=mp.mpf(D['p'][c.d['rows'][0]]);hi=mp.mpf(D['p'][c.d['rows'][-1]])
    def hot(p):return mstate(c,p,msat(c,p))['rho']-rho
    def cold(p):return mstate(c,p,msat(c,p)-c.zmax)['rho']-rho
    if hot(hi)>0 or cold(lo)<0:return dict(status='outside-density-image')
    def solve(f,l,r):
        return mp.findroot(f,(l,r),solver='anderson',tol=mp.mpf('1e-50'),maxsteps=150)
    if hot(lo)>0:lo=solve(hot,lo,hi)
    if cold(hi)<0:hi=solve(cold,lo,hi)
    def at(p):
        ts=msat(c,p);l=ts-c.zmax;r=ts
        tt=solve(lambda T:mstate(c,p,T)['rho']-rho,l,r)
        return mstate(c,p,tt)
    al=at(lo);ah=at(hi);fl=al['u']-u;fh=ah['u']-u
    output=dict(pressureInterval=[float(lo),float(hi)],energyEndpointResiduals=[float(fl),float(fh)])
    if fl>0 or fh<0:return dict(**output,status='outside-energy-image')
    pp=solve(lambda p:at(p)['u']-u,lo,hi);a=at(pp)
    return dict(**output,status='unique-in-domain',state={k:float(v) for k,v in a.items()},
                energyResidual=float(a['u']-u),densityResidual=float(a['rho']-rho),subcoolingK=float(msat(c,pp)-a['T']))

failures=[]
for r in read('holdouts.json')['rows']:
    if 'recoveryFailure' not in r:continue
    c=models[r['patch']];truth=r['EOS'];V=.003;M=truth['rho']*V;U=M*truth['u']
    a=mp_recovery(c,M/V,U/M)
    failures.append(dict(patch=r['patch'],p=r['p'],zEOS=r['zEOS'],originalFailure=r['recoveryFailure'],independentRecovery=a))
    assert a['status']!='unique-in-domain',('Diagnostic inversion defect',failures[-1])
print('All failed holdouts independently classified',len(failures),flush=True)
save('failed-recovery-audit.json',dict(mpDigits=mp.mp.dps,rows=failures,interpretation='Certified monotonicity plus independently computed nonzero endpoint signs. Numeric signs have large margins relative to 65-digit evaluation; not a formal interval root enclosure.'))

saved=[]
for r in read('probes.json')['rows']:
    if 'original' in r:
        q=r['original'];saved.append(dict(name=r['name'],originalInventory=dict(rho=q['rho'],u=q['u']),independentRecovery=mp_recovery(models['high'],q['rho'],q['u'])))
save('saved-inventory-audit.json',dict(rows=saved))

# Validate actual successful roots and theorem-based same-candidate roundtrips.
root_checks=[]
for n,c in models.items():
    for f in [.1,.3,.5,.7,.9]:
        p=D['p'][c.d['rows'][0]]+f*(D['p'][c.d['rows'][-1]]-D['p'][c.d['rows'][0]])
        for z in [.1*c.zmax,.5*c.zmax,.9*c.zmax]:
            a=c.at_z(p,z);r=c.recover(a['rho'],a['u']);ph=c.ph(p,a['h'])
            assert abs(r['densityResidual'])<1e-7 and abs(r['energyResidual'])<1e-7
            assert abs((r['p']-p)*1e5)<1e-3
            root_checks.append(dict(patch=n,p=p,z=z,canonicalErrors={k:r[k]-a[k] for k in ['p','T','h','rho','u']},PHerrors={k:ph[k]-a[k] for k in ['p','T','h','rho','u']}))
save('roundtrip-audit.json',dict(rows=root_checks,uniquenessEstablishedBy='certificate plus connected isochore theorem in report, not these roundtrips'))

# Selected witnesses: replay rejects the same candidate at 65-digit precision.
witnesses=[]
for n in models:
    r=max((r for r in read('holdouts.json')['rows'] if r['patch']==n and 'recoveryErrors' in r),key=lambda r:abs(r['recoveryErrors']['pressurePa']))
    v=r['inventory'];a=mp_recovery(models[n],v['Mkg']/v['Vm3'],v['UkJ']/v['Mkg'])
    assert a['status']=='unique-in-domain'
    err=(a['state']['p']-r['p'])*1e5;assert abs(err)>10
    witnesses.append(dict(patch=n,p=r['p'],zEOS=r['zEOS'],inventory=v,EOS=r['EOS'],independentRecovery=a,pressureErrorPa=err))
save('rejection-witnesses.json',dict(candidateSHA256=h,rows=witnesses,classification='Chosen construction rejected'))

# Strict rejection remains. No other file or protected branch was changed.
summary=dict(evidenceAuditPassed=True,candidateQualified=False,classification='Chosen construction rejected',
    sourceFilesPreserved=len(prov['preservedFiles']),exactSourceIntervalsPass=True,
    stabilityCertificatesPass=True,canonicalInjectivityCertifiedSeparatelyPerPatch=True,
    independentPressureWitnessesPa={r['patch']:r['pressureErrorPa'] for r in witnesses},
    failedRecoveryCount=len(failures),failedRecoveriesAllOutsideCandidateImage=True,
    sameCandidateRoundtrips=len(root_checks),candidateSHA256=h,seconds=time.perf_counter()-start)
save('audit.json',summary);print(json.dumps(summary,indent=2),flush=True)
