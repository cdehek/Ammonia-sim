import os
"""Accepted scientific assertion blocks, each persisted independently."""
import functools,http.server,json,os,threading,time,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
catalog=json.loads(Path('/workspace/b2-runtime/catalog.json').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  for name in os.environ.get('B2_BROWSERS','chromium,webkit').split(','):
   options={'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}
   browser=getattr(p,name).launch(**options)
   try:
    # Complete default scientific contracts first. Additional option combinations
    # remain explicitly unqualified if the short-fixture gates fail.
    for choice in ['fd-aware']:
     for block in catalog['blocks']:
      if os.environ.get('B2_CONTRACTS_ONLY') and block['id'].startswith('operating-'):continue
      if os.environ.get('B2_ONLY') and block['id']!=os.environ['B2_ONLY']:continue
      f=E/f'{name}-suite-{choice}-{block["id"]}.json'
      if f.exists():continue
      context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_backend/')
      page.add_script_tag(url='../browser_eos_b2/assert-bundle.js')
      print(name,choice,block['id'],'start',flush=True)
      try:
       result=page.evaluate('''async ({catalog,block,choice})=>{const {execute}=await import('../browser_eos_b2/browser-suite.mjs');return execute(catalog,block,choice);}''',dict(catalog=catalog,block=block,choice=choice))
      except Exception as e:result=dict(id=block['id'],status='HARNESS ERROR',error=str(e))
      result.update(browser=name,browserVersion=browser.version,choice=choice)
      f.write_text(json.dumps(result,indent=2)+'\n');context.close()
      print(name,block['id'],result['status'],result.get('result',{}).get('failure',{}).get('message',''),flush=True)
   finally:browser.close()
finally:server.shutdown()
