// Unchanged accepted inventory arithmetic applied to saved PH observations.
// This is construction provenance, not a new EOS execution or trajectory.
import fs from 'node:fs';import assert from 'node:assert/strict';import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{inventory}=require('../browser_eos_backend/accepted/conservation.cjs'),{bits}=await import('../browser_eos_b5b_c1/adapter.mjs');
const source=JSON.parse(fs.readFileSync(new URL('../browser_eos_b7/evidence/original-failures.json',import.meta.url))),rows=[];
const keys=new Set([148,162,164,165].map(n=>'native-ledger-'+n));
for(let i=0;i<source.rows.length;i++){
 const f=source.rows[i];if(!['chromium','webkit'].includes(f.runtime)&&!keys.has(f.fixedKey))continue;
 const [p,h]=f.originalPHInput,stored=f.fixedInput;
 const result=inventory({rho:f.originalPH.values.rho,p:p/1e5,h:h/1000},stored.values.V);
 assert.equal(bits(result.massKg),stored.bits.M);assert.equal(bits(result.internalEnergyKJ),stored.bits.U_kJ);
 assert.equal(bits(.003/5),stored.bits.V);
 rows.push({source:'browser_eos_b7/evidence/original-failures.json',sourceRow:i,key:f.fixedKey,runtime:f.runtime,PHInput:f.originalPHInput,PHInputBits:f.originalInputBits,PHObservation:f.originalPH,inventory:stored,acceptedInitializerArithmeticExact:true,fiveSectionVolumeExact:true,scope:'Saved PH density plus requested PH coordinates through unchanged accepted inventory(). Shows admitted initialization construction, not an observed B7-backed complete model.create or a natural transient trajectory.'});
}
assert.equal(rows.length,18);fs.writeFileSync(new URL('evidence/initialization-provenance.json',import.meta.url),JSON.stringify({passed:true,rows},null,2)+'\n');console.log('18 saved constructions match accepted five-section inventory arithmetic exactly');
