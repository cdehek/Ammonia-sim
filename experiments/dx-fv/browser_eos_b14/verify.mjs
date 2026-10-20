// Exact original-versus-observed verification, including actual Jacobian matrices.
import fs from 'node:fs';import zlib from 'node:zlib';import {createHash}from'node:crypto';
import{exact,same,assert}from'../browser_eos_b9/values.mjs';
import{readReceipt,evidenceURL}from'./receipts.mjs';
const B=new URL('./',import.meta.url),names=process.argv.slice(2),digest=v=>createHash('sha256').update(JSON.stringify(exact(v))).digest('hex');
const read=readReceipt;
export function rows(name){return read(name);}
function restore(attempts){for(const a of attempts)for(const e of a.events)if(e.type==='iteration'&&!Object.hasOwn(e,'context'))e.context=undefined;return attempts;}
const canon=read(names[0]),obs=read(names[1]),ca=canon.filter(r=>r.type==='checkpoint'),ob=obs.filter(r=>r.type==='checkpoint');
assert(ca.length===ob.length,'checkpoint count');
for(let i=0;i<ca.length;i++){assert(ca[i].seconds===ob[i].seconds,'times');assert(ca[i].scienceHash===ob[i].scienceHash,'scientific hash');assert(ca[i].attemptsHash===ob[i].attemptsHash,'original attempt hash');assert(digest(ca[i].science)===ca[i].scienceHash,'canonical hash recomputation');assert(same(ca[i].science,ob[i].science),'exact state/record contents');}
const attempts=restore(canon.find(r=>r.type==='attempts').attempts),other=restore(obs.find(r=>r.type==='attempts').attempts);assert(same(attempts,other),'exact original attempt events');assert(digest(attempts)===ca.at(-1).attemptsHash,'original attempt hash recomputation');
let expected=[],active;
for(const a of attempts)for(const e of a.events){
 if(e.type==='iteration'&&e.status==='active')active={residual:e.residual,j:Array.from({length:21},()=>Array(21))};
 if(e.type==='derivative'&&e.outcome==='used'){assert(active,'base residual');for(let i=0;i<21;i++)active.j[i][e.column]=(e.residual[i]-active.residual[i])/e.step;if(e.column===20)expected.push(digest(active.j));}
}
const d=obs.find(r=>r.type==='diagnostics');if(d.matrices.length)assert(same(expected,d.matrices),'actual Jacobian hash vs independently reconstructed original');
let historical=[];
if(names[0].startsWith('canonical-')&&names[0].includes('-r1')&&canon[0].schedule==='original'){
 const fixture=canon.find(r=>r.type==='header').fixture;
 const old=zlib.gunzipSync(fs.readFileSync(new URL('../browser_eos_b13/evidence/canonical-'+fixture+'-010-r1.jsonl.gz',B))).toString().trim().split('\n').map(JSON.parse).filter(r=>r.type==='checkpoint');
 for(let i=0;i<ca.length;i++){assert(ca[i].scienceHash===old[i].scienceHash,'pinned B13 science');assert(ca[i].attemptsHash===old[i].attemptsHash,'pinned B13 attempts');historical.push(ca[i].seconds);}
}
const receipt={passed:true,canonical:names[0],observed:names[1],node:process.version,checkpointCount:ca.length,bitExactStatesRecordsLedgersEventsStopsAndControllers:true,bitExactOriginalAttempts:true,bitExactDerivativeResiduals:true,independentlyReconstructedActualJacobianHashes:expected.length,actualJacobianHashesCompared:d.matrices.length,historicalB13Checkpoints:historical,checks:ca.map(r=>({seconds:r.seconds,scienceHash:r.scienceHash,attemptsHash:r.attemptsHash}))};
fs.writeFileSync(new URL('equivalence-'+names[1]+'.json',evidenceURL),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));
