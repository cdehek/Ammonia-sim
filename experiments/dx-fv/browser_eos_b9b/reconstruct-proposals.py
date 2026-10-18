"""Post-process saved attempts with original Time.factor in the same browser.
No model execution, property evaluations, or changed scientific state.
"""
import asyncio,json,gzip,functools,http.server,threading,platform,subprocess,importlib.metadata,hashlib
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
async def main():
 output={};runtime={'python':platform.python_version(),'platform':platform.platform(),'playwright':importlib.metadata.version('playwright'),'node':json.loads(subprocess.check_output(['node','-p','JSON.stringify({version:process.version,versions:process.versions})'],text=True)),'browsers':{},'profilingDesignCommit':subprocess.check_output(['git','log','--format=%H','--','experiments/dx-fv/browser_eos_b9b/PROFILING_DESIGN.md'],cwd=R,text=True).splitlines()[-1]}
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   opts={'headless':True,'timeout':30000}
   if name=='webkit':opts['executable_path']='/workspace/b9-runtime/webkit.sh'
   browser=await getattr(pw,name).launch(**opts);page=await browser.new_page();await page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9b/index.html')
   source=json.loads(gzip.decompress((E/f'baseline-{name}.json.gz').read_bytes()))['runs']
   data=[dict(fixture=r['fixture'],rows=[dict(state={k:v for k,v in row['state'].items() if k in ['seconds','nextStepSeconds','growthHistory']},attempts=row['attempts']) for row in r['science']['rows']]) for r in source]
   # Discard detailed Newton events: proposal reconstruction uses original attempt error only.
   for f in data:
    for row in f['rows']:
     if row['attempts']:
      for a in row['attempts']:a.pop('events')
   output[name]=await page.evaluate("""async data=>{
    const {loader}=await import('../browser_eos_b9/accepted-bundle.mjs'),Time=loader()('time-control.cjs');const out=[];
    for(const fixture of data){const advances=[];
     for(let i=1;i<fixture.rows.length;i++){
      const previous=fixture.rows[i-1].state,row=fixture.rows[i],target=row.state.seconds;
      if(previous.growthHistory.ceilingSeconds!==null||row.state.growthHistory.ceilingSeconds!==null||row.state.growthHistory.nonlinearFailures!==0)throw Error('Unmodelled proposal ceiling');
      let proposal=previous.nextStepSeconds;const history=[];
      for(const attempt of row.attempts){
       const actual=Math.min(proposal,target-attempt.startSeconds);if(actual!==attempt.trialSeconds)throw Error('Proposal clipping mismatch');
       if(attempt.failure)throw Error('Unmodelled failure proposal');
       const accepted=!attempt.rejectionReason,next=accepted?Math.min(.5,actual*Time.factor(attempt.temporalError,2,true)):actual*Time.factor(attempt.temporalError,2,false);
       history.push({startSeconds:attempt.startSeconds,originalProposal:proposal,clippedTrial:actual,temporalError:attempt.temporalError,accepted,nextProposal:next});proposal=next;
      }
      if(proposal!==row.state.nextStepSeconds)throw Error('Final original proposal mismatch');advances.push({target,history});
     }out.push({fixture:fixture.fixture,passed:true,advances});
    }return out;
   }""",data)
   runtime['browsers'][name]={'version':browser.version,'userAgent':await page.evaluate('navigator.userAgent'),'launch':opts,'physicalIPad':False}
   await browser.close()
 (E/'adaptive-proposal-reconstruction.json').write_text(json.dumps({'passed':True,'method':'Original unchanged Time.factor, same browser engine, post-run saved errors; every clipped attempt and endpoint proposal checked exactly; no property calls','engines':output},indent=2)+'\n')
 for name,pattern in [('chromiumHeadless','chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'),('chromium','chromium-*/chrome-linux64/chrome'),('webkitMiniBrowser','webkit-*/minibrowser-wpe/bin/MiniBrowser')]:
  for p in Path('/workspace/b9-runtime/browsers').glob(pattern):runtime[name]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 runtime['webkitLauncher']={'path':'/workspace/b9-runtime/webkit.sh','sha256':hashlib.sha256(Path('/workspace/b9-runtime/webkit.sh').read_bytes()).hexdigest()}
 (E/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n');print('Exact adaptive proposal reconstruction PASS; runtime versions sealed')
try:asyncio.run(main())
finally:server.shutdown()
