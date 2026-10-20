import{readReceipt,evidenceURL}from'./receipts.mjs';
import fs from'node:fs';import zlib from'node:zlib';import{same,assert,auditRecord,exact}from'../browser_eos_b9/values.mjs';import{loader}from'../browser_eos_b9c/candidate-bundle.mjs';
const E=evidenceURL,read=readReceipt,save=(n,d)=>fs.writeFileSync(new URL(n+'.json',E),JSON.stringify(d,null,2)+'\n');
const analysis=JSON.parse(fs.readFileSync(new URL('analysis.json',E))),load=loader(),engine=load('table-only.cjs').createTableEngine(),thermo=load('thermodynamics.cjs').createThermodynamics(engine);
for(const fixture of ['cold','warm']){
 const name=fixture==='cold'?'observed-cold-r1-fixed':'observed-warm-r1',r=read(name),d=r.find(v=>v.type==='diagnostics'),init=read('initialization-'+fixture).find(v=>v.type==='diagnostics'),v=analysis.fixtures[fixture];
 v.advanceCounts=Object.fromEntries(Object.entries(d.counts).map(([k,n])=>[k,n-(init.counts[k]||0)]));
 v.PHPhaseTotals={};for(const[k,row]of Object.entries(d.phaseCalls)){const phase=k.split('|')[1];const t=v.PHPhaseTotals[phase]??={calls:0,branch:0};t.calls+=row.calls;t.branch+=row.branch;}
 for(const[k,row]of Object.entries(init.phaseCalls)){const phase=k.split('|')[1];v.PHPhaseTotals[phase].calls-=row.calls;v.PHPhaseTotals[phase].branch-=row.branch;}
 const attempts=r.find(v=>v.type==='attempts').attempts,events=attempts.flatMap(v=>v.events);v.newton={converged:events.filter(v=>v.type==='iteration'&&v.status==='converged').length,failed:events.filter(v=>v.type==='solve-failed').length,lineSearches:events.filter(v=>v.type==='line-search').length,allUnitLineSearch:events.filter(v=>v.type==='line-search').every(v=>v.factor===1&&v.outcome==='accepted'),derivatives:events.filter(v=>v.type==='derivative').length,allFirstPositiveDerivative:events.filter(v=>v.type==='derivative').every(v=>v.step>0&&v.shrink===0&&v.outcome==='used')};
 const temporal=JSON.parse(fs.readFileSync(new URL('temporal-'+fixture+'.json',E))),controller=[];
 for(let i=0;i<temporal.length-1;i++){
  const t=temporal[i],n=temporal[i+1];if(t.accepted)continue;assert(t.rejectionReason==='accuracy');assert(same(t.proposal,n.trialSeconds),'rejected controller proposal exact');controller.push({trialIndex:t.trialIndex,proposal:t.proposal,nextActualTrialSeconds:n.trialSeconds,bitExact:true});
 }
 save('controller-'+fixture,{passed:true,rejectedProposals:controller,acceptedControllerObservations:d.controllers});
 const perTrial=d.phTrials||{};v.PHObserverIndexBins={};for(const[key,p]of Object.entries(perTrial)){
  const index=Number(key.split('|')[0]),t=temporal[index],bin=!t?'record-or-initial':t.startSeconds<.001?'startup':t.endSeconds<.00535?'pre-transition':t.startSeconds<.00543?'transition':'post-transition',out=v.PHObserverIndexBins[bin]??={calls:0,branch:0,ms:0};for(const k of ['calls','branch','ms'])out[k]+=p[k];
 }
 for(const col of v.columnTotals){col.supportedPHCalls=col.counts['property.ph']||0;col.failedPHCalls=col.counts['property.failed']||0;col.staticSelectedArrayConstructionsLowerBound=col.evaluations*6;col.heapBytesAndGCAttribution=null;}
 save('columns-'+fixture,v.columnTotals);
 v.staticResidualConstructionLowerBound={residualEvaluations:v.calls.residual,selectedArraySites:['states map','cells map','energies map','fluid residual flatMap','thermal residual map','final residual concat'],atLeastArraysPerResidual:6,atLeastArrays:v.calls.residual*6,atLeastNodeMaps:v.calls.residual,note:'Source construction counts only; excludes many nested blend/evaluate arrays and objects. JIT allocation elimination/bytes/GC time unmeasured.'};
}
for(const boundary of analysis.boundaries){
 const r=read('observed-warm-'+boundary.schedule),d=r.find(v=>v.type==='diagnostics'),initial=r.find(v=>v.type==='checkpoint').science.state,model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'});
 let max=0;
 for(const c of d.commits){const rec=model.record({...structuredClone(initial),cells:c.cells,energies:c.energies,ledger:c.ledger,seconds:c.seconds,lastResidual:c.error});auditRecord(rec);max=Math.max(max,Math.abs(rec.combinedEnergyResidualKJ));}
 boundary.conservation={allAcceptedHalfStatesAudited:d.commits.length,passed:true,maxCombinedEnergyResidualKJ:max};
}
const budget=read('external-budget-witness'),canonical=read('canonical-warm-r1'),comparisons=[];
for(const p of budget.filter(v=>v.type==='partial-progress')){
 const c=canonical.find(v=>v.type==='partial-progress'&&same(v.seconds,p.seconds));assert(c&&same(c,p),'external budget accepted snapshot');comparisons.push({seconds:p.seconds,bitExact:true});
}
assert(comparisons.length>0);const last=comparisons.at(-1);save('external-budget-validation',{passed:true,kind:'external-wall-budget',notNumericalOrDomainRefusal:true,lastIndependentlyProvenAcceptedSeconds:last.seconds,partialSnapshots:comparisons,noRetry:true});
const accepted=JSON.parse(fs.readFileSync(new URL('accepted-warm.json',E))),late=accepted.filter(v=>v.seconds>=.005&&v.seconds<=.0055),flows=late.map(v=>({seconds:v.seconds,hMinusHgKJkg:v.sections[0].derived.hMinusHgKJkg,pressure0:v.sections[0].PHCoordinates.p,pressure1:v.sections[1].PHCoordinates.p,pressureDifferenceBar:v.sections[0].PHCoordinates.p-v.sections[1].PHCoordinates.p,face1:v.endpoint.faces[1],massChangeSection0Kg:v.changes.massKg[0],energyChangeSection0KJ:v.changes.internalEnergyKJ[0],tubeHeatKW:v.endpoint.tubeRefrigerant[0],phase0:v.sections[0].derived.phase,phase1:v.sections[1].derived.phase}));
const reversal=[];for(let i=1;i<flows.length;i++)if(flows[i-1].face1.massKgS*flows[i].face1.massKgS<0)reversal.push([flows[i-1].seconds,flows[i].seconds]);save('hydraulic-transition',{acceptedStates:flows,flowReversalAcceptedBrackets:reversal,faceIndex:1,donorRule:'m>=0 uses section 0 h; m<0 uses section 1 h',notRootSolved:true});
// Verify zero-superheat table continuation exactly; do not create a new state.
const p=late[0].sections[0].derived.pBarAbsolute,sat=engine.sat(p),pt=engine.statePT(p,sat.T);save('saturation-continuity',{p,sat,vaporBranchZeroPT:pt,hEqual:Object.is(sat.hg,pt.h),rhoEqual:Object.is(sat.rhog,pt.rho),notAcceptedSolverState:true,bisectionWidthK:250/2**38});
save('analysis',analysis);console.log(JSON.stringify({advancePH:Object.fromEntries(Object.entries(analysis.fixtures).map(([f,v])=>[f,{PH:v.advanceCounts['property.ph'],branch:v.advanceCounts['lexical.branch'],phase:v.PHPhaseTotals,newton:v.newton}])),boundary:analysis.boundaries.map(v=>({schedule:v.schedule,audit:v.conservation})),flowReversal:reversal},null,2));
