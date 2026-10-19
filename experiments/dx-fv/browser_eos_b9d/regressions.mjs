import {setup,digest,physical} from '../browser_eos_b9c/harness.mjs';
import {assert,same,exact,auditRecord,diagnostic} from '../browser_eos_b9/values.mjs';
export async function additional(mode){
 const base=setup(mode),sat=base.engine.sat(4),ph=x=>({p:4,h:sat.hf+(sat.hg-sat.hf)*x});
 const cases=[...[0,1,.25,.75].flatMap(x=>['inlet','outlet'].map(side=>({name:side+'-phase-'+x,config:{[side]:ph(x)}}))),
 {name:'superheated-inlet',config:{inlet:{p:4,h:base.engine.statePT(4,sat.T+20).h}}},
 {name:'manual-inlet-only',patch:{inlet:{p:4.15,h:575}}},
 {name:'manual-outlet-only',patch:{outlet:{p:3.4,h:1650}}},
 {name:'scheduled-two-boundaries',config:{schedule:[{seconds:.0001,patch:{inlet:{p:4.15,h:575}}},{seconds:.0002,patch:{outlet:{p:3.4,h:1650}}}]}},
 ...[.3,35].map(p=>({name:'strict-valid-boundary-'+p,config:{inlet:{p,h:(base.engine.sat(p).hf+base.engine.sat(p).hg)/2}}}))];
 const rows=[];
 for(const c of cases){
  const s=setup(mode,true),state=s.model.create(c.config||{}),records=[s.model.record(state)];
  records.push(s.model.advance(state,.0001));if(c.patch)records.push(s.model.update(state,c.patch));records.push(s.model.advance(state,.0001));
  const before=structuredClone(state),again=s.model.record(state);assert(same(before,state)&&same(again,records.at(-1)),'record purity');
  const restart=s.model.create(c.config||{});assert(same(s.model.record(restart),records[0]),'original independent restart');
  const science={state,records,attempts:s.attempts};
  const hashes={};for(const key of ['residuals','linear','solves'])hashes[key]=await digest(s.p.out[key]);
  rows.push({name:c.name,config:c.config||{},patch:c.patch||null,science:exact(science),hash:await digest(science),componentHashes:hashes,audits:records.map(auditRecord),stop:state.stop});
 }
 return {mode,rows,passed:true};
}
