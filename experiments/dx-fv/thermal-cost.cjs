'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
function workload(n){
 const {createIntegrator}=require('./thermal-network.cjs'),{createThermalConfig}=require('./thermal-geometry.cjs');
 const I=createIntegrator();I.advance(I.create(createThermalConfig({sectionCount:n})),5);global.gc?.();
 const baseline=process.memoryUsage(),cpuStart=process.cpuUsage(),s=I.create(createThermalConfig({sectionCount:n}));let longest=0,maxHeap=baseline.heapUsed;
 const started=performance.now();
 for(let i=0;i<50;i++){const t=performance.now();I.advance(s,.1);longest=Math.max(longest,performance.now()-t);maxHeap=Math.max(maxHeap,process.memoryUsage().heapUsed);}
 const elapsedMS=performance.now()-started,r=I.record(s),cpu=process.cpuUsage(cpuStart),bytes=Buffer.byteLength(JSON.stringify(s));
 assert.equal(r.stop,null);assert.ok(Math.abs(r.energyResidualKJ)<1e-6&&r.nodes.every(v=>Math.abs(v.residualKJ)<1e-6));
 global.gc?.();const retained=process.memoryUsage().heapUsed;
 return {sections:n,elapsedMS,longestAdvanceMS:longest,cpuMS:(cpu.user+cpu.system)/1000,peakRSSKiB:process.resourceUsage().maxRSS,baselineHeapBytes:baseline.heapUsed,retainedHeapBytes:retained,retainedHeapDeltaBytes:retained-baseline.heapUsed,maxSampledHeapBytes:maxHeap,serializedStateBytes:bytes,linearSolves:r.attemptedLinearSolves,fluxEvaluations:r.attemptedFluxEvaluations,acceptedSteps:r.acceptedSteps,energyResidualKJ:r.energyResidualKJ};
}
if(process.argv[2]==='--sample')console.log(JSON.stringify(workload(Number(process.argv[3]))));
else{
 const report={runtime:process.version,platform:process.platform,scenario:'Five seconds standalone closed relaxation in 0.1 s calls, trace disabled, warmed modules, fresh process per repetition.',limits:'Process RSS includes runtime/JIT and temporary work. Retained heap and serialized state are different quantities. Host timing is observational, not physical-device performance.',samples:[],summary:[]};
 for(let repeat=0;repeat<3;repeat++)for(const n of repeat%2?[9,5]:[5,9]){
  const child=spawnSync(process.execPath,['--expose-gc',__filename,'--sample',String(n)],{encoding:'utf8'});assert.equal(child.status,0,child.stderr);report.samples.push({repeat,...JSON.parse(child.stdout)});
 }
 const median=a=>a.sort((a,b)=>a-b)[1];
 for(const n of [5,9]){const rows=report.samples.filter(v=>v.sections===n);report.summary.push({sections:n,medianElapsedMS:median(rows.map(v=>v.elapsedMS)),worstAdvanceMS:Math.max(...rows.map(v=>v.longestAdvanceMS)),medianPeakRSSMiB:median(rows.map(v=>v.peakRSSKiB))/1024,medianRetainedHeapMiB:median(rows.map(v=>v.retainedHeapBytes))/1024**2,medianSerializedStateBytes:median(rows.map(v=>v.serializedStateBytes)),linearSolves:rows[0].linearSolves});}
 report.passed=true;if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.summary));
}
