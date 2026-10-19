"""Independent source removal/registry check; original sources read-only."""
from pathlib import Path
import hashlib,json,subprocess,difflib
B=Path(__file__).resolve().parent;R=B.parents[2];C=B.parent/'browser_eos_b9c'
original=subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/coupled-model.cjs'],cwd=R).decode()
s=(C/'isolated/coupled-model.cjs').read_text()
assert (B/'isolated/coupled-model.cjs').read_text()==s
actual=''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='accepted/coupled-model.cjs',tofile='b9c/isolated/coupled-model.cjs'))
assert actual==(C/'BOUNDARY_PH_PROTOTYPE.patch').read_text()
for a in ["\n  if(!require('./table-only.cjs').owns(engine))throw Error('B9C requires its owned original table engine.');",'''
    // B9C: two successful exact-input properties owned only by this invocation.
    const boundaries=[undefined,undefined];
    const boundaryPH=(index,p,h)=>{
      const entry=boundaries[index];
      if(entry&&Object.is(entry.p,p)&&Object.is(entry.h,h))return entry.value;
      boundaries[index]=undefined;
      const value=thermo.ph(p,h);
      boundaries[index]={p,h,value};return value;
    };''','\n      } catch(cause) { boundaries[0]=boundaries[1]=undefined;throw cause; }']:
 assert s.count(a)==1;s=s.replace(a,'')
for a,b in [('const solved=coupledNewton(x=>{\n      try {','const solved=coupledNewton(x=>{'),('function evaluate(spec, states, energies, boundaryPH=null) {','function evaluate(spec, states, energies) {'),('evaluate(s.spec,states,energies,boundaryPH)','evaluate(s.spec,states,energies)')]:assert s.count(a)==1;s=s.replace(a,b)
for side,i in [('inlet',0),('outlet',1)]:
 ph=f'thermo.ph(spec.fluid.{side}.p,spec.fluid.{side}.h)';a=f'(boundaryPH?boundaryPH({i},spec.fluid.{side}.p,spec.fluid.{side}.h):{ph})';assert s.count(a)==1;s=s.replace(a,ph)
assert s==original
accepted=json.loads((B/'evidence/accepted-source-manifest.json').read_text())
for name in ['control','candidate']:
 text=(C/(name+'-bundle.mjs')).read_text()
 for path,v in accepted.items():
  key=Path(path).name;body=(C/'isolated/coupled-model.cjs').read_text() if name=='candidate' and key=='coupled-model.cjs' else (R/v['snapshot']).read_text()
  literal=json.dumps(key)+(':function(module){module.exports=JSON.parse('+json.dumps(body)+');},' if key.endswith('.json') else ':function(module,exports,require){\n'+body+'\n},')
  assert literal in text,(name,key)
(B/'evidence/source-review.json').write_text(json.dumps({'passed':True,'exactOriginalRestored':True,'all14LiteralRegistryBodiesVerified':True,'B9DMechanicalCopyExact':True,'scientificAlgorithmModified':False},indent=2)+'\n')
print('Source reconstruction PASS')
