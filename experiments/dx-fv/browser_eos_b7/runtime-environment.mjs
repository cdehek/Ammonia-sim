// Isolated qualification harness. Supply one original CoolProp configuration
// variable through the module's existing WASI process-environment ABI. No EOS
// inputs, code, exported functions, link settings or generated JS are changed.
export function selectEnvironment(imports, memory, observations=[],{fullVLE=false,trace=false}={}) {
  const env=imports.env;
  const sizes=env.environ_sizes_get, get=env.environ_get;
  if(typeof sizes!=='function'||typeof get!=='function')throw Error('Missing audited WASI environment ABI');
  const entries=[];
  if(fullVLE)entries.push('COOLPROP_ENABLE_SUPERANCILLARIES=false');
  if(trace)entries.push('B7_TRACE=1');
  const extra=new TextEncoder().encode(entries.join('\0')+'\0');
  let originalCount,originalBytes;
  env.environ_sizes_get=(countPtr,bytesPtr)=>{
    const rc=sizes(countPtr,bytesPtr);if(rc!==0)return rc;
    const v=new DataView(memory().buffer);
    originalCount=v.getUint32(countPtr,true);originalBytes=v.getUint32(bytesPtr,true);
    v.setUint32(countPtr,originalCount+entries.length,true);v.setUint32(bytesPtr,originalBytes+extra.length,true);
    observations.push({event:'environment-sizes',originalCount,originalBytes,extraBytes:extra.length});return rc;
  };
  env.environ_get=(ptr,buf)=>{
    if(originalCount===undefined)throw Error('Environment read without prior size request');
    const rc=get(ptr,buf);if(rc!==0)return rc;
    const m=memory(),v=new DataView(m.buffer);
    let offset=0;
    for(let i=0;i<entries.length;i++){
      v.setUint32(ptr+4*(originalCount+i),buf+originalBytes+offset,true);
      offset+=new TextEncoder().encode(entries[i]).length+1;
    }
    new Uint8Array(m.buffer).set(extra,buf+originalBytes);
    observations.push({event:'environment-provided',entries,mechanism:'existing WASI environ imports'});return rc;
  };
}
