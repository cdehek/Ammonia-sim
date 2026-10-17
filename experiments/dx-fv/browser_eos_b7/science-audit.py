"""Independent fresh EOS and preserved-reference checks for seven/250 inventories."""
import argparse,hashlib,importlib.util,json,struct,sys
from pathlib import Path
from CoolProp import AbstractState,CoolProp as C
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';read=lambda n:json.loads((E/n).read_text())
p=argparse.ArgumentParser();p.add_argument('--stage',choices=['seven','ledger'],required=True);a=p.parse_args()
inputs=read('fixed-inputs.json');canonical=read('canonical-provenance.json');hp={r['key']:r['reference'] for r in read('high-precision-references.json')['rows']}
references={r['key']:r['reference'] for r in read('independent-fixed-references.json')['rows']}
failures=[];rows=[]
def check(value,kind,**detail):
 if not value:failures.append(dict(kind=kind,**detail))
def differences(s,t):return {k:s[k]-t[k] for k in ['p','h','T']}
def budgets(d,strict=False):return all(abs(d[k])<limit if strict else abs(d[k])<=limit for k,limit in (dict(p=10,h=50,T=.01) if strict else dict(p=.1,h=.1,T=1e-4)).items())
def audit(record,out):
 key=record['key'];x=record['input']['values'];s=out['state']['values'];ref=hp[key];selected=ref['selection'];rs={k:float(v) for k,v in ref[selected].items()}
 dt=AbstractState('HEOS','Ammonia')
 physicalQuality=s['phase']!=6 or 0<=s['Q']<=1
 if s['phase']==6:
  if not physicalQuality:return dict(physicalQuality=False,pass_=False)
  dt.update(C.QT_INPUTS,s['Q'],s['T'])
 else:
  dt.specify_phase(C.iphase_liquid if s['phase']==0 else C.iphase_gas);dt.update(C.DmassT_INPUTS,s['rho'],s['T'])
 fresh=dict(p=dt.p(),h=dt.hmass(),u=dt.umass(),rho=dt.rhomass(),T=dt.T())
 normalized=dict(mass=abs((fresh['rho']-x['rho'])*x['V'])/max(.01,x['M']),energy=abs(x['M']*fresh['u']/1000-x['U_kJ'])/max(1,abs(x['U_kJ'])))
 can=differences(s,canonical[key]);dr=differences(s,rs);getter={k:s[k]-fresh[k] for k in ['p','h','u']}
 stability=None
 if s['phase']!=6:stability=dict(cp=dt.cpmass(),cv=dt.cvmass(),kappa=dt.isothermal_compressibility(),pRho=dt.first_partial_deriv(C.iP,C.iDmass,C.iT))
 result=dict(canonical=can,referenceDifference=dr,mathematicalReferenceSelection=selected,freshEOS=fresh,getterDifference=getter,normalizedMassEnergy=normalized,stability=stability,physicalQuality=physicalQuality,strictRawPressureSupport=3e4<=s['p']<=35e5,canonicalPass=budgets(can),standalonePass=budgets(dr,True),referenceComparisonPass=budgets(dr),freshEOSPass=all(v<=1e-11 for v in normalized.values()) and all(abs(v)<=.1 for v in getter.values()))
 result['pass_']=all(result[k] for k in ['canonicalPass','standalonePass','referenceComparisonPass','freshEOSPass','physicalQuality'])
 return result
native={label:read('native-'+label+'-comparison.json') for label in ['control','candidate']}
nativeCross={label:{(r['input']['bits']['rho'],r['input']['bits']['u'],r['fullVLE']):r for r in data['crossPath']} for label,data in native.items()}
resolved=['native-ledger-146','native-ledger-151','native-ledger-152'];unresolved=['native-ledger-148','native-ledger-162','native-ledger-164','native-ledger-165']
if a.stage=='seven':
 spec=importlib.util.spec_from_file_location('unchanged_hp',X/'browser_eos_b5/high-precision.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);mp=module.mp
 for engine in ['chromium','webkit']:
  data=read(f'activation-{engine}.json')['result']['rows']
  control=next(r for r in data if r['base']=='rebuiltB4C' and r['fullVLE']);candidate=next(r for r in data if r['base']=='gateA' and r['fullVLE'])
  for r,z,c,traced in zip(inputs and candidate['normal'],control['normal'],candidate['normal'],candidate['loggingOn']):
   key=r['key'];record=next(q for q in inputs if q['key']==key);original=r['input'];check(original==record['input'],'originalInputs',key=key)
   check(z['reused'].get('error',{}).get('message')=='Input vapor quality [Q] must be between 0 and 1','controlDefect',key=key)
   check(c['reused'].get('state')==c['fresh'].get('state') and c['reused'].get('error')==c['fresh'].get('error'),'freshReused',key=key)
   result=audit(record,c['reused']) if 'state' in c['reused'] else None
   trace=traced['reused']['trace'];event=lambda name:[e for e in trace if e['event']==name][-1]
   entry=event('HSU_D_entry_rho_u_config_other');phase=event('DU_caloric_value_satvalue_T_rho');final=event('saturation_D_final_T_rhoL_rhoV_error');residual=event('saturation_D_residual_r0_r1_pL_pV')
   refinements=[]
   for dps in [65,90]:
    with mp.workdps(dps):
     d=mp.mpf(entry['a'])*module.D['molar_mass'];u=mp.mpf(entry['b'])/module.D['molar_mass'];liquid=d>module.dc
     seed=references[key]['equilibrium']['vapor' if liquid else 'liquid']['values']['rho']
     def equations(ro,T):
      L,V=(module.eos(d,T),module.eos(ro,T)) if liquid else (module.eos(ro,T),module.eos(d,T))
      return (L['p']-V['p'])/mp.mpf(1e6),(L['g']-V['g'])/mp.mpf(1e6)
     ro,T=mp.findroot(equations,(seed,phase['c']),tol=mp.mpf('1e-52'),maxsteps=15);sat=module.eos(d,T);cached=mp.mpf(phase['b'])/module.D['molar_mass']
     refinement=module.enc(dict(trueUminusSatU=u-sat['u'],cachedUminusTrueSatU=cached-sat['u'],inputMinusCachedSatU=u-cached,finalTerror=mp.mpf(final['a'])-T));refinement['dps']=dps;refinements.append(refinement)
   pressureResidual=residual['c']-residual['d'];chemical=float(mp.mpf(residual['b'])*module.D['gas_constant']*mp.mpf(final['a'])/module.D['molar_mass'])
   check(abs(pressureResidual)<1e-5 and abs(chemical)<1e-8,'saturationReferenceResidual',key=key)
   if key in resolved:
    check(result and result['pass_'] and c['reused']['state']['values']['phase']==0,'resolvedLiquidScience',engine=engine,key=key,result=result)
    check(all(float(x['trueUminusSatU'])>1e-8 and abs(float(x['cachedUminusTrueSatU']))<1e-8 and float(x['inputMinusCachedSatU'])>0 for x in refinements),'independentCaloricSign',key=key)
    nativeResult=nativeCross['candidate'][(record['input']['bits']['rho'],record['input']['bits']['u'],True)]['DU']['values'];nativeDiff=differences(c['reused']['state']['values'],nativeResult);check(budgets(nativeDiff),'nativeA1Agreement',key=key)
    disposition='resolved-stable-liquid'
   else:
    nativeDiff=None;disposition='unresolved physical phase despite raw liquid return' if key.endswith('-162') else 'unresolved historical QT refusal'
    check('state' in c['reused'] if key.endswith('-162') else c['reused'].get('error',{}).get('message')=='Input vapor quality [Q] must be between 0 and 1','endpointDifference',key=key)
   rows.append(dict(engine=engine,key=key,disposition=disposition,input=original,control=z['reused'],candidate=c['reused'],science=result,nativeDifference=nativeDiff,pressureResidual=pressureResidual,chemicalPotentialResidual=chemical,independentSaturation=refinements,physicalQualification=key in resolved))
else:
 for engine in ['chromium','webkit']:
  data=read(f'ledger-{engine}.json')['result']['rows'];lookup={(r['id'],r['fullVLE']):r for r in data}
  for block in data:
   label='candidate' if block['id']=='gateA' else 'control';full=block['fullVLE'];check(len(block['records'])==250,'recordCount',engine=engine)
   for r in block['records']:
    key=r['key'];original=next(q for q in inputs if q['key']==key);check(original['input']==r['input'],'originalInputBits',key=key)
    check(r['reused'].get('state')==r['fresh'].get('state') and r['reused'].get('error')==r['fresh'].get('error'),'freshReused',key=key,engine=engine,full=full)
    nativeResult=nativeCross[label][(r['input']['bits']['rho'],r['input']['bits']['u'],full)]
    out=r['reused'];result=audit(r,out) if 'state' in out else None
    if result:check(result['pass_'],'originalLedgerBudgets',engine=engine,artifact=block['id'],full=full,key=key,result=result)
    if 'state' in out and 'DU' in nativeResult:
     nd=differences(out['state']['values'],nativeResult['DU']['values']);check(budgets(nd),'nativeWasmAgreement',engine=engine,key=key,full=full)
     check(out['state']['values']['phase']==nativeResult['DU']['values']['phase'],'nativePhase',engine=engine,key=key,full=full)
    else:
     nd=None;check(('error' in out)==('error' in nativeResult),'nativeOutcomeDifference',engine=engine,key=key,full=full,artifact=block['id'])
    if not full:
     other=lookup[('gateA' if block['id']=='rebuiltB4C' else 'rebuiltB4C',False)]['records'];other=next(q for q in other if q['key']==key)
     check(out.get('state')==other['reused'].get('state') and out.get('error')==other['reused'].get('error'),'defaultEquivalence',key=key)
    rows.append(dict(engine=engine,artifact=block['id'],fullVLE=full,key=key,science=result,nativeDifference=nd,error=out.get('error'),qualification='Original unresolved endpoint contract retained; numerical checks alone do not certify a physical phase'))
out=dict(stage=a.stage,passed=not failures,rows=rows,failures=failures,budgets=dict(canonical=dict(p=.1,h=.1,T=1e-4),standaloneStrict=dict(p=10,h=50,T=.01),normalizedMassEnergy=1e-11,independentReferenceResolution=dict(p=1e-5,energy=1e-8)),unresolvedEndpointsRetained=unresolved,fullGateBPassed=False)
target=E/f'{a.stage}-science-audit.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n')
print(a.stage,'science audit',out['passed'],'rows',len(rows),'failures',len(failures));print(failures[:4]);sys.exit(bool(failures))
