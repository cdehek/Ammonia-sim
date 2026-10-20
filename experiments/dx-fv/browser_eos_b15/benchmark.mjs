// Primary timing: original trace mode, no scientific hashing or lexical hooks.
import{performance,PerformanceObserver}from'node:perf_hooks';
const[variant,kind]=process.argv.slice(2);if(!['control','candidate','count-control','count-candidate'].includes(variant)||!['ph','cold','warm','notimer-cold','notimer-warm'].includes(kind))throw Error('invalid benchmark');
const counts={};globalThis.__b15count=k=>counts[k]=(counts[k]||0)+1;
const gc=[];const observer=new PerformanceObserver(list=>{for(const e of list.getEntries())gc.push({kind:e.detail.kind,durationMS:e.duration});});observer.observe({entryTypes:['gc']});
const moduleStart=performance.now(),{loader}=await import('./'+variant+'-bundle.mjs'),load=loader(),moduleLoadMS=performance.now()-moduleStart;
let start=performance.now();const engine=load('table-only.cjs').createTableEngine();const engineConstructionMS=performance.now()-start;
const scopes={},memoryBefore=process.memoryUsage(),noTimer=kind.startsWith('notimer-');
function measure(name,fn){const cpu=process.cpuUsage(),t=performance.now();const value=fn();const d=process.cpuUsage(cpu);scopes[name]={wallMS:performance.now()-t,cpuMS:(d.user+d.system)/1000};return value;}
let result;
if(kind==='ph'){
 const vapor=[],mixed=[];for(const p of [3.5,3.65,4,6,12]){const a=engine.sat(p);for(const dh of [.00001,.1,5,50,150])vapor.push([p,a.hg+dh]);mixed.push([p,(a.hf+a.hg)/2],[p,a.hg+50]);}
 const loop=(inputs,n)=>{let checksum=0;for(let i=0;i<n;i++){const[p,h]=inputs[i%inputs.length];checksum+=engine.ph(p,h).rho;}return checksum;};
 loop(vapor,3000);loop(mixed,3000);result={vaporCalls:20000,mixedCalls:20000,vaporChecksum:measure('vapor',()=>loop(vapor,20000)),mixedChecksum:measure('mixed',()=>loop(mixed,20000)),warmupCalls:6000};
}else{
 const fixture=kind.replace('notimer-',''),schedule=[.0001,.0005,.001,.002,.005,.01];let attempts=0;
 start=performance.now();const model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},()=>attempts++),state=model.create(load('coupled-fixtures.cjs').fixture(fixture));const initializationMS=performance.now()-start;
 const go=()=>{let record;for(const target of schedule){record=model.advance(state,target-state.seconds);if(state.stop)throw Error('unexpected benchmark refusal');}return record;};
 const record=noTimer?go():measure('advance',go);
 result={initializationMS,seconds:state.seconds,attempts,accepted:state.acceptedSteps,rejected:state.rejectedSteps,residuals:state.attemptedResidualEvaluations,newtonCorrections:state.attemptedIterations,recordResiduals:[record.massResidualKg,record.combinedEnergyResidualKJ],physicalChecksum:state.cells.reduce((s,c)=>s+c.massKg+c.internalEnergyKJ,0)+state.energies.reduce((s,e)=>s+e,0)};
}
await new Promise(r=>setImmediate(r));observer.disconnect();console.log(JSON.stringify({variant,kind,node:process.version,moduleLoadMS,engineConstructionMS,scopes,result,counts,memoryBefore,memoryAfter:process.memoryUsage(),resources:process.resourceUsage(),gc,primaryCounting:variant.startsWith('count-'),scientificHashingInTimedScope:false}));
