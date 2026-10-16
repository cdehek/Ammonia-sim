"""Independently join trace events to exact inventories and EOS saturation roots."""
import json,importlib.util
from pathlib import Path
import os
B=Path(__file__).resolve().parent;E=Path(os.environ.get('B5_EVIDENCE',B/'evidence'));spec=importlib.util.spec_from_file_location('hp',B/'high-precision.py');hp=importlib.util.module_from_spec(spec);spec.loader.exec_module(hp);mp=hp.mp
def read(f):return json.loads((E/f).read_text())
base=read('rebuilt-uninstrumented.json')['rows'];on=read('trace-on-results.json')['rows'];off=read('trace-off-results.json')['rows'];arch=read('native-fixed-replay.json')['rows']
assert base==on==off
assert all(a['reused']=={k:v for k,v in b['result']['B4C'].items()if k!='strictSupport'}for a,b in zip(base,arch))
blocks={};key=None
for line in (E/'trace-on.jsonl').read_text().splitlines():
 r=json.loads(line)
 if'marker'in r:key=r['marker'];blocks[key]=[]
 else:blocks[key].append(r)
rows=[]
for r in read('original-failures.json')['rows']:
 if r['runtime']!='native-full-VLE':continue
 events=blocks[r['fixedKey']];entry=next(x for x in events if x['event']=='DU_entry_rhomolar_umolar_config');phase=next(x for x in events if x['event']=='legacy_phase_value_satValue_satT_satRho');exit=next(x for x in events if x['event']=='satD_exit_Tadvanced_TL_TV_error');ret=next(x for x in events if x['event']=='legacy_two_phase_return_Treturn_Tstate_Qd')
 assert entry['c']==0 and phase['a']<=phase['b'] and (ret['c']<0 or ret['c']>1)
 # Use the actual INTERNAL molar density/value, including mass-to-molar rounding.
 M=hp.D['molar_mass'];d=mp.mpf(entry['a'])*M;u=mp.mpf(entry['b'])/M
 seed=r['independentReference']['equilibrium'];l=seed['liquid']['values'];g=seed['vapor']['values'];liquid=d>hp.dc
 def f(rOther,T):
  L,G=(hp.eos(d,T),hp.eos(rOther,T))if liquid else(hp.eos(rOther,T),hp.eos(d,T))
  return ((L['p']-G['p'])/1e6,(L['g']-G['g'])/1e6)
 ro,T=mp.findroot(f,(g['rho']if liquid else l['rho'],phase['c']),tol=mp.mpf('1e-52'))
 sat=hp.eos(d,T);trueAbove=u-sat['u'];legacyAbove=(mp.mpf(phase['a'])-mp.mpf(phase['b']))/M
 # Re-evaluate saturated coordinates at the advanced temperature without changing
 # the accepted implementation: this is an independent diagnostic only.
 advanced=hp.eos(d,mp.mpf(exit['a']))
 vals=dict(exactInternalMassDensity=d,exactInternalMassEnergy=u,independentSatT=T,independentSatU=sat['u'],trueUminusSatU=trueAbove,legacyUminusSatU=legacyAbove,legacySatUerror=mp.mpf(phase['b'])/M-sat['u'],advancedTerror=mp.mpf(exit['a'])-T,lastEvaluatedTerror=mp.mpf(exit['b'])-T,advancedEOSUminusTrueSatU=advanced['u']-sat['u'])
 rows.append(dict(failureKey=r['failureKey'],fixedKey=r['fixedKey'],phase=phase,saturationExit=exit,twoPhaseReturn=ret,satRoot=hp.enc(sat),comparison=hp.enc(vals),decisionSignWrong=bool(trueAbove>0),events=events[:len(events)//2],exceptionLocation='HelmholtzEOSMixtureBackend.cpp:1547 QT_INPUTS quality range check, reached from HSU_D_flash_twophase final HEOS.update(QT_INPUTS,resid.Qd,HEOS.T())'))
out=dict(loggingParity=True,archivalParity=True,freshReusedEqual=all(r['equal']for r in base),rows=rows,traceEvents=sum(len(x)for x in blocks.values()),markerCount=len(blocks),eventFields='See TRACE_SCHEMA.md; a,b,c,d field meanings are encoded in each event name and exact source patch.')
(E/'trace-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('trace verified',len(rows),'original failures;',sum(x['decisionSignWrong']for x in rows),'wrong phase-decision signs')
