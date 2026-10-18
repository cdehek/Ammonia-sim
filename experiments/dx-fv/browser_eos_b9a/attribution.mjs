import {loader} from '../browser_eos_b9/accepted-bundle.mjs';
import {same,exact,assert} from '../browser_eos_b9/values.mjs';
const now=()=>performance.now();
function run(instrumented,fixture){
 const load=loader(),cost={},counts={};
 const time=(name,fn)=>function(...args){const t=now();try{return Reflect.apply(fn,this,args);}finally{cost[name]=(cost[name]||0)+now()-t;counts[name]=(counts[name]||0)+1;}};
 const all=now(),parse=now(),data=load('properties.json'),parseMS=now()-parse;
 const factory=now(),raw=load('engine.js').createEngine(data),engineMS=now()-factory;
 const propertyCounts={};const engine=new Proxy(raw,{get(o,k){const f=o[k];return typeof f!=='function'?f:function(...args){propertyCounts[k]=(propertyCounts[k]||0)+1;return Reflect.apply(instrumented?time('engine.'+k,f):f,o,args);};}});
 if(instrumented){
 const thermo=load('thermodynamics.cjs'),original=thermo.createThermodynamics;
 thermo.createThermodynamics=function(...args){const t=original(...args);for(const k of Object.keys(t))t[k]=time('thermo.'+k,t[k]);return t;};
 const linear=load('implicit.cjs');linear.solveLinear=time('linearSolve',linear.solveLinear);
 const implicit=load('coupled-implicit.cjs'),originalNewton=implicit.coupledNewton;
 implicit.coupledNewton=time('NewtonInclusive',function(evaluate,...args){return originalNewton(time('residualInclusive',evaluate),...args);});
 }
 const attempts=[],observer=a=>attempts.push(a),make=now();
 const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},instrumented?time('observerCallback',observer):observer),factoryMS=now()-make;
 const create=now(),state=model.create(load('coupled-fixtures.cjs').fixture(fixture)),createMS=now()-create;
 let t=now();const initial=model.record(state),recordMS=now()-t;const rows=[{state:structuredClone(state),record:initial}],advances=[];
 for(const duration of [.0001,.0004,.0005]){t=now();const record=model.advance(state,duration);advances.push(now()-t);rows.push({state:structuredClone(state),record});}
 const totalMS=now()-all;
 const events=attempts.flatMap(a=>a.events),types={};for(const e of events)types[e.type]=(types[e.type]||0)+1;
 const micro={};const payload={...rows.at(-1),attempts};
 for(const [k,fn] of Object.entries({stateClone:()=>structuredClone(state),attemptClone:()=>structuredClone(attempts),cacheClone:()=>structuredClone(payload),bitTag:()=>exact(payload),fullComparisonSerialization:()=>JSON.stringify(exact(payload)),jsonSizeEstimate:()=>JSON.stringify(payload)})){
 const samples=[];for(let i=0;i<3;i++){t=now();fn();samples.push(now()-t);}micro[k]=samples;
 }
 return {instrumented,fixture,parseMS,engineMS,factoryMS,createMS,recordMS,advances,totalMS,cost,counts,propertyCounts,eventTypes:types,micro,payloadJSONEstimateBytes:new TextEncoder().encode(JSON.stringify(payload)).length,science:{rows,attempts}};
}
export async function local(){const results=[];for(const fixture of ['cold','warm'])for(let round=0;round<3;round++){
 const runs=(round%2?[true,false]:[false,true]).map(i=>run(i,fixture));assert(same(runs[0].science,runs[1].science),'attribution changed scientific work');assert(same(runs[0].propertyCounts,runs[1].propertyCounts));for(const r of runs)delete r.science;results.push({round,fixture,exactParity:true,runs});
 }return {passed:true,results,limitation:'Inclusive nested timers overlap; private FD/line-search/commit loops not independently timed'};}
export async function worker(){const w=new Worker(new URL('./attribution-worker.mjs',import.meta.url),{type:'module'});try{return await new Promise((resolve,reject)=>{const t=setTimeout(()=>reject(Error('attribution timeout')),90000);w.onmessage=e=>{clearTimeout(t);e.data.success?resolve(e.data.result):reject(Error(JSON.stringify(e.data.error)));};w.onerror=e=>{clearTimeout(t);reject(Error(e.message));};});}finally{w.terminate();}}
