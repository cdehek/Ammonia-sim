import fs from 'node:fs';
import zlib from 'node:zlib';
import {createHash} from 'node:crypto';
import {same,exact,assert} from '../browser_eos_b9/values.mjs';
const B=new URL('./',import.meta.url);
const read=p=>JSON.parse(zlib.gunzipSync(fs.readFileSync(new URL(p,B))));
const rows=name=>zlib.gunzipSync(fs.readFileSync(new URL('evidence/'+name,B))).toString().trim().split('\n').map(JSON.parse).filter(r=>r.type==='checkpoint').map(r=>{if(r.scienceReference){const ref=r.scienceReference,src=rows(ref.file).find(x=>x.seconds===ref.seconds);for(const k of ['science','scienceExact','attempts'])r[k]=src[k];}return r;});
const historical=read('../browser_eos_b11/evidence/integration-chromium.json.gz');
const digest=v=>createHash('sha256').update(JSON.stringify(v)).digest('hex');
for(const fixture of ['cold','warm'])for(const r of rows(`canonical-${fixture}-010-r1.jsonl.gz`)){assert(digest(r.scienceExact)===r.scienceHash,'retained binary64 science hash mismatch');// JSON omits the original iteration event's explicitly undefined context.
for(const a of r.attempts)for(const event of a.events)if(event.type==='iteration'&&!Object.hasOwn(event,'context'))event.context=undefined;
assert(digest(exact(r.attempts))===r.attemptsHash,'retained attempt hash mismatch');}
const result=[];
for(const fixture of ['cold','warm']){
 const c=rows(`baseline-${fixture}-r1.jsonl.gz`),o=rows(`observed-${fixture}-baseline.jsonl.gz`),a=rows(`control-${fixture}-baseline.jsonl.gz`),h=historical.science.find(r=>r.fixture===fixture);
 assert(c.length===4&&o.length===4,'four baseline checkpoints');
 for(let i=0;i<4;i++){
  assert(c[i].scienceHash===o[i].scienceHash,'instrumentation changed science');assert(c[i].attemptsHash===o[i].attemptsHash,'instrumentation changed decisions');
  assert(c[i].scienceHash===a[i].scienceHash,'accepted A2 same-engine science changed');assert(c[i].attemptsHash===a[i].attemptsHash,'accepted A2 same-engine decisions changed');
  const old=h.fullAcceptedDetails[i],now=c[i].science;

  const compare={record:exact(now.record),state:exact(now.state)};
  // Historical details are already f64-encoded; report equality without tolerances.
  const historicalExact=JSON.stringify(old)===JSON.stringify(compare);
  result.push({fixture,seconds:c[i].seconds,acceptedA2SameEngineBitExact:true,canonicalObservedScienceBitExact:true,canonicalObservedAttemptsBitExact:true,historicalChromiumBitExact:historicalExact,oldKeys:Object.keys(old),scienceHash:c[i].scienceHash});
 }
}
fs.writeFileSync(new URL('evidence/baseline-parity.json',B),JSON.stringify({retainedCanonicalScienceAndAttemptHashesIndependentlyRecomputed:true,omittedUndefinedIterationContextRestored:true,node:process.version,historicalBrowser:historical.version,checks:result},null,2)+'\n');
console.log(JSON.stringify(result,null,2));
