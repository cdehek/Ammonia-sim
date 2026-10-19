"""Three additional sequential bounded brackets to investigate observed CPU overhead."""
import asyncio,functools,gzip,http.server,json,threading,hashlib
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{s.server_port}/experiments/dx-fv/'
async def main():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   binary='/workspace/b9-runtime/webkit.sh' if name=='webkit' else str(next(Path('/workspace/b9-runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')))
   browser=await getattr(pw,name).launch(executable_path=binary,headless=True);out={'browser':name,'version':browser.version,'rounds':[],'passed':False}
   try:
    p=await browser.new_page();await p.goto(base+'browser_eos_b9d/');await p.wait_for_function('!!window.shadow')
    await p.evaluate('async()=>{window.Client=(await import("./client.mjs")).Client;window.digest=(await import("../browser_eos_b9c/harness.mjs")).digest;}')
    ref=await browser.new_page();await ref.goto(base+'browser_eos_b9c/index.html');await ref.wait_for_function('!!window.workerRun')
    expected=json.loads((E/'review-summary.json').read_text())[name]['fixtures']
    for round in range(3):
     for fixture in (['cold','warm'] if round%2==0 else ['warm','cold']):
      row={'round':round,'fixture':fixture,'samples':[]}
      for mode in ['control','candidate','shadow','candidate','control']:
       if mode!='shadow':
        r=await ref.evaluate('a=>workerRun(a)',{'fixture':fixture,'mode':mode,'observed':False});assert r['scienceHash']==expected[fixture]['hash'];row['samples'].append({'mode':mode,'computeMS':sum(t['advanceMS'] for t in r['timing']),'timing':r['timing'],'scienceHash':r['scienceHash']})
       else:
        # Test copy/checkpoint retrieval is outside compute timers. Same model, observer and projection.
        r=await p.evaluate('''async fixture=>{const c=new Client(v=>shadow.update(v),{test:true});try{await c.request('initialize',{fixture});for(let i=0;i<3;i++)await c.request('advance');const d=(await c.request('testDetail')).result;const hash=await digest({record:d.record,state:d.state});const attemptsHash=await digest(d.attempts);return {metrics:c.metrics,checkpointHash:hash,attemptsHash};}finally{await c.dispose();}}''',fixture)
        primary=json.loads(gzip.decompress((E/f'shadow-{name}.json.gz').read_bytes()));expected_hash=next(x for x in primary['science'] if x['fixture']==fixture)['checkpointHashes'][-1]
        review=json.loads(gzip.decompress((E/f'review-{name}.json.gz').read_bytes()));encoded=review['results'][fixture]['control']['science']['attempts'];expected_attempts=hashlib.sha256(json.dumps(encoded,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        assert r['checkpointHash']==expected_hash and r['attemptsHash']==expected_attempts;row['samples'].append({'mode':'shadow','computeMS':sum(t['timing'].get('advanceMS',0) for t in r['metrics']),'metrics':r['metrics'],'exactOriginalFinalCheckpoint':True,'exactOriginalAllAttemptDiagnostics':True,'testOnlyPreAdvanceCopyOutsideTimer':True})
      out['rounds'].append(row);print(name,round,fixture,[round_value['computeMS'] for round_value in row['samples']],flush=True)
    out['passed']=True
   finally:
    await browser.close();(E/f'performance-{name}.json').write_text(json.dumps(out,indent=2)+'\n')
try:asyncio.run(main())
finally:s.shutdown()
