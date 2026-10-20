import{readReceipt,evidenceURL}from'./receipts.mjs';
import fs from'node:fs';import zlib from'node:zlib';import{same,assert}from'../browser_eos_b9/values.mjs';
const E=evidenceURL,read=readReceipt;
const result=[];
for(const fixture of ['cold','warm']){
 const can=read('canonical-'+fixture+'-r1').filter(r=>r.type==='checkpoint'),ctl=read('control-'+fixture+'-baseline').filter(r=>r.type==='checkpoint');assert(ctl.length===4);
 for(let i=0;i<4;i++){assert(ctl[i].scienceHash===can[i].scienceHash&&ctl[i].attemptsHash===can[i].attemptsHash,'A2 baseline parity');result.push({fixture,seconds:can[i].seconds,scienceHash:can[i].scienceHash,attemptsHash:can[i].attemptsHash,originalA2B9CBitExact:true});}
}
fs.writeFileSync(new URL('baseline-parity.json',E),JSON.stringify({passed:true,checks:result},null,2)+'\n');console.log('PASS: A2/B9C baseline parity');
