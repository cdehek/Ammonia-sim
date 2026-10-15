import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2];E=Path(os.environ.get('B2_EVIDENCE',B/'evidence'));E.mkdir(parents=True,exist_ok=True)
catalog=json.loads(Path('/workspace/b2-runtime/catalog.json').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   browser=getattr(p,name).launch(**({'executable_path':os.environ['EOS_WEBKIT_EXECUTABLE']} if name=='webkit' else {}))
   try:
    for choice in ['fd-aware','exact-aware']:
     f=E/f'{name}-domain-pt-{choice}.json';assert not f.exists()
     page=browser.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/experiments/dx-fv/browser_eos_b2/');page.add_script_tag(url='./assert-bundle.js')
     r=page.evaluate('''async({catalog,choice})=>{const {domain}=await import('./domain.mjs');return domain(catalog,choice);}''',dict(catalog=catalog,choice=choice))
     r.update(browser=name,browserVersion=browser.version);f.write_text(json.dumps(r,indent=2)+'\n');page.close();print(name,choice,r['report'].get('passed'),len(r['report']['cases']),r['report'].get('failure'),flush=True)
   finally:browser.close()
finally:server.shutdown()
