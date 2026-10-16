"""Independent final-coordinate and phase-decision audit for the seven originals."""
import os
import importlib.util,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5A_EVIDENCE',B/'evidence'));H=B.parent/'browser_eos_b5'
spec=importlib.util.spec_from_file_location('hp',H/'high-precision.py');hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp
blocks={};key=None
for line in (E/'A1-trace-on.jsonl').read_text().splitlines():
 r=json.loads(line)
 if 'marker' in r:key=r['marker'];blocks[key]=[]
 else:blocks[key].append(r)
orig=json.loads((E/'original-failures.json').read_text())['rows'];comp=json.loads((E/'A1-comparison.json').read_text());lut={r['key']:r for r in comp['rows']};rows=[]
for r in orig:
 if r['runtime']!='native-full-VLE':continue
 events=blocks[r['fixedKey']]; entries=[i for i,x in enumerate(events) if x['event']=='DU_entry_rhomolar_umolar_config'];events=events[:entries[1]] if len(entries)>1 else events
 def event(name):return next(x for x in events if x['event']==name)
 entry=event('DU_entry_rhomolar_umolar_config');phase=event('legacy_phase_value_satValue_satT_satRho');exit=event('satD_exit_Tadvanced_TL_TV_error')
 cachedDensity=event('satD_final_rhoL_rhoV_TL_TV')
 evs=[x for x in events if x['event']=='satD_eval_T_rhoL_rhoV_iter'];final=evs[-1];res=[x for x in events if x['event']=='satD_residual_r0_r1_pL_pV'][-1]
 d=mp.mpf(entry['a'])*hp.D['molar_mass'];u=mp.mpf(entry['b'])/hp.D['molar_mass'];seed=r['independentReference']['equilibrium'];liquid=d>hp.dc
 def f(ro,T):
  l,g=(hp.eos(d,T),hp.eos(ro,T)) if liquid else (hp.eos(ro,T),hp.eos(d,T))
  return (l['p']-g['p'])/1e6,(l['g']-g['g'])/1e6
 ro,T=mp.findroot(f,(seed['vapor' if liquid else 'liquid']['values']['rho'],phase['c']),tol=mp.mpf('1e-52'))
 sat=hp.eos(d,T);cached=mp.mpf(phase['b'])/hp.D['molar_mass'];pResidual=res['c']-res['d'];gResidual=float(mp.mpf(res['b'])*hp.D['gas_constant']*mp.mpf(exit['a'])/hp.D['molar_mass'])
 result=lut[r['fixedKey']];old=next(x for x in json.loads((H/'evidence/trace-audit.json').read_text())['rows'] if x['fixedKey']==r['fixedKey'])
 # Original B5 failure matrix is authoritative at its reference resolution.
 isResolved=r['fixedKey'] in ['native-ledger-146','native-ledger-151','native-ledger-152']
 outcome='resolved-stable-liquid' if isResolved and 'DU' in result and result['DU']['values']['phase']==0 else 'endpoint-unresolved' if not isResolved else 'FAILED'
 checks=dict(finalCacheMatchesEvaluatedCoordinates=exit['a']==exit['b']==exit['c']==final['a'],imposedDensityPreserved=phase['d']==entry['a'],bothCachedDensitiesMatchEvaluatedCoordinates=cachedDensity['a']==final['b'] and cachedDensity['b']==final['c'],pressureWithinOriginalReference=abs(pResidual)<1e-5,chemicalPotentialWithinOriginalReference=abs(gResidual)<1e-8)
 if isResolved:checks.update(positiveResolvedEnergySeparation=entry['b']>phase['b'],stableLiquidRecovered='DU' in result and result['DU']['values']['phase']==0,canonical=result.get('canonicalPass',False),nonlinear=result.get('nonlinearPass',False))
 rows.append(dict(key=r['fixedKey'],id=r['id'],originalClassification='liquid' if isResolved else 'endpoint-unresolved at original reference resolution',disposition=outcome,checks=checks,result=result,phaseDecision=phase,finalSaturation=exit,finalEvaluation=final,finalCachedDensities=cachedDensity,pressureDifferencePa=pResidual,chemicalPotentialDifferenceJkg=gResidual,saturationEvaluations=len(evs),originalSaturationEvaluations=sum(x['event']=='satD_eval_T_rhoL_rhoV_iter' for x in old['events']),comparison=hp.enc(dict(trueUminusSatU=u-sat['u'],cachedUminusTrueSatU=cached-sat['u'],inputMinusCachedSatU=u-cached,finalTerror=mp.mpf(exit['a'])-T)),events=events))
resolvedCross=[]
refs={x['key']:x['reference'] for x in json.loads((E/'independent-fixed-references.json').read_text())['rows']}
for r in comp['crossPath']:
 # Retain all cross-path rows. Resolution tests below select only phase-resolved roots.
 eq=refs[r['key']]['equilibrium'];quality=eq['state']['values']['Q']
 if min(abs(quality),abs(quality-1))>1e-12:
  resolvedCross.append(dict(key=r['key'],fullVLE=r['fullVLE'],pass_=r.get('canonicalPass',False) and r.get('nonlinearPass',False) and r.get('physicalQuality',False),referenceQ=quality))
focused=json.loads((E/'native-A1-full-vle.json').read_text())['rows']
resolvedFocused=[]
for r in focused:
 if r.get('base',{}).get('physicalPhase') in ['liquid','gas'] and r['request']['args'][0]<=3500000:
  c=r.get('inventories',{}).get('C',{});resolvedFocused.append(dict(id=r['request']['id'],physicalPhase=r['base']['physicalPhase'],canonicalPass=c.get('canonicalPass',False),error=c.get('error')))
out=dict(rows=rows,resolvedCrossPath=resolvedCross,resolvedFocused=resolvedFocused,gateAApplicableChecksPass=all(all(r['checks'].values()) for r in rows) and all(r['pass_'] for r in resolvedCross) and all(r['canonicalPass'] for r in resolvedFocused),gateBPassed=False,endpointUncertaintyRetained=True)
p=E/'gate-A-audit.json';assert not p.exists(),p
p.write_text(json.dumps(out,indent=2)+'\n');print('Gate A applicable checks',out['gateAApplicableChecksPass']);print([(r['key'],r['disposition'],r['checks']) for r in rows])
