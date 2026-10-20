import fs from 'node:fs';import zlib from 'node:zlib';import{createHash}from'node:crypto';import{run}from'./property-tests.mjs';
const extra=[];for(const fixture of ['cold','warm']){
 const rows=zlib.gunzipSync(fs.readFileSync(new URL('../browser_eos_b14/evidence/canonical-'+fixture+'-r1.jsonl.gz',import.meta.url))).toString().trim().split('\n').map(JSON.parse);
 function walk(x,label){if(!x||typeof x!=='object')return;if(typeof x.p==='number'&&typeof x.h==='number')extra.push({p:x.p,h:x.h,label});for(const [k,v]of Object.entries(x))walk(v,label+'.'+k);}
 for(const r of rows.filter(r=>r.type==='checkpoint'))walk(r.science,fixture+'@'+r.seconds);
}
const b=JSON.parse(fs.readFileSync(new URL('../browser_eos_b14/evidence/transition-bracket.json',import.meta.url)));for(const r of b.acceptedStates)for(const s of r.sections)extra.push({p:s.PHCoordinates.p,h:s.PHCoordinates.h,label:'transition@'+r.seconds});
const result=run(extra),raw=JSON.stringify(result);fs.writeFileSync(new URL('./evidence/property-binary64.json.gz',import.meta.url),zlib.gzipSync(raw));const summary={...result};delete summary.rows;summary.receiptSHA256=createHash('sha256').update(raw).digest('hex');fs.writeFileSync(new URL('./evidence/property-summary.json',import.meta.url),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify(summary));
