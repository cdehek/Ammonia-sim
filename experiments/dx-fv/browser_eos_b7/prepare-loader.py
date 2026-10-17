"""Produce isolated B7 mapping/configuration wrapper; keep B6 ownership code intact."""
import difflib,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent
original=(B.parent/'browser_eos_b6/loader.mjs').read_text();s=original
def replace(a,b):
 global s
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
replace("const assets={controlA:'../browser_eos_b4b/vendor/candidateB',rebuiltA:'../browser_eos_b4c/vendor/controlA',candidateB:'../browser_eos_b4c/vendor/candidateB'};", "const assets={controlA:'../browser_eos_b4b/vendor/candidateB',rebuiltB4C:'./vendor/control',gateA:'./vendor/candidate',diagnosticB4C:'./vendor/control-diagnostic',diagnosticGateA:'./vendor/candidate-diagnostic'};")
replace("throw Error('Unknown isolated B4C build');", "throw Error('Unknown isolated B7 artifact');")
replace('const {default:factory}=await import(`${asset}/coolprop.js`);', '''if(options.identity){
    if(options.identity.id!==version)throw Error('Explicit artifact identity mismatch');
    const js=await(await fetch(new URL(`${asset}/coolprop.js`,import.meta.url))).arrayBuffer();
    if(await digest(js)!==options.identity.jsSHA256)throw Error('Generated JS identity mismatch');
  }
  const {default:factory}=await import(`${asset}/coolprop.js`);''')
replace('mime=response.headers.get(\'content-type\');const bytes=await response.arrayBuffer();fetchMS=performance.now()-jsReady;', '''mime=response.headers.get('content-type');const bytes=await response.arrayBuffer();fetchMS=performance.now()-jsReady;
  if(options.identity&&await digest(bytes)!==options.identity.wasmSHA256)throw Error('WASM identity mismatch');
  const environmentObservations=[];''')
replace('// Pinned B4C Emscripten JS exception ABI; see pre-edit ownership design.', '// Newly audited B7 Emscripten JS exception ABI; see EXCEPTION_ABI.md.')
replace("throw Error('B6 requires the audited B4C exception ABI');", "throw Error('B7 requires the independently audited exception ABI');")
replace("throw Error('B6 missing generated exception callback: '+name);", "throw Error('B7 missing generated exception callback: '+name);")
replace('bindExceptionABI(imports);', '''if(options.fullVLE||options.trace)selectEnvironment(imports,()=>memory,environmentObservations,{fullVLE:options.fullVLE,trace:options.trace});
    observeImports(imports,()=>wasmExports,()=>memory,options);
    bindExceptionABI(imports);''')
replace('const initialized=performance.now(),beforeFactory=', 'observeModule(module,()=>wasmExports,()=>memory,options);\n  const initialized=performance.now(),beforeFactory=')
replace("const state=module.factory('HEOS','Ammonia');", "let state=module.factory('HEOS','Ammonia');")
replace("PT:['PT_INPUTS',a,b]", "PT:['PT_INPUTS',a,b],PS:['PSmass_INPUTS',a,b],PU:['PUmass_INPUTS',a,b],DH:['DmassHmass_INPUTS',a,b],DS:['DmassSmass_INPUTS',a,b],DP:['DmassP_INPUTS',a,b],DT:['DmassT_INPUTS',a,b],QT:['QT_INPUTS',a,b]")
replace('const message=decodeError(e);wasmExports.', 'observeCatch(e,()=>wasmExports,()=>memory,options);\n      const message=decodeError(e);wasmExports.')
replace("'B6 native exception cleanup failed: '+message", "'B7 native exception cleanup failed: '+message")
replace('return {module,state,capabilities,init,evaluate,', '''function evaluateFresh(request,settings={}){
    const previous=state;state=module.factory('HEOS','Ammonia');
    try{const value=evaluate(request,settings);return {...value,phase:state.keyed_output(module.parameters.iPhase)};}
    finally{state.delete();state=previous;}
  }
  return {module,state,capabilities,init,evaluate,evaluateFresh,environmentObservations,artifact:version,fullVLE:!!options.fullVLE,''')
s="import {selectEnvironment} from './runtime-environment.mjs';\nimport {observeImports,observeCatch,observeModule} from '../browser_eos_b6/observe.mjs';\nconst digest=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');\n"+s
s+='''
// Qualification never relies on the historical default. Identity is explicit,
// selected from the independently retained build manifest by each harness.
export function loadQualifiedEOS(identity, options={}) {
  if(!identity||!['rebuiltB4C','gateA','diagnosticB4C','diagnosticGateA'].includes(identity.id)||
     !/^[a-f0-9]{64}$/.test(identity.jsSHA256)||!/^[a-f0-9]{64}$/.test(identity.wasmSHA256))
    throw Error('Explicit B7 JS/WASM artifact identity is required');
  options.identity=identity;
  return loadEOS(identity.id,options);
}
'''
(B/'loader.mjs').write_text(s)
(B/'evidence/loader-vs-B6.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='B6/loader.mjs',tofile='B7/loader.mjs')))
print('B7 isolated loader generated; B6 source SHA256',hashlib.sha256(original.encode()).hexdigest())
