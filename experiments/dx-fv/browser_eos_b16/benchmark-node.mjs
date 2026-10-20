import {performance,PerformanceObserver} from 'node:perf_hooks';
import {open,setup,replay,schedules,propertyBench} from './science.mjs';
import {assert} from './assets/values.mjs';
const [variant,kind,warmupText='0',schedule='original']=process.argv.slice(2),warmups=Number(warmupText);
assert(['control','candidate','count-control','count-candidate'].includes(variant)&&['cold','warm','ph'].includes(kind)&&Number.isSafeInteger(warmups)&&warmups>=0&&warmups<=3&&schedules[schedule],'bounded invocation');
const counts={};globalThis.__b15count=k=>counts[k]=(counts[k]||0)+1;
const gc=[],observer=new PerformanceObserver(list=>{for(const e of list.getEntries())gc.push({startTime:e.startTime,durationMS:e.duration,kind:e.detail.kind});});observer.observe({entryTypes:['gc']});
const scopes={},memoryStart=process.memoryUsage(),owned=await open(variant),{load,engine}=owned;
function measure(name,fn){const t=performance.now(),cpu=process.cpuUsage();const result=fn(),used=process.cpuUsage(cpu);scopes[name]={startMS:t,endMS:performance.now(),wallMS:performance.now()-t,cpuMS:(used.user+used.system)/1000};return result;}
let result;
if(kind==='ph')result=measure('properties',()=>propertyBench(engine));
else{
 measure('untimedWarmup',()=>{for(let i=0;i<warmups;i++)replay(load,engine,kind,schedule);});
 const s=measure('initialize',()=>setup(load,engine,kind)),initialCounts={...counts};
 const intervals=[];let record;
 measure('compute',()=>{for(const target of schedules[schedule]){const t=performance.now();record=s.model.advance(s.state,target-s.state.seconds);intervals.push({target,wallMS:performance.now()-t});assert(!s.state.stop,'unexpected timing refusal');}});
 const advanceCounts=Object.fromEntries(Object.entries(counts).map(([k,v])=>[k,v-(initialCounts[k]||0)]));
 result={clock:s.state.seconds,accepted:s.state.acceptedSteps,rejected:s.state.rejectedSteps,residuals:s.state.attemptedResidualEvaluations,corrections:s.state.attemptedIterations,attempts:s.attempts.length,physical:s.state.cells.reduce((a,v)=>a+v.massKg+v.internalEnergyKJ,0)+s.state.energies.reduce((a,v)=>a+v,0),recordResiduals:[record.massResidualKg,record.combinedEnergyResidualKJ],advanceCounts,intervals};
}
await new Promise(r=>setImmediate(r));observer.disconnect();
console.log('B16_RESULT '+JSON.stringify({variant,kind,warmups,schedule,node:process.version,execArgv:process.execArgv,importMS:owned.importMS,tableMS:owned.tableMS,scopes,result,memoryStart,memoryEnd:process.memoryUsage(),resources:process.resourceUsage(),gc,counts,primaryCounting:variant.startsWith('count-'),scientificHashingInTimedScope:false}));
