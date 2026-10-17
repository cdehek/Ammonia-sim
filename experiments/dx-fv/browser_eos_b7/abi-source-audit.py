"""Compare new generated exception implementation, not merely emcc version."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence';old=B.parent/'browser_eos_b4c/vendor/candidateB/coolprop.js'
markers=[('class EmscriptenEH','var runtimeDebug'),('var ___cxa_begin_catch=','var PATH='),('function createJsInvoker','function getRequiredArgCount'),('var incrementExceptionRefcount=','FS.createPreloadedFile'),('function invoke_vii(','function invoke_i('),('var ENV=','function _fd_close')]
def slices(p):
 s=p.read_text();out={}
 for left,right in markers:
  i=s.index(left);j=s.index(right,i);part=s[i:j];out[left]=dict(byteOffset=i,source=part,sha256=hashlib.sha256(part.encode()).hexdigest())
 return out
historical=slices(old);rows={}
for label in ['control','candidate','control-diagnostic','candidate-diagnostic']:
 p=B/'vendor'/label/'coolprop.js';segments=slices(p)
 rows[label]=dict(jsSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),segments=segments,identicalHistoricalExceptionAndEnvironmentImplementation=all(segments[k]['source']==historical[k]['source'] for k in historical))
out=dict(historicalSHA256=hashlib.sha256(old.read_bytes()).hexdigest(),artifacts=rows,allMatch=all(r['identicalHistoricalExceptionAndEnvironmentImplementation'] for r in rows.values()),scope='Static generated source audit; live ownership and imports/exports checked separately before science.')
t=E/'abi-generated-source.json';assert not t.exists();t.write_text(json.dumps(out,indent=2)+'\n')
assert out['allMatch'],'Generated ABI differs: establish and review difference before using B6 cleanup'
print('Both generated exception and WASI implementations equal reviewed historical source slices')
