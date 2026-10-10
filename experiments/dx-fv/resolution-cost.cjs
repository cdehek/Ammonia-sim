'use strict';
// Fresh child per sample: Linux maxRSS is a process high-water mark, not retained
// model memory or an iPad estimate. Forced GC is used only for heap accounting.
const fs=require('node:fs'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
if(process.argv[2]==='--sample'){
 const n=Number(process.argv[3]);if(![3,5,9].includes(n))throw Error('Unapproved cost mesh.');
 const engine=require('../../engine').createEngine(require('../../properties.json')),{createEvaporator}=require('./evaporator.cjs'),{fixture,numericalOptions}=require('./spatial-fixtures.cjs');
 const model=createEvaporator(engine,numericalOptions(1e-6));model.advance(model.create(fixture(n)),.1);global.gc?.();const baseline=process.memoryUsage(),baselineRSS=process.resourceUsage().maxRSS,baselineCPU=process.cpuUsage();
 const state=model.create(fixture(n)),started=performance.now();let longest=0,maxSampleHeap=baseline.heapUsed;
 for(let i=0;i<50;i++){const t=performance.now();model.advance(state,.1);longest=Math.max(longest,performance.now()-t);maxSampleHeap=Math.max(maxSampleHeap,process.memoryUsage().heapUsed);}
 const elapsedMS=performance.now()-started,usage=process.resourceUsage(),cpu=process.cpuUsage(baselineCPU),record=model.record(state),stateBytes=Buffer.byteLength(JSON.stringify(state));assert(!record.stop);assert(Math.abs(record.massResidualKg)<1e-8);assert(Math.abs(record.energyResidualKJ)<1e-6);global.gc?.();const after=process.memoryUsage();
 console.log(JSON.stringify({sectionCount:n,elapsedMS,longestCallMS:longest,cpuMS:(cpu.user+cpu.system)/1000,baselineHeapBytes:baseline.heapUsed,retainedHeapBytes:after.heapUsed,retainedHeapDeltaBytes:after.heapUsed-baseline.heapUsed,maxSampleHeapBytes:maxSampleHeap,baselineMaxRSSKiB:baselineRSS,peakRSSKiB:usage.maxRSS,stateSerializedBytes:stateBytes,calls:record.attemptedResidualEvaluations,iterations:record.attemptedIterations,steps:record.acceptedSteps,rejected:record.rejectedSteps,massResidualKg:record.massResidualKg,energyResidualKJ:record.energyResidualKJ}));
}else{
 const report={runtime:process.version,platform:process.platform,scenario:'5 simulated seconds cold startup in 0.1 s calls; fresh process per repeat',memoryMeaning:'maxRSS includes property table, module/JIT overhead and temporary allocations; heap peaks are sampled between calls; serialized bytes describe persistent state, not JS object heap.',samples:[],summary:[]};
 for(let repeat=0;repeat<3;repeat++)for(const n of repeat%2?[9,5,3]:[3,5,9]){const child=spawnSync(process.execPath,['--expose-gc',__filename,'--sample',String(n)],{encoding:'utf8',maxBuffer:1024*1024});if(child.status!==0||!child.stdout.trim())throw Error(JSON.stringify({status:child.status,signal:child.signal,error:child.error?.message,stderr:child.stderr}));report.samples.push({repeat,...JSON.parse(child.stdout)});}
 const median=a=>[...a].sort((a,b)=>a-b)[1];for(const n of [3,5,9]){const rows=report.samples.filter(v=>v.sectionCount===n);report.summary.push({sectionCount:n,medianElapsedMS:median(rows.map(v=>v.elapsedMS)),medianCPUMS:median(rows.map(v=>v.cpuMS)),medianPeakRSSMiB:median(rows.map(v=>v.peakRSSKiB))/1024,medianRetainedHeapMiB:median(rows.map(v=>v.retainedHeapBytes))/1024**2,medianStateSerializedBytes:median(rows.map(v=>v.stateSerializedBytes)),maximumCallMS:Math.max(...rows.map(v=>v.longestCallMS))});}
 report.passed=true;if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
}
