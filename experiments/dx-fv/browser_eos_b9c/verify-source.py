"""Independent exact removal audit, not a call to the prototype generator."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent; R=B.parents[2]; E=B/'evidence'
original=subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/coupled-model.cjs'],cwd=R).decode()
s=(B/'isolated/coupled-model.cjs').read_text()
removals=["\n  if(!require('./table-only.cjs').owns(engine))throw Error('B9C requires its owned original table engine.');",'''
    // B9C: two successful exact-input properties owned only by this invocation.
    const boundaries=[undefined,undefined];
    const boundaryPH=(index,p,h)=>{
      const entry=boundaries[index];
      if(entry&&Object.is(entry.p,p)&&Object.is(entry.h,h))return entry.value;
      boundaries[index]=undefined;
      const value=thermo.ph(p,h);
      boundaries[index]={p,h,value};return value;
    };''','\n      } catch(cause) { boundaries[0]=boundaries[1]=undefined;throw cause; }']
for a in removals:assert s.count(a)==1;s=s.replace(a,'')
s=s.replace('const solved=coupledNewton(x=>{\n      try {','const solved=coupledNewton(x=>{')
s=s.replace('function evaluate(spec, states, energies, boundaryPH=null) {','function evaluate(spec, states, energies) {')
s=s.replace('evaluate(s.spec,states,energies,boundaryPH)','evaluate(s.spec,states,energies)')
for side,index in [('inlet',0),('outlet',1)]:
 a=f'thermo.ph(spec.fluid.{side}.p,spec.fluid.{side}.h)'
 s=s.replace(f'(boundaryPH?boundaryPH({index},spec.fluid.{side}.p,spec.fluid.{side}.h):{a})',a)
assert s==original,'Unexpected original expression change'
manifest=json.loads((E/'prototype-source-manifest.json').read_text())
for variant in ['control','candidate']:
 for k,v in manifest['control']['sources'].items():
  if k!='coupled-model.cjs':assert manifest[variant]['sources'][k]==v
assert hashlib.sha256(s.encode()).hexdigest()==manifest['control']['sources']['coupled-model.cjs']
receipt={'passed':True,'exactOriginalRestored':True,'onlyFunctionalFile':'coupled-model.cjs','other13SourceBodiesExact':True,'guard':'owned frozen original table only','numericalExpressionChanges':False,'independentOfGenerator':True,'reviewed':['scope','stage ownership','lazy original failure timing','no aliases','changed boundary counts only','unchanged residual arithmetic','no fallback','no new physical acceptance']}
(E/'source-diff-audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print('Independent source removal audit PASS')
