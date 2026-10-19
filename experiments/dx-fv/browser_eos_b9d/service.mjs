import {BACKEND,SOURCE,INTERVALS,project} from './snapshot.mjs';
import {same,diagnostic} from '../browser_eos_b9/values.mjs';
const bundleURL=new URL('../browser_eos_b9c/candidate-bundle.mjs',import.meta.url);
const sha=async bytes=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');
const physical=s=>({cells:s.cells,energies:s.energies,ledger:s.ledger,seconds:s.seconds,events:s.events,boundaryEvents:s.boundaryEvents,spec:s.spec,scheduleIndex:s.scheduleIndex,acceptedSteps:s.acceptedSteps});
export function service(sessionId,{test=false}={}){
 let sequence=0,status='new',model=null,state=null,record=null,lastSnapshot=null,fault=null,version=null,step=0,stopped=false,attempts=[],proof=null,lastClock=null,trackedSteps=0;
 const synchronize=()=>{if(state){if(state.acceptedSteps!==trackedSteps)version++;trackedSteps=state.acceptedSteps;lastClock=state.seconds;}};
 const responses=new Map();let chain=Promise.resolve();
 const envelope=q=>({protocol:1,backendId:BACKEND,sessionId,requestId:q?.requestId??null,sequence:q?.sequence??null,type:q?.type??null,status,clockSeconds:state?.seconds??lastClock,acceptedVersion:version,fault:structuredClone(fault)});
 const refuse=(q,message)=>({...envelope(q),success:false,snapshot:null,error:{name:'ProtocolError',message},stale:!!lastSnapshot});
 async function execute(q){
  const started=performance.now(),timing={};
  if(!q||q.protocol!==1||q.backendId!==BACKEND||q.sessionId!==sessionId||typeof q.requestId!=='string'||!q.requestId||!Number.isSafeInteger(q.sequence))return refuse(q,'Invalid envelope/backend/session');
  if(responses.has(q.requestId)){const prior=responses.get(q.requestId);return same(prior.q,q)?structuredClone(prior.r):refuse(q,'Duplicate ID content mismatch');}
  if(q.sequence!==sequence+1)return refuse(q,'Out-of-order sequence');sequence=q.sequence;
  if(responses.size>=256&&q.type!=='dispose')return refuse(q,'Session response cache exhausted');
  let r,scientific=false;
  try{
   if(status==='disposed')throw Error('Disposed session');
   if(q.args?.expectedVersion!==undefined&&q.args.expectedVersion!==version)throw Error('Stale expected accepted-state version');
   let snapshot=null,result=null;
   switch(q.type){
   case 'initialize':{
    if(status!=='new')throw Error('Already initialized');status='initializing';
    const fixture=q.args?.fixture;if(!['cold','warm',...(test?['numerical','thermal200','thermal400']:[])].includes(fixture))throw Error('Unsupported named original fixture');
    let t=performance.now();const response=await fetch(bundleURL);if(!response.ok)throw Error('Scientific bundle unavailable: '+response.status);
    if(await sha(await response.arrayBuffer())!==SOURCE.bundleSHA256)throw Error('Unqualified scientific bundle identity');timing.assetVerificationMS=performance.now()-t;
    t=performance.now();const {loader}=await import(bundleURL.href),load=loader(),engine=load('table-only.cjs').createTableEngine();timing.importAndOwnedTableMS=performance.now()-t;
    t=performance.now();model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware',...(fixture==='numerical'?{maxIterations:1,maxAttempts:20}:{})},a=>attempts.push(a));
    let config=['cold','warm'].includes(fixture)?load('coupled-fixtures.cjs').fixture(fixture):{};
    if(fixture.startsWith('thermal')){const k=Number(fixture.slice(7));config={sealed:true,refrigerantConductanceKWK:0,thermal:{tubeProfileK:k,finProfileK:k,airInitialK:k,airLoadKW:0}};}
    state=model.create(config);record=model.record(state);
    if(fixture.startsWith('thermal'))record=model.update(state,{airLoadKW:fixture==='thermal200'?-1:1});
    timing.createAndRecordMS=performance.now()-t;version=0;lastClock=state.seconds;status='ready';snapshot=project(record,state,sessionId,version);lastSnapshot=snapshot;break;
   }
   case 'advance':{
    if(!state||stopped||fault)throw Error(fault?'Original fault retained; restart required':stopped?'Scheduling stopped; restart required':'Not initialized');
    if(step>=INTERVALS.length)throw Error('Bounded .001 s research horizon complete');
    if(Object.keys(q.args||{}).some(k=>k!=='expectedVersion'))throw Error('No arbitrary physics input edits');
    const before=test?structuredClone(physical(state)):null,refs=test?{cells:state.cells,energies:state.energies,ledger:state.ledger}:null,oldSteps=state.acceptedSteps;
    scientific=true;let t=performance.now();record=model.advance(state,INTERVALS[step++]);timing.advanceMS=performance.now()-t;
    synchronize();
    fault=structuredClone(state.stop);
    if(fault){
     status=fault.kind==='domain'&&fault.evidence?.confirmed===true?'modeled-domain-stop':'numerical-refusal';
     if(test)proof={wholeAdvancePhysicalUnchanged:same(before,physical(state)),wholeAdvanceIdentityUnchanged:state.cells===refs.cells&&state.energies===refs.energies&&state.ledger===refs.ledger,acceptedStepsBefore:oldSteps,acceptedStepsAfter:state.acceptedSteps,scope:'Whole requested interval; prior accepted substeps are retained. Per-rejection rollback is separately verified by original C1 tests.'};
     r={...envelope(q),success:false,snapshot:null,error:structuredClone(fault),stale:!!lastSnapshot};break;
    }
    t=performance.now();snapshot=project(record,state,sessionId,version);timing.projectionMS=performance.now()-t;lastSnapshot=snapshot;status='accepted-state';break;
   }
   case 'latest':if(!lastSnapshot||fault)throw Error(fault?'Only stale previously accepted readings available':'No accepted record');snapshot=structuredClone(lastSnapshot);break;
   case 'diagnostics':
    if(!state)throw Error('No scientific state');
    result={clockSeconds:state.seconds,acceptedSteps:state.acceptedSteps,rejectedSteps:state.rejectedSteps,accuracyRejectedSteps:state.accuracyRejectedSteps,attemptedResidualEvaluations:state.attemptedResidualEvaluations,attemptedIterations:state.attemptedIterations,attemptCount:attempts.length,stop:structuredClone(state.stop),proof,source:{...SOURCE},scope:'Original current accepted state; original diagnostic generation; no equipment interpretation'};break;
   case 'testDetail':if(!test||!state)throw Error('Test detail unavailable');result={record:structuredClone(record),state:structuredClone(state),attempts:structuredClone(attempts),proof};break;
   case 'stop':stopped=true;if(!fault)status='scheduling-stopped';result={stoppedAtSynchronousBoundary:true};break;
   case 'dispose':
    result={ownerReferencesDropped:true,lastAcceptedClockSeconds:state?.seconds??null,attemptsReleased:attempts.length};model=null;state=null;record=null;lastSnapshot=null;attempts=[];proof=null;responses.clear();status='disposed';break;
   default:throw Error('Unsupported command');
   }
   r??={...envelope(q),success:true,snapshot,result,error:null,stale:false};
  }catch(e){
   if(status==='initializing'){status='unqualified-backend';model=null;state=null;record=null;fault=diagnostic(e);}
   else if(scientific){synchronize();status='numerical-refusal';fault=diagnostic(e);record=null;}
   r={...envelope(q),success:false,snapshot:null,error:diagnostic(e),stale:!!lastSnapshot};
  }
  r.timing={...timing,serviceMS:performance.now()-started};responses.set(q.requestId,{q:structuredClone(q),r:structuredClone(r)});return r;
 }
 return q=>{const work=chain.then(()=>execute(q));chain=work.catch(()=>{});return work;};
}
