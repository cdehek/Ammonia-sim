"""Generate isolated candidate and separately auditable observation-only copy."""
import difflib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;X=B.parent;E=B/'evidence'
assert subprocess.check_output(['git','merge-base','--is-ancestor','183295983435deea4d59a926dac8b8d86666123c','HEAD'])==b''
src=(X/'browser_eos_b4c/loader.mjs').read_text();s=src.replace("'./vendor/","'../browser_eos_b4c/vendor/")
s=s.replace('let failInstantiation;', '''// Pinned B4C Emscripten JS exception ABI; see pre-edit ownership design.
  // Only identities actually thrown by this module's generated callbacks may
  // enter native catch cleanup. An excPtr field or numeric throw is insufficient.
  const nativeThrows=new WeakSet();let beginCatch,endCatch;
  function bindExceptionABI(imports){
    const env=imports.env;
    beginCatch=env.__cxa_begin_catch;endCatch=env.__cxa_end_catch;
    if(typeof beginCatch!=='function'||typeof endCatch!=='function')throw Error('B6 requires the audited B4C exception ABI');
    for(const name of ['__cxa_throw','__cxa_rethrow','__resumeException']){
      const original=env[name];
      if(typeof original!=='function')throw Error('B6 missing generated exception callback: '+name);
      env[name]=(...args)=>{try{return original(...args);}catch(e){
        if(e&&typeof e==='object'&&Number.isInteger(e.excPtr)&&e.excPtr>0)nativeThrows.add(e);
        throw e;
      }};
    }
  }
  let failInstantiation;''',1)
s=s.replace('const t=performance.now();','bindExceptionABI(imports);\n    const t=performance.now();',1)
s=s.replace("const pointer=typeof e==='number'?e:e?.excPtr;\n      if(Number.isInteger(pointer)&&pointer>0)module.decrementExceptionRefcount(pointer);\n      throw new Error(message);",'''const propagated=new Error(message);
      if(nativeThrows.has(e)){
        nativeThrows.delete(e);
        const diagnostic=Object.freeze({representation:'CppException',name:e.name,message,cleanup:'generated-begin/end-catch'});
        propagated.nativeException=diagnostic;
        // begin acquires the count (zero -> one) and fixes uncaught bookkeeping;
        // end destroys/frees, pops catch state and clears exceptionLast.
        try{beginCatch(e.excPtr);endCatch();}
        catch(cleanupError){throw new AggregateError([propagated,cleanupError],'B6 native exception cleanup failed: '+message);}
      }
      throw propagated;''')
(B/'loader.mjs').write_text(s)
(E/'loader-repair.diff').write_text(''.join(difflib.unified_diff(src.splitlines(True),s.splitlines(True),fromfile='browser_eos_b4c/loader.mjs',tofile='browser_eos_b6/loader.mjs')))
d="import {observeImports,observeCatch,observeModule} from './observe.mjs';\n"+s
d=d.replace('bindExceptionABI(imports);','observeImports(imports,()=>wasmExports,()=>memory,options);\n    bindExceptionABI(imports);',1)
d=d.replace('const initialized=performance.now(),beforeFactory','observeModule(module,()=>wasmExports,()=>memory,options);\n  const initialized=performance.now(),beforeFactory',1)
d=d.replace('const message=decodeError(e);wasmExports.',"observeCatch(e,()=>wasmExports,()=>memory,options);\n      const message=decodeError(e);wasmExports.")
d=d.replace('const propagated=new Error(message);',"options.events?.push({kind:'stack-restored',stack:wasmExports.emscripten_stack_get_current()});\n      const propagated=new Error(message);")
(B/'candidate-diagnostic.mjs').write_text(d)
(E/'candidate-instrumentation.diff').write_text(''.join(difflib.unified_diff(s.splitlines(True),d.splitlines(True),fromfile='candidate',tofile='candidate-diagnostic')))
(E/'pre-edit-commit.json').write_text(json.dumps(dict(designCommit='6b1c69b82ed90ee113689f713cd10e31a089eef5',completeGateAReceiptCommit='183295983435deea4d59a926dac8b8d86666123c',functionalCandidateAbsentInBoth=True),indent=2)+'\n')
print('candidate generated from historical loader; exact diff saved')
