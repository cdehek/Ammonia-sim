import {open,setup,replay,parityRun,failures,propertyBench,schedules} from './science.mjs';
import {diagnostic,assert} from './assets/values.mjs';
import {project} from './assets/snapshot.mjs';
const session=new URL(location.href).searchParams.get('session');
const hashes={control:'f1f028e5454b8090b61c06a8afebcaaac332b3c70f3cd8ac1d4fbc0b2c0bf919',candidate:'afab073693d6d4eb3e734f84a847805ff9866dada75114add92ca6f911f483c7'};
let seq=0,status='new',owned=null,live=null,last=null,version=0,history=[],responseCount=0,chain=Promise.resolve();
const epoch=()=>performance.timeOrigin+performance.now();
async function execute(q){
 const receivedEpochMS=epoch(),start=performance.now(),timing={};let snapshot=null,result=null,error=null,success=true;
 try{
  if(!q||q.protocol!==1||q.session!==session||!Number.isSafeInteger(q.sequence)||q.sequence!==seq+1||typeof q.id!=='string')throw Error('Invalid session/sequence/envelope');
  seq=q.sequence;
  if(status==='disposed')throw Error('Disposed session');
  if(++responseCount>128&&q.type!=='dispose')throw Error('Session command cap');
  switch(q.type){
   case 'init':{
    assert(status==='new','already initialized');const {variant,fixture='cold',warmups=0,test}=q.args??{};
    assert(hashes[variant]&&['cold','warm','domain','partial','numerical'].includes(fixture)&&Number.isSafeInteger(warmups)&&warmups>=0&&warmups<=3,'initialization arguments');
    assert(['cold','warm'].includes(fixture)||test===true,'test fixture');status='initializing';
    const t=performance.now(),url=new URL('./assets/'+variant+'-bundle.mjs',import.meta.url),response=await fetch(url);assert(response.ok,'asset load');const bytes=await response.arrayBuffer();
    const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(v=>v.toString(16).padStart(2,'0')).join('');assert(digest===hashes[variant],'frozen scientific source mismatch');timing.assetVerificationMS=performance.now()-t;
    owned={...await open(variant),variant,fixture};timing.importMS=owned.importMS;timing.tableMS=owned.tableMS;
    const w=performance.now();for(let i=0;i<warmups;i++)replay(owned.load,owned.engine,fixture);timing.untimedWarmupMS=performance.now()-w;
    const i=performance.now();let config,extra={};if(['domain','partial'].includes(fixture))config={sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:200,finProfileK:200,airInitialK:200,airLoadKW:0},...(fixture==='partial'?{schedule:[{seconds:.0001,patch:{airLoadKW:-1}}]}:{})};
    if(fixture==='numerical')extra={maxIterations:1,maxAttempts:20};
    live=setup(owned.load,owned.engine,['cold','warm'].includes(fixture)?fixture:'cold',config,extra);if(fixture==='domain')live.model.update(live.state,{airLoadKW:-1});
    live.record=live.model.record(live.state);timing.initializeMS=performance.now()-i;status='ready';break;
   }
   case 'advance':{
    assert(live,'not initialized');assert(!live.state.stop,'original stopped state retained; restart required');
    const targets=q.args?.targets;assert(Array.isArray(targets)&&targets.length>0&&targets.length<=12&&targets.every((t,i)=>Number.isFinite(t)&&t> (i?targets[i-1]:live.state.seconds)&&t<=.01),'bounded targets');
    const t=performance.now(),intervals=[];for(const target of targets){const a=performance.now();live.record=live.model.advance(live.state,target-live.state.seconds);intervals.push({target,wallMS:performance.now()-a,acceptedClock:live.state.seconds});if(live.state.stop)break;}
    timing.computeMS=performance.now()-t;timing.intervals=intervals;version++;status=live.state.stop?'scientific-refusal':'accepted';
    if(live.state.stop){success=false;error=structuredClone(live.state.stop);}break;
   }
   case 'detail':assert(live,'not initialized');result={state:structuredClone(live.state),record:structuredClone(live.record),attempts:structuredClone(live.attempts)};break;
   case 'latest':assert(last&&!live?.state.stop,'no fresh accepted snapshot');snapshot=structuredClone(last);break;
   case 'stats':result={attempts:live?.attempts.length??0,history:history.length,commands:responseCount,modelPresent:!!live,tablePresent:!!owned,serializedSnapshotJSONBytes:last?new TextEncoder().encode(JSON.stringify(last)).length:0};break;
   case 'echo':result=q.args?.payload;break;
   case 'ping':result={pong:true};break;
   case 'parity':assert(!owned,'parity requires isolated worker');result=await parityRun(q.args.variant,q.args.fixture,q.args.schedule,q.args.observed);break;
   case 'failures':assert(!owned,'failure replay requires isolated worker');result=await failures(q.args.variant);break;
   case 'micro':assert(owned,'not initialized');{const t=performance.now();result=propertyBench(owned.engine);timing.computeMS=performance.now()-t;}break;
   case 'dispose':result={releasedAttempts:live?.attempts.length??0,releasedSnapshots:history.length,priorClock:live?.state.seconds??null};live=null;owned=null;last=null;history=[];status='disposed';break;
   default:throw Error('Unknown command');
  }
  if(['init','advance'].includes(q.type)&&live&&success){const t=performance.now();snapshot=project(live.record,live.state,session,version);snapshot.source={b15:'eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35',variant:owned.variant,sha256:hashes[owned.variant]};snapshot.qualification='NONPRODUCTION / EXPERIMENTAL; >0.001 s UNQUALIFIED RESEARCH; max 0.01 s';timing.projectionMS=performance.now()-t;last=snapshot;history.push(snapshot);history=history.slice(-8);}
 }catch(e){success=false;error=diagnostic(e);if(status==='initializing')status='initialization-failed';}
 return {protocol:1,session,id:q?.id,sequence:q?.sequence,type:q?.type,success,status,clock:live?.state.seconds??null,version,snapshot,result,error,stale:!success&&!!last,timing:{...timing,serviceMS:performance.now()-start},receivedEpochMS};
}
self.onmessage=e=>{chain=chain.then(async()=>{const r=await execute(e.data);r.sentEpochMS=epoch();const t=performance.now();self.postMessage(r);const postMS=performance.now()-t;self.postMessage({kind:'post-cost',id:r.id,postMS});}).catch(e=>self.postMessage({kind:'worker-error',error:diagnostic(e)}));};
self.postMessage({kind:'ready',session,epochMS:epoch()});
