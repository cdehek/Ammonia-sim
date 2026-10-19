"""Build exact control, minimal candidate and separately labeled diagnostics."""
import hashlib,json,subprocess,difflib,re
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
def sha(v):return hashlib.sha256(v).hexdigest()
manifest=json.loads((E/'accepted-source-manifest.json').read_text()); original={}
for path,v in manifest.items():
 raw=(R/v['snapshot']).read_bytes();assert sha(raw)==v['sha256']
 assert raw==subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:'+path],cwd=R)
 original[Path(path).name]=raw.decode()
candidate=dict(original)
def change(s,a,b):assert s.count(a)==1,a;return s.replace(a,b)
s=candidate['coupled-model.cjs']
s=change(s,'function createCoupledModel(engine, options={}, observeAttempt=null) {',"function createCoupledModel(engine, options={}, observeAttempt=null) {\n  if(!require('./table-only.cjs').owns(engine))throw Error('B9C requires its owned original table engine.');")
s=change(s,'function evaluate(spec, states, energies) {','function evaluate(spec, states, energies, boundaryPH=null) {')
for side,index in [('inlet',0),('outlet',1)]:
 a=f'thermo.ph(spec.fluid.{side}.p,spec.fluid.{side}.h)'
 s=change(s,a,f'(boundaryPH?boundaryPH({index},spec.fluid.{side}.p,spec.fluid.{side}.h):{a})')
s=change(s,'const properties=new Map();', '''const properties=new Map();
    // B9C: two successful exact-input properties owned only by this invocation.
    const boundaries=[undefined,undefined];
    const boundaryPH=(index,p,h)=>{
      const entry=boundaries[index];
      if(entry&&Object.is(entry.p,p)&&Object.is(entry.h,h))return entry.value;
      boundaries[index]=undefined;
      const value=thermo.ph(p,h);
      boundaries[index]={p,h,value};return value;
    };''')
s=change(s,'const solved=coupledNewton(x=>{','const solved=coupledNewton(x=>{\n      try {')
s=change(s,'const endpoint=evaluate(s.spec,states,energies),','const endpoint=evaluate(s.spec,states,energies,boundaryPH),')
s=change(s,'return {residual,states,cells,energies,endpoint,integratedRate};','return {residual,states,cells,energies,endpoint,integratedRate};\n      } catch(cause) { boundaries[0]=boundaries[1]=undefined;throw cause; }')
candidate['coupled-model.cjs']=s
(B/'isolated').mkdir(exist_ok=True);(B/'isolated/coupled-model.cjs').write_text(s)
(B/'BOUNDARY_PH_PROTOTYPE.patch').write_text(''.join(difflib.unified_diff(original['coupled-model.cjs'].splitlines(True),s.splitlines(True),fromfile='accepted/coupled-model.cjs',tofile='b9c/isolated/coupled-model.cjs')))
def body_end(s,start):
 depth=0;i=start
 while i<len(s):
  c=s[i]
  if c in "'\"`":
   q=c;i+=1
   while i<len(s):
    if s[i]=='\\':i+=2;continue
    if s[i]==q:break
    i+=1
  elif s.startswith('//',i):i=s.index('\n',i)
  elif s.startswith('/*',i):i=s.index('*/',i+2)+1
  elif c=='{':depth+=1
  elif c=='}':
   depth-=1
   if depth==0:return i
  i+=1
 raise AssertionError('unbalanced')
def diagnostic(src):
 out=dict(src);s=out['coupled-model.cjs']
 for fn,label in [('solveStage','stage'),('trial','trial'),('evaluate','evaluate'),('record','record')]:
  m=re.search(r'function '+fn+r'\([^\n]*?\)\s*\{',s);assert m
  end=body_end(s,m.end()-1)
  s=s[:m.end()]+f"\nconst __done=globalThis.__b9c.enter('{label}');try{{\n"+s[m.end():end]+'\n}finally{__done();}\n'+s[end:]
 for side in ['inlet','outlet']:
  a=f'thermo.ph(spec.fluid.{side}.p,spec.fluid.{side}.h)'
  # In candidate include the whole optional reuse expression, not just misses.
  index=0 if side=='inlet' else 1
  expr=f'(boundaryPH?boundaryPH({index},spec.fluid.{side}.p,spec.fluid.{side}.h):{a})'
  if expr in s:a=expr
  s=change(s,a,f"globalThis.__b9c.boundary('{side}',spec.fluid.{side}.p,spec.fluid.{side}.h,()=>{a})")
 s=change(s,'const key=`${x[2*i]}:${x[2*i+1]}`;','const key=`${x[2*i]}:${x[2*i+1]}`;globalThis.__b9c.section(properties.has(key));')
 out['coupled-model.cjs']=s
 s=out['engine.js']
 for fn in ['sat','branch','inverse','stateMVU']:
  m=re.search(r'function '+fn+r'\([^\n]*?\)\s*\{',s);assert m
  s=s[:m.end()]+f"globalThis.__b9c.count('lexical.{fn}');"+s[m.end():]
 s=change(s,'return {sat,satP,statePT,statePX,ph,ps,stateDU,stateMVU,solve,roomSimulation,defaults};',"const observe=(name,fn)=>(...args)=>globalThis.__b9c.property(name,fn,args);\n return {sat:observe('sat',sat),satP,statePT,statePX,ph:observe('ph',ph),ps,stateDU,stateMVU:observe('stateMVU',stateMVU),solve,roomSimulation,defaults};")
 out['engine.js']=s
 return out
def bundle(sources):
 out='// B9C literal registry; diagnostics are separately identified.\nconst registry={\n'
 for key,s in {**sources,'table-only.cjs':(B/'table-only.cjs').read_text()}.items():
  out+=json.dumps(key)+(':function(module){module.exports=JSON.parse('+json.dumps(s)+');},\n' if key.endswith('.json') else ':function(module,exports,require){\n'+s+'\n},\n')
 return out+'''};
export function loader(){const cache=Object.create(null);return function load(name){const id=name.startsWith('./')?name.slice(2):name;if(!Object.hasOwn(registry,id))throw Error('Unresolved B9C module: '+name);if(cache[id])return cache[id].exports;const m={exports:{}};cache[id]=m;registry[id](m,m.exports,load);return m.exports;};}
'''
receipts={}
for name,src in [('control',original),('candidate',candidate),('diagnostic-control',diagnostic(original)),('diagnostic-candidate',diagnostic(candidate))]:
 raw=bundle(src).encode();(B/(name+'-bundle.mjs')).write_bytes(raw)
 receipts[name]={'bundleSHA256':sha(raw),'sources':{k:sha(v.encode()) for k,v in src.items()}}
 if name.startswith('diagnostic-'):
  base=original if name=='diagnostic-control' else candidate
  (E/(name+'.patch')).write_text(''.join(''.join(difflib.unified_diff(base[k].splitlines(True),src[k].splitlines(True),fromfile=name+'/before/'+k,tofile=name+'/observed/'+k)) for k in src if src[k]!=base[k]))
assert all(candidate[k]==v for k,v in original.items() if k!='coupled-model.cjs')
(E/'prototype-source-manifest.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('Built unchanged accepted control, one-file candidate, separate diagnostic copies')
