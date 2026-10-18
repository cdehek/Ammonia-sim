"""Generate observational copies with insertion-only auditable diffs; no accepted edits."""
import json,hashlib,difflib,re
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
manifest=json.loads((E/'accepted-source-manifest.json').read_text())
original={Path(v['snapshot']).name:(R/v['snapshot']).read_text() for v in manifest.values()}
sources=dict(original); changes=[]
def insert_after(name,anchor,addition):
 s=sources[name];assert s.count(anchor)==1,(name,anchor);sources[name]=s.replace(anchor,anchor+addition)
def body_end(s,start):
 # Balanced JS function body, ignoring quoted strings and comments. Selected
 # functions contain no regex literals; template literals have no nested ticks.
 depth=0;i=start
 while i<len(s):
  c=s[i]
  if c in "'\"`":
   quote=c;i+=1
   while i<len(s):
    if s[i]=='\\':i+=2;continue
    if s[i]==quote:break
    i+=1
  elif s.startswith('//',i):i=s.index('\n',i)
  elif s.startswith('/*',i):i=s.index('*/',i+2)+1
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:return i
  i+=1
 raise AssertionError('unbalanced function')
def instrument(name,fn,label,args='[]',timer=True):
 s=sources[name];m=re.search(r'function '+fn+r'\([^\n]*?\)\s*\{',s);assert m,(name,fn)
 start=m.end();end=body_end(s,start-1)
 if timer:
  a='\n/* B9B observation */ const __b9bEnd=globalThis.__b9b.enter('+json.dumps(label)+','+args+');try{\n'
  z='\n}finally{__b9bEnd();}/* B9B observation */\n'
 else:a='globalThis.__b9b.count('+json.dumps(label)+');';z=''
 sources[name]=s[:start]+a+s[start:end]+z+s[end:]
for fn in ['evaluate','blend','temperatures','coordinates','recover','solveStage','trial','record','commit','errorEstimate']:
 args={'solveStage':'[dt,weight]','trial':'[s.seconds,dt]','commit':'[start,dt]','record':'[s.seconds]'}.get(fn,'[]')
 instrument('coupled-model.cjs',fn,'model.'+fn,args)
insert_after('coupled-model.cjs','const key=`${x[2*i]}:${x[2*i+1]}`;','globalThis.__b9b.cache(key,properties.has(key));')
insert_after('coupled-model.cjs','Object.assign(s,accepted);',"globalThis.__b9b.note('state-install',[start,dt]);")
for fn in ['sat','branch','statePT','statePX','inverse','atDensity','stateDU','stateMVU']:
 instrument('engine.js',fn,'internal.'+fn,timer=False)
insert_after('engine.js',"function inverse(p,target,key){globalThis.__b9b.count(\"internal.inverse\");const a=sat(p),f=key==='h'?a.hf:a.sf,g=key==='h'?a.hg:a.sg;",'globalThis.__b9b.count(target>=f-eps&&target<=g+eps?"inverse.mixture":"inverse.single-phase");')
out='// B9B PROFILING-ONLY observational copy. NOT accepted A2.\nconst registry={\n'
for key,s in sources.items():
 if key.endswith('.json'):out+=json.dumps(key)+':function(module){module.exports=JSON.parse('+json.dumps(s)+');},\n'
 else:out+=json.dumps(key)+':function(module,exports,require){\n'+s+'\n},\n'
out+='};\nexport function loader(){const cache=Object.create(null);return function load(name){const id=name.startsWith("./")?name.slice(2):name;if(!Object.hasOwn(registry,id))throw Error("Unknown module "+name);if(cache[id])return cache[id].exports;const m={exports:{}};cache[id]=m;registry[id](m,m.exports,load);return m.exports;};}\n'
(B/'diagnostic-bundle.mjs').write_text(out)
for name in ['coupled-model.cjs','engine.js']:
 p=B/'isolated'/name;p.parent.mkdir(exist_ok=True);p.write_text(sources[name])
 changes.append(''.join(difflib.unified_diff(original[name].splitlines(True),sources[name].splitlines(True),fromfile='accepted/'+name,tofile='profiling-only/'+name)))
(E/'observational.patch').write_text(''.join(changes))
(E/'diagnostic-source-manifest.json').write_text(json.dumps({'accepted':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in original.items()},'diagnostic':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sources.items()},'bundleSHA256':hashlib.sha256(out.encode()).hexdigest(),'modification':'Insertions only: function observation try/finally, read-only counters/Map.has and event notes; all original expressions retained'},indent=2)+'\n')
print('Diagnostic copy generated; exact diff retained')
