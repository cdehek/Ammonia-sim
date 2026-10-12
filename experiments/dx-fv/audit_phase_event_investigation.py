"""Read-only phase investigation audit; no accepted reference/solver changes."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE, OUT = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
SAVED = Path(sys.argv[3]) if len(sys.argv)>3 else Path('/tmp/ammonia-stage2b-evidence')
assert not OUT.is_relative_to(ROOT)
def load(folder, name):
    return json.loads((folder/(name+'.json')).read_text())
preserved = load(HERE, 'preserved-files')
for name, expected in preserved.items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected, name
legacy = load(HERE, 'legacy-prefix')
assert legacy['passed'] and legacy['legacyExactlyReproducesSavedPrefix']
result = dict(passed=False, existingFilesPreserved=len(preserved),
              legacyAcceptedSHA=legacy['startingCommit'], meshes=[],
              interpretation='Diagnostic evidence; the strict phase-accuracy gate still fails.')

def conservation(r, n):
    assert r['passed'] and r['diagnosticOnly']
    # The unchanged independent generator already supports a direct D/T flash
    # when CoolProp's D/U backend rejects a quality probe. Enforce its original
    # thermodynamic recovery requirement; zero fallbacks is not a contract.
    for record in r.get('fallbackRecords',[]):
        assert abs(record['result']['u']-record['inputUKJkg'])<1e-7
        assert abs(record['result']['rho']/record['inputDensityKgM3']-1)<1e-7
    j=4*n+1;f=2*n; y=r['eventVector'];initial=r['seedVector'];delta=[a-b for a,b in zip(y,initial)]
    face=[delta[j+2*i:j+2*i+2] for i in range(n+1)];q=delta[j+2*(n+1):j+2*(n+1)+n]
    links=delta[j+2*(n+1)+n:-1];assert len(links)==3*n
    nodes=[0.]*(2*n+1);nodes[-1]=delta[-1]
    for i in range(n):
        at,af,ft=links[3*i:3*i+3]
        nodes[-1]-=at+af;nodes[2*i]+=at+ft-q[i];nodes[2*i+1]+=af-ft
    m=[delta[2*i]-face[i][0]+face[i+1][0] for i in range(n)]
    e=[delta[2*i+1]-face[i][1]+face[i+1][1]-q[i] for i in range(n)]
    t=[delta[f+i]-nodes[i] for i in range(2*n+1)]
    combined=sum(delta[1:f:2])+sum(delta[f:j])-face[0][1]+face[-1][1]-delta[-1]
    assert abs(sum(m))<1e-8 and max(map(abs,m))<1e-8
    assert abs(sum(e))<1e-6 and max(map(abs,e))<1e-6 and max(map(abs,t))<1e-6 and abs(combined)<1e-6
    assert all(math.isfinite(v) for v in y)
    return dict(massKg=max(map(abs,m)),energyKJ=max(map(abs,e)),thermalKJ=max(map(abs,t)),combinedKJ=abs(combined))

for n,mesh in ((5,'five'),(9,'nine')):
    matrix=load(SAVED,mesh+'-extra')
    runs=[r for r in matrix['runs'] if r['name'].startswith('extended')]
    events=[next(e for e in r['state']['events'] if e['section']==n-1 and e['boundary']=='vapor' and e['direction']=='heating') for r in runs]
    js=load(HERE,'local-'+mesh+'-js');assert js['passed'] and js['observationalEquivalence'] and js['eventDifferenceFromSavedSeconds']==0
    if n==5:assert js['legacyLocalExactlyEquivalent']
    cp=load(HERE,'eos-'+mesh+'-fine');matched=load(HERE,'eos-'+mesh+'-js-seed')
    recorded=load(HERE,'eos-nine-recorded' if n==9 else 'eos-five-js-seed-recorded')
    counterpart=cp if n==9 else matched
    for key in ('eventSeconds','eventVector','seedVector','steps','nfev','njev','nlu'):
        assert recorded[key]==counterpart[key],('Fallback observation changed reference',key)
    assert len(recorded['fallbackRecords'])==recorded['fallbacks']
    conservation(recorded,n)
    table=load(HERE,'table-'+mesh+'-js-seed');temperature=load(HERE,'temperature-'+mesh+'-js-seed')
    refined=load(HERE,'table-'+mesh+'-refined');localized=load(HERE,'localization-'+mesh)
    interpolation=load(HERE,'localization-check-'+mesh);assert interpolation['passed']
    assert abs(interpolation['result']['nativeMinusConservedLinearSeconds'])<1e-6
    check=load(HERE,'table-check-'+mesh);assert check['passed']
    balances={name:conservation(r,n) for name,r in [('directEOS',cp),('matchedMUEOS',matched),('table',table),('satTemperatureComponent',temperature),('refinedTable',refined),('localized',localized)]}
    frozenfile='extended-five-reference.json' if n==5 else 'extended-nine-reference.json.partial.json'
    old=json.loads((SAVED/frozenfile).read_text())['cases'][0]['runs']
    coarse=old[0]['terminalSaturationEventsSeconds'][0]
    refinement=abs(coarse-cp['eventSeconds']);assert refinement<1e-6
    if n==5:assert abs(old[1]['terminalSaturationEventsSeconds'][0]-cp['eventSeconds'])<1e-6
    assert abs(table['eventSeconds']-refined['eventSeconds'])<1e-6
    assert abs(cp['rootResidualKJkg'])<1e-8
    derivatives=[d['wetSideKJkgS'] for d in cp['derivatives'] if d['epsilonSeconds'] in (.001,.0001)]
    assert all(40<v<60 for v in derivatives)
    native=events[-1]['seconds'];upstream=matched['eventSeconds']-cp['eventSeconds'];properties=table['eventSeconds']-matched['eventSeconds']
    evolution=localized['eventSeconds']-table['eventSeconds'];localization=native-localized['eventSeconds']
    total=native-cp['eventSeconds'];assert abs(total-(upstream+properties+evolution+localization))<1e-12
    temperature_effect=temperature['eventSeconds']-matched['eventSeconds']
    assert abs(localization)<1e-6 and abs(evolution)<.0001 and total>.001
    assert .95<temperature_effect/properties<1.01
    # Verify the recorded half-step endpoints correspond to the actual event.
    # All values here were evaluated and detached by the unchanged observer.
    trial=next(c for c in js['run']['captures'] if c['kind']=='evaluated-endpoints' and c['startSeconds']<=events[-1]['bracketStartSeconds'] and c['startSeconds']+c['trialSeconds']>=events[-1]['bracketEndSeconds'])
    assert len(trial['endpoints'])==6
    assert events[-1]['bracketStartSeconds']<=native<=events[-1]['bracketEndSeconds']
    point=next(p for p in load(HERE,'properties-'+mesh)['comparisons'] if abs(p['seconds']-cp['eventSeconds'])<1e-9)
    surface_time=abs(point['MUPropertyMarginKJkg'])/derivatives[-1]
    result['meshes'].append(dict(sectionCount=n,zeroBasedSection=n-1,physicalInterval=[(n-1)/n,1.],direction='wet to vapor; heating',
        JSSeconds=native,EOSSeconds=cp['eventSeconds'],errorSeconds=total,strictBudgetSeconds=.001,originalPhaseGatePassed=False,
        referenceRefinementSeconds=refinement,EOSRootResidualKJkg=cp['rootResidualKJkg'],conditioning=cp['derivatives'],
        phaseState=cp['eventState'],eventMassKg=cp['eventVector'][2*n-2],eventEnergyKJ=cp['eventVector'][2*n-1],
        tableReferenceRefinementSeconds=abs(table['eventSeconds']-refined['eventSeconds']),
        nativeBracketWidthSeconds=events[-1]['bracketEndSeconds']-events[-1]['bracketStartSeconds'],
        nativeMinusConservedLinearSeconds=interpolation['result']['nativeMinusConservedLinearSeconds'],
        decompositionSeconds=dict(inheritedTo120=upstream,post120PropertySource=properties,
                                  trajectoryNumerics=evolution,eventLocalization=localization,total=total),
        saturationTemperatureEffectSeconds=temperature_effect,temperatureFractionOfPost120Properties=temperature_effect/properties,
        otherPost120PropertiesSeconds=properties-temperature_effect,
        sameMUPhaseSurfaceEquivalentSeconds=surface_time,tableEngineAgreement=check['worst'],
        observedFlashFallbacks=recorded['fallbackRecords'],
        savedTemporalRegimes=[dict(tolerance=r['tolerance'],eventSeconds=e['seconds'],errorFromIndependentTableSeconds=e['seconds']-table['eventSeconds']) for r,e in zip(runs,events)],
        localConservation=balances))
result['spatialClockDifferenceSeconds']=result['meshes'][1]['EOSSeconds']-result['meshes'][0]['EOSSeconds']
data=json.loads((ROOT/'properties.json').read_text());logs=[math.log(v) for v in data['p']]
result['temperaturePointComparators']=[]
for item in result['meshes']:
    p=item['phaseState']['p'];target=math.log(p)
    i=next(j for j in range(len(logs)-1) if logs[j]<=target<=logs[j+1])
    indices=[i-1,i,i+1];assert indices[0]>=0
    xs=[logs[j] for j in indices];ys=[data['sat'][j][0] for j in indices]
    quad=sum(ys[k]*math.prod((target-xs[j])/(xs[k]-xs[j]) for j in range(3) if j!=k) for k in range(3))
    weight=(target-logs[i])/(logs[i+1]-logs[i]);linear=data['sat'][i][0]+weight*(data['sat'][i+1][0]-data['sat'][i][0])
    truth=load(HERE,'eos-'+('five' if item['sectionCount']==5 else 'nine')+'-fine')['saturation']['T']
    result['temperaturePointComparators'].append(dict(sectionCount=item['sectionCount'],pressureBar=p,
        bracketingPressuresBar=data['p'][i:i+2],linearErrorK=linear-truth,quadraticPointErrorK=quad-truth,
        interpretation='Unintegrated point comparator only; no correction installed or qualified.'))
result['passed']=True
OUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
