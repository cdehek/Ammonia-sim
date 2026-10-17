"""Independent build/ABI/activation gate. No scientific acceptance relaxation."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';read=lambda n:json.loads((E/n).read_text())
assert read('abi-generated-source.json')['allMatch'] and read('wasm-abi-inventory.json')['allMatch']
assert read('dependency-verification.json')['allNineMatch']
assert read('native-inherited-audit.json')['passOriginalFocusedRequirements']
candidate=read('source-candidate.json')['trackedSourceSHA256'];S=Path('/workspace/b7-work/upstream')
assert all(hashlib.sha256((S/n).read_bytes()).hexdigest()==h for n,h in candidate.items())
rows=[];activation=[]
for engine in ['chromium','webkit']:
 d=read(f'abi-{engine}-corrected.json');assert 'harnessError' not in d
 for r in d['result']['rows']:
  assert r['baseline']==r['after']==dict(uncaught=0,observedCatchDepth=0)
  catches=[(i,e) for i,e in enumerate(r['events']) if e['kind']=='loader-catch' and e.get('header')]
  assert len(catches)==16
  for index,event in catches:
   assert event['raw']['type']=='object' and event['raw']['constructor']=='CppException'
   assert event['header']['referenceCount']==event['header']['caught']==event['header']['rethrown']==0
   after=r['events'][index+1:]
   begin=next(e for e in after if e['kind']=='__cxa_begin_catch' and e['stage']=='before')
   end=next(e for e in after if e['kind']=='__cxa_end_catch' and e['stage']=='before')
   assert begin['header']['ptr']==end['header']['ptr']==event['header']['ptr']
   assert begin['header']['referenceCount']==0 and end['header']['referenceCount']==1
   assert begin['uncaught']==1 and end['uncaught']==0
   assert begin['stack']-event['stack']==2928
  assert not r['high']['error']['nativeException']
  assert all(x['rejection']['error']['nativeException'] and x['supported'].get('value') for x in r['operations'])
  rows.append(dict(engine=engine,artifact=r['id'],nativeEscapes=16,baseline=r['baseline'],after=r['after'],representation='CppException',liveReferenceAtEscape=0,referenceBeforeEndCatch=1,stackRestoreBytes=2928,highLevelSeparatelyCaught=True))
 d=read(f'activation-{engine}.json');assert 'harnessError' not in d
 for r in d['result']['rows']:
  for index,normal in enumerate(r['normal']):
   for variant in ['reused','fresh']:
    def sig(z):return z.get('state',z.get('error'))
    assert sig(normal[variant])==sig(r['loggingOn'][index][variant])==sig(r['loggingOff'][index][variant]),(engine,r['base'],r['fullVLE'],normal['key'],variant,'logging parity')
   trace=r['loggingOn'][index]['reused']['trace'];by=lambda name:[e for e in trace if e['event']==name]
   entry=by('HSU_D_entry_rho_u_config_other');assert len(entry)==1
   assert entry[0]['c']==int(not r['fullVLE']) and entry[0]['d']==31
   if r['fullVLE']:
    assert by('legacy_DU_entry') and by('saturation_D_entry_rho_polish_imposed_iterations')
    polish=by('DU_saturation_options_polish_other')[0]['a'];assert polish==int(r['base']=='gateA')
    if r['base']=='gateA':
     final=by('saturation_D_final_T_rhoL_rhoV_error')[-1];cache=by('saturation_D_cached_TL_rhoL_TV_rhoV')[-1];evaluated=by('saturation_D_evaluated_T_rhoL_rhoV_iteration')[-1];decision=by('DU_caloric_value_satvalue_T_rho')[0]
     assert final['a']==cache['a']==cache['c']==evaluated['a']
     assert final['b']==cache['b']==evaluated['b'] and final['c']==cache['d']==evaluated['c']
     assert decision['c']==final['a'] and decision['d'] in [final['b'],final['c']]
     if normal['key'] in ['native-ledger-146','native-ledger-151','native-ledger-152']:
      assert decision['a']>decision['b'] and not by('legacy_dispatch_twophase')
      assert normal['reused']['state']['values']['phase']==0
    else:assert normal['reused']['error']['message']=='Input vapor quality [Q] must be between 0 and 1'
   else:assert not by('legacy_DU_entry') and not by('saturation_D_entry_rho_polish_imposed_iterations')
  activation.append(dict(engine=engine,artifact=r['base'],fullVLE=r['fullVLE'],records=7,loggingOnOffUninstrumentedExact=True,actualCompiledPathObserved=True))
out=dict(gate1='PASS',buildAndABIVerified=True,liveOwnership=rows,activation=activation,scope='Exact scientific source and unchanged generated ABI; full VLE accessible through isolated WASI environment harness. Broader scientific/regression/compatibility gates still required.')
t=E/'gate1-audit.json';assert not t.exists();t.write_text(json.dumps(out,indent=2)+'\n');print('Gate 1 PASS: exact sources/builds, actual generated ABI, live ownership, full-VLE access and logging parity verified')
