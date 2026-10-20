// Validate the evidence SHA implementation against Node crypto, including boundaries.
import {SHA256,hash} from './hash.mjs';
import {createHash} from 'node:crypto';
import {assert} from './assets/values.mjs';
const cases=[];
for(const n of [0,1,3,55,56,63,64,65,127,128,1000,100000]){
 const bytes=new TextEncoder().encode('a'.repeat(n)),expected=createHash('sha256').update(bytes).digest('hex');
 for(const chunk of [1,7,64,301]){const h=new SHA256();for(let i=0;i<bytes.length;i+=chunk)h.update(bytes.subarray(i,i+chunk));assert(h.hex()===expected,'SHA boundary/chunk '+n+'/'+chunk);}
 cases.push({bytes:n,sha256:expected});
}
const unicode='NH₃ — 氨';assert(new SHA256().update(unicode).hex()===createHash('sha256').update(unicode).digest('hex'),'Unicode');
assert(hash(-0)!==hash(0)&&hash(NaN)!==hash(null)&&hash(undefined)!==hash(null),'exact encoding distinctions');
console.log(JSON.stringify({passed:true,algorithm:'SHA-256 checked against Node crypto; exact evidence distinguishes signed zero/nonfinite/undefined',cases,chunkSizes:[1,7,64,301],unicode:true}));
