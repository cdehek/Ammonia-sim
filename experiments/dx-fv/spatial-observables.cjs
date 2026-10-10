'use strict';
const H=require('./hydraulics.cjs');
// Overlap bins are a common accounting grid, never thermodynamic cells.
// The historical default is 15; the approved 3/5/9 comparison uses 45.
// Preserve each cell's stored M/U.
function profile(record,binCount=15){
 if(!Number.isInteger(binCount)||binCount<1)throw Error('Positive diagnostic bin count required.');
 const n=record.sectionCount,bins=[];
 for(let b=0;b<binCount;b++){
  const left=b/binCount,right=(b+1)/binCount,row={left,right,massKg:0,energyKJ:0,liquidMassKg:0,liquidVolumeM3:0};
  record.sections.forEach((v,i)=>{const overlap=Math.max(0,Math.min(right,(i+1)/n)-Math.max(left,i/n)),fraction=overlap*n;if(fraction===0)return;
   const liquid=v.x===null?(v.phase.includes('liquid')?1:0):1-v.x;
   row.massKg+=fraction*v.massKg;row.energyKJ+=fraction*v.internalEnergyKJ;row.liquidMassKg+=fraction*v.massKg*liquid;row.liquidVolumeM3+=fraction*v.volumeM3*v.liquidVolumeFraction;
  });bins.push(row);
 }
 return bins;
}
function observe(record,spec,engine,binCount=15){
 const states=record.sections,n=states.length,nodes=[engine.ph(spec.inlet.p,spec.inlet.h),...states,engine.ph(spec.outlet.p,spec.outlet.h)];
 const faces=spec.connections.map((c,i)=>{const left=nodes[i],right=nodes[i+1],flow=c.closed?0:H.connectionFlow(left,right,c),donor=flow>=0?left:right;
  return {massKgS:flow,pressureDropBar:left.p-right.p,pipePressureDropBar:c.closed?null:H.pressureDropPa(flow,donor,{...c,minorK:0})/1e5};
 });
 const bins=profile(record,binCount),totalLiquidKg=bins.reduce((a,v)=>a+v.liquidMassKg,0),liquidVolumeM3=bins.reduce((a,v)=>a+v.liquidVolumeM3,0);
 return {seconds:record.seconds,sectionCount:n,terminal:record.terminal,reservoirPressureBar:spec.outlet.p,portOutflowKgS:faces.at(-1).massKgS,inletFlowKgS:faces[0].massKgS,totals:record.totals,totalLiquidKg,liquidVolumeM3,pressureDrop:{imposedTotalBar:spec.inlet.p-spec.outlet.p,coreBar:states[0].p-states.at(-1).p,terminalConnectionBar:faces.at(-1).pressureDropBar,pipeBar:faces.reduce((a,v)=>a+(v.pipePressureDropBar??0),0),faces},sections:states.map((v,i)=>({left:i/n,right:(i+1)/n,center:(i+.5)/n,p:v.p,h:v.h,T:v.T,quality:v.x,liquidVolumeFraction:v.liquidVolumeFraction,massKg:v.massKg,internalEnergyKJ:v.internalEnergyKJ})),profile:bins,terminalEvents:record.events.filter(v=>v.section===n-1),allEvents:record.events,massResidualKg:record.massResidualKg,energyResidualKJ:record.energyResidualKJ,sectionResiduals:record.sectionResiduals,steps:record.acceptedSteps,rejected:record.rejectedSteps,iterations:record.attemptedIterations,calls:record.attemptedResidualEvaluations,minStep:record.minAcceptedStepSeconds,maxStep:record.maxAcceptedStepSeconds,stop:record.stop};
}
function delta(a,b){
 const terminal={pressureBar:b.terminal.p-a.terminal.p,temperatureK:b.terminal.T-a.terminal.T,enthalpyKJkg:b.terminal.h-a.terminal.h,superheatK:b.terminal.superheatK-a.terminal.superheatK,wetDisagrees:a.terminal.wet!==b.terminal.wet};
 return {terminal,totalMassKg:b.totals.massKg-a.totals.massKg,totalEnergyKJ:b.totals.internalEnergyKJ-a.totals.internalEnergyKJ,totalLiquidKg:b.totalLiquidKg-a.totalLiquidKg,liquidVolumeM3:b.liquidVolumeM3-a.liquidVolumeM3,outflowKgS:b.portOutflowKgS-a.portOutflowKgS,corePressureDropBar:b.pressureDrop.coreBar-a.pressureDrop.coreBar,pipePressureDropBar:b.pressureDrop.pipeBar-a.pressureDrop.pipeBar,profileMassL1Kg:a.profile.reduce((sum,v,i)=>sum+Math.abs(v.massKg-b.profile[i].massKg),0),profileEnergyL1KJ:a.profile.reduce((sum,v,i)=>sum+Math.abs(v.energyKJ-b.profile[i].energyKJ),0)};
}
module.exports={observe,profile,delta};
