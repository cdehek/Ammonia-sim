"""Actual matched-native shared callers against accepted records and both engines."""
import ctypes as ct,json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence';sys.path.insert(0,str(X/'browser_eos_b3'))
from native import Backend,pack
read=lambda p:json.loads(p.read_text());rows=[]
pairs=dict(PH='HmassP_INPUTS',PS='PSmass_INPUTS',PU='PUmass_INPUTS',DH='DmassHmass_INPUTS',DS='DmassSmass_INPUTS',DP='DmassP_INPUTS')
fields=dict(p='P',h='Hmass',T='T',rho='Dmass',u='Umass',Q='Q',phase='Phase',s='Smass')
def close(e):
 e.lib.AbstractState_free.argtypes=[ct.c_long,ct.POINTER(ct.c_long),ct.c_char_p,ct.c_long];e.call(e.lib.AbstractState_free,e.handle)
def call(e,r):
 a,b=r['input'];a,b=(b,a) if r['mode']=='PH' else (a,b)
 try:
  e.call(e.lib.AbstractState_update,e.handle,e.lib.get_input_pair_index(pairs[r['mode']].encode()),a,b)
  return dict(state=pack({k:e.call(e.lib.AbstractState_keyed_output,e.handle,e.lib.get_param_index(v.encode())) for k,v in fields.items()}))
 except Exception as error:return dict(error=str(error))
def agree(out,expected,require_phase=True):
 if 'error' in out:return 'error' in expected
 if 'state' not in expected:return False
 a,b=out['state']['values'],expected['state']['values']
 return (not require_phase or a['phase']==b['phase']) and all(abs(a[k]-b[k])<=limit for k,limit in dict(p=.1,h=.1,T=1e-4).items())
for label in ['control','candidate']:
 path='/workspace/b7-work/native/'+label+'.so';e=Backend(path);e.lib.set_config_bool.argtypes=[ct.c_char_p,ct.c_bool]
 try:
  for full in [False,True]:
   e.lib.set_config_bool(b'ENABLE_SUPERANCILLARIES',not full)
   cases=read(E/'shared-chromium.json')['result']['rows'];cases=next(r for r in cases if r['id']==('gateA' if label=='candidate' else 'rebuiltB4C') and r['fullVLE']==full)['results']
   pressure=read(X/f'browser_eos_b5a/evidence/shared-A1-{"full-vle" if full else "default"}.json')['rows'];density=read(X/'browser_eos_b5a/evidence/shared-density.json')['rows']
   for r in cases:
    out=call(e,r);fresh=Backend(path)
    try:f=call(fresh,r)
    finally:close(fresh)
    assert out==f,(label,full,r['id'],r['mode'],'native fresh/reused')
    if r['mode'] in ['PH','PS','PU']:
     old=next(q for q in pressure if q['id']==r['id'] and q['inputBits']==r['inputBits']);expected={'state':old['state']} if 'state' in old else {'error':old['error']}
    else:
     old=next(q for q in density if q['mode']==r['mode'] and q['fullVLE']==full and q['inputBits']==r['inputBits']);expected=old['result']['A1']
    assert agree(out,expected),(label,full,r['id'],r['mode'],'accepted native comparison')
    comparisons=[]
    for engine in ['chromium','webkit']:
     block=next(q for q in read(E/f'shared-{engine}.json')['result']['rows'] if q['id']==('gateA' if label=='candidate' else 'rebuiltB4C') and q['fullVLE']==full)
     browser=next(q for q in block['results'] if q['id']==r['id'] and q['mode']==r['mode'] and q['inputBits']==r['inputBits'])['reused']
     assert agree(out,browser,False),(engine,label,full,r['id'],r['mode'],'original numeric limits')
     endpoint=r['id'].endswith(('-hf','-hg','-hf-minus-ULP','-hf-plus-ULP','-hg-minus-ULP','-hg-plus-ULP'))
     phase_difference='state' in out and out['state']['values']['phase']!=browser['state']['values']['phase']
     if phase_difference:assert endpoint,(engine,label,full,r['id'],r['mode'],'resolved phase mismatch')
     historical_exact=None
     if not full and r['mode'] in ['PH','PS','PU']:
      historical=read(X/f'browser_eos_b4c/evidence/{engine}-candidateB-shared.json')['rows']
      old_browser=next(q for q in historical if q['id']==r['id'] and q['inputBits']==r['inputBits'])
      historical_exact=all(browser['state']['values'][k]==v for k,v in old_browser['state'].items())
      assert historical_exact,(engine,r['id'],'original browser shared behavior changed')
     comparisons.append(dict(engine=engine,difference={k:browser['state']['values'][k]-out['state']['values'][k] for k in ['p','h','T','s']} if 'state' in out else None,errorPreserved='error' in out,nativeBrowserPhaseDifference=phase_difference,originalEndpointControl=endpoint,nativePhase=out.get('state',{}).get('values',{}).get('phase'),browserPhase=browser.get('state',{}).get('values',{}).get('phase'),historicalDefaultBrowserExact=historical_exact,phaseQualification='Original endpoint control remains unresolved; numerical agreement is not phase certification' if phase_difference else 'Original qualification unchanged'))
    rows.append(dict(label=label,fullVLE=full,id=r['id'],mode=r['mode'],input=r['input'],inputBits=r['inputBits'],reused=out,fresh=f,browserComparisons=comparisons))
 finally:close(e)
out=dict(passed=True,rows=rows,entropyDifferencesRecordedWithoutInventingAnEntropyBudget=True,canonicalComparisonBudgets=dict(p=.1,h=.1,T=1e-4),originalErrorsRetained=True)
p=E/'shared-native-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Actual native PH/PS/PU/DH/DS/DP fresh/reused and both-browser comparisons PASS;',len(rows),'native records')
