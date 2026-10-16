import {step} from './lifecycle.mjs';
self.onmessage=async({data:{kind,fixture}})=>{
 let e;const rows=[];
 try{const {loadEOS}=await import(kind==='candidate'?'./loader.mjs':'../browser_eos_b4c/loader.mjs');e=await loadEOS('candidateB');const before=e.memory(),start=performance.now();
  for(let i=0;i<64;i++){
   const refusal=step(e,fixture.request,{candidate:kind==='candidate',expectReject:true});const supported=step(e,{mode:'PT',args:[350000,300]},{candidate:kind==='candidate'});
   if(i<2||i===63)rows.push({i,refusal,supported});
  }
  const ph=step(e,{mode:'PH',args:[799999.9981754856,1624022.744737779]},{candidate:kind==='candidate'}),s=ph.value.values;
  const du=step(e,{mode:'DU',args:[s.rho,s.u]},{candidate:kind==='candidate'}),pq=step(e,{mode:'PQ',args:[350000,.4]},{candidate:kind==='candidate'});e.dispose();
  postMessage({passed:true,rows,ph,du,pq,lastSupported:rows.at(-1).supported.value,before,memoryAfter:e.memory(),elapsedWorkMS:performance.now()-start,deleted:e.state.isDeleted(),alternations:64});
 }catch(error){postMessage({passed:false,error:String(error),stack:error.stack,rows});}
 finally{if(e&&!e.state.isDeleted())e.dispose();}
};
