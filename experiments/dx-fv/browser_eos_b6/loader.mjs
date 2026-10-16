// Isolated browser research only. SI mass-based values; no production imports.
export async function loadEOS(version='controlA', options={}) {
  const start=performance.now(),logs=[];
  const assets={controlA:'../browser_eos_b4b/vendor/candidateB',rebuiltA:'../browser_eos_b4c/vendor/controlA',candidateB:'../browser_eos_b4c/vendor/candidateB'};
  const asset=assets[version];if(!asset)throw Error('Unknown isolated B4C build');
  const {default:factory}=await import(`${asset}/coolprop.js`);
  const jsReady=performance.now();let memory,wasmExports,fetchMS=0,compileInstantiateMS=0,mime,streaming=false;
  const response=await fetch(new URL(options.wasmURL||`${asset}/coolprop.wasm${options.badMime?'?mime=bad':''}`,import.meta.url));
  if(!response.ok)throw Error(`WASM asset unavailable: HTTP ${response.status}`);
  mime=response.headers.get('content-type');const bytes=await response.arrayBuffer();fetchMS=performance.now()-jsReady;
  // Pinned B4C Emscripten JS exception ABI; see pre-edit ownership design.
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
  let failInstantiation;
  const failed=new Promise((_,reject)=>{failInstantiation=reject;});
  const module=await Promise.race([factory({printErr:v=>logs.push(String(v)),instantiateWasm(imports,done){
    bindExceptionABI(imports);
    const t=performance.now();
    (async()=>{
      let result;
      if(!options.noStreaming&&mime?.split(';')[0]==='application/wasm'){
        // Fetch timing is separated; this still tests browser streaming compiler
        // support on an equivalent local response. Download/compile overlap is
        // deliberately not claimed by this instrumented loader.
        try{result=await WebAssembly.instantiateStreaming(new Response(bytes,{headers:{'Content-Type':mime}}),imports);streaming=true;}
        catch(e){logs.push('Streaming compile failed; ArrayBuffer fallback: '+String(e));}
      }
      if(!result)result=await WebAssembly.instantiate(bytes,imports);
      wasmExports=result.instance.exports;memory=Object.values(wasmExports).find(v=>v instanceof WebAssembly.Memory);
      compileInstantiateMS=performance.now()-t;done(result.instance,result.module);
    })().catch(failInstantiation);return {};
  }}),failed]);
  const initialized=performance.now(),beforeFactory=memory.buffer.byteLength;
  const state=module.factory('HEOS','Ammonia');const ready=performance.now();
  const capabilities={version:module.get_global_param_string('version'),git:module.get_global_param_string('gitrevision'),
    exports:Object.keys(module).filter(k=>!k.startsWith('_')),inputPairs:Object.keys(module.input_pairs),stateMethods:Object.getOwnPropertyNames(Object.getPrototypeOf(state)),
    phaseImpositionAvailable:typeof state.specify_phase==='function',referenceSetterAvailable:typeof module.set_reference_state==='function',
    exceptionCleanupAvailable:typeof wasmExports.emscripten_stack_get_current==='function'&&typeof wasmExports._emscripten_stack_restore==='function',
    sharedMemory:typeof SharedArrayBuffer!=='undefined'&&memory.buffer instanceof SharedArrayBuffer};
  const init={totalMS:ready-start,importMS:jsReady-start,fetchMS,compileInstantiateMS,runtimeMS:initialized-jsReady-fetchMS,
    firstFactoryMS:ready-initialized,initialLinearMemoryBytes:beforeFactory,readyLinearMemoryBytes:memory.buffer.byteLength,wasmBytes:bytes.byteLength,mime,streaming,logs};
  function decodeError(e){return e?.message||String(e);}
  function high(request,extras=false){
    const {mode,args:[a,b]}=request;
    const keys={PH:['P','Hmass'],DU:['Dmass','Umass'],PQ:['P','Q'],PT:['P','T'],PTliquid:['P','T|liquid']}[mode];
    if(!keys)throw Error('Unsupported research input pair');
    const fields={p:'P',T:'T',h:'Hmass',s:'Smass',rho:'Dmass',u:'Umass',Q:'Q'};const out={};
    for(const [key,value]of Object.entries(fields))out[key]=module.PropsSI(value,keys[0],a,keys[1],b,'HEOS::Ammonia');
    if(extras&&!(out.Q>0&&out.Q<1))for(const [key,value]of Object.entries({cp:'Cpmass',cv:'Cvmass',kappa:'ISOTHERMAL_COMPRESSIBILITY',rhoP:'d(Dmass)/d(P)|T',rhoT:'d(Dmass)/d(T)|P',hp:'d(Hmass)/d(P)|T'}))out[key]=module.PropsSI(value,keys[0],a,keys[1],b,'HEOS::Ammonia');
    return out;
  }
  function evaluate(request,{highLevel=false,extras=false}={}){
    const stackPointer=wasmExports.emscripten_stack_get_current();
    try{
      let out;
      if(!request.args.every(Number.isFinite))throw Error('Nonfinite state input');
      if(request.mode==='SAT'){
        const p=request.args[0],k=module.parameters;
        if(state.hmass&&!highLevel){
          state.update(module.input_pairs.PQ_INPUTS,p,0);
          out={p:state.p(),T:state.T(),hf:state.saturated_liquid_keyed_output(k.iHmass),hg:state.saturated_vapor_keyed_output(k.iHmass),
            sf:state.saturated_liquid_keyed_output(k.iSmass),sg:state.saturated_vapor_keyed_output(k.iSmass),
            rhof:state.saturated_liquid_keyed_output(k.iDmass),rhog:state.saturated_vapor_keyed_output(k.iDmass)};
        }else{
          out={p,T:module.PropsSI('T','P',p,'Q',0,'HEOS::Ammonia')};
          for(const [key,field,q]of [['hf','Hmass',0],['hg','Hmass',1],['sf','Smass',0],['sg','Smass',1],['rhof','Dmass',0],['rhog','Dmass',1]])out[key]=module.PropsSI(field,'P',p,'Q',q,'HEOS::Ammonia');
        }
      }else if(highLevel||!state.hmass||request.mode==='PTliquid')out=high(request,extras);
      else{
        const [a,b]=request.args;const pairs={PH:['HmassP_INPUTS',b,a],DU:['DmassUmass_INPUTS',a,b],PQ:['PQ_INPUTS',a,b],PT:['PT_INPUTS',a,b]};
        const pair=pairs[request.mode];if(!pair)throw Error('Unsupported research input pair');
        state.update(module.input_pairs[pair[0]],pair[1],pair[2]);
        out={p:state.p(),T:state.T(),h:state.hmass(),s:state.smass(),rho:state.rhomass(),u:state.umass(),Q:state.Q()};
        if(extras&&!(out.Q>0&&out.Q<1)){
          const k=module.parameters;
          Object.assign(out,{cp:state.cpmass(),cv:state.cvmass(),kappa:state.isothermal_compressibility(),rhoP:state.first_partial_deriv(k.iDmass,k.iP,k.iT),rhoT:state.first_partial_deriv(k.iDmass,k.iT,k.iP),hp:state.first_partial_deriv(k.iHmass,k.iP,k.iT)});
        }
      }
      if(!Object.values(out).every(Number.isFinite))throw Error('EOS returned a nonfinite property');
      return out;
    }catch(e){
      const message=decodeError(e);wasmExports._emscripten_stack_restore(stackPointer);
      const propagated=new Error(message);
      if(nativeThrows.has(e)){
        nativeThrows.delete(e);
        const diagnostic=Object.freeze({representation:'CppException',name:e.name,message,cleanup:'generated-begin/end-catch'});
        propagated.nativeException=diagnostic;
        // begin acquires the count (zero -> one) and fixes uncaught bookkeeping;
        // end destroys/frees, pops catch state and clears exceptionLast.
        try{beginCatch(e.excPtr);endCatch();}
        catch(cleanupError){throw new AggregateError([propagated,cleanupError],'B6 native exception cleanup failed: '+message);}
      }
      throw propagated;
    }
  }
  return {module,state,capabilities,init,evaluate,memory:()=>memory.buffer.byteLength,stackPointer:()=>wasmExports.emscripten_stack_get_current(),dispose:()=>state.delete()};
}
export function exactCache(eos,limit=1024){
  const cache=new Map();let hits=0,misses=0;
  return {evaluate(request){const key=request.mode+':'+request.args.join(':');if(cache.has(key)){hits++;return cache.get(key);}misses++;
    const result=Object.freeze(eos.evaluate(request));if(cache.size>=limit)cache.delete(cache.keys().next().value);cache.set(key,result);return result;},
    clear(){cache.clear();hits=0;misses=0;},stats(){return {hits,misses,size:cache.size,limit};}};
}
