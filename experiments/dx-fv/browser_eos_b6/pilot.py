import functools,http.server,json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
B=Path(__file__).resolve().parent;R=B.parents[2]
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(R)));threading.Thread(target=s.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  for name in ['chromium','webkit']:
   b=getattr(p,name).launch(executable_path='/usr/bin/chromium' if name=='chromium' else '/workspace/b6-browsers/webkit-2336/b6-wpe.sh',timeout=30000)
   try:
    page=b.new_page();page.goto(f'http://127.0.0.1:{s.server_port}/');out=page.evaluate("async()=>{const m=await import('/experiments/dx-fv/browser_eos_b6/pilot.mjs');return m.run();}")
    target=B/'evidence'/f'pilot-{name}.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n');print(name,[(r.get('error',{}).get('message'),r['before']['stack'],r['after']['stack']) for r in out['rows']])
   finally:b.close()
finally:s.shutdown()
