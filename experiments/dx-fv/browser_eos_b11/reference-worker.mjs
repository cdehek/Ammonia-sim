// Test-only unchanged accepted control; compact exact comparisons, no probe copies.
import {setup,digest} from '../browser_eos_b9c/harness.mjs';
import {same,assert} from '../browser_eos_b9/values.mjs';
self.onmessage=async({data:fixture})=>{try{
 const s=setup('control'),state=s.model.create(s.load('coupled-fixtures.cjs').fixture(fixture)),initial=s.model.record(state),rows=[{state:structuredClone(state),record:initial,attempts:null}];
 for(const duration of [.0001,.0004,.0005]){const a0=s.attempts.length,record=s.model.advance(state,duration);rows.push({state:structuredClone(state),record,attempts:structuredClone(s.attempts.slice(a0))});assert(same(s.model.record(state),record),'original record purity');}
 postMessage({ok:true,result:{scienceHash:await digest({rows,attempts:s.attempts}),checkpointHashes:await Promise.all(rows.map(r=>digest({record:r.record,state:r.state}))),attemptsHash:await digest(s.attempts)}});
}catch(e){postMessage({ok:false,error:e.message});}};
