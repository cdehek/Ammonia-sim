import {loadEOS} from '../browser_eos_backend/loader.mjs';
import {createAdapter} from '../browser_eos_backend/adapter.mjs';
export async function execute(catalog,block,choice='fd-aware'){
 const selected={...(choice.startsWith('exact')?{thermalJacobian:'exact'}:{}),...(choice.endsWith('aware')?{timestepGrowth:'failure-aware'}:{})};
 const em={exports:{}};new Function('module','exports',catalog.sources['../../engine'])(em,em.exports);
 const table=em.exports.createEngine(JSON.parse(catalog.sources['../../properties.json']));
 const eos=await loadEOS('build44'),adapter=createAdapter(eos,table),cache={},histories=[],initialStates=new WeakMap();let captured;
 const process={argv:['browser','coupled-test.cjs','capture'],env:{},version:'browser'};
 function require(name){
  if(name==='node:assert/strict')return globalThis.b2assert;
  if(name==='node:fs')return {readFileSync:p=>{const key=p.split('/').pop();if(!catalog.sources[key])throw Error('Missing accepted data '+key);return catalog.sources[key];},writeFileSync:(p,v)=>{captured=JSON.parse(v);}};
  if(name==='node:path')return {join:(...a)=>a.join('/')};
  if(name==='../../engine')return {createEngine:()=>adapter};
  const key=name.startsWith('./')?name.slice(2):name;
  if(cache[key])return cache[key].exports;
  if(key.endsWith('.json'))return JSON.parse(catalog.sources[key]);
  if(!catalog.sources[key])throw Error('Missing accepted module '+key);
  const m={exports:{}};cache[key]=m;new Function('module','exports','require','process','__dirname',catalog.sources[key])(m,m.exports,require,process,'accepted');
  if(key==='coupled-model.cjs'){
   const original=m.exports.createCoupledModel;
   m.exports={...m.exports,createCoupledModel:(e,o={},observer)=>{
    const history={selectedOptions:{...o,...selected},attempts:[],rollbackChecks:[],records:[],initialRecords:[]};histories.push(history);const modelIndex=histories.length-1;let checkpointAttempt=0;
    let active,pending;
    const physical=s=>JSON.stringify({cells:s.cells,energies:s.energies,ledger:s.ledger,seconds:s.seconds,events:s.events,boundaryEvents:s.boundaryEvents,scheduleIndex:s.scheduleIndex,spec:s.spec,acceptedSteps:s.acceptedSteps});
    const model=original(e,{...o,...selected},attempt=>{
     const snapshot=physical(active);
     if(pending)history.rollbackChecks.push({seconds:attempt.startSeconds,previous:pending.reason,exactPhysicalRollback:snapshot===pending.snapshot});
     const rejected=!!(attempt.failure||attempt.rejectionReason);
     pending=rejected?{snapshot,reason:attempt.failure||attempt.rejectionReason}:null;
     const converged=attempt.events.filter(v=>v.type==='iteration'&&v.status==='converged');
     history.attempts.push({advanceIndex:history.records.length,seconds:attempt.startSeconds,dt:attempt.trialSeconds,rejected,failure:attempt.failure,reason:attempt.rejectionReason,error:attempt.temporalError,iterations:attempt.iterations,evaluations:attempt.evaluations,linearSolves:attempt.linearSolves,maxConvergedFluidNorm:Math.max(0,...converged.map(v=>v.fluidNorm)),maxConvergedThermalNorm:Math.max(0,...converged.map(v=>v.thermalNorm))});
     if(observer)observer(attempt);
    });
    const advance=model.advance,create=model.create;
    return {...model,create(...args){const s=create(...args);initialStates.set(s,JSON.parse(JSON.stringify({sections:s.initialCells,temperaturesK:s.spec.thermal.nodes.map(n=>n.initialK),initialEnergies:s.initialEnergies,declaredInitialPH:s.spec.fluid.initial})));return s;},advance(s,duration){active=s;history.initialRecords.push(initialStates.get(s)||null);const result=advance(s,duration);if(pending){history.rollbackChecks.push({seconds:s.seconds,previous:pending.reason,exactPhysicalRollback:physical(s)===pending.snapshot,terminal:true});pending=null;}history.records.push(result);
     const checkpoint={browser:navigator.userAgent.includes('Chrome/')?'chromium':'webkit',userAgent:navigator.userAgent,choice,block:block.id,model:modelIndex,advanceIndex:history.records.length-1,initial:initialStates.get(s)||null,record:result,attempts:history.attempts.slice(checkpointAttempt),counts:{...adapter.counts},linearMemory:eos.memory(),completeAssertionBlock:false};checkpointAttempt=history.attempts.length;
     // Synchronous loopback telemetry persists completed samples even while the
     // remaining assertion block occupies the JS thread. No property/model call.
     // This overhead belongs to the qualification harness, never cost workloads.
     try{const request=new XMLHttpRequest();request.open('POST','http://127.0.0.1:8871/',false);request.setRequestHeader('Content-Type','text/plain');request.send(JSON.stringify(checkpoint));if(request.status!==200)console.warn('B2 checkpoint HTTP '+request.status);}catch(error){console.warn('B2 optional checkpoint receiver unavailable: '+String(error));}
     return result;}};
   }};
  }
  if(key==='coupled-fixtures.cjs'&&block.caseName){const cases=m.exports.cases;m.exports={...m.exports,cases:()=>cases().filter(c=>c.name===block.caseName)};}
  return m.exports;
 }
 const start=performance.now();
 try{
  const code=catalog.prefix+'\ntry{\n'+catalog.setup+'\n'+block.text+'\nreport.passed=true;\n}catch(error){report.passed=false;report.failure={activeCase,message:error.message,stack:error.stack,lastAcceptedRecord:lastRecord};}\nfs.writeFileSync("capture",JSON.stringify(report));';
  new Function('require','process','__dirname',code)(require,process,'accepted');
  return {id:block.id,line:block.line,harnessVersion:4,assertionTextSHA256:block.sha256,status:captured.passed?'PASS':'FAIL',result:captured,histories,elapsedMS:performance.now()-start,propertyCalls:adapter.counts,linearMemory:eos.memory(),init:eos.init,selected};
 }finally{eos.dispose();}
}
