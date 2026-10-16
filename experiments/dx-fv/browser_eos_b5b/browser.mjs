// Diagnostic only: the loader and adapter imports are unchanged historical code.
export async function run({fixtures,sweep,falseAcceptanceControls,engine,table}) {
 const {loadEOS}=await import('../browser_eos_b4c/loader.mjs');
 const {createAdapter}=await import('../browser_eos_backend/adapter.mjs');
 const em={exports:{}};new Function('module','exports',engine)(em,em.exports);
 const guard=em.exports.createEngine(table),eos=await loadEOS('candidateB');
 const bits=x=>{const v=new DataView(new ArrayBuffer(8));v.setFloat64(0,x);return v.getBigUint64(0).toString(16).padStart(16,'0');};
 const decode=x=>{const v=new DataView(new ArrayBuffer(8));v.setBigUint64(0,BigInt('0x'+x));return v.getFloat64(0);};
 const snapshot=s=>({values:s,bits:Object.fromEntries(Object.entries(s).filter(([,v])=>typeof v==='number').map(([k,v])=>[k,bits(v)]))});
 const error=e=>({message:String(e),faultKind:e.faultKind??null,stack:e.stack});
 const fields=s=>({p:s.p(),T:s.T(),h:s.hmass(),u:s.umass(),rho:s.rhomass()});
 const rows=[],matrix=[],guards=[],falseAcceptance=[];
 function trace(x){
  const events=[];
  const a=createAdapter({evaluate(q){events.push({event:'EOS_call',request:q});try{const s=eos.evaluate(q);events.push({event:'EOS_return',state:snapshot(s)});return s;}catch(e){events.push({event:'EOS_error',...error(e)});throw e;}}},
   {ph(p,h){events.push({event:'table_PH_call',p,h});try{const s=guard.ph(p,h);events.push({event:'table_PH_pass'});return s;}catch(e){events.push({event:'table_PH_error',...error(e)});throw e;}}});
  const out={events};try{out.adapter=snapshot(a.stateMVU(x.M,x.V,x.U_kJ,35));}catch(e){out.error=error(e);}out.counts={...a.counts};return out;
 }
 function recovery(x){
  const row={input:snapshot(x)};try{row.raw=snapshot(eos.evaluate({mode:'DU',args:[x.rho,x.u]}));}catch(e){row.rawError=error(e);}
  if(row.raw){const s=row.raw.values;row.pressure={Pa:s.p,bar:s.p/1e5,barBits:bits(s.p/1e5),PaAfterRoundTrip:(s.p/1e5)*1e5,PaMinusLimit:s.p-3500000};
   try{const dt=eos.module.factory('HEOS','Ammonia');try{dt.update(eos.module.input_pairs.DmassT_INPUTS,s.rho,s.T);row.independentDT=snapshot(fields(dt));}finally{dt.delete();}}catch(e){row.independentDTError=error(e);}}
  Object.assign(row,trace(x));return row;
 }
 try{
  for(const f of fixtures){const x=Object.fromEntries(Object.entries(f.fixedInput.bits).map(([k,v])=>[k,decode(v)]));
   if(bits(x.M/x.V)!==f.fixedInput.bits.rho||bits((x.U_kJ/x.M)*1000)!==f.fixedInput.bits.u)throw Error('Inventory bits mismatch');
   const row={key:f.fixedKey,id:f.id,originalPHInput:f.originalPHInput,...recovery(x)};
   try{row.originatingRawPH=snapshot(eos.evaluate({mode:'PH',args:f.originalPHInput}));}catch(e){row.originatingPHError=error(e);}
   try{row.originatingAdapterPH=snapshot(createAdapter(eos,guard).ph(f.originalPHInput[0]/1e5,f.originalPHInput[1]/1000));}catch(e){row.originatingAdapterPHError=error(e);}
   rows.push(row);
  }
  for(const f of falseAcceptanceControls){const x=Object.fromEntries(Object.entries(f.input.bits).map(([k,v])=>[k,decode(v)]));falseAcceptance.push({key:f.key,id:f.id,origin:f.origin,...recovery(x)});}
  const probes=sweep.map((s,i)=>({...s,id:'B5-sweep-'+i,origin:'saved B5 diagnostic PH input'}));
  const sat=eos.evaluate({mode:'SAT',args:[3500100,0]});
  for(const [region,h]of [['liquid',sat.hf-1000],['mixture',(sat.hf+sat.hg)/2],['vapor',sat.hg+10000]])probes.push({id:'outside-100Pa-'+region,p:3500100,h,region,origin:'new B5B diagnostic only',requestedSupported:false});
  for(const q of probes){const row={id:q.id,origin:q.origin,region:q.region,request:snapshot({p:q.p,h:q.h}),requestedSupported:q.requestedSupported};
   try{row.PH=snapshot(eos.evaluate({mode:'PH',args:[q.p,q.h]}));const V=.003/5,M=row.PH.values.rho*V,U_kJ=M*(q.h/1000)-100*(q.p/1e5)*V;
    Object.assign(row,recovery({M,V,U_kJ,rho:M/V,u:(U_kJ/M)*1000}));}catch(e){row.error=error(e);}
   try{row.adapterPH=snapshot(createAdapter(eos,guard).ph(q.p/1e5,q.h/1000));}catch(e){row.adapterPHError=error(e);}matrix.push(row);
  }
  // Bounded guard-isolation tests. No PT updates and no claim of physical states.
  for(const p of [0.3,0.29999999999999993,35,35.00000000000001]){let calls=0;const a=createAdapter({evaluate(q){calls++;return eos.evaluate(q);}},guard),row={kind:'sat-pressure',p,bits:bits(p)};
   try{row.result=a.sat(p);}catch(e){row.error=error(e);}row.EOSCalls=calls;guards.push(row);}
  for(const T of [195.494,345.5636735993518-30-0.001,345.5636735993518+250+0.001]){
   const row={kind:'synthetic-temperature-guard',T,note:'Guard isolation only; artificial DU output, never an EOS recovery or accepted state'};
   const a=createAdapter({evaluate(q){if(q.mode==='DU')return {p:3500000,h:1100000,rho:100,u:1000000,T,s:3000,Q:-1};return eos.evaluate(q);}},guard);
   try{row.unexpectedReturn=a.stateMVU(1,.01,1000,35);}catch(e){row.error=error(e);}guards.push(row);
  }
 }finally{eos.dispose();}
 return {rows,matrix,guards,falseAcceptance,capabilities:eos.capabilities};
}
