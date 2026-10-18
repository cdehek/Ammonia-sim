import {verifyHash} from './verification.mjs';
import {service as baseline,BACKEND} from '../browser_eos_b9/service.mjs';
import {diagnostic,same,exact,assert,auditRecord} from './values.mjs';
import {compact} from './snapshot.mjs';
export {BACKEND};
export function service(workerId,sessionId,{mode='B',test=false}={}){
 if(mode==='A')return baseline(workerId,sessionId);
 if(!['B','C'].includes(mode))throw Error('Unsupported transport mode');
 let sequence=0,status='new',model=null,state=null,counts={},attempts=[],stopped=false,lastClock=null,lastVersion=null,record=null,fault=null;
 let c1=null;let proof=null,reference=null,referenceSequence=0,fixtures=null,verifiedEndpoints=[];
 const cache=new Map(),evidence=new Map();let chain=Promise.resolve();
 const envelope=q=>({protocol:1,mode,workerId,backendId:BACKEND,requestId:q?.requestId??null,sessionId,sequence:q?.sequence??null,type:q?.type??null,clock:state?.seconds??lastClock,acceptedVersion:state?.acceptedSteps??lastVersion,status,diagnosticScope:mode==='B'?'complete-generation/cumulative-session':'complete-generation/four-recent-endpoints'});
 function retain(a0=0){if(!state)return;evidence.delete(state.acceptedSteps);evidence.set(state.acceptedSteps,{clock:state.seconds,acceptedVersion:state.acceptedSteps,record,attempts:attempts.slice(a0),fault:structuredClone(fault),counts:{...counts}});while(evidence.size>4)evidence.delete(evidence.keys().next().value);}
 function view(){return record?compact(record,state,{status,fault}):null;}
 async function verifyControl(type,args){if(!reference)return;
 const q={protocol:1,workerId:'control',backendId:BACKEND,sessionId:'control',requestId:String(++referenceSequence),sequence:referenceSequence,type,args};
 const r=await reference(q);assert(r.success,'reference failed');assert(same(state,r.result.state),'STOP full state parity');assert(same(record,r.result.record),'STOP record parity');if(type==='advance'){assert(same(attempts.slice(proof),r.result.attempts),'STOP attempt parity');}
 verifiedEndpoints.push({clock:state.seconds,version:state.acceptedSteps,audit:auditRecord(record),state:exact(state),record:exact(record),propertyCalls:r.result.propertyCalls??null,attemptsExact:type==='advance',scientificStateComparedInsideOwner:true});
 }
 async function execute(q){const start=performance.now(),components={};
 const refuse=message=>({...envelope(q),success:false,error:{name:'ProtocolError',message},fault:structuredClone(fault??state?.stop??null),displayStale:!!state,result:null,timing:{serviceMS:performance.now()-start}});
 if(!q||q.protocol!==1||q.workerId!==workerId||q.backendId!==BACKEND||q.sessionId!==sessionId||typeof q.requestId!=='string'||!q.requestId.length||!Number.isSafeInteger(q.sequence))return refuse('Invalid request envelope');
 if(cache.has(q.requestId)){const old=cache.get(q.requestId);return same(old.q,q)?structuredClone(old.response):refuse('Duplicate ID content mismatch');}
 if(q.sequence!==sequence+1)return refuse('Out-of-order command sequence');sequence=q.sequence;
 if(cache.size>=256&&q.type!=='dispose')return refuse('Session response cache exhausted');
 let response,scientificDispatch=false;
 try{let result;
 if(status==='disposed')throw Error('Disposed model request');
 if(q.args?.expectedVersion!==undefined&&q.args.expectedVersion!==state?.acceptedSteps)throw Error('Stale accepted-state version');
 switch(q.type){
 case 'initialize':{
 if(status!=='new')throw Error('Session already initialized');status='initializing';
 let t=performance.now();const {loader}=await import('../browser_eos_b9/accepted-bundle.mjs');components.importMS=performance.now()-t;const load=loader();
 t=performance.now();const data=load('properties.json');components.tableParseAndLoaderMS=performance.now()-t;
 t=performance.now();const raw=load('engine.js').createEngine(data);components.engineConstructionMS=performance.now()-t;
 const engine=new Proxy(raw,{get(o,k){const f=o[k];return typeof f!=='function'?f:(...a)=>{counts[k]=(counts[k]||0)+1;return Reflect.apply(f,o,a);};}});
 if(!['cold','warm'].includes(q.args?.fixture))throw Error('Unsupported original fixture');fixtures=q.args.fixture;
 if(q.args.c1Scenario){if(!test)throw Error('Test-only C1 disabled');const {c1Session}=await import('./c1-session.mjs');c1=c1Session(raw,q.args.c1Scenario,a=>attempts.push(a));({model,state,record}=c1);status='ready';retain();}
 else {
 t=performance.now();model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>attempts.push(a));components.modelFactoryMS=performance.now()-t;
 t=performance.now();state=model.create(load('coupled-fixtures.cjs').fixture(fixtures));components.modelConstructionMS=performance.now()-t;
 t=performance.now();record=model.record(state);components.initialRecordMS=performance.now()-t;status='ready';retain();
 if(test){reference=baseline('control','control');await verifyControl('initialize',{fixture:fixtures});}}
 t=performance.now();result={compact:view()};components.projectionMS=performance.now()-t;break;}
 case 'advance':{
 if(!state||stopped)throw Error(stopped?'Session stopped at accepted boundary':'Model unavailable');
 if(state.stop)throw Error('Model stopped; original fault history retained');
 if(mode==='C')attempts=[];const a0=attempts.length,before={...counts};proof=a0;
 scientificDispatch=true;const t=performance.now();record=model.advance(state,q.args?.duration);components.advanceMS=performance.now()-t;
 fault=structuredClone(state.stop);status=state.stop?(state.stop.kind==='domain'?'physical-domain-stop':'numerical-stop'):'ready';retain(a0);
 await verifyControl('advance',{duration:q.args?.duration});
 const project=performance.now();result={compact:view(),advanceMS:components.advanceMS,propertyCalls:Object.fromEntries(Object.entries(counts).map(([k,v])=>[k,v-(before[k]||0)]))};components.projectionMS=performance.now()-project;break;}
 case 'snapshot':{if(!state)throw Error('Model unavailable');scientificDispatch=true;const t=performance.now();record=model.record(state);components.recordMS=performance.now()-t;await verifyControl('snapshot',{});result={compact:view()};break;}
 case 'snapshotCompact':if(!state)throw Error('Model unavailable');result={compact:view()};break;
 case 'diagnosticsSummary':case 'diagnosticsDetail':{
 if(!state)throw Error('Model unavailable');const version=q.args?.version;if(!Number.isSafeInteger(version))throw Error('Explicit diagnostic accepted version required');const e=evidence.get(version);
 result=e?{available:true,acceptedVersion:version,clock:e.clock,scope:mode==='B'?'endpoint original record/attempts; cumulative session via diagnostics':'endpoint original record/attempts; four recent only',fault:structuredClone(e.fault),counts:{...e.counts},attemptCount:e.attempts.length}: {available:false,acceptedVersion:version,reason:'unavailable/expired',retainedVersions:[...evidence.keys()]};
 if(e&&q.type==='diagnosticsDetail'){result.record=structuredClone(e.record);result.attempts=structuredClone(e.attempts);result.state=version===state.acceptedSteps?structuredClone(state):null;result.stateScope=result.state?'current full authoritative copy':'historic scientific state not retained';}break;}
 case 'diagnostics':if(!state)throw Error('Model unavailable');result={counts:{...counts},attempts:structuredClone(mode==='B'?attempts:[...evidence.values()].flatMap(e=>e.attempts)),retainedVersions:[...evidence.keys()],scope:mode==='B'?'complete cumulative session':'four recent endpoints; older traces expired',cacheEntries:cache.size,heap:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null};break;
 case 'testEvidence':if(!test)throw Error('Test-only command disabled');if(reference){const r=await reference({protocol:1,workerId:'control',backendId:BACKEND,sessionId:'control',requestId:String(++referenceSequence),sequence:referenceSequence,type:'diagnostics',args:{}});assert(same(counts,r.result.counts),'STOP original property count mismatch');}result={c1Proof:c1?.proof()??null,verifiedEndpoints,counts:{...counts},observerCount:attempts.length,retainedVersions:[...evidence.keys()]};break;
 case 'stop':if(!state)throw Error('Model unavailable');stopped=true;status='stopped';result={schedulingStop:true,physicalStop:structuredClone(state.stop),compact:view()};break;
 case 'dispose':lastClock=state?.seconds??lastClock;lastVersion=state?.acceptedSteps??lastVersion;model=null;state=null;record=null;attempts=[];counts={};reference=null;c1=null;verifiedEndpoints=[];evidence.clear();status='disposed';cache.clear();result={referencesDropped:true,nativeDestructorApplicable:false,retainedEvidence:0,priorCacheCleared:true};break;
 default:throw Error('Unsupported command');
 }
 response={...envelope(q),success:true,result,error:null,timing:{serviceMS:performance.now()-start,components}};
 }catch(e){if(status==='initializing'){model=null;state=null;record=null;status='failed';}else if(state&&scientificDispatch){fault=diagnostic(e);record=null;status='record-unavailable';retain();}
 response={...envelope(q),success:false,result:null,error:diagnostic(e),fault:structuredClone(fault),displayStale:!!state,timing:{serviceMS:performance.now()-start,components}};}
 if(q.args?.scientificHash&&state&&record&&response.success){const t=performance.now();await verifyHash({record,state},q.args.scientificHash);response.verificationMS=performance.now()-t;response.scientificHashVerifiedInsideOwner=true;}
 const t=performance.now();cache.set(q.requestId,{q:structuredClone(q),response:structuredClone(response)});response.timing.cacheCopyMS=performance.now()-t;return response;
 }
 return q=>{const r=chain.then(()=>execute(q));chain=r.catch(()=>{});return r;};
}
