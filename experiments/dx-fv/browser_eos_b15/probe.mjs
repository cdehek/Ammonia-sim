import fs from 'node:fs';
import {createHash} from 'node:crypto';
import {performance,PerformanceObserver} from 'node:perf_hooks';
import {exact,same,auditRecord,diagnostic} from '../browser_eos_b9/values.mjs';

const [variant='canonical',fixture='warm',schedule='original',horizonText='.01']=process.argv.slice(2);
if(!['control','candidate','observe-control','observe-candidate'].includes(variant)||!['cold','warm'].includes(fixture))throw Error('Invalid bounded invocation');
const schedules={original:[.0001,.0005,.001,.002,.005,.01],added:[.0001,.0005,.001,.002,.005,.00525,.0055,.01],fine:[.0001,.0005,.001,.002,.005,.0051,.0052,.0053,.0054,.0055,.0056,.01]};
const horizon=Number(horizonText);if(!(horizon>0&&horizon<=.01)||!schedules[schedule])throw Error('Horizon/schedule bound');
const targets=schedules[schedule].filter(t=>t<=horizon);
const observed=variant.startsWith('observe-'),timed=false;
const hash=x=>createHash('sha256').update(JSON.stringify(exact(x))).digest('hex');
const emit=x=>fs.writeSync(1,JSON.stringify(x)+'\n');
const pressureCounts={};globalThis.__b15count=k=>pressureCounts[k]=(pressureCounts[k]||0)+1;
const captures={residual:[],linear:[]};const examples={};
const counts={},ms={},calls={},ranges={},stack=[];let column=null,lastTemporal=null,trialIndex=0,stageIndex=0,residualIndex=0;
const columns=[],temporals=[],commits=[],controllers=[],matrices=[],repeats=new Map(),phaseCalls={},contextCounts={},phTrials={};
const add=(obj,key,n=1)=>obj[key]=(obj[key]||0)+n;
const snapshot=()=>({...counts});
const diff=(a,b)=>Object.fromEntries(Object.keys(b).map(k=>[k,b[k]-(a[k]||0)]).filter(([,v])=>v));
const enter=label=>{
 if(label==='stage')stageIndex++;
 add(calls,label);stack.push(label);const t=timed?performance.now():0;
 return ()=>{if(stack.pop()!==label)throw Error('Scope mismatch '+label);if(timed)add(ms,label,performance.now()-t);};
};
const context=()=>column!==null?'column-'+column:stack.includes('residual')?'residual-other':stack.includes('record')?'record':stack.includes('trial')?'trial-other':'initialization';
let publicProperty=null;
const hook={enter,count(k){add(counts,k);},section(hit){add(counts,'section.requests');add(counts,'section.'+(hit?'hits':'misses'));},
 boundary(side,p,h,fn){add(counts,'boundary.requests');const before=counts['property.ph']||0;try{return fn();}finally{add(counts,'boundary.'+((counts['property.ph']||0)>before?'misses':'hits'));}},
 property(method,fn,args){
  add(counts,'property.'+method);const before=snapshot(),t=timed?performance.now():0,previous=publicProperty;publicProperty=method;
  const ctx=context();add(contextCounts,ctx+'.'+method);
  if(method==='ph'){
   const key=args.map(v=>JSON.stringify(exact(v))).join(':');
   if(repeats.size>40000)throw Error('Bounded input-map cap');
   const r=repeats.get(key)||{calls:0,contexts:{},firstStage:stageIndex,stages:new Set()};r.calls++;r.stages.add(stageIndex);add(r.contexts,ctx);repeats.set(key,r);
  }
  try{
   const result=fn(...args);
   if(method==='ph'){
    const group=ctx+'|'+result.phase,row=phaseCalls[group]??={calls:0,branch:0,inverse:0,sat:0,ms:0,minP:Infinity,maxP:-Infinity,minH:Infinity,maxH:-Infinity,minT:Infinity,maxT:-Infinity};
    const trialGroup=trialIndex+'|'+result.phase,tt=phTrials[trialGroup]??={calls:0,branch:0,ms:0};tt.calls++;tt.branch+=(counts['lexical.branch']||0)-(before['lexical.branch']||0);if(timed)tt.ms+=performance.now()-t;
    row.calls++;row.branch+=(counts['lexical.branch']||0)-(before['lexical.branch']||0);row.inverse+=(counts['lexical.inverse']||0)-(before['lexical.inverse']||0);row.sat+=(counts['lexical.sat']||0)-(before['lexical.sat']||0);if(timed)row.ms+=performance.now()-t;
    for(const [key,value]of [['P',args[0]],['H',args[1]],['T',result.T]]){row['min'+key]=Math.min(row['min'+key],value);row['max'+key]=Math.max(row['max'+key],value);}
   }
   return result;
  }catch(e){add(counts,'property.failed');throw e;}finally{if(timed)add(ms,'property.'+method,performance.now()-t);publicProperty=previous;}
 }
};
globalThis.__b9c=hook;
globalThis.__b14={enter,
 column(k,variable,value){if(column!==null)throw Error('Nested column');column=k;const before=snapshot(),t=timed?performance.now():0;const row={trialIndex,stageIndex,column:k,kind:variable.kind,value,probes:[]};columns.push(row);return ()=>{row.counts=diff(before,counts);if(timed)row.ms=performance.now()-t;column=null;if(columns.length>60000)throw Error('Column cap');};},
 probe(step,shrink){columns.at(-1).probes.push({step,shrink});},
 matrix(j){matrices.push(hash(j));if(matrices.length>3000)throw Error('Matrix cap');},
 temporal(s,coarse,fine,error){lastTemporal={trialIndex,startSeconds:s.seconds,initialCells:structuredClone(s.cells),initialEnergies:[...s.energies],coarse:structuredClone(coarse),fine:structuredClone(fine),error};temporals.push(lastTemporal);},
 controller(seconds,proposal,next){controllers.push({seconds,proposal,next});},
 committed(s,piece,dt,start){commits.push({startSeconds:start,seconds:start+dt,dt,cells:structuredClone(s.cells),energies:[...s.energies],states:structuredClone(piece.states),ledger:structuredClone(s.ledger),integratedRate:structuredClone(piece.integratedRate),endpoint:structuredClone(piece.endpoint),error:piece.error});if(commits.length>500)throw Error('Commit cap');}
};
let loader,manifest=null;
const construct=performance.now();
loader=(await import('./'+variant+'-bundle.mjs')).loader;
const load=loader(),engine=load('table-only.cjs').createTableEngine();
if(observed){
 const lin=load('implicit.cjs'),originalLinear=lin.solveLinear;lin.solveLinear=(a,b)=>{const end=enter('linear');try{const delta=originalLinear(a,b);captures.linear.push(hash({a,b,delta}));examples.linear??=exact({a,b,delta});return delta;}finally{end();}};
 const imp=load('coupled-implicit.cjs'),original=imp.coupledNewton;
 imp.coupledNewton=(evaluate,...args)=>{const end=enter('newton');try{return original(x=>{const end=enter('residual');residualIndex++;try{const value=evaluate(x);captures.residual.push(hash({x,value}));return value;}finally{end();}},...args);}finally{end();}};
}
const attempts=[],checkpoints=[];let state,lastProgress=-1;
const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>{
 if(attempts.length>250)throw Error('Attempt cap');attempts.push(a);
 if(observed&&lastTemporal&&lastTemporal.trialIndex===trialIndex){lastTemporal.trialSeconds=a.trialSeconds;lastTemporal.rejectionReason=a.rejectionReason;lastTemporal.failure=a.failure;}
 trialIndex++;
 if(state&&state.seconds!==lastProgress){lastProgress=state.seconds;emit({type:'partial-progress',seconds:state.seconds,cells:state.cells,energies:state.energies,ledger:state.ledger,note:'Earlier accepted state, before pending trial commit'});}
});
const constructionMS=performance.now()-construct;
const createStart=performance.now();
state=model.create(load('coupled-fixtures.cjs').fixture(fixture));let record=model.record(state);const initializationMS=performance.now()-createStart;
const emitCheckpoint=(wallMS,cpuMS)=>{auditRecord(record);const science={state:structuredClone(state),record:structuredClone(record)},r={type:'checkpoint',seconds:state.seconds,science,scienceHash:hash(science),attemptsHash:hash(attempts),wallMS,cpuMS};checkpoints.push(r);emit(r);};
emit({type:'header',variant,fixture,schedule,targets,node:process.version,buildSHA256:createHash('sha256').update(fs.readFileSync(new URL('./'+variant+'-bundle.mjs',import.meta.url))).digest('hex'),constructionMS,initializationMS,settings:model.settings,manifest,qualification:'UNQUALIFIED RESEARCH beyond 0.001 s'});
emitCheckpoint(0,0);
for(const target of targets){
 const t=performance.now(),cpu=process.cpuUsage();record=model.advance(state,target-state.seconds);const d=process.cpuUsage(cpu);emitCheckpoint(performance.now()-t,(d.user+d.system)/1000);if(state.stop)throw Error('Unexpected normal-fixture refusal');
}
const repeatRows=[...repeats.values()];
emit({type:'diagnostics',pressureCounts,captures,examples,counts,ms,calls,columns,temporals,commits,controllers,matrices,phaseCalls,contextCounts,phTrials,repeatPH:{calls:repeatRows.reduce((s,r)=>s+r.calls,0),uniqueInputs:repeats.size,duplicateCalls:repeatRows.reduce((s,r)=>s+Math.max(0,r.calls-1),0),repeatedAcrossStages:repeatRows.filter(r=>r.stages.size>1).length,top:[...repeats].sort((a,b)=>b[1].calls-a[1].calls).slice(0,15).map(([input,r])=>({input,calls:r.calls,contexts:r.contexts,stageCount:r.stages.size}))}});
emit({type:'attempts',attempts});
emit({type:'complete',seconds:state.seconds,stop:state.stop,resource:process.resourceUsage(),memory:process.memoryUsage(),stackEmpty:stack.length===0});
