// Lossless content references after science verification; never substitute failed runs.
import fs from'node:fs';import zlib from'node:zlib';import{createHash}from'node:crypto';import{readReceipt}from'./receipts.mjs';
const E=new URL('./evidence/',import.meta.url),report=[],hash=x=>createHash('sha256').update(JSON.stringify(x)).digest('hex');
for(const f of ['cold','warm'])for(const s of ['','-added','-fine'])for(const variant of ['candidate','observe-control','observe-candidate']){
 const name=variant+'-'+f+s,base='control-'+f+s,observed='observe-control-'+f+s,path=new URL(name+'.jsonl.gz',E),raw=fs.readFileSync(path),rows=structuredClone(readReceipt(name)),beforeHash=hash(rows);let fields=0;
 const original=readReceipt(base),obs=variant==='observe-candidate'?readReceipt(observed):null;
 function replace(row,key,receipt,source){if(JSON.stringify(row[key])!==JSON.stringify(source[key]))throw Error('reference inequality '+name+' '+key);row[key]={$b15ref:{receipt,type:row.type,...(row.type==='checkpoint'?{seconds:row.seconds}:{}),field:key}};fields++;}
 for(const row of rows){if(row.type==='checkpoint')replace(row,'science',base,original.find(x=>x.type==='checkpoint'&&x.seconds===row.seconds));if(row.type==='attempts')replace(row,'attempts',base,original.find(x=>x.type==='attempts'));if(obs&&row.type==='diagnostics')for(const key of ['columns','temporals','commits','controllers','matrices','captures','examples'])replace(row,key,observed,obs.find(x=>x.type==='diagnostics'));}
 const bytes=zlib.gzipSync(rows.map(x=>JSON.stringify(x)).join('\n')+'\n',{level:9});fs.writeFileSync(path,bytes);report.push({name,resolvedJSONSHA256:beforeHash,bytesBefore:raw.length,bytesAfter:bytes.length,referencedFields:fields});
}
// Fresh separate process must resolve references and validate exact original parsed JSON.
fs.writeFileSync(new URL('receipt-compaction.json',E),JSON.stringify({scope:'lossless exact references only, all sources retained locally',receipts:report},null,2)+'\n');
