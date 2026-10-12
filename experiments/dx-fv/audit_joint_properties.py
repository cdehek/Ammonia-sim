"""Evidence/preservation audit; no property correction or coupled solver import."""
import hashlib
import json
import math
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];E=Path(sys.argv[1]).resolve()
assert not E.is_relative_to(ROOT)
load=lambda name:json.loads((E/name).read_text())
manifest=load('preserved-files.json')
for name,digest in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
A=load('analysis.json');C=load('conditioning.json');N=load('conditioning-native.json');L=load('legacy-liquid.json');P=load('properties.json')
assert L['passed'] and L['legacyExactlyReproducesLiquidTrajectory']
assert L['gitBlobs']==dict(model='0fbde5ab7f1182237d643f015c393ecd82e91c55',implicit='d195842cb9579b7a5bbce4f6dbd6e4e22fcb34c3')
for point in P['points']:
    s=point['eos'];assert abs(s['h']-s['u']-100*s['p']/s['rho'])<1e-9
    if point['originalPH']['success']:
        a,b=dict(point['originalPH']['state']),dict(point['candidatePH']['state']);a.pop('T');b.pop('T');assert a==b
        c=point['tableInventory'];assert abs(c['internalEnergyKJ']-c['massKg']*a['h']+100*a['p']*c['volumeM3'])<1e-9
for r in A['pressureDecomposition']:
    assert r['exactExistingTable']['diagnosticRootScope']=='local'
    assert abs(sum(r['termsBar'].values())-r['pressureErrorBar'])<1e-12
    assert abs(r['termsBar']['nativeInversion'])<1e-7
    assert abs(r['uniformVolumeConventionEffectBar'])<1e-8
    predicted=r['EOSUMismatchAtTablePressureKJkg']/r['EOSIsochoricDUDpKJkgBar']
    assert abs(predicted-r['termsBar']['constitutive'])<1e-5
for p in A['points']:
    if 'liquidComponents' not in p:continue
    c=p['liquidComponents'];rho=next(r['originalPH']['state']['rho'] for r in P['points'] if r['name']==p['name']);true=next(r['eos']['rho'] for r in P['points'] if r['name']==p['name'])
    assert abs(c['enthalpyAnchorOffsetErrorK']+c['otherEnthalpyShapeOffsetErrorK']-c['offsetErrorK'])<1e-12
    assert abs(c['densitySurfaceErrorKgM3']+c['enthalpyOffsetDensityEffectKgM3']+c['nativePHInversionDensityEffectKgM3']-(rho-true))<1e-10
    assert abs(c['saturatedDensityAnchorEffectKgM3']+c['otherDensityShapeEffectKgM3']-c['densitySurfaceErrorKgM3'])<1e-10
for point in C['points']:
    native=next(p for p in N['points'] if p['name']==point['name'])
    assert abs(point['thermodynamicIdentities']['directEOS']['maxwellMismatchKJkgBar'])<1e-10
    for d in native['derivatives']:
        identity=point['thermodynamicIdentities'][d['interpolation']]
        assert abs(d['rhoPressureSlopeAtFixedTKgM3Bar']-identity['rhoPressureSlopeAtFixedTKgM3Bar'])<2e-5
        assert abs(d['hPressureSlopeAtFixedTKJkgBar']-identity['hPressureSlopeAtFixedTKJkgBar'])<2e-5
    if point['name']=='liquid-p0.3029893712344606-sc1.0':
        assert len(point['tableRootsBar'])==3
        assert all(d['rhoPressureSlopeAtFixedTKgM3Bar']<0 for d in native['derivatives'])
        assert point['thermodynamicIdentities']['directEOS']['rhoPressureSlopeAtFixedTKgM3Bar']>0
for knot in A['frozenKnotChecks']:
    assert abs(knot['temperatureErrorK'])<=5.1e-9
    assert max(abs(knot[k]) for k in ['hfErrorKJkg','hgErrorKJkg','rhofErrorKgM3','rhogErrorKgM3'])<5.1e-8
assert A['acceptedFixtureCoverage']['liquidStates']==0
assert C['temperatureScanStats']['candidate']['maximumAbsoluteK']<C['temperatureScanStats']['original']['maximumAbsoluteK']
reference_errors={k:0. for k in ['p','h','T','thermalK']}
coarse,fine=load('liquid-five-eos-coarse.json'),load('liquid-five-eos-fine.json')
for a,b in zip(coarse['samples'],fine['samples']):
    for v,w in zip(a['sections'],b['sections']):
        for k in ['p','h','T']:reference_errors[k]=max(reference_errors[k],abs(v[k]-w[k]))
    reference_errors['thermalK']=max(reference_errors['thermalK'],*(abs(v-w) for v,w in zip(a['temperaturesK'],b['temperaturesK'])))
assert reference_errors['p']<1e-7 and reference_errors['h']<1e-4 and reference_errors['T']<1e-4 and reference_errors['thermalK']<1e-5
for n,name in [(5,'five'),(9,'nine')]:
    for r in load(f'liquid-{name}-eos-fine.json')['samples']:
        assert n*r['maximumMassResidualKg']<1e-8 and n*r['maximumFluidEnergyResidualKJ']<1e-6
        assert (2*n+1)*r['maximumThermalResidualKJ']<1e-6 and abs(r['combinedEnergyResidualKJ'])<1e-6
    for kind in ['linear','pchip']:
        run=load(f'liquid-{name}-{kind}.json')['run'];assert run['stop'] is None
        for row in run['rows']:
            assert abs(row['massResidualKg'])<1e-8 and max(abs(row[k]) for k in ['refrigerantEnergyResidualKJ','thermalEnergyResidualKJ','combinedEnergyResidualKJ'])<1e-6
            assert all(abs(v['energyKJ'])<1e-6 and abs(v['massKg'])<1e-8 for v in row['sectionResiduals'])
            assert all(abs(v['residualKJ'])<1e-6 for v in row['nodes'])
            assert row['lastResidual']<=1e-11 and row['settings']['thermalResidualK']==1e-12
summary=dict(evidenceAuditPassed=True,candidateQualified=False,existingFilesPreserved=len(manifest),
    legacyExactlyReproduced=True,propertyRequests=len(P['points']),completedPropertyComparisons=len(A['points']),
    unsupportedOrNonlocalConditions=len(A['failures']),
    pressureDecomposition=[r for r in A['pressureDecomposition'] if r['seconds'] in [0.,.1]],
    initialLiquidComponents=next(p['liquidComponents'] for p in A['points'] if p['name']=='saved-five-linear-0'),
    temperatureScanStats=C['temperatureScanStats'],acceptedFixtureCoverage=A['acceptedFixtureCoverage'],
    maximumVolumeConventionEffectBar=max(abs(r['uniformVolumeConventionEffectBar']) for r in A['pressureDecomposition']),
    maximumMainProbeInversionErrorBar=max(abs(r['termsBar']['nativeInversion']) for r in A['pressureDecomposition']),
    maximumFrozenKnotGibbsMismatchKJkg=max(abs(p['gibbsMismatchKJkg']) for p in A['frozenKnotChecks']),
    shortReferenceConvergence=reference_errors,
    interpretation='Pre-existing constitutive and derivative inconsistency identified; no correction implemented or qualification claimed.')
(E/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['evidenceAuditPassed','candidateQualified','existingFilesPreserved','legacyExactlyReproduced','propertyRequests','completedPropertyComparisons','unsupportedOrNonlocalConditions']}))
