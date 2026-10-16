"""Independent checks, malformed proof proposals and thermodynamic adversaries.

Finite mpmath checks support correspondence; Arb + contraction supplies proofs.
The checks here do not prove the complete library/compiler/software stack.
"""
import itertools,json,os,time
from fractions import Fraction as F
from pathlib import Path
from flint import ctx,arb
import diagnostic as dg
import eos_interval as ei
import validated as va
from run import attempt,write,contains

B=Path(__file__).resolve().parent
E=Path(os.environ.get('P1_EVIDENCE',B/'evidence'))

def compare(z,x):
    assert contains(dg.mp.nstr(x,95),z),(z,str(x))

def nested(inner,outer):
    return F(outer['lower'])<=F(inner['lower'])<=F(inner['upper'])<=F(outer['upper'])

def rejection(label,fun):
    out=attempt('negative/'+label,fun)
    assert not out['success'],'invalid proposal unexpectedly succeeded: '+label
    return out

def main():
    started=time.perf_counter()
    results=json.loads((E/'results.json').read_text())['rows']
    lookup={r['case']['key']:r for r in results}
    assert len(results)==17
    assert all(all(x['success'] for x in r['diagnosticLevels']+r['validated']+[r['displacedSeed']]) for r in results)
    checks=[]
    dg.precision(105)
    ctx.prec=256
    points=[]
    for ds,ts in [('521.53','345.56'),('26','345.57'),('540','335'),('24','365'),('30','345.56')]:
        d,T=dg.number(F(ds)),dg.number(F(ts))
        b=ei.eos(ei.ball(F(ds)),ei.ball(F(ts)))
        p=dg.hp.eos(d,T)
        values={k:p[k] for k in ['p','u','s','g']}
        for field,prop,axis in [('cv','u',1),('pr','p',0),('pt','p',1),('ur','u',0),('gr','g',0),('gt','g',1)]:
            values[field]=dg.mp.diff(lambda x:dg.hp.eos(x,T)[prop] if axis==0 else dg.hp.eos(d,x)[prop],d if axis==0 else T)
        for k,x in values.items():compare(ei.serialize(b[k]),x)
        legacy=ei.local.eos(ei.ball(F(ds)),ei.ball(F(ts)))
        for k in ['p','u','cv']:assert b[k].overlaps(legacy[k])
        points.append(dict(density=ds,T=ts,comparisons={k:ei.serialize(b[k]) for k in values}))
    checks.append(dict(check='independently differentiated inherited mpmath EOS; analytic Arb derivatives',passed=True,points=points))
    jacchecks=[]
    for key,kind in [('webkit-ledger-69','saturation'),('webkit-ledger-76','saturation'),('generated-interior-mixture','mixture'),('native-ledger-162','mixture')]:
        r=lookup[key]
        proof=r['validated'][-1]['result'][kind]
        z=r['diagnosticLevels'][-1]['result']
        d,u=map(dg.number,dg.target(r['case']['inputBits']))
        axes=[[F(b['lower']),F(b['upper'])] for b in proof['box']]
        if kind=='saturation':
            temp=[F(proof['parameterTemperature']['lower']),F(proof['parameterTemperature']['upper'])]
        else:temp=[None]
        count=0
        for coords in itertools.product(*axes):
            x=[dg.number(v) for v in coords]
            for Tq in temp:
                T=dg.number(Tq) if Tq else None
                fun=(lambda xx:dg.sat_res(xx,T)) if kind=='saturation' else (lambda xx:dg.mix_res(xx,d,u,z['mode']))
                for i in range(len(x)):
                    compare(proof['fullResidual'][i],fun(x)[i])
                    for j in range(len(x)):
                        val=dg.mp.diff(lambda y:fun([y if k==j else x[k] for k in range(len(x))])[i],x[j])
                        compare(proof['wholeBoxJacobian'][i][j],val)
                        count+=1
        jacchecks.append(dict(key=key,kind=kind,cornerDerivativeComparisons=count))
    checks.append(dict(check='whole-box Jacobian expressions independently audited at all corners including parameter endpoints',passed=True,rows=jacchecks,
                       limitation='finite differentiation checks are implementation audits, not the enclosure theorem'))
    nesting=[]
    repeats=[]
    for r in results:
        low,high=[x['result'] for x in r['validated']]
        z=r['diagnosticLevels'][-1]['result']
        for kind in ['saturation','mixture']:
            if kind not in high:continue
            p=high[kind]
            assert p['rootExists'] and p['uniqueWithinBox'] and p['strictInclusion'] and F(p['contractionNormUpper'])<1
            for i,x in enumerate(z['sat' if kind=='saturation' else 'mix']):compare(p['box'][i],dg.mp.mpf(x))
            for a in p['fullResidual']:assert F(a['lower'])<=0<=F(a['upper'])
            # Arb uses a fixed-size radius representation. Independently made
            # balls need not nest when midpoint precision changes. Revalidate
            # the EXACT old rational box at 256 bits instead of mistaking
            # nesting of independently rounded ball hulls for a theorem.
            prior=low[kind]
            centers=[str((F(a['lower'])+F(a['upper']))/2) for a in prior['box']]
            radii=[str((F(a['upper'])-F(a['lower']))/2) for a in prior['box']]
            if kind=='saturation':
                tt=prior['parameterTemperature']
                param=va.interval(tt['lower'],tt['upper'])
                system=lambda x:va.sat_system(x,param)
            else:
                dd,uu=dg.target(r['case']['inputBits'])
                system=lambda x:va.mix_system(x,ei.ball(dd),ei.ball(uu),z['mode'])
            again=va.prove(centers,radii,prior['preconditioner'],system,256)[1]
            nesting.append(dict(key=r['case']['key'],kind=kind,
                independentlyRoundedBox256Inside192=all(nested(hi,lo) for hi,lo in zip(high[kind]['box'],low[kind]['box'])),
                pressure256Inside192=nested(high[kind]['pressurePa'],low[kind]['pressurePa']),
                oldRationalBoxRevalidatedAt256=again))
            # Separate original p/g/volume/u expressions on the entire mixture box.
            if kind=='mixture':
                rl,rv,T=[va.interval(x['lower'],x['upper']) for x in p['box']]
                ll,vv=ei.eos(rl,T),ei.eos(rv,T)
                gres=(ll['u']+ll['p']/rl-T*ll['s'])-(vv['u']+vv['p']/rv-T*vv['s'])
                assert gres.contains(0)
                p['independentGResidualAudit']=ei.serialize(gres)
        a,b=[x['result'] for x in r['diagnosticLevels']]
        rep=r['displacedSeed']['result']
        fields=['mix']+(['sat'] if 'sat'in b else [])
        for field in fields:
            assert max(abs(dg.mp.mpf(x)-dg.mp.mpf(y)) for x,y in zip(a[field],b[field]))<dg.mp.mpf('1e-48')
            assert max(abs(dg.mp.mpf(x)-dg.mp.mpf(y)) for x,y in zip(rep[field],b[field]))<dg.mp.mpf('1e-60')
        repeats.append(dict(key=r['case']['key'],precision65vs90=True,displacedSeed90=True))
        assert not high['completePhysicalBranchCertification']
    checks.append(dict(check='precision/seed repeats and enclosure consistency',passed=True,nesting=nesting,repeats=repeats))
    for r in results:
        for v in r['validated']:
            for kind in ['saturation','mixture']:
                if kind not in v['result']:continue
                for endpoint in v['result'][kind]['endpointStability']:
                    assert all(F(x['lower'])>0 for x in endpoint.values())
    assert all(x['oldRationalBoxRevalidatedAt256']['rootExists'] for x in nesting)
    r=lookup['webkit-ledger-76']
    z=r['diagnosticLevels'][-1]['result']
    h=r['validated'][-1]['result']['homogeneous']['temperature']
    negatives=[]
    negatives.append(rejection('non-enclosing-density-box',lambda:va.saturation([str(F(z['sat'][0])+F('1e-8')),z['sat'][1]],z['satInverse'],h['lower'],h['upper'])))
    negatives.append(rejection('singular-preconditioner',lambda:va.saturation(z['sat'],[['0','0'],['0','0']],h['lower'],h['upper'])))
    negatives.append(rejection('equal-density-trivial-root',lambda:va.saturation([z['sat'][1]]*2,z['satInverse'],h['lower'],h['upper'])))
    negatives.append(rejection('negative-density',lambda:ei.eos(ei.ball(-1),ei.ball(345))))
    negatives.append(rejection('zero-temperature',lambda:ei.eos(ei.ball(25),ei.ball(0))))
    negatives.append(rejection('nonfinite-temperature',lambda:ei.eos(ei.ball(25),arb('nan'))))
    negatives.append(rejection('midpoint-proof-cannot-cover-wide-parameter',lambda:va.saturation(z['sat'],z['satInverse'],str(F(z['homT'])-F('1e-8')),str(F(z['homT'])+F('1e-8')))))
    d,u=dg.target(r['case']['inputBits'])
    negatives.append(rejection('bad-homogeneous-seed',lambda:ei.local.enclose(d,u,str(F(z['homT'])+1))))
    # Validated roots with inadmissible signed fractions remain rejected.
    for key,status in [('native-ledger-162','Q_LT_ZERO'),('native-ledger-165','Q_GT_ONE')]:
        p=lookup[key]['validated'][-1]['result']['mixture']
        assert p['rootExists'] and p['qualityStatus']==status and not p['mixtureAdmissible']
        negatives.append(dict(label=key,expected=status,result=p))
    r=lookup['native-ledger-162']
    z=r['diagnosticLevels'][-1]['result']
    d,u=dg.target(r['case']['inputBits'])
    wide=attempt('negative/quality-sign-unresolved',lambda:va.mixture(z['mix'],z['mixInverse'],d,u,z['mode'],radii=('1e-10','1e-10','1e-12'))[1])
    assert wide['success'] and wide['result']['qualityStatus']=='ENDPOINT_SIGN_UNRESOLVED' and not wide['result']['mixtureAdmissible']
    negatives.append(wide)
    r=lookup['generated-dome-interior-homogeneous']['validated'][-1]['result']
    assert r['relativeSide']=='DOME_INTERIOR'
    assert F(r['homogeneousStability']['cv']['lower'])>0 and F(r['homogeneousStability']['dp_drho_T']['lower'])>0
    assert F(r['competingMixtureEntropyAdvantageJkgK']['lower'])>0
    assert not r['completePhysicalBranchCertification']
    negatives.append(dict(label='locally stable homogeneous wrong-phase root',result=r))
    r=lookup['generated-subcooled-liquid']['validated'][-1]['result']
    assert r['mathematicalPressureSupport']=='INSIDE' and not r['completePhysicalBranchCertification']
    negatives.append(dict(label='local pressure/support/stability checks pass; topology proof missing',result=r))
    # An independently verified mixture is a feasible competitor; it is not
    # silently upgraded to global equilibrium proof.
    q=lookup['generated-interior-mixture']['validated'][-1]['result']['mixture']
    assert q['mixtureAdmissible'] and F(q['quality']['lower'])>F('.49') and F(q['quality']['upper'])<F('.51')
    checks.append(dict(check='essential adversarial controls and incomplete proof conditions',passed=True,negativeControls=negatives))
    write('verification.json',dict(checks=checks,seconds=time.perf_counter()-started,completePhysicalCertificates=0,
        trustedAssumptions='correct formula mapping, python-flint/FLINT/Arb arithmetic and runtime; usual additive bulk-phase thermodynamics'))
    print('independent derivative/box/precision audits and adversarial controls passed; no complete physical certificates')

if __name__=='__main__':main()
