"""Independent evidence checks; an audit PASS is not backend qualification."""
import hashlib, json, math, statistics, struct, sys
from pathlib import Path
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B));import math_reference as m
E=m.E;mp=m.mp
def load(n):return json.loads((E/n).read_text())
def run():
    m.precision(90);fixed=load('fixed-inputs.json');refs=load('mathematical-references.json')['rows']
    dp=load('binary64-results.json')['rows'];native=load('native-neighbors.json')['rows'];rep=load('four-case-reproduction-and-controls.json')['rows']
    assert len(fixed)==7 and len(refs)==len(dp)==len(native)==47
    assert {r['key']for r in fixed}=={'native-ledger-'+str(i)for i in [146,148,151,152,162,164,165]}
    assert all(r['equal']for r in native)
    repeat=[];originals=[];neighborhood=[]
    for r in refs:
        assert 'error'not in r,r
        c=r['case'];d,u=mp.mpf(c['rho']),mp.mpf(c['u'])
        assert all(m.bits(c[k])==c['bits'][k]for k in ['rho','u'])
        final=r['levels'][-1];e=final['equilibrium'];h=final['homogeneous']
        if c['label']=='exact saved inventory':
            a,b=r['levels'];s=b['selection'];delta={k:mp.mpf(b[s][k])-mp.mpf(a[s][k])for k in ['T','p']}
            assert abs(delta['T'])<mp.mpf('1e-4')and abs(delta['p'])<mp.mpf('1e-5')
            l,v=m.hp.eos(mp.mpf(e['rhoL']),mp.mpf(e['T'])),m.hp.eos(mp.mpf(e['rhoV']),mp.mpf(e['T']))
            # Audit volume with independent reciprocal-volume formula.
            q=(1/d-1/l['rho'])/(1/v['rho']-1/l['rho'])
            ru=(1-q)*l['u']+q*v['u']-u;rv=(1-q)/l['rho']+q/v['rho']-1/d
            assert abs(l['p']-v['p'])<mp.mpf('1e-5')and abs(l['g']-v['g'])<mp.mpf('1e-8')and abs(ru)<mp.mpf('1e-8')
            assert (0<=q<=1 and e['liquidStability']['positive'] and e['vaporStability']['positive']) if s=='equilibrium' else h['stableSideOfSaturation'] and h['stability']['positive']
            z=next(x for x in dp if x['case']['key']==c['key']);ff=[a['result']['final']for a in z['attempts']]
            originals.append(dict(key=c['key'],mathematicalSelection=s,precisionDelta=delta,independentlyReevaluatedResiduals=dict(p=l['p']-v['p'],mu=l['g']-v['g'],u=ru,volume=rv),
                binary64QualityRange=[min(f['Q']for f in ff),max(f['Q']for f in ff)],binary64AdmissibleAttemptCount=sum(f['physicalQuality']for f in ff),binary64Attempts=len(ff),
                A='YES: same-EOS mathematical solution',B='NOT DEMONSTRATED: certified binary64 recovery' if c['key']in ['native-ledger-148','native-ledger-162','native-ledger-164','native-ledger-165']else 'inherited resolved liquid control',
                C='UNRESOLVED: original independent physical phase resolution and browser qualification' if c['key']in ['native-ledger-148','native-ledger-162','native-ledger-164','native-ledger-165']else 'inherited focused native control passes; no new backend qualification'))
        z=next(x for x in dp if x['case']['key']==c['key']);n=next(x for x in native if x['case']['key']==c['key']);ff=[a['result']['final']for a in z['attempts']if 'result'in a]
        neighborhood.append(dict(key=c['key'],originalKey=c['originalKey'],label=c['label'],mathematicalSelection=final['selection'],mathematicalQ=e['Q'],binary64AdmissibleAttempts=sum(f['physicalQuality']for f in ff),binary64Attempts=len(z['attempts']),nativeError=n['reused'].get('error'),freshReusedEqual=n['equal']))
    for s in load('seed-sensitivity.json'):
        assert 'error'not in s
        eq=next(r for r in refs if r['case']['key']==s['key'])['levels'][0]['equilibrium']
        repeat.append(dict(key=s['key'],seedOffsetK=s['offsetK'],dT=mp.mpf(s['result']['T'])-mp.mpf(eq['T']),dQ=mp.mpf(s['result']['Q'])-mp.mpf(eq['Q']),iterations=s['result']['convergence']['iterations']))
    ff=[a['result']for r in dp for a in r['attempts']if 'result'in a]
    costs=[z['seconds']for z in ff];hp=[z['equilibrium']['convergence']for r in refs for z in r['levels']]
    # Verify exact originals, native outcomes, and original controls individually.
    for r in rep:
        result=r['result']['reused'];assert r['result']['equal']
        if r['key']in ['native-ledger-148','native-ledger-164','native-ledger-165']:assert result['error']=='Error: Input vapor quality [Q] must be between 0 and 1'
        else:assert result['DU']['values']['phase']==0
    summary=dict(finalClassification='CONDITIONALLY FEASIBLE',originals=originals,seedRepeats=repeat,neighborRows=neighborhood,
        native=dict(rows=47,exceptions=sum('error'in r['reused']for r in native),freshReusedDifferences=0,medianUpdateSeconds=statistics.median(r['reusedSeconds']for r in native)),
        binary64=dict(attempts=sum(len(r['attempts'])for r in dp),exceptions=sum('error'in a for r in dp for a in r['attempts']),originalReferenceResidualPasses=sum(z['final']['originalReferenceResidualsPass']for z in ff),
            medianSeconds=statistics.median(costs),maxSeconds=max(costs),scaledConditionRange=[min(z['final']['jacobianConditionScaled']for z in ff),max(z['final']['jacobianConditionScaled']for z in ff)],
            terminationCounts={t:sum(z['termination']==t for z in ff)for t in sorted(set(z['termination']for z in ff))}),
        highPrecision=dict(equilibriumSolves=len(hp),medianSeconds=statistics.median(z['seconds']for z in hp),maxSeconds=max(z['seconds']for z in hp),minIterations=min(z['iterations']for z in hp),maxIterations=max(z['iterations']for z in hp)),
        auditPass=True,backendQualified=False,acceptedScientificBudgetsUnchanged=True,browserCandidateExecuted=False)
    m.write('scientific-audit.json',summary)
    lines=['| Inventory | Perturbation | Mathematical branch | Float64 admissible attempts / 6 | Gate A raw outcome |','|---|---|---|---:|---|']
    for r in neighborhood:
        if r['originalKey']in ['native-ledger-146','native-ledger-151','native-ledger-152']:continue
        lines.append(f"| {r['key']} | {r['label']} | {r['mathematicalSelection']} | {r['binary64AdmissibleAttempts']} | {'QT exception' if r['nativeError'] else 'returned'} |")
    p=B/'NEIGHBORS.md';text='# Bounded diagnostic neighborhood\n\n'+ '\n'.join(lines)+'\n\nAdmissible means only that the algebraic mixture fraction lies in [0,1]. It does not certify the correct branch. All quantities use the exact labeled rho/u bits in `evidence/cases.json`. Modified neighbors never replace originals. The +0.01 J/kg cases have stable homogeneous mathematical roots; their extrapolated mixture rejection is expected. All 13 native exceptions remain in evidence. No derivative smoothness is imposed across saturation.\n'
    if p.exists():assert p.read_text()==text,'Generated neighbor report differs; preserve and investigate'
    else:p.write_text(text)
    print('scientific evidence audit PASS; backend NOT qualified; CONDITIONALLY FEASIBLE')
if __name__=='__main__':run()
