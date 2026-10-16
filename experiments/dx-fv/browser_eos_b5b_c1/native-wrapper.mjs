import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import {execFileSync,spawn} from 'node:child_process';
import {createAdapter,pack,errorJSON} from './adapter.mjs';
import {createAdapter as historicalAdapter} from '../browser_eos_backend/adapter.mjs';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),guard=require('../../../engine.js').createEngine(require('../../../properties.json'));
const bridge=new URL('./native.py',import.meta.url).pathname;
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'c1-native-')),request=path.join(temp,'request'),response=path.join(temp,'response');
execFileSync('mkfifo',[request,response]);const child=spawn('python',[bridge,'--server',request,response],{stdio:['ignore','inherit','inherit']});
const req=fs.openSync(request,'w'),res=fs.openSync(response,'r'),buffer=Buffer.alloc(65536);
const eos={evaluate(q){fs.writeSync(req,JSON.stringify(q)+'\n');let line='';while(!line.includes('\n')){const n=fs.readSync(res,buffer,0,buffer.length);if(!n)throw Error('native bridge closed');line+=buffer.toString('utf8',0,n);}const r=JSON.parse(line);if(r.error)throw Error(r.error);return r.raw;}};
const c=historicalAdapter(eos,guard),a=createAdapter(eos,guard),rows=[];
const capture=f=>{try{return {state:pack(f())};}catch(e){return {error:errorJSON(e)};}};
try{
const fixed=JSON.parse(fs.readFileSync(new URL('../browser_eos_b5/evidence/fixed-inputs.json',import.meta.url)));
for(const q of fixed.filter(q=>['webkit-ledger-64','webkit-ledger-65','webkit-ledger-67','webkit-ledger-68','webkit-ledger-70','webkit-ledger-75','webkit-ledger-79'].includes(q.key))){
 const x=q.input.values,control=capture(()=>c.stateMVU(x.M,x.V,x.U_kJ,35)),candidate=capture(()=>a.stateMVU(x.M,x.V,x.U_kJ,35));
 if(!!control.state!==!!candidate.state)throw Error('native outcome changed');if(control.state&&JSON.stringify(control.state)!==JSON.stringify(candidate.state))throw Error('native state changed');
 if(candidate.error&&candidate.error.evidence.propertyFailure.physicalTrajectoryExit!=='unproved')throw Error('manufactured proof');
 rows.push({key:q.key,control,candidate});
}
for(const [p,h]of [[30298.937123458254,94523.34612321304],[30298.937123458254,98904.56398938334],[799999.9981754856,1624022.744737779],[799999.9981754856,1624019.7431341156],[350000,1100000]]){
 const control=capture(()=>c.ph(p/1e5,h/1000)),candidate=capture(()=>a.ph(p/1e5,h/1000));
 if(!!control.state!==!!candidate.state||(control.state&&JSON.stringify(control.state)!==JSON.stringify(candidate.state)))throw Error('native focused outcome changed '+JSON.stringify({request:[p,h],control,candidate}));
 if(control.error&&control.error.message!==candidate.error.message)throw Error('native focused error changed');
 rows.push({request:[p,h],control,candidate});
}
// Actual preserved native QT exception, full-VLE test configuration only.
for(const key of ['native-ledger-148','native-ledger-164','native-ledger-165']){
 const q=fixed.find(q=>q.key===key),x=q.input.values,fullEOS={evaluate:q=>eos.evaluate({...q,fullVLE:true})};
 const control=capture(()=>historicalAdapter(fullEOS,guard).stateMVU(x.M,x.V,x.U_kJ,35)),candidate=capture(()=>createAdapter(fullEOS,guard).stateMVU(x.M,x.V,x.U_kJ,35));
 if(!control.error||!candidate.error||candidate.state||candidate.error.evidence.propertyFailure.reason!=='inverse-recovery-failure')throw Error('native QT exception lost');
 if(candidate.error.evidence.propertyFailure.rawRecovery!=='failed')throw Error('native rejected raw state leak');rows.push({key,fullVLE:true,control,candidate});
}
fs.writeFileSync(new URL('./evidence/native-wrapper.json',import.meta.url),JSON.stringify({passed:true,rows,nativeBridge:'Persistent archived B4C C ABI over local FIFOs; identical library for candidate/control; no build.'},null,2)+'\n');
console.log('native wrapper',rows.length,'matched cases');
if(!process.argv.includes('--properties-only')){
const directory=new URL('./a2/',import.meta.url),sources=Object.fromEntries(fs.readdirSync(directory).filter(n=>n.endsWith('.cjs')).map(n=>[n,fs.readFileSync(new URL(n,directory),'utf8')]));
const acceptedDirectory=new URL('../browser_eos_backend/accepted/',import.meta.url),controlSources=Object.fromEntries(fs.readdirSync(acceptedDirectory).filter(n=>n.endsWith('.cjs')).map(n=>[n,fs.readFileSync(new URL(n,acceptedDirectory),'utf8')]));
const fixture=fixed.find(q=>q.key==='webkit-ledger-64').input.values;
const refusal=adapter=>{const r=capture(()=>adapter.stateMVU(fixture.M,fixture.V,fixture.U_kJ,35));if(!r.error)throw Error('expected native refusal');return Object.assign(Error(r.error.message),{faultKind:r.error.faultKind,evidence:r.error.evidence});};
const {runA2}=require('./a2-tests.cjs');const a2=runA2({sources,controlSources,engine:a,tableEngine:guard,realFailure:()=>refusal(a),historicalFailure:()=>refusal(c),onProgress:rows=>{fs.writeFileSync(new URL('./evidence/native-A2-progress.json',import.meta.url),JSON.stringify({completed:rows.length,lastScenario:rows.at(-1).scenario})+'\n');console.log('native A2 progress',rows.length,rows.at(-1).scenario);}});
fs.writeFileSync(new URL('./evidence/native-A2.json',import.meta.url),JSON.stringify(a2,null,2)+'\n');console.log('native A2',a2.passed,a2.rows.length,'scenarios');
}
}finally{fs.closeSync(req);fs.closeSync(res);child.kill();fs.rmSync(temp,{recursive:true});}
