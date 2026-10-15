"""Optional loopback-only persistence of completed advances during long blocks."""
import http.server,json,os,re
from pathlib import Path
E=Path(os.environ.get('B2_EVIDENCE',Path(__file__).resolve().parent/'evidence'));E.mkdir(parents=True,exist_ok=True)
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  try:
   d=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
   assert d['browser'] in ['chromium','webkit'] and d['choice'] in ['baseline','exact','fd-aware','exact-aware']
   assert re.fullmatch(r'(operating-[a-z-]+|block-[0-9]+)',d['block'])
   f=E/f"{d['browser']}-progress-{d['choice']}-{d['block']}.jsonl"
   with f.open('a') as stream:stream.write(json.dumps(d,separators=(',',':'))+'\n')
   self.send_response(200);self.send_header('Access-Control-Allow-Origin','*');self.end_headers();self.wfile.write(b'OK')
   print(d['browser'],d['block'],'model',d['model'],'seconds',d['record']['seconds'],'stop',d['record']['stop'],flush=True)
  except Exception as e:self.send_error(400,str(e))
http.server.ThreadingHTTPServer(('127.0.0.1',8871),Handler).serve_forever()
