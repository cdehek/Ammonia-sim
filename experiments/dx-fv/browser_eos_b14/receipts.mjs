import fs from'node:fs';import zlib from'node:zlib';import path from'node:path';import{fileURLToPath}from'node:url';
const base=fileURLToPath(new URL('./',import.meta.url));
export const evidence=path.resolve(base,process.env.B14_RECEIPTS||'evidence');
if(!evidence.startsWith(base))throw Error('Receipts must stay inside B14');
export const evidenceURL=new URL('file://'+evidence+'/');
export function readReceipt(name){
 const file=path.join(evidence,name+'.jsonl.gz');if(path.dirname(file)!==evidence)throw Error('Receipt path');
 const rows=zlib.gunzipSync(fs.readFileSync(file)).toString().trim().split('\n').map(JSON.parse);
 for(const row of rows){
  if(row.scienceReference){const ref=row.scienceReference;const source=readReceipt(ref.name).find(r=>r.type==='checkpoint'&&r.seconds===ref.seconds);row.science=source.science;}
  if(row.attemptsReference)row.attempts=readReceipt(row.attemptsReference).find(r=>r.type==='attempts').attempts;
 }
 return rows;
}
