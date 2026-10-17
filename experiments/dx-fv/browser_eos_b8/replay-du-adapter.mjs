// Saved-row replay through unchanged C1 wrapper, not a new EOS call or trajectory.
import fs from 'node:fs';import {createRequire} from 'node:module';import assert from 'node:assert/strict';
import {createAdapter,errorJSON,bits} from '../browser_eos_b5b_c1/adapter.mjs';
const require=createRequire(import.meta.url),{createEngine}=require('../../../engine.js'),table=createEngine(require('../../../properties.json'));
const url=n=>new URL('evidence/'+n,import.meta.url),du=JSON.parse(fs.readFileSync(url('du-endpoints.json'))),rows=[];
for(const r of du.rows)for(const obs of r.observations.filter(z=>['candidate','gateA'].includes(z.artifact))){
 const v=r.original.input.values,raw=obs.reused;let requests=[];
 const eos={evaluate(request){requests.push({mode:request.mode,bits:request.args.map(bits)});assert.equal(request.mode,'DU');assert.deepEqual(request.args.map(bits),[r.original.input.bits.rho,r.original.input.bits.u]);
 if(raw.error)throw Error(typeof raw.error==='string'?raw.error:raw.error.message);return {...raw.state.values};}};
 const adapter=createAdapter(eos,table);let result,error;
 try{result=adapter.stateMVU(v.M,v.V,v.U_kJ,35);}catch(e){error=errorJSON(e);}
 assert.equal(result,undefined);assert.equal(error.faultKind,'solver');const reason=obs.returned?'boundary-unresolved':'inverse-recovery-failure';
 assert.equal(error.evidence.propertyFailure.reason,reason);assert.equal(error.evidence.propertyFailure.physicalTrajectoryExit,'unproved');
 rows.push({issueId:r.issueId,runtime:obs.runtime,fullVLE:obs.fullVLE,requests,error,accepted:false});
}
fs.writeFileSync(url('du-adapter-replay.json'),JSON.stringify({passed:true,scope:'Saved raw observation injection only; unchanged C1 adapter, actual table guard. Proves classification for these raw rows, not natural A2 reachability or a fresh EOS execution.',rows},null,2)+'\n');
console.log('24 saved DU outcomes refused; C1 B/C solver classification, no physical exit proof');
