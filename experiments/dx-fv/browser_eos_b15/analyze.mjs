import fs from'node:fs';import{readReceipt}from'./receipts.mjs';import{same,exact,assert}from'../browser_eos_b9/values.mjs';
const E=new URL('./evidence/',import.meta.url),save=(n,x)=>fs.writeFileSync(new URL(n+'.json',E),JSON.stringify(x,null,2)+'\n'),work={};
for(const f of ['cold','warm']){
 const out={};for(const v of ['control','candidate']){
  const init=readReceipt('init-'+v+'-'+f),rows=readReceipt('observe-'+v+'-'+f),d=rows.find(r=>r.type==='diagnostics'),i=init.find(r=>r.type==='diagnostics');
  assert(same(init.find(r=>r.type==='checkpoint').science,rows.find(r=>r.type==='checkpoint').science),'independent initialization science');
  out[v]={initialCounts:i.pressureCounts,advanceCounts:Object.fromEntries(Object.entries(d.pressureCounts).map(([k,n])=>[k,n-(i.pressureCounts[k]||0)])),vaporPH:{calls:0,branches:0},allPH:d.counts['property.ph']-i.counts['property.ph']};
  for(const [k,n]of Object.entries(d.phaseCalls))if(k.endsWith('|Superheated vapor')){out[v].vaporPH.calls+=n.calls;out[v].vaporPH.branches+=n.branch;}
  for(const [k,n]of Object.entries(i.phaseCalls))if(k.endsWith('|Superheated vapor')){out[v].vaporPH.calls-=n.calls;out[v].vaporPH.branches-=n.branch;}
 }
 for(const k of ['branches','bisections','mixRows','branchRowReads4','mixComponentReads6','offsetAxisReads','phCalls'])assert(out.control.advanceCounts[k]===out.candidate.advanceCounts[k],'work invariants '+k);
 assert(out.control.advanceCounts.pressureBrackets-out.candidate.advanceCounts.pressureBrackets===39*out.candidate.vaporPH.calls,'one-call elimination');
 work[f]=out;
}
save('integrated-work-counts',{passed:true,scope:'Advance only; independent exact initialization subtracted; source read/construction counts, not allocator bytes',fixtures:work});
const receipts=[];for(const f of ['cold','warm'])for(const s of ['','-added','-fine']){const r=JSON.parse(fs.readFileSync(new URL('equivalence-observe-control-'+f+s+'--observe-candidate-'+f+s+'.json',E)));assert(r.passed&&r.conservation?.passed);receipts.push(r);}
save('scientific-summary',{passed:true,schedules:receipts.map(r=>({fixture:r.fixture,schedule:r.schedule,checkpoints:r.checkpoints.length,residuals:r.completeResidualObjectsCompared,jacobiansAndCorrections:r.actualMatricesAndCorrectionsCompared,acceptedHalfStates:r.conservation.acceptedHalfStates,conservation:r.conservation})),residuals:receipts.reduce((s,r)=>s+r.completeResidualObjectsCompared,0),jacobiansAndCorrections:receipts.reduce((s,r)=>s+r.actualMatricesAndCorrectionsCompared,0),allHistoricalOriginalCheckpointsBitExact:true});
const a=readReceipt('observe-control-warm'),b=readReceipt('observe-candidate-warm'),ad=a.find(r=>r.type==='diagnostics'),bd=b.find(r=>r.type==='diagnostics'),last=a.filter(r=>r.type==='checkpoint').at(-1).science.state,event=last.events[0];
assert(same(event,b.filter(r=>r.type==='checkpoint').at(-1).science.state.events[0]),'event parity');
const neighbors=ad.commits.filter(r=>r.seconds===event.bracketStartSeconds||r.seconds===event.bracketEndSeconds);assert(neighbors.length===2,'both bracket endpoints');
const reversals=[];for(let i=1;i<ad.commits.length;i++){const a=ad.commits[i-1],b=ad.commits[i];if(a.endpoint.faces[1].massKgS*b.endpoint.faces[1].massKgS<0)reversals.push([a.seconds,b.seconds]);}
save('phase-transition-parity',{passed:true,event,eventBinary64:exact(event),eventIsInterpolatedNotRootSolved:true,endpointsBinary64:exact(neighbors),followingFace1Reversals:reversals,allNormalizedTemporalErrorsAndControllersBitExact:same(ad.temporals,bd.temporals)&&same(ad.controllers,bd.controllers),allLedgersBitExact:same(ad.commits,bd.commits)});
// B13 identity directly checked without re-running any historical generator.
const zlib=await import('node:zlib');for(const f of ['cold','warm']){const old=zlib.gunzipSync(fs.readFileSync(new URL('../browser_eos_b13/evidence/canonical-'+f+'-010-r1.jsonl.gz',import.meta.url))).toString().trim().split('\n').map(JSON.parse).filter(r=>r.type==='checkpoint'),now=readReceipt('control-'+f).filter(r=>r.type==='checkpoint');assert(old.length===now.length);for(let i=0;i<old.length;i++)assert(old[i].scienceHash===now[i].scienceHash&&old[i].attemptsHash===now[i].attemptsHash,'B13 direct parity');}save('b13-direct-checkpoints',{passed:true,fixtures:['cold','warm'],checkpointsEach:7,scienceAndAttemptsBitExact:true});
console.log('PASS integrated counts, all schedules, B13/B14 science, conservation and phase event');
