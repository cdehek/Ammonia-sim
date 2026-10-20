// Node worker/process research harness. Scientific registry files are imported read-only.
import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {exact, diagnostic, auditRecord, same} from '../browser_eos_b9/values.mjs';
const [variant='canonical',fixture='cold',targetText='0.0001,0.0005,0.001']=process.argv.slice(2);
const targets=targetText.split(',').map(Number);
if(!['canonical','observed','control'].includes(variant)||!['cold','warm'].includes(fixture)||targets.some((t,i)=>!Number.isFinite(t)||t<=0||t>.01||(i&&t<=targets[i-1])))throw Error('Bounded research arguments required');
const hash=v=>createHash('sha256').update(JSON.stringify(exact(v))).digest('hex');
const emit=v=>fs.writeSync(1,JSON.stringify(v)+'\n');
const stats={propertyRanges:{},counts:{},calls:{},ms:{},section:{requests:0,hits:0,misses:0},boundary:{requests:0,hits:0,misses:0},propertyErrors:[],stages:[],newton:[]};
const stack=[];
const add=(o,k,v=1)=>o[k]=(o[k]||0)+v;
const enter=label=>{const t=performance.now();add(stats.calls,label);stack.push(label);return ()=>{if(stack.pop()!==label)throw Error('Instrumentation scope mismatch');add(stats.ms,label,performance.now()-t);};};
const probe={enter,count:k=>add(stats.counts,k),section(hit){stats.section.requests++;stats.section[hit?'hits':'misses']++;},
 boundary(side,p,h,fn){stats.boundary.requests++;const n=stats.calls['property.ph']||0;try{return fn();}finally{stats.boundary[(stats.calls['property.ph']||0)>n?'misses':'hits']++;}},
 property(method,fn,args){const end=enter('property.'+method);try{const result=fn(...args),range=stats.propertyRanges[method]??={count:0,phase:{},min:{},max:{}};range.count++;for(const k of ['p','h','T','x'])if(Number.isFinite(result[k])){range.min[k]=Math.min(range.min[k]??Infinity,result[k]);range.max[k]=Math.max(range.max[k]??-Infinity,result[k]);}if(result.phase)add(range.phase,result.phase);return result;}catch(e){if(stats.propertyErrors.length<100)stats.propertyErrors.push({method,args,error:diagnostic(e)});throw e;}finally{end();}}
};
let loader;
const constructionStart=performance.now();
if(variant==='observed'){
 globalThis.__b9c=probe;
 // A measurement-only copy in memory. Exact replacements fail closed on drift.
 let src=fs.readFileSync(new URL('../browser_eos_b9c/diagnostic-candidate-bundle.mjs',import.meta.url),'utf8');
 const change=(a,b)=>{if(src.split(a).length!==2)throw Error('Instrumentation anchor drift: '+a);src=src.replace(a,b);};
 change('for (let k = 0; k < x.length; k++) {',"const __endJac=globalThis.__b9c.enter('jacobian');try{\nfor (let k = 0; k < x.length; k++) {");
 change('      work.linearSolves++;', '      }finally{__endJac();}\n      work.linearSolves++;');
 loader=(await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'))).loader;
}else loader=(await import(variant==='control'?'../browser_eos_b9c/control-bundle.mjs':'../browser_eos_b9c/candidate-bundle.mjs')).loader;
const load=loader(),engine=load('table-only.cjs').createTableEngine();
if(variant==='observed'){
 // Install before coupled-implicit/model destructure these exports.
 const lin=load('implicit.cjs'),L=lin.solveLinear;
 lin.solveLinear=(a,b)=>{const end=enter('linear');try{return L(a,b);}finally{end();}};
 const imp=load('coupled-implicit.cjs'),N=imp.coupledNewton;
 imp.coupledNewton=(evaluate,initial,variables,settings,work,columns)=>{
  const end=enter('newton'),start={evaluations:work.evaluations,iterations:work.iterations,linearSolves:work.linearSolves};
  const row={context:work.diagnosticContext};
  try{const value=N(x=>{const end=enter('residual');try{return evaluate(x);}finally{end();}},initial,variables,settings,work,columns);row.error=value.error;return value;}
  catch(e){row.failure=diagnostic(e);throw e;}
  finally{row.evaluations=work.evaluations-start.evaluations;row.iterations=work.iterations-start.iterations;row.linearSolves=work.linearSolves-start.linearSolves;stats.newton.push(row);end();}
 };
}
let state,attempts=[],lastProgress=-1,observerMS=0,fatalFault=null;
const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>{
 const t=performance.now();attempts.push(a);
 // On termination retain actual earlier committed substeps. This snapshot precedes
 // the current trial's commit; it never claims the pending trial was accepted.
 if(state&&state.seconds!==lastProgress){lastProgress=state.seconds;emit({type:'partial-progress',seconds:state.seconds,physical:{cells:state.cells,energies:state.energies,ledger:state.ledger,spec:state.spec,acceptedSteps:state.acceptedSteps},warning:'Last accepted state observed before current trial commit; current trial not accepted by this receipt.'});}
 observerMS+=performance.now()-t;
});
const constructionMS=performance.now()-constructionStart;
const init=performance.now();state=model.create(load('coupled-fixtures.cjs').fixture(fixture));let record=model.record(state);
const initializationMS=performance.now()-init;
function checkpoint(requested,start,timing){
 let audit,auditError;try{audit=auditRecord(record);}catch(e){auditError=diagnostic(e);}
 const science={state:structuredClone(state),record:structuredClone(record)};
 const result={type:'checkpoint',variant,fixture,qualification:state.seconds>.001?'UNQUALIFIED RESEARCH':'ACCEPTED-HORIZON BASELINE REPRODUCTION',requestedIncrement:requested,actualIncrement:state.seconds-start,seconds:state.seconds,...timing,science,scienceExact:exact(science),scienceHash:hash(science),attemptsHash:hash(attempts),attempts:structuredClone(attempts),audit,auditError,stats:variant==='observed'?structuredClone(stats):null,resource:process.resourceUsage(),memory:process.memoryUsage()};
 emit(result);return !auditError&&!state.stop;
}
emit({type:'header',variant,fixture,targets,constructionMS,initializationMS,node:process.version,platform:process.platform,arch:process.arch,settings:model.settings,qualification:'B13-A0 diagnostic research; accepted horizon remains 0.001 s'});
checkpoint(0,0,{wallMS:0,observerMS:0});
for(const target of targets){
 stats.propertyRanges={};
 const start=state.seconds,requested=target-start,begin=performance.now(),obs0=observerMS,cpu=process.cpuUsage();let error,recordUnavailable=false;
 try{record=model.advance(state,requested);}catch(e){error=diagnostic(e);fatalFault=error;try{record=model.record(state);}catch(re){recordUnavailable=true;emit({type:'record-refusal',error:diagnostic(re),advanceError:error,state:exact(state),warning:'Current record unavailable; no stale record is represented as current.'});}}
 if(recordUnavailable)break;
 const wallMS=performance.now()-begin,cpuUsage=process.cpuUsage(cpu);
 const ok=checkpoint(requested,start,{wallMS,observerMS:observerMS-obs0,cpuMS:(cpuUsage.user+cpuUsage.system)/1000,error});
 if(error||!ok)break;
}
if(state.stop){const before=hash({cells:state.cells,energies:state.energies,ledger:state.ledger,seconds:state.seconds}),again=model.advance(state,.0001);emit({type:'stopped-repeat',unchanged:before===hash({cells:state.cells,energies:state.energies,ledger:state.ledger,seconds:state.seconds}),stop:again.stop});}
emit({type:'complete',seconds:state.seconds,stop:state.stop,fatalFault,settings:model.settings,stackEmpty:stack.length===0});
