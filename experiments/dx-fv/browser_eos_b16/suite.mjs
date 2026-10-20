import {Client} from './client.mjs';
import {same,assert} from './assets/values.mjs';
import {schedules} from './science.mjs';
import {hash} from './hash.mjs';
const orders=['AB','BA','BA','AB','AB','BA'];
const clone=x=>structuredClone(x);
async function isolated(type,args){const c=new Client();try{const r=await c.request(type,args);assert(r.success,JSON.stringify(r.error));return r.result;}finally{await c.dispose().catch(()=>c.lose());}}
export async function scientificSuite(progress=()=>{},onCase=()=>{}){
 const cases=[];
 for(const fixture of ['cold','warm'])for(const schedule of ['original','added','fine']){
  const runs={};for(const observed of [false,true])for(const variant of ['control','candidate']){progress(`science ${fixture} ${schedule} ${observed?'observed':'plain'} ${variant}`);runs[(observed?'observed-':'')+variant]=await isolated('parity',{variant,fixture,schedule,observed});}
  const ref=runs.control;for(const [name,r]of Object.entries(runs)){for(const key of ['checkpoints','attempts','events','finalClock','accepted','rejected','audits'])assert(same(ref[key],r[key]),`science ${fixture} ${schedule} ${name} ${key}`);}
  assert(same(runs['observed-control'].diagnostics.streams,runs['observed-candidate'].diagnostics.streams),'diagnostic full stream mismatch');
  const receipt={fixture,schedule,passed:true,runs};cases.push(receipt);await onCase(receipt);
 }
 const failures={};for(const variant of ['control','candidate'])failures[variant]=await isolated('failures',{variant});assert(same(failures.control,failures.candidate),'failure/public interface parity');
 const protocol=[];for(const variant of ['control','candidate']){
  for(const fixture of ['domain','partial','numerical']){const c=new Client();try{
   const init=await c.request('init',{variant,fixture,test:true});assert(init.success,'init test');
   const r=await c.request('advance',{targets:[.0002]});assert(!r.success&&r.status==='scientific-refusal'&&r.stale,'worker original refusal');
   assert(r.error.kind===(fixture==='numerical'?'solver':'domain'),'original refusal kind');if(fixture!=='numerical')assert(r.clock===(fixture==='partial'?.0001:0),'original partial accepted clock');else assert(r.clock>=0&&r.clock<.0002,'original numerical partial clock');
   const detail=await c.request('detail'),repeat=await c.request('advance',{targets:[.0003]}),again=await c.request('detail');assert(!repeat.success&&same(detail.result,again.result),'stopped worker state retained');
   assert(!c.receive(init),'stale display rejected');assert(!c.receive({...init,session:'other-session',sequence:999}),'session isolation');
   const latest=await c.request('latest');assert(!latest.success&&!latest.snapshot,'no fresh readings after refusal');
   const unknown=await c.request('not-a-command');assert(!unknown.success,'malformed command');
   const disposed=await c.dispose();assert(disposed.status==='disposed','dispose status');
   protocol.push({variant,fixture,kind:r.error.kind,clock:r.clock,detail:detail.result,repeatRejected:true,latestRejected:true,unknownRejected:true,staleDisplayRejected:true,otherSessionRejected:true,disposed:true});
  }finally{if(!c.closed)c.lose();}}
  const c=new Client();await c.request('init',{variant,fixture:'warm'});const pending=c.request('advance',{targets:schedules.original});const t=performance.now();setTimeout(()=>c.lose(),25);let message;try{await pending;}catch(e){message=e.message;}assert(c.closed&&c.status==='lost'&&c.stale&&message?.includes('unknown'),'external worker loss distinct');
  const lossAcknowledgementMS=performance.now()-t,restartStart=performance.now(),restarted=new Client();const r=await restarted.request('init',{variant,fixture:'cold'});assert(r.clock===0&&!restarted.stale,'restart isolation');await restarted.dispose();protocol.push({variant,externalLoss:message,lossAcknowledgementMS,restartAndDisposeMS:performance.now()-restartStart,freshRestartClock:r.clock});
  const bad=new Client();const malformed=await bad.request('ping',{}, {protocol:99});assert(!malformed.success,'invalid protocol rejected');bad.lose();protocol.push({variant,malformedEnvelopeRejected:true});
 }
 for(const fixture of ['domain','partial','numerical']){const p=protocol.filter(x=>x.fixture===fixture);assert(same(p[0].detail,p[1].detail),'worker-visible refusal science parity');}
 return {passed:true,runtime:navigator.userAgent,cases,failures,protocol,qualificationSeconds:.001,maximumResearchSeconds:.01};
}
function heartbeat(){
 const delays=[],inputs=[],tools=[],longTasks=[];let previous=performance.now(),scheduledInput=null,scheduledTool=null;const start=previous;
 const button=document.getElementById('input'),tool=document.getElementById('tool');
 const onInput=()=>{if(scheduledInput!==null){inputs.push(performance.now()-scheduledInput);scheduledInput=null;}};
 const onTool=()=>{if(scheduledTool!==null){document.getElementById('tool-state').textContent=document.getElementById('tool-state').textContent==='Overview'?'Diagnostics':'Overview';tools.push(performance.now()-scheduledTool);scheduledTool=null;}};
 button.addEventListener('click',onInput);tool.addEventListener('click',onTool);
 const timer=setInterval(()=>{const now=performance.now();delays.push(Math.max(0,now-previous-10));previous=now;},10);
 const interaction=setInterval(()=>{scheduledInput=performance.now();setTimeout(()=>button.click(),0);scheduledTool=performance.now();setTimeout(()=>tool.click(),0);},25);
 let obs;try{obs=new PerformanceObserver(list=>{for(const e of list.getEntries())longTasks.push({startTime:e.startTime,duration:e.duration});});obs.observe({entryTypes:['longtask']});}catch{}
 return ()=>{clearInterval(timer);clearInterval(interaction);obs?.disconnect();button.removeEventListener('click',onInput);tool.removeEventListener('click',onTool);return {wallMS:performance.now()-start,heartbeatPeriodMS:10,delaysMS:delays,inputAcknowledgementMS:inputs,toolSwitchMS:tools,longTasks,interaction:'timer-scheduled synthetic DOM clicks; no human/device input claim',longTasksObservable:PerformanceObserver.supportedEntryTypes?.includes('longtask')??false};};
}
export async function sample(variant,fixture,warmups=0,schedule='original'){
 const c=new Client();const stop=heartbeat();try{
  await c.ready;const init=await c.request('init',{variant,fixture,warmups});assert(init.success,'benchmark init');
  const advance=await c.request('advance',{targets:schedules[schedule]});assert(advance.success&&advance.clock===.01,'benchmark advancement');
  const responsiveness=stop();
  const stats=await c.request('stats');const ping=[];for(let i=0;i<12;i++)ping.push((await c.request('ping')).metric);
  const echo=[];for(let i=0;i<8;i++)echo.push((await c.request('echo',{payload:init.snapshot})).metric);
  const detail=await c.request('detail');const checksum={fullScientificSHA256:hash(detail.result),clock:detail.result.state.seconds,accepted:detail.result.state.acceptedSteps,rejected:detail.result.state.rejectedSteps,residuals:detail.result.state.attemptedResidualEvaluations,corrections:detail.result.state.attemptedIterations,physical:detail.result.state.cells.reduce((a,v)=>a+v.massKg+v.internalEnergyKJ,0)+detail.result.state.energies.reduce((a,v)=>a+v,0)};
  const disposal=await c.dispose();await new Promise(r=>setTimeout(r,0));
  return {variant,fixture,warmups,schedule,constructMS:c.constructMS,readyMS:c.readyMS,init:init.metric,advance:advance.metric,ping,echo,stats:stats.result,disposalMS:disposal.terminateAndDisposeMS,disposal:disposal.metric,checksum,postCosts:c.postCosts,responsiveness,rendererMemory:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize,jsHeapSizeLimit:performance.memory.jsHeapSizeLimit}:null};
 }catch(e){stop();c.lose();throw e;}
}
export async function performanceSuite(progress=()=>{},onSample=()=>{}){
 const rows=[];
 for(const warmups of [0,2])for(const fixture of ['cold','warm'])for(let pair=1;pair<=6;pair++)for(const letter of orders[pair-1]){
  const variant=letter==='A'?'control':'candidate';progress(`worker ${fixture} warmups=${warmups} pair=${pair} ${variant}`);const row={...await sample(variant,fixture,warmups),pair,order:orders[pair-1],primary:true};rows.push(row);await onSample(row);
 }
 // Supplemental schedule sensitivity; independent pairs with the same bounded physics.
 for(const schedule of ['added','fine'])for(const fixture of ['cold','warm'])for(let pair=1;pair<=2;pair++)for(const letter of orders[pair-1]){
  const variant=letter==='A'?'control':'candidate';progress(`worker supplemental ${fixture} ${schedule} pair=${pair}`);const row={...await sample(variant,fixture,0,schedule),pair,order:orders[pair-1],primary:false};rows.push(row);await onSample(row);
 }
 return {passed:true,runtime:navigator.userAgent,rows};
}
export async function microSuite(progress=()=>{}){
 const rows=[];for(let pair=1;pair<=6;pair++)for(const letter of orders[pair-1]){const variant=letter==='A'?'control':'candidate',c=new Client();try{progress(`worker micro pair=${pair} ${variant}`);await c.request('init',{variant,fixture:'cold'});const r=await c.request('micro');assert(r.success,'micro');rows.push({pair,variant,order:orders[pair-1],result:r.result,metric:r.metric});}finally{await c.dispose().catch(()=>c.lose());}}return {passed:true,rows};
}
export async function retentionSuite(){
 const rows=[];for(const variant of ['control','candidate']){for(let session=0;session<6;session++){
  const c=new Client();await c.request('init',{variant,fixture:session%2?'warm':'cold'});await c.request('advance',{targets:schedules.original});const before=(await c.request('stats')).result;
  for(let i=0;i<48;i++)await c.request('latest');const after=(await c.request('stats')).result;assert(after.history<=8&&after.attempts===before.attempts,'bounded histories');const disposed=await c.dispose();
  rows.push({variant,session,before,after,clientSnapshots:c.history.length,clientMetrics:c.metrics.length,released:disposed.result,rendererMemory:performance.memory?{usedJSHeapSize:performance.memory.usedJSHeapSize,totalJSHeapSize:performance.memory.totalJSHeapSize}:null});
 }}return {passed:true,rows,scope:'12 short reset sessions, no scientific horizon extension; coarse renderer heap includes instrumentation; no hours-long stability claim'};
}
export async function ownerRun(machine,progress=()=>{}){
 const rows=[];for(let pair=1;pair<=6;pair++)for(const fixture of ['cold','warm'])for(const letter of orders[pair-1]){const variant=letter==='A'?'control':'candidate';progress(`Desktop ${fixture} pair ${pair}/6 ${variant}`);rows.push({...await sample(variant,fixture,1),pair,order:orders[pair-1]});}
 return {experimental:true,ownerSuppliedMachine:machine,userAgent:navigator.userAgent,hardwareConcurrency:navigator.hardwareConcurrency,deviceMemoryGiB:navigator.deviceMemory??null,measuredAt:new Date().toISOString(),rows,qualificationSeconds:.001,maximumResearchSeconds:.01};
}
