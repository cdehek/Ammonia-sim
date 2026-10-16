// Diagnostic harness only. Every property/adapter implementation is historical.
export async function origins(args) {
 const {loadEOS}=await import('../browser_eos_b4c/loader.mjs');
 const {createAdapter}=await import('../browser_eos_backend/adapter.mjs');
 const m={exports:{}};new Function('module','exports',args.engine)(m,m.exports);
 const guard=m.exports.createEngine(args.table),eos=await loadEOS('candidateB');
 const bits=x=>{const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
 const decode=s=>{const d=new DataView(new ArrayBuffer(8));d.setBigUint64(0,BigInt('0x'+s));return d.getFloat64(0);};
 const pack=x=>({values:x,bits:Object.fromEntries(Object.entries(x).filter(([,v])=>typeof v==='number').map(([k,v])=>[k,bits(v)]))});
 const rows=[];
 try{for(const f of args.origins){
  const [p,h]=f.requestBits.map(decode),raw=eos.evaluate({mode:'PH',args:[p,h]}),V=.003/5,M=raw.rho*V,U_kJ=M*(h/1000)-100*(p/1e5)*V;
  const input=pack({M,V,U_kJ,rho:M/V,u:(U_kJ/M)*1000});
  if(Object.entries(f.inventoryBits).some(([k,b])=>input.bits[k]!==b))throw Error('Origin construction changed');
  rows.push({key:f.key,request:pack({p,h}),raw:pack(raw),adapter:pack(createAdapter(eos,guard).ph(p/1e5,h/1000)),input});
 }}finally{eos.dispose();}return {rows};
}
export async function run(args) {
 const {run: historical}=await import('../browser_eos_b5b/browser.mjs');
 const result=await historical(args);
 const {loadEOS}=await import('../browser_eos_b4c/loader.mjs');
 const {createAdapter}=await import('../browser_eos_backend/adapter.mjs');
 const {createAdapter:c1}=await import('../browser_eos_b5b_c1/adapter.mjs');
 const m={exports:{}};new Function('module','exports',args.engine)(m,m.exports);
 const guard=m.exports.createEngine(args.table),eos=await loadEOS('candidateB');
 const bits=x=>{const d=new DataView(new ArrayBuffer(8));d.setFloat64(0,x);return d.getBigUint64(0).toString(16).padStart(16,'0');};
 const decode=s=>{const d=new DataView(new ArrayBuffer(8));d.setBigUint64(0,BigInt('0x'+s));return d.getFloat64(0);};
 const pack=x=>({values:x,bits:Object.fromEntries(Object.entries(x).filter(([,v])=>typeof v==='number').map(([k,v])=>[k,bits(v)]))});
 const error=e=>({message:e.message,faultKind:e.faultKind??null,evidence:e.evidence??null});
 result.endpoints=[];result.c1=[];
 try {
  for(const f of args.endpoints){
   const x=Object.fromEntries(Object.entries(f.input.bits).map(([k,v])=>[k,decode(v)]));
   const row={key:f.key,input:pack(x),qualification:'Original Gate B phase qualification unresolved'};
   try{row.raw=pack(eos.evaluate({mode:'DU',args:[x.rho,x.u]}));}catch(e){row.rawError=error(e);}
   try{row.adapter=pack(createAdapter(eos,guard).stateMVU(x.M,x.V,x.U_kJ,35));}catch(e){row.error=error(e);}
   result.endpoints.push(row);
  }
  for(const f of [...args.fixtures.map(f=>({key:f.fixedKey,input:f.fixedInput})),...args.falseAcceptanceControls]){
   const x=Object.fromEntries(Object.entries(f.input.bits).map(([k,v])=>[k,decode(v)])),row={key:f.key};
   try{row.adapter=pack(c1(eos,guard).stateMVU(x.M,x.V,x.U_kJ,35));}catch(e){row.error=error(e);}
   result.c1.push(row);
  }
  result.linearMemoryBytes=eos.memory();
 }finally{eos.dispose();}
 return result;
}
