"""Bounded, reproducible P1 experiment. All output stays below P1/evidence.

Run with python-flint==0.8.0 and mpmath==1.3.0. Each attempt has a 20-second
SIGALRM wall timeout. Results are appended before moving to the next attempt.
"""
import hashlib,importlib.metadata,json,os,platform,signal,time,statistics
from contextlib import contextmanager
from fractions import Fraction as F
from pathlib import Path
from flint import ctx,arb
import flint
import diagnostic as dg
import eos_interval as ei
import validated as va

B=Path(__file__).resolve().parent
E=Path(os.environ.get('P1_EVIDENCE',B/'evidence'))
C2=dg.C2

@contextmanager
def timeout():
    def expired(*_):raise TimeoutError('20-second attempt deadline')
    old=signal.signal(signal.SIGALRM,expired)
    signal.alarm(20)
    try:yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM,old)

def write(name,value):
    (E/name).write_text(json.dumps(value,indent=2)+'\n')

def attempt(label,fun):
    start=time.perf_counter()
    try:
        with timeout():result=fun()
        out=dict(label=label,success=True,result=result)
    except Exception as ex:
        out=dict(label=label,success=False,status='NUMERICAL_FAILURE',reason=repr(ex))
        if hasattr(ex,'evidence'):out['failedEnclosureEvidence']=ex.evidence
    out['seconds']=time.perf_counter()-start
    with (E/'attempts.jsonl').open('a') as f:f.write(json.dumps(out)+'\n')
    return out

def contains(x,z):
    return F(z['lower'])<=F(str(x))<=F(z['upper'])

def reproduce():
    refs=json.loads((C2/'evidence/references.json').read_text())
    saved=json.loads((C2/'evidence/local-enclosures.json').read_text())
    saved={r['key']:r for r in saved['rows']}
    rows=[]
    for row in refs['rows']:
        c=row['case']
        if c['group'] not in ['rows','falseAcceptance']:continue
        b=c['input']['bits']
        d,u=dg.target(b)
        t=row['targets']['exact_MUV']
        assert d==F(int(t['exactDensity']['numerator']),int(t['exactDensity']['denominator']))
        assert u==F(int(t['exactEnergyJkg']['numerator']),int(t['exactEnergyJkg']['denominator']))
        trials=[]
        for prec in [192,256]:
            z=ei.local.enclose(d,u,t['levels'][-1]['homogeneous']['T'],precision=prec)
            old=next(x for x in saved[c['key']]['targets']['exact_MUV']['trials'] if x['precisionBits']==prec)
            assert z['localPressureSide']==old['localPressureSide']
            # Containment of the saved independent diagnostic and exact sign.
            assert contains(t['levels'][-1]['homogeneous']['p'],z['pressurePa'])
            trials.append(z)
        if c['key']=='webkit-ledger-69':
            assert [b[k] for k in ['M','U_kJ','V']]==['3fd406de00d710be','406b448176d039b2','3f43a92a30553262']
        if c['key']=='webkit-ledger-76':
            assert [b[k] for k in ['M','U_kJ','V']]==['3f913c19a47fa406','40394d3fa3941ea6','3f43a92a30553262']
        rows.append(dict(key=c['key'],inputBits=b,exactDensity=str(d),exactEnergyJkg=str(u),
                         trials=trials,historicalRawPressureMinusLimitPa=str(F(dg.decode(c['raw']['bits']['p']))-3500000)))
    assert len(rows)==9
    assert sum(r['trials'][-1]['localPressureSide']=='INSIDE' for r in rows[:7])==1
    write('c2-reproduction.json',dict(rows=rows,roundedDUHistoricalSplit='two inside / five outside',
        exactMUVSplit='one inside / six outside',scope='local homogeneous only; no physical phase proof'))
    return refs

def inputs(refs):
    out=[]
    for row in refs['rows']:
        c=row['case']
        if c['group'] not in ['rows','falseAcceptance'] and c['key'] not in ['native-ledger-148','native-ledger-162','native-ledger-165']:continue
        z=row['targets']['exact_MUV']['levels'][-1]
        eq=z['coexistence']
        out.append(dict(key=c['key'],inputBits=c['input']['bits'],origin='unchanged saved C2 inventory',
            homseed=z['homogeneous']['T'],mixseed=[eq[k] for k in ['rhoL','rhoV','T']],
            historicalOutcome='refuse' if c['group']=='rows' else 'return' if c['group']=='falseAcceptance' else 'Gate B unqualified'))
    return out+dg.generated()

def diag_case(c,precision,offset=0):
    dg.precision(precision)
    if c['homseed'] is not None:
        return dg.enc(dg.solve(c['inputBits'],c['homseed'],c['mixseed'],offset))
    d,u=map(dg.number,dg.target(c['inputBits']))
    seed=[dg.mp.mpf(v)+offset for v in c['mixseed']]
    mix=list(dg.mp.findroot(lambda a,b,t:dg.mix_res([a,b,t],d,u,'vapor'),seed,maxsteps=20,
        tol=dg.mp.power(10,-precision+12)))
    return dg.enc(dict(mix=mix,mode='vapor',mixInverse=dg.inverse(lambda x:dg.mix_res(x,d,u,'vapor'),mix),
                      mixResidual=dg.mix_res(mix,d,u,'vapor')))

def validated_case(c,z,prec):
    ctx.prec=prec
    d,u=dg.target(c['inputBits'])
    out=dict(precisionBits=prec,coexistenceRootStatus='NOT_ATTEMPTED',
        competingPhaseExclusion='UNRESOLVED: no bounded convex-envelope/topology proof',
        topologyCategory='C: diagnostics only; no external theorem imported',
        completePhysicalBranchCertification=False,status='UNRESOLVED')
    if 'homT' in z:
        hom=ei.local.enclose(d,u,z['homT'],precision=prec)
        out['homogeneous']=hom
        Tlo,Thi=hom['temperature']['lower'],hom['temperature']['upper']
        X,sat=va.saturation(z['sat'],z['satInverse'],Tlo,Thi,prec)
        out['saturation']=sat
        T=va.interval(Tlo,Thi)
        hz=ei.eos(ei.ball(d),T)
        out['homogeneousStability']=ei.stability(hz,ei.ball(d),T)
        dl,dv=ei.ball(d)-X[0],ei.ball(d)-X[1]
        side='LIQUID_SIDE' if dl>0 else 'VAPOR_SIDE' if dv<0 else 'DOME_INTERIOR' if dl<0 and dv>0 else 'INEQUALITY_UNRESOLVED'
        out.update(relativeSide=side,densityMinusLiquid=ei.serialize(dl),densityMinusVapor=ei.serialize(dv),
                   mathematicalPressureSupport=hom['localPressureSide'],
                   pressureScope='homogeneous root; physical admissibility unresolved')
        # Independently evaluate original thermodynamic g expression on the
        # entire saturation box; this does not rely on a tiny point residual.
        l,v=ei.eos(X[0],T),ei.eos(X[1],T)
        alt=(l['u']+l['p']/X[0]-T*l['s'])-(v['u']+v['p']/X[1]-T*v['s'])
        assert alt.contains(0)
        sat['independentGResidual']=ei.serialize(alt)
        if side in ['LIQUID_SIDE','VAPOR_SIDE']:
            out['status']='CONDITIONAL_PHASE_PROOF'
            out['conditionalDependency']='UNPROVED: selected local coexistence is the equilibrium convex envelope, with no competing relevant phases'
        elif side=='DOME_INTERIOR':
            out['homogeneousPhysicalAdmissibility']='WITHHELD: inside local coexistence endpoints'
    X,mix=va.mixture(z['mix'],z['mixInverse'],d,u,z['mode'],prec)
    out['mixture']=mix
    out['coexistenceRootStatus']='VALIDATED_LOCAL_ALGEBRAIC_ROOT'
    if mix['mixtureAdmissible']:
        out['mixturePressureSupport']='OUTSIDE' if ei.ball(F(mix['pressurePa']['lower']))>3500000 else 'INSIDE' if ei.ball(F(mix['pressurePa']['upper']))<3500000 else 'STRADDLES'
    if c['key']=='generated-dome-interior-homogeneous':
        hom=out['homogeneous']
        hT=va.interval(hom['temperature']['lower'],hom['temperature']['upper'])
        hs=ei.eos(ei.ball(d),hT)['s']
        rl,rv,T=X
        q,w=va.fractions(rl,rv,ei.ball(d))
        ms=w*ei.eos(rl,T)['s']+q*ei.eos(rv,T)['s']
        advantage=ms-hs
        assert mix['mixtureAdmissible'] and advantage>0
        out['competingMixtureEntropyAdvantageJkgK']=ei.serialize(advantage)
        out['homogeneousPhysicalAdmissibility']='REJECTED: a validated same-U,V mixture has strictly greater entropy'
        out['competingPhaseExclusion']='homogeneous root excluded by one explicit feasible competitor; global mixture optimality still unproved'
    return out

def main():
    E.mkdir(parents=True,exist_ok=True)
    assert not (E/'attempts.jsonl').exists(),'preserve old output; do not overwrite attempts'
    started=time.perf_counter()
    identities={str(p.relative_to(B.parent.parent.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [dg.source,C2/'local_enclosure.py',C2/'evidence/Ammonia.json',C2/'evidence/references.json',C2/'evidence/local-enclosures.json']}
    manifest=json.loads((C2/'evidence/source-manifest.json').read_text())
    assert all(hashlib.sha256((C2/p).read_bytes()).hexdigest()==h for p,h in manifest.items())
    refs=reproduce()  # first numerical work: unchanged C2 inputs and code
    write('runtime.json',dict(python=platform.python_version(),platform=platform.platform(),
        pythonFlint=flint.__version__,FLINT=flint.__FLINT_VERSION__,mpmath=dg.mp.__version__,
        inheritedIdentities=identities,
        prototypeIdentities={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in B.glob('*.py')},
        coefficientConvention='exact parsed binary64 rationals',
        referenceConvention='unchanged original JSON lead a1/a2; no setter',perAttemptDeadlineSeconds=20,
        pathRedirection='in-memory B5 evaluator JSON path only; original source bytes unmodified',
        flintArtifacts={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(flint.__file__).parent.parent.glob('python_flint.libs/*') if p.is_file()}))
    cases=inputs(refs)
    write('inputs.json',cases)
    # Prioritize inward hazards, then adversarial / generated controls.
    cases.sort(key=lambda c:0 if c['key'].startswith('webkit') else 1 if c['key'].startswith('generated') or c['key'].startswith('native') else 2)
    rows=[]
    for c in cases:
        print(c['key'],flush=True)
        levels=[attempt(c['key']+f'/diagnostic-{n}',lambda n=n:diag_case(c,n)) for n in [65,90]]
        row=dict(case=c,diagnosticLevels=levels,validated=[],originalScientificQualification='UNRESOLVED / unchanged historical qualification',browserPortability='NOT DEMONSTRATED',completePhysicalBranchCertification=False)
        if all(x['success'] for x in levels):
            z=levels[-1]['result']
            row['displacedSeed']=attempt(c['key']+'/diagnostic-displaced-seed',lambda:diag_case(c,90,dg.mp.mpf('.01')))
            for prec in [192,256]:
                row['validated'].append(attempt(c['key']+f'/validated-{prec}',lambda prec=prec:validated_case(c,z,prec)))
        rows.append(row)
        write('results.json',dict(classification='PARTIAL PHASE CERTIFICATION',rows=rows,
            fullPhysicalCertificates=0,globalTopologyProved=False,seconds=time.perf_counter()-started))
    write('performance.json',dict(totalSeconds=time.perf_counter()-started,
        scope='standalone Python diagnostic/verification only; excludes install/audit/browser/runtime integration',
        perAttemptDeadlineSeconds=20,validatedAttempts=[dict(key=r['case']['key'],precision=x['result']['precisionBits'],seconds=x['seconds']) for r in rows for x in r['validated'] if x['success']]))
    print('completed',len(rows),'rows; zero complete physical branch certificates',flush=True)

if __name__=='__main__':main()
