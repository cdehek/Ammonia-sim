// Diagnostic harness only; imports the exact inherited loader and adapter.
export async function run({inputs,sweep,referenceInventories,guardFixtures,engine,table}) {
 const {loadEOS}=await import('../browser_eos_b4c/loader.mjs');
 const {createAdapter}=await import('../browser_eos_backend/adapter.mjs');
 const em={exports:{}};new Function('module','exports',engine)(em,em.exports);
 const eos=await loadEOS('candidateB'),adapter=createAdapter(eos,em.exports.createEngine(table));
 const fields=s=>({p:s.p(),T:s.T(),h:s.hmass(),s:s.smass(),rho:s.rhomass(),u:s.umass(),Q:s.Q()});
 const lifecycle=[],boundary=[],reference=[],guardTraces=[];
 try {
  for(const r of inputs){const x=r.input.values,row={key:r.key};
   try {
    row.reused=eos.evaluate({mode:'DU',args:[x.rho,x.u]});
    const fresh=eos.module.factory('HEOS','Ammonia');
    try{fresh.update(eos.module.input_pairs.DmassUmass_INPUTS,x.rho,x.u);row.fresh=fields(fresh);row.phase=fresh.keyed_output(eos.module.parameters.iPhase);}finally{fresh.delete();}
    row.scalar={};for(const [k,f]of Object.entries({p:'P',T:'T',rho:'Dmass',h:'Hmass',u:'Umass',Q:'Q'}))row.scalar[k]=eos.module.PropsSI(f,'Dmass',x.rho,'Umass',x.u,'HEOS::Ammonia');
   }catch(e){row.error=String(e);}lifecycle.push(row);
  }
  for(const r of sweep){const row={p:r.p,h:r.h,region:r.region,requestedSupported:r.requestedSupported};
   try{row.PH=eos.evaluate({mode:'PH',args:[r.p,r.h]});
    const V=.003/5,M=row.PH.rho*V,U_kJ=M*(r.h/1000)-100*(r.p/1e5)*V,x={M,V,U_kJ,rho:M/V,u:U_kJ/M*1000};row.inventory=x;
    row.DU=eos.evaluate({mode:'DU',args:[x.rho,x.u]});row.differences={p:row.DU.p-r.p,h:row.DU.h-r.h,T:row.DU.T-row.PH.T};
    try{row.adapterPH=adapter.ph(r.p/1e5,r.h/1000);}catch(e){row.adapterPHError=String(e);row.adapterPHFault=e.faultKind;}
    try{row.adapterDU=adapter.stateMVU(M,V,U_kJ,35);}catch(e){row.adapterDUError=String(e);row.adapterDUFault=e.faultKind;}
   }catch(e){row.error=String(e);}boundary.push(row);
  }
  for(const r of referenceInventories){const x=r.input,row={failureKey:r.failureKey,input:x};
   try{row.DU=eos.evaluate({mode:'DU',args:[x.rho,x.u]});row.differences={p:row.DU.p-r.requestedP,h:row.DU.h-r.requestedH,T:row.DU.T-r.referenceT};
    try{row.adapter=adapter.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){row.adapterError=String(e);}
   }catch(e){row.error=String(e);}reference.push(row);
  }
  for(const r of guardFixtures){const x=r.fixedInput.values,events=[],row={failureKey:r.failureKey,input:x};
   row.originatingAdapterPHCoordinates={pBar:r.originalPHInput[0]/1e5,hKJkg:r.originalPHInput[1]/1000,PaAfterRoundTrip:(r.originalPHInput[0]/1e5)*1e5,hAfterRoundTrip:(r.originalPHInput[1]/1000)*1000};
   try{row.originatingAdapterPH=adapter.ph(r.originalPHInput[0]/1e5,r.originalPHInput[1]/1000);}catch(e){row.originatingAdapterPHError=String(e);}
   const traceEOS={evaluate(q){events.push({event:'EOS_call',request:q});return eos.evaluate(q);}};
   const traceGuard={ph(p,h){events.push({event:'table_guard_call',p,h});try{const out=em.exports.createEngine(table).ph(p,h);events.push({event:'table_guard_pass'});return out;}catch(e){events.push({event:'table_guard_reject',error:String(e)});throw e;}}};
   const traced=createAdapter(traceEOS,traceGuard);
   try{row.adapter=traced.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){row.error=String(e);row.faultKind=e.faultKind;row.stack=e.stack;}
   row.events=events;row.counts={...traced.counts};guardTraces.push(row);
  }
 }finally{eos.dispose();}
 return {lifecycle,boundary,reference,guardTraces};
}
