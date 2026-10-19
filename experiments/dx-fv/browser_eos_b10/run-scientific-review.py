"""Reuse unchanged B9D review/harness; write only B10 receipts."""
import asyncio,functools,gzip,hashlib,http.server,json,threading,traceback,importlib.metadata
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=B/'evidence'
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
async def main():
 async with async_playwright() as pw:
  for name in ['chromium','webkit']:
   out={'browser':name,'playwright':importlib.metadata.version('playwright'),'passed':False,'results':{}}
   path=str(B/'.runtime/webkit.sh') if name=='webkit' else str(next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell')))
   browser=None
   try:
    browser=await getattr(pw,name).launch(executable_path=path,headless=True);page=await browser.new_page();out.update(version=browser.version,executable=path,executableSHA256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
    await page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b9d/review.html');out['userAgent']=await page.evaluate('navigator.userAgent')
    async def run(a):
     print(name,a,flush=True);return json.loads(await asyncio.wait_for(page.evaluate('async a=>JSON.stringify(await reviewRun(a))',a),180))
    out['results']['hardening']=await run({'task':'hardening'})
    for fixture in ['cold','warm']:
     c=await run({'mode':'control','fixture':fixture});p=await run({'mode':'candidate','fixture':fixture})
     assert c['science']==p['science'] and c['componentHashes']==p['componentHashes']
     saved=json.loads(gzip.decompress((B.parent/'browser_eos_b9c/evidence'/f'parity-{name}.json.gz').read_bytes()))
     old=next(r for r in saved['runs'] if r['mode']=='control' and r['fixture']==fixture)
     assert c['scienceHash']==old['scienceHash'],'saved B9C same-engine science'
     out['results'][fixture]={'control':c,'candidate':p,'exact':True,'savedB9CMatch':True}
    for task in ['regressions','additional']:
     c=await run({'task':task,'mode':'control'});p=await run({'task':task,'mode':'candidate'})
     if task=='regressions':
      assert c['property']==p['property'] and c['invalidUpdates']==p['invalidUpdates'] and c['missingRegion']==p['missingRegion']
      for x,y in zip(c['cases'],p['cases']):
       for key in ['name','state','records','error','attempts','componentHashes','audits']: assert x.get(key)==y.get(key),(task,key,x['name'])
       assert x['evidence']['logicalBoundaryHash']==y['evidence']['logicalBoundaryHash']
     else: assert c['rows']==p['rows']
     out['results'][task]={'control':c,'candidate':p,'exact':True}
    out['results']['c1']=await run({'task':'c1'});out['passed']=True
   except Exception as e:out.update(error=str(e),traceback=traceback.format_exc())
   finally:
    if browser:await browser.close()
    (E/f'review-{name}.json.gz').write_bytes(gzip.compress(json.dumps(out,separators=(',',':'),allow_nan=False).encode(),mtime=0))
   print(name,'PASS' if out['passed'] else out['error'],flush=True)
   if not out['passed']:raise RuntimeError(out['error'])
try:asyncio.run(main())
finally:server.shutdown()
