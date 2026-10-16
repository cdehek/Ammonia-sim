// Observation only. No additional cleanup, refcount adjustment, or native call.
export function raw(e){return {type:typeof e,constructor:e?.constructor?.name,name:e?.name,message:e?.message,string:String(e),excPtr:e?.excPtr,ownKeys:e&&typeof e==='object'?Object.getOwnPropertyNames(e):[],stack:e?.stack};}
function snap(ptr,exports,memory){const w=exports(),m=memory();const out={stack:w?.emscripten_stack_get_current?.(),memory:m?.buffer.byteLength};
 // Only call at a live native callback argument or while caught and not yet released.
 if(Number.isInteger(ptr)&&ptr>=24&&ptr+4<=m?.buffer.byteLength){const v=new DataView(m.buffer);out.header={ptr,referenceCount:v.getUint32(ptr-24,true),type:v.getUint32(ptr-20,true),destructor:v.getUint32(ptr-16,true),caught:v.getUint8(ptr-12),rethrown:v.getUint8(ptr-11)};}return out;}
export function observeImports(imports,exports,memory,options){const events=options.events;if(!events)return;
 const env=imports.env;const caught=[];
 options.nativeObserved=new WeakSet();
 const status=()=>({uncaught:env.__cxa_uncaught_exceptions(),observedCatchDepth:caught.length});
 options.runtimeStatus=status;
 for(const k of ['__cxa_throw','__cxa_rethrow','__resumeException','__cxa_begin_catch','__cxa_end_catch']){
  if(typeof env[k]!=='function')continue;const f=env[k];env[k]=(...args)=>{
   const ptr=k==='__cxa_end_catch'?caught.at(-1):args[0];events.push({kind:k,stage:'before',args,...snap(ptr,exports,memory),...status()});
   try{const v=f(...args);if(k==='__cxa_begin_catch')caught.push(args[0]);if(k==='__cxa_end_catch')caught.pop();events.push({kind:k,stage:'returned',stack:exports()?.emscripten_stack_get_current?.(),...status()});return v;}
   catch(e){
    const native=['__cxa_throw','__cxa_rethrow','__resumeException'].includes(k)&&e&&typeof e==='object'&&Number.isInteger(e.excPtr)&&e.excPtr>0;
    if(native)options.nativeObserved.add(e);
    events.push({kind:k,stage:'thrown',raw:raw(e),...snap(native?e.excPtr:undefined,exports,memory),...status()});throw e;}
  };
 }
}
export function observeModule(module,exports,memory,options){if(!options.events)return;for(const k of ['incrementExceptionRefcount','decrementExceptionRefcount']){const f=module[k];module[k]=ptr=>{options.events.push({kind:k,stage:'before',...snap(ptr,exports,memory)});try{const v=f(ptr);options.events.push({kind:k,stage:'returned',stack:exports().emscripten_stack_get_current()});return v;}catch(e){options.events.push({kind:k,stage:'thrown',raw:raw(e)});throw e;}};}}
export function observeCatch(e,exports,memory,options){options.events?.push({kind:'loader-catch',raw:raw(e),...snap(options.nativeObserved?.has(e)?e.excPtr:undefined,exports,memory)});}
