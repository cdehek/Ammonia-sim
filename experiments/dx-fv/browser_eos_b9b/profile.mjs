import {loader as originalLoader} from '../browser_eos_b9/accepted-bundle.mjs';
import {loader as diagnosticLoader} from './diagnostic-bundle.mjs';
import {same,exact,assert,auditRecord,bits,diagnostic} from '../browser_eos_b9/values.mjs';
const now=()=>performance.now();
export function run(mode,fixture,{sequence=false}={}){
 const instrumented=mode==='instrumented',wrapped=mode==='pass-through'||instrumented;
 const metrics={counts:{},phaseCounts:{},phaseInclusiveMS:{},phaseExclusiveMS:{},inclusiveMS:{},exclusiveMS:{},cache:{requests:0,hits:0,misses:0},events:[],propertyByContext:{},residuals:[],solves:[],linear:[]};
 const stack=[],calls=[],propertyCounts={},attempts=[],contexts=[];
 const count=k=>{metrics.counts[k]=(metrics.counts[k]||0)+1;const c=metrics.phaseCounts[contexts[0]||'outside']??={};c[k]=(c[k]||0)+1;};
 function enter(name,args=[]){
  count(name);const frame={name,start:now(),child:0};stack.push(frame);
  let event;const phase=contexts[0]||'outside';
  if(['model.trial','model.solveStage','model.commit','model.record'].includes(name)){event={name,args,phase,id:metrics.events.length,parent:stack.slice(0,-1).findLast(f=>f.event)?.event.id??null,propertyBefore:{...propertyCounts},cacheBefore:{...metrics.cache}};frame.event=event;metrics.events.push(event);}
  return ()=>{const elapsed=now()-frame.start;assert(stack.pop()===frame,'timer stack');metrics.inclusiveMS[name]=(metrics.inclusiveMS[name]||0)+elapsed;metrics.exclusiveMS[name]=(metrics.exclusiveMS[name]||0)+elapsed-frame.child;if(stack.length)stack.at(-1).child+=elapsed;
   const inclusive=metrics.phaseInclusiveMS[phase]??={},exclusive=metrics.phaseExclusiveMS[phase]??={};inclusive[name]=(inclusive[name]||0)+elapsed;exclusive[name]=(exclusive[name]||0)+elapsed-frame.child;
   if(event){event.inclusiveMS=elapsed;event.propertyDelta=Object.fromEntries(Object.entries(propertyCounts).map(([k,v])=>[k,v-(event.propertyBefore[k]||0)]));event.cacheDelta=Object.fromEntries(Object.entries(metrics.cache).map(([k,v])=>[k,v-event.cacheBefore[k]]));delete event.propertyBefore;delete event.cacheBefore;}
  };
 }
 globalThis.__b9b={enter,count,cache(key,hit){metrics.cache.requests++;metrics.cache[hit?'hits':'misses']++;},note(name,args){metrics.events.push({name,args,phase:contexts[0]});}};
 const load=instrumented?diagnosticLoader():originalLoader();
 const wrap=(name,fn,after)=>function(...args){if(!instrumented)return Reflect.apply(fn,this,args);const end=enter(name);try{const result=Reflect.apply(fn,this,args);after?.(args,result);return result;}finally{end();}};
 const raw=load('engine.js').createEngine(load('properties.json'));
 const engine=new Proxy(raw,{get(o,k){const fn=o[k];if(typeof fn!=='function')return fn;return function(...args){
  propertyCounts[k]=(propertyCounts[k]||0)+1;
  if(!instrumented&&!sequence)return Reflect.apply(fn,o,args);
  const context=[...contexts,...stack.map(f=>f.name)].join('/');
  if(instrumented){const c=metrics.propertyByContext[context]??={};c[k]=(c[k]||0)+1;}
  const end=instrumented?enter('engine.'+k):()=>{};
  try{const result=Reflect.apply(fn,o,args);if(sequence)calls.push({method:k,args,result});return result;}catch(e){if(sequence)calls.push({method:k,args,error:diagnostic(e)});throw e;}finally{end();}
 };}});
 if(wrapped){
  const thermo=load('thermodynamics.cjs'),f=thermo.createThermodynamics;
  thermo.createThermodynamics=function(...a){const t=f(...a);for(const k of Object.keys(t))t[k]=wrap('thermo.'+k,t[k]);return t;};
  const linear=load('implicit.cjs');linear.solveLinear=wrap('linearSolve',linear.solveLinear,(a,x)=>{
   // Read-only matrix/correction diagnostics; no second solve and no feedback.
   const matrix=a[0],rhs=a[1],n=rhs.length,diagonal=matrix.map((r,i)=>Math.abs(r[i]));
   const normA=Math.max(...matrix.map(r=>r.reduce((s,v)=>s+Math.abs(v),0))),normX=Math.max(...x.map(Math.abs));
   const absoluteResidual=Math.max(...matrix.map((r,i)=>Math.abs(r.reduce((s,v,j)=>s+v*x[j],0)-rhs[i])));
   metrics.linear.push({n,normA,diagonalMin:Math.min(...diagonal),diagonalMax:Math.max(...diagonal),absoluteResidual,normX,conditionNumber:null});
  });
  const implicit=load('coupled-implicit.cjs'),fNewton=implicit.coupledNewton;
  implicit.coupledNewton=wrap('NewtonInclusive',function(evaluate,initial,variables,settings,work,exactColumns){
   if(!instrumented)return fNewton(wrap('residualInclusive',evaluate),initial,variables,settings,work,exactColumns);
   const solve={id:(work.diagnosticSolveCount||0)+1,context:structuredClone(work.diagnosticContext),initial:[...initial],residuals:0,exactThermal:!!exactColumns};if(instrumented)metrics.solves.push(solve);
   const callback=wrapped?wrap('residualInclusive',function(x){solve.residuals++;return evaluate(x);}):evaluate;
   return fNewton(callback,initial,variables,settings,work,exactColumns);
  });
 }
 const initStart=now();contexts.push('initialization');
 const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>attempts.push(a));
 const config=load('coupled-fixtures.cjs').fixture(fixture),state=model.create(config),rows=[],timing=[],initial=model.record(state);
 rows.push({state:structuredClone(state),record:initial,attempts:null});contexts.pop();const initializationMS=now()-initStart;
 for(const duration of [.0001,.0004,.0005]){
  const startSeconds=state.seconds,proposal=state.nextStepSeconds,a0=attempts.length,countsBefore={...propertyCounts};contexts.push('advance-'+duration);
  const t=now(),record=model.advance(state,duration),advanceMS=now()-t;contexts.pop();
  const cloneStart=now();rows.push({state:structuredClone(state),record,attempts:structuredClone(attempts.slice(a0))});const stateAndAttemptCopyMS=now()-cloneStart;
  contexts.push('extra-snapshot-record');const r0=now(),snapshot=model.record(state),snapshotRecordMS=now()-r0;contexts.pop();assert(same(snapshot,record),'record purity');
  timing.push({duration,startSeconds,acceptedIncrement:state.seconds-startSeconds,originalProposal:proposal,nextProposal:state.nextStepSeconds,advanceMS,snapshotRecordMS,stateAndAttemptCopyMS,propertyDelta:Object.fromEntries(Object.entries(propertyCounts).map(([k,v])=>[k,v-(countsBefore[k]||0)]))});
 }
 const audits=rows.map(r=>auditRecord(r.record));
 return {mode,fixture,initializationMS,timing,propertyCounts,metrics,science:{rows,attempts},audits,config,settings:model.settings,sequence:sequence?exact(calls):null,timerResolutionMS:resolution(),notAcceptedA2:instrumented};
}
function resolution(){let previous=now(),delta=Infinity;for(let i=0;i<10000;i++){const t=now();if(t>previous)delta=Math.min(delta,t-previous);previous=t;}return Number.isFinite(delta)?delta:null;}
export async function digest(v){const bytes=new TextEncoder().encode(JSON.stringify(exact(v)));return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');}
export async function seal(r){r.checkpointHashes=await Promise.all(r.science.rows.map(row=>digest({record:row.record,state:row.state})));r.scienceHash=await digest(r.science);if(r.sequence){r.sequenceHash=await digest(r.sequence);delete r.sequence;}return r;}
export async function failures(){
 const original=await(await import('../browser_eos_b9/c1-tests.mjs')).local(),{c1Session}=await import('../browser_eos_b9a/c1-session.mjs'),results=[];
 for(const instrumented of [false,true])for(const scenario of ['transient','persistent','boundary','recordFailure','thermal200','thermal400']){
  const load=originalLoader(),raw=load('engine.js').createEngine(load('properties.json')),counts={};
  const table=instrumented?new Proxy(raw,{get(o,k){const fn=o[k];return typeof fn==='function'?function(...a){counts[k]=(counts[k]||0)+1;return Reflect.apply(fn,o,a);}:fn;}}):raw;
  const attempts=[],s=c1Session(table,scenario,a=>attempts.push(a));let record,error;
  try{record=s.model.advance(s.state,.001);}catch(e){error=diagnostic(e);}
  const proof=s.proof();results.push({instrumented,scenario,proof,record,error,attempts,counts});
 }
 for(const scenario of ['transient','persistent','boundary','recordFailure','thermal200','thermal400']){
  const [a,b]=results.filter(r=>r.scenario===scenario);assert(same({...a,instrumented:null,counts:null},{...b,instrumented:null,counts:null}),'failure wrapper parity '+scenario);
  assert(scenario==='transient'?a.proof.failures===2:a.proof.acceptedBitsUnchanged&&a.proof.identityUnchanged,'failure contract');
 }
 return {passed:true,original,results};
}
