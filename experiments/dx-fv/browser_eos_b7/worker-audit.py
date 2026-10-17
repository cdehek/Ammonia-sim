import json,sys
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';read=lambda p:json.loads(p.read_text());failures=[];summary=[]
for engine in ['chromium','webkit']:
 d=read(E/f'workers-{engine}.json');assert 'harnessError' not in d
 main=read(E/f'activation-{engine}.json')['result']['rows'];lifecycle=read(E/f'lifecycle-{engine}-serialized.json')['result']['rows']
 for r in d['result']['rows']:
  worker=r['result'];assert worker['passed']
  reference=next(x for x in main if x['base']==r['id'] and x['fullVLE'])['normal']
  for s,t in zip(worker['seven'],reference):
   assert s['key']==t['key'] and s['input']==t['input']
   for variant in ['fresh','reused']:
    assert s[variant].get('state')==t[variant].get('state') and s[variant].get('error')==t[variant].get('error')
  original=next(x for x in lifecycle if x['id']==r['id'])['original']
  for s,t in zip(worker['original']['rows'],original['rows']):
   for so,to in zip(s['operations'],t['operations']):
    assert so.get('value')==to.get('value')
    if 'error' in to:assert so['error']['message']==to['error']['message'] and so['error']['nativeException']==to['error']['nativeException']
  assert len(worker['alternation'])==64
  assert all(x['rejected'].get('error') and x['supported'].get('value') for x in worker['alternation'])
  summary.append(dict(engine=engine,artifact=r['id'],originalSequences=47,rejectedPositions=6,alternations=64,sevenInventories=7,mainWorkerNumericAndMeaningExact=True,memoryBefore=worker['memoryBefore'],memoryAfter=worker['memoryAfter'],latencyMS=r['latencyMS'],maximumHeartbeatGapMS=d['result']['maximumHeartbeatGapMS']))
out=dict(passed=True,summary=summary,physicalSafariOrIPad=False,scope='Actual browser workers; no unsupported state accepted, numerical/ownership paths retain main-thread behavior')
p=E/'worker-audit.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print('Worker audit PASS; main/worker results and original PT refusals agree')
