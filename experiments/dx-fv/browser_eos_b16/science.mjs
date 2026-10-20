import {same,assert,diagnostic,auditRecord,exact} from './assets/values.mjs';
import {Stream,hash} from './hash.mjs';
export const schedules={original:[.0001,.0005,.001,.002,.005,.01],added:[.0001,.0005,.001,.002,.005,.00525,.0055,.01],fine:[.0001,.0005,.001,.002,.005,.0051,.0052,.0053,.0054,.0055,.0056,.01]};
export const options={trace:true,timestepGrowth:'failure-aware'};
export async function open(variant){
 assert(['control','candidate','count-control','count-candidate','observe-control','observe-candidate'].includes(variant),'variant');
 const t=performance.now(),{loader}=await import('./assets/'+variant+'-bundle.mjs'),importMS=performance.now()-t;
 const t2=performance.now(),load=loader(),engine=load('table-only.cjs').createTableEngine();return {load,engine,importMS,tableMS:performance.now()-t2};
}
export function setup(load,engine,fixture,config,extra={}){
 const attempts=[],model=load('coupled-model.cjs').createCoupledModel(engine,{...options,...extra},a=>{assert(attempts.length<256,'attempt cap');attempts.push(a);});
 const state=model.create(config??load('coupled-fixtures.cjs').fixture(fixture));return {model,state,attempts};
}
export function replay(load,engine,fixture,schedule='original'){
 const s=setup(load,engine,fixture);let record=s.model.record(s.state);for(const target of schedules[schedule]){record=s.model.advance(s.state,target-s.state.seconds);assert(!s.state.stop,'unexpected stop');}return {...s,record};
}
export function diagnostics(load){
 const streams={},counts={},contexts={},stack=[];let column=null;
 const capture=(k,v)=>{(streams[k]??=new Stream()).add(v);};
 const inc=(k,n=1)=>counts[k]=(counts[k]||0)+n;
 const enter=k=>{stack.push(k);return ()=>assert(stack.pop()===k,'diagnostic scope');};
 globalThis.__b15count=k=>inc(k);
 globalThis.__b9c={enter,count:k=>inc('b9c.'+k),section(hit){inc('section.'+(hit?'hit':'miss'));},boundary(side,p,h,fn){const n=counts['public.ph']||0;try{return fn();}finally{inc('boundary.'+((counts['public.ph']||0)>n?'miss':'hit'));}},property(method,fn,args){
  inc('public.'+method);const ctx=column!==null?'column-'+column:stack.includes('residual')?'residual-other':stack.includes('record')?'record':stack.includes('trial')?'trial-other':'outside-stage';
  try{const value=fn(...args);if(method==='ph'){const key=ctx+'|'+value.phase;contexts[key]=(contexts[key]||0)+1;}return value;}catch(e){inc('failed.'+method);throw e;}
 }};
 globalThis.__b14={enter,column(k,variable,value){assert(column===null,'column scope');column=k;capture('columns',{k,variable,value});return ()=>column=null;},probe(step,shrink){capture('probes',{step,shrink});},matrix:j=>capture('matrices',j),temporal(s,coarse,fine,error){capture('temporals',{s,coarse,fine,error});},controller(seconds,proposal,next){capture('controllers',{seconds,proposal,next});},committed(s,piece,dt,start){capture('commits',{s,piece,dt,start});}};
 const lin=load('implicit.cjs'),L=lin.solveLinear;lin.solveLinear=(a,b)=>{const delta=L(a,b);capture('linear',{a,b,delta});return delta;};
 const imp=load('coupled-implicit.cjs'),N=imp.coupledNewton;imp.coupledNewton=(evaluate,...args)=>N(x=>{const end=enter('residual');try{const value=evaluate(x);capture('residuals',{x,value});return value;}finally{end();}},...args);
 return {capture,counts,contexts,finish(){assert(stack.length===0&&column===null,'empty scopes');return {streams:Object.fromEntries(Object.entries(streams).map(([k,v])=>[k,v.finish()])),counts,contexts};}};
}
export async function parityRun(variant,fixture,schedule,observed=false){
 globalThis.__b15count=()=>{};const {load,engine}=await open((observed?'observe-':'')+variant),d=observed?diagnostics(load):null;
 const s=setup(load,engine,fixture),checkpoints=[],audits=[];
 function checkpoint(){const record=s.model.record(s.state);audits.push(auditRecord(record));checkpoints.push({seconds:s.state.seconds,sha256:hash({state:s.state,record}),phase:record.sections.map(v=>v.phase),flows:record.fluxes.faces.map(v=>v.massKgS)});}
 checkpoint();for(const target of schedules[schedule]){s.model.advance(s.state,target-s.state.seconds);assert(!s.state.stop,'unexpected parity stop');checkpoint();}
 return {fixture,schedule,observed,checkpoints,attempts:hash(s.attempts),events:exact(s.state.events),finalClock:s.state.seconds,accepted:s.state.acceptedSteps,rejected:s.state.rejectedSteps,audits,diagnostics:d?.finish(),passed:true};
}
const outcome=fn=>{try{return {ok:true,value:fn()};}catch(e){return {ok:false,error:diagnostic(e)};}};
export async function failures(variant){
 const {load,engine}=await open(variant),rows=[];
 for(const [p,h]of [[NaN,500],[0,500],[35.0001,1700],[4,NaN],[4,1e9],[4,-1e9]]){const raw=outcome(()=>engine.ph(p,h)),wrapped=outcome(()=>load('thermodynamics.cjs').createThermodynamics(engine).ph(p,h));assert(!wrapped.ok,'validated property interface must refuse');if(!Number.isNaN(h))assert(!raw.ok,'original raw failure');rows.push({p,h,raw,wrapped});}
 const counter=engine.statePT(4,50,undefined,{value:[0,0]});assert(same(counter,engine.statePT(4,50)),'private holder');
 for(const fourth of [null,false,{get value(){throw Error('external holder read');}}])assert(same(engine.statePT(4,50,undefined,fourth),counter),'extra public arg');
 for(const partial of [false,true]){
  const config={sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:200,finProfileK:200,airInitialK:200,airLoadKW:0},...(partial?{schedule:[{seconds:.0001,patch:{airLoadKW:-1}}]}:{})},s=setup(load,engine,'cold',config);
  if(!partial)s.model.update(s.state,{airLoadKW:-1});
  const record=s.model.advance(s.state,.0002);assert(s.state.stop?.kind==='domain'&&s.state.stop.evidence.confirmed,'genuine domain refusal');assert(s.state.seconds===(partial?.0001:0),'partial clock');
  const before=structuredClone(s.state);assert(same(s.model.advance(s.state,.0001),record)&&same(before,s.state),'stopped repeat');rows.push({partial,state:s.state,record,attempts:s.attempts});
 }
 const s=setup(load,engine,'cold',undefined,{maxIterations:1,maxAttempts:20});const record=s.model.advance(s.state,.0001);assert(s.state.stop?.kind==='solver','original solver refusal');rows.push({numerical:true,state:s.state,record,attempts:s.attempts});
 const p=setup(load,engine,'cold'),before=structuredClone(p.state);const invalid=outcome(()=>p.model.update(p.state,{inlet:{p:4,h:1e9}}));assert(!invalid.ok&&same(before,p.state),'invalid update rollback');rows.push(invalid);
 return {passed:true,sha256:hash(rows),rows:exact(rows),publicArity:engine.statePT.length,counter:exact(counter)};
}
export function propertyBench(engine,n=20000){
 const inputs={vapor:[],twoPhase:[],mixed:[]};for(const p of [3.5,3.65,4,6,12]){const a=engine.sat(p);for(const dh of [.00001,.1,5,50,150])inputs.vapor.push([p,a.hg+dh]);for(const x of [.1,.3,.5,.7,.9])inputs.twoPhase.push([p,a.hf+(a.hg-a.hf)*x]);inputs.mixed.push([p,(a.hf+a.hg)/2],[p,a.hg+50]);}
 const loop=(xs,n)=>{let checksum=0;for(let i=0;i<n;i++){const[p,h]=xs[i%xs.length];checksum+=engine.ph(p,h).rho;}return checksum;},results={};
 for(const[k,xs]of Object.entries(inputs)){loop(xs,3000);const t=performance.now(),checksum=loop(xs,n);results[k]={wallMS:performance.now()-t,calls:n,warmupCalls:3000,checksum};}return results;
}
