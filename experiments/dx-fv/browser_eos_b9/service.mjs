import {diagnostic,same} from './values.mjs';
export const BACKEND='accepted-A2-table';
export function service(workerId,sessionId){
 let sequence=0,status='new',model=null,state=null,counts={},attempts=[],stopped=false,lastClock=null,lastVersion=null;
 const cache=new Map();let chain=Promise.resolve();
 const envelope=q=>({protocol:1,workerId,backendId:BACKEND,requestId:q?.requestId??null,sessionId,sequence:q?.sequence??null,type:q?.type??null,clock:state?.seconds??lastClock,acceptedVersion:state?.acceptedSteps??lastVersion,status});
 function snapshot(){const t=performance.now(),record=model.record(state),recordMS=performance.now()-t;return {record,state:structuredClone(state),recordMS};}
 async function execute(q){
 const start=performance.now(),refuse=message=>({...envelope(q),success:false,error:{name:'ProtocolError',message},result:null,timing:{serviceMS:performance.now()-start}});
 if(!q||q.protocol!==1||q.workerId!==workerId||q.backendId!==BACKEND||q.sessionId!==sessionId||typeof q.requestId!=='string'||!q.requestId.length||!Number.isSafeInteger(q.sequence))return refuse('Invalid request envelope');
 if(cache.has(q.requestId)){const old=cache.get(q.requestId);return same(old.q,q)?structuredClone(old.response):refuse('Duplicate ID content mismatch');}
 if(q.sequence!==sequence+1)return refuse('Out-of-order command sequence');
 sequence=q.sequence;
 if(cache.size>=256&&q.type!=='dispose')return refuse('Session response cache exhausted');
 let response;
 try{
 let result;
 if(status==='disposed')throw Error('Disposed model request');
 switch(q.type){
 case 'initialize':{
 if(status!=='new')throw Error('Session already initialized');status='initializing';
 const t=performance.now(),{loader}=await import('./accepted-bundle.mjs'),importMS=performance.now()-t,load=loader();
 const begin=performance.now(),raw=load('engine.js').createEngine(load('properties.json'));
 const engine=new Proxy(raw,{get(o,k){const v=o[k];return typeof v==='function'?(...a)=>{counts[k]=(counts[k]||0)+1;return Reflect.apply(v,o,a);}:v;}});
 const factoryMS=performance.now()-begin;
 if(!['cold','warm'].includes(q.args?.fixture))throw Error('Unsupported original fixture');
 const config=load('coupled-fixtures.cjs').fixture(q.args.fixture),construction=performance.now();
 model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},a=>attempts.push(a));state=model.create(config);
 const constructionMS=performance.now()-construction;status='ready';result={...snapshot(),config,importMS,factoryMS,constructionMS};break;}
 case 'advance':{
 if(!state||stopped)throw Error(stopped?'Session stopped at accepted boundary':'Model unavailable');
 const before={...counts},a0=attempts.length,t=performance.now();
 const record=model.advance(state,q.args?.duration),advanceMS=performance.now()-t;
 result={record,state:structuredClone(state),advanceMS,attempts:structuredClone(attempts.slice(a0)),propertyCalls:Object.fromEntries(Object.entries(counts).map(([k,v])=>[k,v-(before[k]||0)]))};break;}
 case 'snapshot':if(!state)throw Error('Model unavailable');result=snapshot();break;
 case 'diagnostics':if(!state)throw Error('Model unavailable');result={counts:{...counts},attempts:structuredClone(attempts),heap:performance.memory?{used:performance.memory.usedJSHeapSize,total:performance.memory.totalJSHeapSize}:null,wasmMemoryBytes:null};break;
 case 'stop':if(!state)throw Error('Model unavailable');stopped=true;status='stopped';result={schedulingStop:true,physicalStop:structuredClone(state.stop)};break;
 case 'dispose':lastClock=state?.seconds??lastClock;lastVersion=state?.acceptedSteps??lastVersion;model=null;state=null;attempts=[];counts={};status='disposed';cache.clear();result={referencesDropped:true,nativeDestructorApplicable:false};break;
 default:throw Error('Unsupported command');
 }
 response={...envelope(q),success:true,result,error:null,timing:{serviceMS:performance.now()-start}};
 }catch(e){if(status==='initializing'){model=null;state=null;status='failed';}response={...envelope(q),success:false,result:null,error:diagnostic(e),timing:{serviceMS:performance.now()-start}};}
 cache.set(q.requestId,{q:structuredClone(q),response:structuredClone(response)});return response;
 }
 return q=>{const result=chain.then(()=>execute(q));chain=result.catch(()=>{});return result;};
}
