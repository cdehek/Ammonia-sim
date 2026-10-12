"""Audit static research evidence; passing this audit does NOT qualify candidates."""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
import numpy as np
from CoolProp.CoolProp import PropsSI
from static_property_reconstruction import ROOT,P,X,Z,SAT,F,VALID,candidates

E=Path(sys.argv[1]).resolve();assert not E.is_relative_to(ROOT)
load=lambda name:json.loads((E/name).read_text())
manifest=load('preserved-files.json')
for name,digest in manifest.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='be9eb35a4ddf5098e685182f8104685127c6a6ee'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='experimental/dx-fv-stage-3'
allowed=['static_property_reconstruction.py','static_property_qualification.py',
         'static_property_diagnostics.py','audit_static_properties.py','STATIC_PROPERTY_RECONSTRUCTION.md']
files=subprocess.check_output(['git','ls-files','-co','--exclude-standard'],cwd=ROOT,text=True).splitlines()
new=sorted(set(files)-set(manifest))
assert new==sorted('experiments/dx-fv/'+name for name in allowed),new
K=load('knots.json');I=load('interior.json');S=load('summary.json');R=load('roots-refined.json')
B=load('baseline.json');PH=load('ph.json');BP=load('baseline-ph.json');SATURATION=load('saturation.json')
assert S['completed'] and S['staticOnly'] and not S['candidateQualified']
assert K['count']==int(VALID.sum())==7234 and I['count']==30006 and PH['count']==77
for k,s in K['sourceRoundingAgainstEOS'].items():assert s['maximumAbsolute']<=(5e-9 if k=='T' else 5e-8),k
for name,summary in K['summary'].items():
    for k,s in summary.items():
        # Only floating evaluation roundoff at an already demonstrated interval
        # endpoint: one ulp-scale allowance, not a scientific budget change.
        allowance=5e-9 if k=='T' else 5e-8
        assert s['maximumAbsolute']<=allowance+5e-16,k
assert I['summary']['joint-pchip']['failureCount']==0
assert I['summary']['joint-pchip']['kappa']['minimum']>0
assert I['summary']['joint-pchip']['maxwell']['maximumAbsolute']>1e-4
for name in ['gibbs-bicubic','gibbs-biquintic','gibbs-rounded-projection']:
    s=I['summary'][name]
    assert s['maxwell']['maximumAbsolute']<1e-13
    assert s['kappa']['minimum']<0 and s['cv']['minimum']<0
assert B['summary']['negativeCompressibility']>0
assert max(abs(r['temperatureErrorK']) for r in SATURATION['rows'])<1e-8
assert all(r['coordinateSlopeKBar']>0 and r['inKnotTemperatureRange'] for r in SATURATION['rows'])
root_counts={}
for row in R['rows']:
    root_counts[row['coordinates']]={}
    for name,v in row['candidates'].items():
        assert all(.3<=p<=35 for p in v['rootsBar'])
        assert all(abs(x)<1e-7 for x in v['energyResidualsKJkg'])
        valid=[r for r in v['bracketChecks'] if r['validated']]
        assert all(abs(r['densityResidualKgM3'])<1e-7 and abs(r['energyResidualKJkg'])<1e-7 for r in valid)
        assert len(valid)==len(v['rootsBar'])
        root_counts[row['coordinates']][name]=dict(validatedRoots=len(v['rootsBar']),
                   rejectedBrackets=sum(not r['validated'] for r in v['bracketChecks']))
    assert len(row['candidates']['gibbs-rounded-projection']['rootsBar'])>1
    assert len(row['candidates']['joint-pchip']['rootsBar'])==1

# Direct EOS identities and response functions at independently evaluated PT.
models=candidates();checks=[]
for p,z in [(.3029893712344606,1.),(1.,.1),(3.5,10.),(32.65314902038559,.1)]:
    Ts=PropsSI('T','P',p*1e5,'Q',0,'Ammonia');T=Ts-z
    rho=PropsSI('Dmass','P',p*1e5,'T',T,'Ammonia')
    rp=1e5*PropsSI('d(Dmass)/d(P)|T','P',p*1e5,'T',T,'Ammonia')
    rt=PropsSI('d(Dmass)/d(T)|P','P',p*1e5,'T',T,'Ammonia')
    hp=100*PropsSI('d(Hmass)/d(P)|T','P',p*1e5,'T',T,'Ammonia')
    mismatch=hp-100*(1/rho+T*rt/rho**2)
    assert abs(mismatch)<1e-10 and rp>0
    q=dict(p=p,z=z,EOS=dict(rho=rho,kappa=rp/rho,maxwell=mismatch),candidates={})
    for name,c in models.items():
        a=c.at(p,c.temperature(p,0)-T);q['candidates'][name]={k:a[k] for k in ['rho','kappa','cp','maxwell']}
        if 'cv' in a:q['candidates'][name]['cv']=a['cv']
    checks.append(q)

# Domain rejection, supported edge values, and missing cold-grid masking.
for name,c in models.items():
    for p,z in [(.299,1),(35.001,1),(.3,-.001),(.3,30.001),(35,30.001)]:
        try:c.at(p,z,derivatives=False)
        except ValueError:pass
        else:raise AssertionError((name,'unsupported state admitted',p,z))
    for p,z in [(.3,0.),(.3,c.bounds(.3)[1]),(35.,0.),(35.,30.)]:
        a=c.at(p,z,derivatives=False);assert all(math.isfinite(a[k]) for k in ['T','h','rho','u'])

# Roundtrip results are revalidated, not inferred from a converged root bracket.
roundtrip=[]
for row in load('roots.json')['roundtrips']:
    q=dict(p=row['p'],z=row['z'],candidates={})
    for name,v in row['candidates'].items():
        target=models[name].at(row['p'],row['z'],derivatives=False)
        valid=[s for s in v['rootStates'] if abs(s['u']-target['u'])<1e-7 and abs(s['rho']-target['rho'])<1e-7]
        start_recovered=any(abs(s['p']-row['p'])<1e-7 for s in valid)
        if name in ['joint-pchip','gibbs-rounded-projection']:assert start_recovered
        assert abs(v['PHroundtrip']['T'])<1e-8 and abs(v['PHroundtrip']['h'])<1e-7
        try:
            same_pressure=models[name].at_density(row['p'],target['rho'])
            same_pressure_error=same_pressure['u']-target['u'];density_failure=None
        except ValueError as error:
            # Rejected raw fits can fold their density curve: an interior state
            # exists but endpoint bracketing cannot recover it. Record the defect.
            assert name in ['gibbs-bicubic','gibbs-biquintic']
            same_pressure_error=None;density_failure=str(error)
        q['candidates'][name]=dict(validatedRoots=len(valid),startingStateRecovered=start_recovered,
             samePressureDensityInversionEnergyErrorKJkg=same_pressure_error,
             densityInversionFailure=density_failure,
             PHroundtrip=v['PHroundtrip'])
    roundtrip.append(q)

pressure={}
for name in models:
    values=[r['candidates'][name]['pressureConstitutiveErrorBar'] for r in PH['rows']
            if 'failure' not in r['candidates'][name]]
    pressure[name]=dict(count=len(values),maximumAbsoluteBar=max(abs(x) for x in values))
    assert pressure[name]['maximumAbsoluteBar']>1e-4

# Model arrays separately from the large JSON/independent-comparison process.
memory={}
for name,c in models.items():
    if hasattr(c,'coefficients'):n=sum(a.nbytes for a in c.coefficients.values())+c.H.nbytes
    else:n=sum(curve.c.nbytes+curve.x.nbytes for axis in c.curves for curve in axis)
    memory[name]=dict(retainedInterpolationArrayBytes=n,
                      excludes='Python object/dictionary overhead and shared frozen arrays')
performance={}
for name in ['original','joint-pchip','gibbs-rounded-projection']:
    rows=[r for r in load('baseline-performance.json')['timings'] if r['method']==name]
    assert len(rows)==5 and all(r['evaluations']==300 for r in rows)
    t=np.array([r['seconds'] for r in rows])
    performance[name]=dict(meanSeconds=float(t.mean()),standardDeviationSeconds=float(t.std(ddof=1)),
                           minimumSeconds=float(min(t)),maximumSeconds=float(max(t)),evaluationsPerRound=300)
summary=dict(evidenceAuditPassed=True,scientificCandidateQualified=False,allTestedCandidatesRejected=True,
    existingFilesPreserved=len(manifest),newFiles=new,sourceHash=S['sourceHash'],
    staticCounts=S['counts'],versions=S['versions'],rootCounts=root_counts,
    roundtrips=roundtrip,EOSChecks=checks,pressureConstitutiveErrors=pressure,
    interpolationArrayMemory=memory,prototypePerformance=performance,
    diagnosticPeakRSSKiB=load('performance.json')['peakProcessRSSKiB'],
    evidenceStorageBytes=sum(p.stat().st_size for p in E.iterdir() if p.is_file()),
    interpretation='Evidence verified; stability, Maxwell consistency and/or pressure gates fail. No adoption.')
(E/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['evidenceAuditPassed','scientificCandidateQualified','allTestedCandidatesRejected','existingFilesPreserved','staticCounts','rootCounts']}))
