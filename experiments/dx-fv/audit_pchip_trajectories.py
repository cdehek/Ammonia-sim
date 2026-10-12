"""Bounded trajectory/EOS/accounting audit; candidate remains unqualified."""
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from CoolProp.CoolProp import PropsSI

ROOT=Path(__file__).resolve().parents[2]
E=Path(sys.argv[1]);TARGET=Path(sys.argv[2]).resolve()
assert not TARGET.is_relative_to(ROOT)
OLD=Path('/tmp/ammonia-stage2b-evidence');PHASE=Path('/tmp/ammonia-phase-event-evidence')
load=lambda p:json.loads(p.read_text())
manifest=load(E/'preserved-files.json')
for name,digest in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

length=.003/(math.pi*.020**2/4)
tube=math.pi/4*(.024**2-.020**2)*length*7850*.470
fin=1910*math.pi/4*(.080**2-.024**2)*.0002*2700*.900
air=6*.718
worst=dict(massKg=0.,globalMassKg=0.,fluidKJ=0.,globalFluidKJ=0.,thermalKJ=0.,combinedKJ=0.)
def accounting(run):
    n=run['sectionCount'];initial=run['initial'];caps=[tube/n,fin/n]*n+[air]
    for row in run['rows']:
        assert row['stop'] is None
        assert row['settings']['nonlinearTolerance']==1e-11 and row['settings']['thermalResidualK']==1e-12
        assert row['lastResidual'] is None or row['lastResidual']<=1e-11
        assert row['lastTimeError']<=1
        l=row['ledger'];f=l['faces'];q=l['tubeRefrigerantKJ'];expected=[0.]*(2*n)+[l['airLoadKJ']]
        combined=0.
        for i,(a,b) in enumerate(zip(initial['sections'],row['sections'])):
            dm=b['massKg']-a['massKg']-f[i]['massKg']+f[i+1]['massKg']
            du=b['internalEnergyKJ']-a['internalEnergyKJ']-f[i]['energyKJ']+f[i+1]['energyKJ']-q[i]
            assert abs(dm)<1e-8 and abs(du)<1e-6
            worst['massKg']=max(worst['massKg'],abs(dm));worst['fluidKJ']=max(worst['fluidKJ'],abs(du))
            qa,qf,qc=l['thermalLinksKJ'][3*i:3*i+3];expected[-1]-=qa+qf;expected[2*i]+=qa+qc-q[i];expected[2*i+1]+=qf-qc
            combined+=b['internalEnergyKJ']-a['internalEnergyKJ']
        for cap,a,b,budget in zip(caps,initial['nodes'],row['nodes'],expected):
            de=cap*(b['temperatureK']-a['temperatureK']);err=de-budget
            assert abs(err)<1e-6;worst['thermalKJ']=max(worst['thermalKJ'],abs(err));combined+=de
        combined-=f[0]['energyKJ']-f[-1]['energyKJ']+l['airLoadKJ'];assert abs(combined)<1e-6
        gm=sum(v['massKg'] for v in row['sections'])-sum(v['massKg'] for v in initial['sections'])-f[0]['massKg']+f[-1]['massKg']
        gu=sum(v['internalEnergyKJ'] for v in row['sections'])-sum(v['internalEnergyKJ'] for v in initial['sections'])-f[0]['energyKJ']+f[-1]['energyKJ']-sum(q)
        assert abs(gm)<1e-8 and abs(gu)<1e-6
        worst['globalMassKg']=max(worst['globalMassKg'],abs(gm));worst['globalFluidKJ']=max(worst['globalFluidKJ'],abs(gu))
        worst['combinedKJ']=max(worst['combinedKJ'],abs(combined))

def liquid(row):
    return sum(v['massKg']*(1-v['x'] if v['x'] is not None else (1 if 'liquid' in v['phase'] else 0)) for v in row['sections'])

def error(js,ref):
    out=dict(pressureBar=0.,enthalpyKJkg=0.,fluidK=0.,thermalK=0.,liquidMassKg=0.,quality=0.,outletQuality=0.,heatIntegralKJ=0.,heatRateKW=0.)
    for a,b in zip(js['sections'],ref['sections']):
        for label,key in [('pressureBar','p'),('enthalpyKJkg','h'),('fluidK','T')]:out[label]=max(out[label],abs(a[key]-b[key]))
        q=b.get('quality',b.get('x'))
        if a['x'] is not None and q is not None:out['quality']=max(out['quality'],abs(a['x']-q))
    if 'temperaturesK' in ref:
        out['thermalK']=max(abs(a['temperatureK']-b) for a,b in zip(js['nodes'],ref['temperaturesK']))
    else:out['thermalK']=max(abs(a['temperatureK']-b['temperatureK']) for a,b in zip(js['nodes'],ref['nodes']))
    V=.003/len(js['sections'])
    lm=ref.get('liquidMassKg')
    if lm is None:
        if 'nodes' in ref:lm=liquid(ref)
        else:lm=sum(v.get('massKg',v['rho']*V)*(1-v['quality']) for v in ref['sections'] if v['quality'] is not None)
    out['liquidMassKg']=abs(liquid(js)-lm)
    heat=ref.get('tubeRefrigerantKJ',ref.get('ledger',{}).get('tubeRefrigerantKJ'))
    if heat is not None:out['heatIntegralKJ']=abs(sum(js['ledger']['tubeRefrigerantKJ'])-sum(heat))
    if 'tubeRefrigerantKW' in ref:out['heatRateKW']=abs(sum(js['fluxes']['tubeRefrigerant'])-sum(ref['tubeRefrigerantKW']))
    elif 'fluxes' in ref:out['heatRateKW']=abs(sum(js['fluxes']['tubeRefrigerant'])-sum(ref['fluxes']['tubeRefrigerant']))
    else:
        reference_heat=sum(.60/len(js['sections'])*(ref['temperaturesK'][2*i]-(v['T']+273.15)) for i,v in enumerate(ref['sections']))
        out['heatRateKW']=abs(sum(js['fluxes']['tubeRefrigerant'])-reference_heat)
    if 'outlet' in ref:ref_quality=ref['outlet'].get('quality')
    else:
        h=ref['sections'][-1]['h'] if ref['sections'][-1]['p']>=3.5 else 1700.
        q=PropsSI('Q','P',3.5e5,'Hmass',h*1000,'Ammonia');ref_quality=q if 0<=q<=1 else None
    q=js['outlet'].get('quality')
    if q is not None and ref_quality is not None:out['outletQuality']=abs(q-ref_quality)
    return out

def accumulate(rows):return {key:max(r[key] for r in rows) for key in rows[0]}

result=dict(diagnosticOnly=True,evidenceAuditPassed=False,candidateQualified=False,preservedFiles=len(manifest),meshes=[])
for n,name in [(5,'five'),(9,'nine')]:
    runs={kind:load(E/f'extended-{name}-{kind}.json')['run'] for kind in ['linear','pchip']}
    assert runs['linear']['seed']==runs['pchip']['seed'] and runs['linear']['config']==runs['pchip']['config']
    assert runs['linear']['settings']==runs['pchip']['settings']
    identity=lambda r:[(e['section'],e['boundary'],e['direction']) for e in r['events']]
    assert identity(runs['linear'])==identity(runs['pchip'])
    assert load(E/f'extended-{name}-linear.json')['defaultExactlyReproducesSavedPrefix']
    for r in runs.values():accounting(r)
    frozen=load(ROOT/'experiments/dx-fv'/('coupled-reference.json' if n==5 else 'coupled-stage2b-reference.json'))
    fresh=load(OLD/f'{name}-fresh-reference.json')
    a=next(c for c in frozen['cases'] if c['name']=='cold')['runs'][1]
    b=next(c for c in fresh['cases'] if c['name']=='cold')['runs'][1]
    assert a['samples']==b['samples']
    if n==5:
        extended=load(OLD/'extended-five-reference.json')['cases'][0]['runs'][1]
        refs={r['seconds']:r for r in extended['samples'] if r['seconds']<=150}
        own=load(OLD/'extended-five-reference.json')['cases'][0]['runs'][0]
    else:
        extended=load(E/'extended-nine-eos-fine.json')
        refs={r['seconds']:r for r in b['samples']}
        refs.update({r['seconds']:r for r in extended['samples'] if r['seconds']>120})
        own=load(OLD/'extended-nine-reference.json.partial.json')['cases'][0]['runs'][0]
    eos_clock=load(PHASE/f'eos-{name}-fine.json')['eventSeconds']
    clock_fine=extended['terminalSaturationEventsSeconds'][0]
    assert abs(clock_fine-eos_clock)<1e-6
    own_clock_error=abs(own['terminalSaturationEventsSeconds'][0]-clock_fine);assert own_clock_error<1e-6
    reference_own=dict(pressureBar=0.,enthalpyKJkg=0.,fluidK=0.,thermalK=0.)
    coarse_rows={r['seconds']:r for r in own['samples']}
    for time,row in refs.items():
        if time not in coarse_rows:continue
        other=coarse_rows[time]
        for v,w in zip(row['sections'],other['sections']):
            for key,field in [('pressureBar','p'),('enthalpyKJkg','h'),('fluidK','T')]:reference_own[key]=max(reference_own[key],abs(v[field]-w[field]))
        reference_own['thermalK']=max(reference_own['thermalK'],*(abs(v-w) for v,w in zip(row['temperaturesK'],other['temperaturesK'])))
    assert reference_own['pressureBar']<1e-7 and reference_own['enthalpyKJkg']<1e-4 and reference_own['fluidK']<1e-4 and reference_own['thermalK']<1e-5
    comparisons={kind:accumulate([error(row,refs[min(refs,key=lambda t:abs(t-row['seconds']))]) for row in run['rows']]) for kind,run in runs.items()}
    differences=accumulate([error(a,b) for a,b in zip(runs['pchip']['rows'],runs['linear']['rows'])])
    candidate_limits={'pressureBar':1e-4,'enthalpyKJkg':.05,'fluidK':.01,'thermalK':.01}
    assert all(comparisons['pchip'][k]<v for k,v in candidate_limits.items()),comparisons
    events={kind:dict(seconds=r['terminalVaporEventSeconds'],errorSeconds=r['terminalVaporEventSeconds']-eos_clock,
        strictGatePassed=abs(r['terminalVaporEventSeconds']-eos_clock)<.001) for kind,r in runs.items()}
    assert events['pchip']['strictGatePassed'] and not events['linear']['strictGatePassed']
    tight=load(E/f'extended-{name}-pchip-tight.json')['run'];accounting(tight)
    temporal=accumulate([error(a,b) for a,b in zip(tight['rows'],runs['pchip']['rows'])])
    temporal['eventSeconds']=abs(tight['terminalVaporEventSeconds']-runs['pchip']['terminalVaporEventSeconds'])
    assert temporal['pressureBar']<5e-5 and temporal['enthalpyKJkg']<.05
    assert temporal['fluidK']<.001 and temporal['thermalK']<.001 and temporal['eventSeconds']<.001
    liqs={kind:load(E/f'liquid-{name}-{kind}.json')['run'] for kind in ['linear','pchip']}
    assert liqs['linear']['seed']==liqs['pchip']['seed']
    assert liqs['linear']['events']==liqs['pchip']['events']==[]
    for r in liqs.values():accounting(r)
    coarse=load(E/f'liquid-{name}-eos-coarse.json');fine=load(E/f'liquid-{name}-eos-fine.json')
    own_errors={key:0. for key in ['p','h','T','thermalK']}
    for a,b in zip(coarse['samples'],fine['samples']):
        for key in ['p','h','T']:own_errors[key]=max(own_errors[key],*(abs(v[key]-w[key]) for v,w in zip(a['sections'],b['sections'])))
        own_errors['thermalK']=max(own_errors['thermalK'],*(abs(v-w) for v,w in zip(a['temperaturesK'],b['temperaturesK'])))
    assert own_errors['p']<1e-7 and own_errors['h']<1e-4 and own_errors['T']<1e-4 and own_errors['thermalK']<1e-5
    lc={kind:accumulate([error(r,s) for r,s in zip([run['initial']]+run['rows'],fine['samples'])]) for kind,run in liqs.items()}
    ld=accumulate([error(a,b) for a,b in zip(liqs['pchip']['rows'],liqs['linear']['rows'])])
    path=[]
    for kind,run in liqs.items():
        for row,ref in zip([run['initial']]+run['rows'],fine['samples']):
            v=row['sections'][-1]
            ph_eos=PropsSI('T','P',v['p']*1e5,'Hmass',v['h']*1000,'Ammonia')-273.15
            path.append(dict(interpolation=kind,seconds=row['seconds'],p=v['p'],h=v['h'],tableTemperatureC=v['T'],
                EOSAtSamePHC=ph_eos,PHErrorK=v['T']-ph_eos,EOSAtMatchedMUC=ref['sections'][-1]['T'],
                trajectoryErrorK=v['T']-ref['sections'][-1]['T']))
    timing=load(E/f'liquid-{name}-timing-clean.json')
    timing_stats={kind:dict(medianMS=statistics.median(p[kind]['elapsedMS'] for p in timing['pairs']),
        minimumMS=min(p[kind]['elapsedMS'] for p in timing['pairs']),maximumMS=max(p[kind]['elapsedMS'] for p in timing['pairs'])) for kind in ['linear','pchip-log-pressure']}
    first=liqs['linear']['initial']['sections'][0]
    eos_rho=PropsSI('Dmass','P',first['p']*1e5,'Hmass',first['h']*1000,'Ammonia')
    eos_u=PropsSI('Umass','P',first['p']*1e5,'Hmass',first['h']*1000,'Ammonia')/1000
    cold_rho=PropsSI('Dmass','P',3.5e5,'Hmass',500e3,'Ammonia')
    cold_u=PropsSI('Umass','P',3.5e5,'Hmass',500e3,'Ammonia')/1000
    liquid_constitutive=dict(tableDensityKgM3=first['rho'],EOSDensityAtSamePHKgM3=eos_rho,
        relativeDensityError=first['rho']/eos_rho-1,tableUKJkg=first['u'],EOSUAtSamePHKJkg=eos_u)
    initial_inventory=dict(JSColdMassKg=sum(c['massKg'] for c in runs['linear']['seed']['cells']),EOSColdMassKg=cold_rho*.003,
        JSColdEnergyKJ=sum(c['internalEnergyKJ'] for c in runs['linear']['seed']['cells']),EOSColdEnergyKJ=cold_rho*.003*cold_u)
    result['meshes'].append(dict(sectionCount=n,events=events,referenceEventConvergenceSeconds=own_clock_error,referenceStateConvergence=reference_own,
        extendedAccuracy=comparisons,extendedCandidateMinusOriginal=differences,
        extendedCost={k:{label:r[label] for label in ['work','propertyCalls','elapsedMS']} for k,r in runs.items()},
        candidateTemporalRefinement=temporal,extendedInitialInventories=initial_inventory,liquidConstitutiveComparison=liquid_constitutive,
        liquidAccuracy=lc,liquidReferenceConvergence=own_errors,liquidCandidateMinusOriginal=ld,liquidPropertyPaths=path,
        liquidAbsoluteEOSBudgetsPassed={k:all(r[label]<budget for label,budget in candidate_limits.items()) for k,r in lc.items()},
        liquidInitialErrors={k:error(r['initial'],fine['samples'][0]) for k,r in liqs.items()},
        liquidFinalErrors={k:error(r['rows'][-1],fine['samples'][-1]) for k,r in liqs.items()},
        liquidCost={k:{label:r[label] for label in ['work','propertyCalls','elapsedMS']} for k,r in liqs.items()},
        liquidFinalInventory={k:r['finalLiquidMassKg'] for k,r in liqs.items()},liquidTiming=timing_stats))
result['conservationWorst']=worst
result['propertyRegressionStillPresent']=load(Path('/tmp/ammonia-saturation-evidence/final-audit.json'))['regionRegressions']==['liquid']
assert result['propertyRegressionStillPresent']
result['evidenceAuditPassed']=True
TARGET.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['evidenceAuditPassed','candidateQualified','preservedFiles','conservationWorst']}))
