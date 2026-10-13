import {loadEOS} from './eos.mjs';import {diagnose} from './diagnostic.mjs';
const progress=message=>postMessage({type:'progress',message});
self.onmessage=async({data})=>{let eos;try{
 progress('Loading pinned CoolProp '+data.version+'…');eos=await loadEOS(data.version);
 const inputs=await (await fetch('./inputs.json')).json();progress('Checking saved and nearby liquid flashes…');const precision=await diagnose(eos,inputs);
 const p=30298.937123458254,h=94523.34612321304,low=eos.evaluate({mode:'PH',args:[p,h]}),vapor=eos.evaluate({mode:'PQ',args:[350000,1]}),mix=eos.evaluate({mode:'PQ',args:[350000,.5]});
 const states=[low,vapor,mix],groups=[{mode:'PH',requests:states.map(s=>({mode:'PH',args:[s.p,s.h]}))},{mode:'DU',requests:states.map(s=>({mode:'DU',args:[s.rho,s.u]}))}],throughput=[];
 for(const g of groups)for(let round=0;round<3;round++){
  progress(g.mode+' throughput round '+(round+1)+'…');const t=performance.now();let calls=0,checksum=0,failures=0;
  do{for(const q of g.requests){try{const a=eos.evaluate(q);checksum+=a.rho;}catch(e){failures++;}calls++;}}while(performance.now()-t<500);
  throughput.push({mode:g.mode,round,calls,failures,elapsedMS:performance.now()-t,checksum,linearMemory:eos.memory()});
 }
 const sustained=[];for(let epoch=0;epoch<3;epoch++){
  progress('Sustained mixed PH/DU epoch '+(epoch+1)+'…');const t=performance.now();let calls=0,checksum=0,failures=0;
  do{for(const g of groups)for(const q of g.requests){try{checksum+=eos.evaluate(q).rho;}catch(e){failures++;}calls++;}}while(performance.now()-t<1000);
  sustained.push({epoch,calls,failures,elapsedMS:performance.now()-t,checksum,linearMemory:eos.memory()});
 }
 progress('Checking invalid-state errors and subsequent valid updates…');const stress={stackBefore:eos.stackPointer(),memoryBefore:eos.memory(),errors:[],validAfterError:0};
 for(let i=0;i<5;i++){try{eos.evaluate({mode:'PQ',args:[350000,1.1]});stress.errors.push('Unexpected success');}catch(e){stress.errors.push(e.message);}if(Number.isFinite(eos.evaluate({mode:'PH',args:[p,h]}).rho))stress.validAfterError++;}
 Object.assign(stress,{stackAfter:eos.stackPointer(),memoryAfter:eos.memory()});
 postMessage({type:'result',result:{precision,throughput,sustained,stress,init:eos.init,linearMemory:eos.memory(),noCoupledSimulation:true,physicalIPadQualification:false,notes:'Observable WASM linear memory only. PH and DU use fresh calculations; no approximate caching, rounding or hidden fallback.'}});
}catch(e){postMessage({type:'error',error:e.message||String(e)});}finally{eos?.dispose();}};
