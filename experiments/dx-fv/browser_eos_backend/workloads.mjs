// Identical uncached workloads for every build; no solver or model imported.
export async function performanceWork(eos,requests){
 const groups=[];
 for(const mode of ['PH','DU'])for(const region of ['liquid','vapor','two-phase']){
  groups.push({name:mode+'-'+region,requests:requests.filter(q=>q.mode===mode&&q.region===region).slice(0,12)});
 }
 const timings=[];
 for(let round=0;round<3;round++)for(const g of groups){
  let calls=0,failures=0,checksum=0;const errors=[];
  const start=performance.now();
  do{for(const q of g.requests){try{checksum+=eos.evaluate(q).rho;}catch(err){failures++;if(errors.length<5)errors.push(String(err));}calls++;}}while(performance.now()-start<150);
  timings.push({group:g.name,round,calls,failures,errors,checksum,elapsedMS:performance.now()-start,linearMemory:eos.memory()});
 }
 const sustained=[],mixed=groups.flatMap(g=>g.requests);
 for(let epoch=0;epoch<3;epoch++){
  let calls=0,failures=0;const start=performance.now();
  do{for(const q of mixed){try{eos.evaluate(q);}catch(err){failures++;}calls++;}}while(performance.now()-start<500);
  sustained.push({epoch,calls,failures,elapsedMS:performance.now()-start,linearMemory:eos.memory()});
 }
 const before={memory:eos.memory(),stack:eos.stackPointer()};let failures=0,recoveries=0;
 for(let i=0;i<20;i++){try{eos.evaluate({mode:'PQ',args:[350000,1.1]});}catch(err){failures++;}if(Number.isFinite(eos.evaluate(groups[0].requests[0]).rho))recoveries++;}
 return {init:eos.init,timings,sustained,errorRecovery:{before,after:{memory:eos.memory(),stack:eos.stackPointer()},failures,recoveries},linearMemory:eos.memory(),jsHeap:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize}:null};
}
