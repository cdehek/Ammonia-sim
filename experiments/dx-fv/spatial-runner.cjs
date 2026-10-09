'use strict';
const {createEvaporator}=require('./evaporator.cjs'),{observe,delta}=require('./spatial-observables.cjs'),{numericalOptions}=require('./spatial-fixtures.cjs');
function run(engine,c,options={}){
 const n=c.config.sectionCount;if(![3,5].includes(n))throw Error('Unapproved comparison mesh.');
 const model=createEvaporator(engine,{...numericalOptions(1e-6),...options}),state=model.create(c.config),rows=[],initial=observe(model.record(state),state.spec,engine),started=performance.now();let change=0;
 const times=[...new Set([0,...c.samples,...c.changes.map(v=>v.seconds)])].sort((a,b)=>a-b);
 for(const target of times){
  if(target>state.seconds)model.advance(state,target-state.seconds);
  if(state.stop)break;
  if(c.samples.includes(target))rows.push(observe(model.record(state),state.spec,engine));
  while(change<c.changes.length&&c.changes[change].seconds===target)model.update(state,c.changes[change++].patch);
 }
 return {initial,rows,final:observe(model.record(state),state.spec,engine),elapsedMS:performance.now()-started};
}
function temporalDifference(a,b){
 const max={pressureBar:0,temperatureK:0,enthalpyKJkg:0,superheatK:0,massKg:0,energyKJ:0,profileMassL1Kg:0,eventSeconds:0,domainSeconds:0};
 if(a.rows.length!==b.rows.length)throw Error('Different completed sample counts during temporal refinement.');
 a.rows.forEach((row,i)=>{const ref=b.rows[i];if(Math.abs(row.seconds-ref.seconds)>1e-9)throw Error('Temporal samples do not align.');const d=delta(row,ref);
  for(const key of ['pressureBar','temperatureK','enthalpyKJkg','superheatK'])max[key]=Math.max(max[key],Math.abs(d.terminal[key]));
  row.sections.forEach((v,k)=>{max.pressureBar=Math.max(max.pressureBar,Math.abs(v.p-ref.sections[k].p));max.enthalpyKJkg=Math.max(max.enthalpyKJkg,Math.abs(v.h-ref.sections[k].h));max.temperatureK=Math.max(max.temperatureK,Math.abs(v.T-ref.sections[k].T));});
  max.massKg=Math.max(max.massKg,Math.abs(d.totalMassKg));max.energyKJ=Math.max(max.energyKJ,Math.abs(d.totalEnergyKJ));max.profileMassL1Kg=Math.max(max.profileMassL1Kg,d.profileMassL1Kg);
 });
 if(a.final.allEvents.length!==b.final.allEvents.length)throw Error('Temporal refinement changed saturation crossing count.');
 a.final.allEvents.forEach((v,i)=>{const w=b.final.allEvents[i];if(v.section!==w.section||v.boundary!==w.boundary||v.direction!==w.direction)throw Error('Temporal refinement changed event sequence.');max.eventSeconds=Math.max(max.eventSeconds,Math.abs(v.seconds-w.seconds));});
 if(a.final.stop?.kind!==b.final.stop?.kind)throw Error('Temporal refinement changed stop classification.');
 if(a.final.stop)max.domainSeconds=Math.abs(a.final.seconds-b.final.seconds);
 return max;
}
module.exports={run,temporalDifference};
