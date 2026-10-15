import {loadEOS} from '../browser_eos_backend/loader.mjs';
import {createAdapter} from '../browser_eos_backend/adapter.mjs';
self.onmessage=async ({data:{build,sources,engine,table}})=>{
 const em={exports:{}};new Function('module','exports',engine)(em,em.exports);
 const guard=em.exports.createEngine(table);let eos;
 const rows=[];
 try{
  eos=await loadEOS(build);const adapter=createAdapter(eos,guard),cache={};
  function require(name){const key=name.slice(2);if(cache[key])return cache[key].exports;if(!sources[key])throw Error('Unexpected accepted import '+key);const m={exports:{}};cache[key]=m;new Function('module','exports','require',sources[key])(m,m.exports,require);return m.exports;}
  const {createCoupledModel}=require('./coupled-model.cjs'),F=require('./coupled-fixtures.cjs');
  for(let round=-1;round<3;round++)for(const name of ['cold','warm','heat-reversal']){
   const fixture=F.cases().find(c=>c.name===name),counts={...adapter.counts},start=performance.now();
   try{
    const model=createCoupledModel(adapter,{...F.accuracyOptions(1e-6),timestepGrowth:'failure-aware'}),s=model.create(fixture.config),r=model.advance(s,.2);
    rows.push({round,warmup:round<0,case:name,durationSeconds:.2,reachedSeconds:r.seconds,completedTarget:r.stop===null&&r.seconds===.2,elapsedMS:performance.now()-start,propertyCalls:Object.fromEntries(Object.keys(counts).map(k=>[k,adapter.counts[k]-counts[k]])),acceptedHalfSteps:r.acceptedSteps,rejectedSteps:r.rejectedSteps,accuracyRejected:r.accuracyRejectedSteps,eventRejected:r.eventRejectedSteps,domainRejected:r.domainRejectedSteps,iterations:r.attemptedIterations,residualEvaluations:r.attemptedResidualEvaluations,linearSolves:s.attemptedLinearSolves,stop:r.stop,terminal:r.terminal,conservation:{massKg:r.massResidualKg,refrigerantKJ:r.refrigerantEnergyResidualKJ,thermalKJ:r.thermalEnergyResidualKJ,combinedKJ:r.combinedEnergyResidualKJ},linearMemory:eos.memory()});
   }catch(e){rows.push({round,case:name,error:String(e),elapsedMS:performance.now()-start});}
  }
  self.postMessage({build,init:eos.init,rows,linearMemory:eos.memory(),workerJSHeap:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize}:null,qualification:false,measurement:'Matched 0.2 s original cold/warm/reversal physical fixtures; one warmup plus three repeats. Timed model create/advance/record, adapter and table support guard; excludes WASM init, source transfer and JSON output.'});
 }catch(e){self.postMessage({build,error:String(e),rows});}finally{eos?.dispose();}
};
