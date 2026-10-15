"""Derive the report ledger from raw measurements; no scientific pass laundering."""
import json,hashlib,subprocess,os
from pathlib import Path
from native import save
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B3_EVIDENCE',B/'evidence'))
def read(name):return json.loads((E/name).read_text())
primary='approach-30298.937123458254-liquid-0.001'
def selected(rows,id=primary):return next(r for r in rows if r.get('id',r.get('request',{}).get('id'))==id)
summary=dict(classification='INCONCLUSIVE',reproductions=[],boundaries=[],native=[],traceChecks={})
for browser in ['chromium','webkit']:
 for build in ['official8','build30','build44','official72']:
    d=read(f'{browser}-{build}.json');r=selected(d['rows'])
    summary['reproductions'].append(dict(browser=browser,build=build,browserVersion=d['browserVersion'],
        base=r['base'],inventoryA=r['inventories'].get('A'),inventoryB=r['inventories']['B'],
        repeatsBitIdentical=len({json.dumps(s['bits'],sort_keys=True)for s in r['repeat']})==1,
        baseErrors=[q for q in d['rows']if 'error'in q],probes=sum(len(q['probes'])for q in d['rows'])))
summary['engineEquality']={b:read(f'chromium-{b}.json')['rows']==read(f'webkit-{b}.json')['rows']for b in ['official8','build30','build44','official72']}
summary['official8EqualsSource30Browser']=read('chromium-official8.json')['rows']==read('chromium-build30.json')['rows']
for r in read('chromium-build44.json')['rows']:
 if r['id'].endswith(('liquid-0.001','liquid-0.0','vapor-0.0')) or ('quality-band' in r['id'] and '-hf--' in r['id']):
    summary['boundaries'].append(dict(id=r['id'],args=r['args'],phase=r['base']['phase'],Q=r['base']['state']['Q'],
        residuals={k:r['base'][k]for k in ['pResidual','hResidual']},inventoryB=r['inventories']['B']))
for label in ['wheel8','wheel72','source30','diag30','source44','diag44']:
    d=read(f'native-{label}.json');r=selected(d['rows']);summary['native'].append(dict(label=label,primary=r,
        exceptions=[dict(id=x['request']['id'],error=x['error'])for x in d['rows']if 'error'in x],
        failedPhysicalInventoryA=[dict(id=x['request']['id'],result=x['inventoryA'])for x in d['rows']if 'inventoryA'in x and not x['inventoryA']['canonicalPass']]))
for bits in [30,44]:
    baseline=read(f'native-source{bits}.json')['rows'];diag=read(f'native-diag{bits}.json')['rows']
    raw=[json.loads(l) for l in (E/f'trace{bits}.jsonl').read_text().splitlines()]
    start=next(i for i,e in enumerate(raw)if e.get('marker')==primary)
    stop=next((i for i in range(start+1,len(raw))if 'marker'in raw[i]),len(raw))
    block=raw[start:stop];events=[x for x in block if 'event'in x]
    # The first PH dispatcher belongs to the original requested state. DU calls
    # follow it in this block; they are not mislabeled part of the PH decision.
    dispatch=next(i for i,e in enumerate(events)if e['event']=='PH_dispatch')
    trace=events[:dispatch+1];quality=next(e for e in trace if e['event']=='superanc_quality')
    branch=next(e for e in trace if e['event']=='superanc_selected')
    mechanism=quality['Q']<0 and not quality['below_lower'] and not quality['above_upper'] and branch['phase']==6 and events[dispatch]['homogeneous']==0
    probeRaw=[json.loads(l)for l in (E/f'probes-trace{bits}.jsonl').read_text().splitlines()]
    chunks={};marker=None
    for e in probeRaw:
        if 'marker'in e:
            marker=(e['marker'],e.get('probe'),e.get('repeat'));chunks[marker]=[]
        elif marker is not None:chunks[marker].append(e)
    repeated={f'{k[0]}:{k[1]}':v==chunks.get((k[0],k[1],1)) for k,v in chunks.items()if k[2]==0 and k[0]in [primary,'B1-vapor-regression','isolated-PT']}
    pt=chunks[('isolated-PT',None,0)];assign=next(x for x in reversed(pt)if x['event']=='PT_density_assigned');resid=next(x for x in reversed(pt)if x['event']=='density_residual_call')
    lastfill=next(x for x in reversed(pt)if x['event']=='alphar_cache_fill');hmolar=next(x for x in pt if x['event']=='homogeneous_hmolar')
    summary['traceChecks'][str(bits)]=dict(instrumentedEqualsBaseline=baseline==diag,primaryMechanismCaptured=mechanism,
        primaryDecisionTrace=trace,repeatedTraceEquality=repeated,
        isolatedPT=dict(finalDensityAssignment=assign,lastResidual=resid,lastCacheFill=lastfill,hmolar=hmolar,
            assignedRhoMinusLastEvaluated=assign['rho_molar']-resid['rho_molar'],
            sameCachedDerivativeValues=hmolar['dar_dtau']==lastfill['dar_dtau'] and hmolar['dar_ddelta']==lastfill['dar_ddelta'],
            explicitDeltaMinusCacheFill=hmolar['explicit_delta']-lastfill['delta']))
independent=summary['native'][0]['primary'];rt=independent['reference']
referenceConfirmed=rt['converged'] and all(x>0 for x in rt['stability'].values()) and independent['physicalPhase']=='liquid' and independent['inventoryA']['canonicalPass'] and not independent['inventoryB']['canonicalPass']
summary['independentPhysicalInventoryConfirmation']=referenceConfirmed
if referenceConfirmed and all(v['primaryMechanismCaptured'] and v['instrumentedEqualsBaseline'] for v in summary['traceChecks'].values()) and all(summary['engineEquality'].values()):summary['classification']='ROOT CAUSE CONFIRMED'
pres=read('preservation-start.json');changed=[p for p,h in pres['trackedSHA256'].items()if hashlib.sha256((B.parents[2]/p).read_bytes()).hexdigest()!=h]
summary['preservation']=dict(originalTrackedFiles=len(pres['trackedSHA256']),changed=changed,allA2SnapshotsVerified=all(pres['acceptedA2'].values()))
summary['originalBudgets']=dict(canonical=dict(p_Pa=.1,h_Jkg=.1,T_K=1e-4),standalone=dict(p_Pa=10,h_Jkg=50,T_K=.01),nonlinear=1e-11,
    referenceRoot=dict(p_Pa=1e-5,h_Jkg=1e-8),mass_kg=1e-8,energy_kJ=1e-6,thermal_K=1e-12)
assert not changed
save(E/'summary.json',summary)
print(summary['classification']);print({k:v['instrumentedEqualsBaseline'] for k,v in summary['traceChecks'].items()})
