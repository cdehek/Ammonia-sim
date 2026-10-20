"""Owner handoff: Python standard library only. Localhost, correct module MIME."""
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import argparse
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args()
B=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
 extensions_map={**SimpleHTTPRequestHandler.extensions_map,'.mjs':'text/javascript','.js':'text/javascript'}
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(B),**kwargs)
print(f'B16 NONPRODUCTION benchmark: http://127.0.0.1:{a.port}/index.html ; Ctrl-C to stop',flush=True)
ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
