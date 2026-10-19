"""Small origin reachability probe, no physics; retain response rather than assume app loaded."""
import asyncio,functools,http.server,json,socket,threading
from pathlib import Path
from playwright.async_api import async_playwright
B=Path(__file__).resolve().parent
class H(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=http.server.ThreadingHTTPServer(('0.0.0.0',0),functools.partial(H,directory=str(B/'preview')));threading.Thread(target=s.serve_forever,daemon=True).start()
async def run():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path=str(next((B/'.runtime/browsers').glob('chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell'))),headless=True);rows=[]
  try:
   for ip in ['127.0.0.1',*socket.gethostbyname_ex(socket.gethostname())[2]]:
    p=await browser.new_page();response=await p.goto(f'http://{ip}:{s.server_port}/');rows.append({'ip':ip,'httpStatus':response.status,'url':p.url,'bodyExcerpt':(await p.locator('body').inner_text())[:350],'secureContext':await p.evaluate('isSecureContext'),'originalReady':await p.evaluate('!!window.AmmoniaStartup?.ready'),'cryptoUUID':await p.evaluate('typeof crypto.randomUUID'),'cryptoSubtle':await p.evaluate('!!crypto.subtle')});await p.close()
  finally:await browser.close()
  (B/'evidence/private-origin-reachability.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
try:asyncio.run(run())
finally:s.shutdown()
