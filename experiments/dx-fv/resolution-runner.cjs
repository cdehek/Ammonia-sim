'use strict';
const {createEvaporator}=require('./evaporator.cjs'),{numericalOptions}=require('./spatial-fixtures.cjs'),{measurement,meshes}=require('./resolution-observables.cjs');
function run(engine,c,options={}){
 if(!meshes.includes(c.config.sectionCount))throw Error('Unapproved comparison mesh.');
 const model=createEvaporator(engine,{...numericalOptions(1e-6),...options}),state=model.create(c.config),rows=[],initial=measurement(model.record(state),state.spec,engine),started=performance.now();let change=0;
 const times=[...new Set([0,...c.samples,...c.changes.map(v=>v.seconds)])].sort((a,b)=>a-b);
 for(const target of times){if(target>state.seconds)model.advance(state,target-state.seconds);if(state.stop)break;if(c.samples.includes(target))rows.push(measurement(model.record(state),state.spec,engine));while(change<c.changes.length&&c.changes[change].seconds===target)model.update(state,c.changes[change++].patch);}
 return {initial,rows,final:measurement(model.record(state),state.spec,engine),elapsedMS:performance.now()-started};
}
module.exports={run};
