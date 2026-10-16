"""Extract immutable fixtures and generate observation-only historical loader."""
import hashlib,json,struct,difflib
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence'
def bits(x):return struct.pack('>d',x).hex()
def write(n,x):(E/n).write_text(json.dumps(x,indent=2)+'\n')
rows=[]
for engine in ['chromium','webkit']:
 p=X/f'browser_eos_b4c/evidence/{engine}-candidateB-lifecycle.json';d=json.loads(p.read_text())
 for i,r in enumerate(d['rows']):
  for j,s in enumerate(r['sequences']):
   if 'error' in s:
    rows.append(dict(engine=engine,source=str(p.relative_to(X)),sourceSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),row=i,sequence=j,fixture=r['request'],request={k:s[k] for k in ['mode','args']},inputBits=list(map(bits,s['args'])),phaseImposition=False,fresh=False,priorOperations=[r['base']]+r['sequences'][:j],historicalError=s['error'],freshPTError=r.get('freshPTError')))
write('historical-rejected-pt.json',rows)
source=(X/'browser_eos_b4c/loader.mjs').read_text()
# Relative asset locations must resolve to the exact historical files.
s=source.replace("'../browser_eos_b4b/vendor/candidateB'","'../browser_eos_b4b/vendor/candidateB'").replace("'./vendor/","'../browser_eos_b4c/vendor/")
s="import {observeImports,observeCatch,observeModule} from './observe.mjs';\n"+s
s=s.replace('const t=performance.now();','observeImports(imports,()=>wasmExports,()=>memory,options);\n    const t=performance.now();',1)
s=s.replace("const initialized=performance.now(),beforeFactory",'observeModule(module,()=>wasmExports,()=>memory,options);\n  const initialized=performance.now(),beforeFactory',1)
s=s.replace('const message=decodeError(e);wasmExports.',"observeCatch(e,()=>wasmExports,()=>memory,options);\n      const message=decodeError(e);wasmExports.")
s=s.replace('const pointer=typeof e',"options.events?.push({kind:'stack-restored',stack:wasmExports.emscripten_stack_get_current()});\n      const pointer=typeof e")
(B/'control-diagnostic.mjs').write_text(s)
(E/'control-instrumentation.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True),s.splitlines(True),fromfile='historical-loader',tofile='control-diagnostic')))
js=(X/'browser_eos_b4c/vendor/candidateB/coolprop.js').read_text()
segments={}
for a,b in [('class EmscriptenEH','var runtimeDebug'),('var ___cxa_begin_catch=','var PATH='),('function createJsInvoker','function getRequiredArgCount'),('var incrementExceptionRefcount=','FS.createPreloadedFile'),('function invoke_vii(','function invoke_i(')]:
 p=js.index(a);q=js.index(b,p);segments[a]=dict(byteOffset=p,source=js[p:q])
write('generated-js-trace.json',segments)
print('extracted',len(rows),'sequence failures; generated observation-only copy')
