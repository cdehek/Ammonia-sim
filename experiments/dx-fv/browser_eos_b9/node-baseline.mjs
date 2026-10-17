import {createRequire} from 'node:module';import {writeFileSync} from 'node:fs';import {createHash} from 'node:crypto';
import {loader} from './accepted-bundle.mjs';import {same,assert,exact,auditRecord} from './values.mjs';
const require=createRequire(import.meta.url),a=require('../browser_eos_backend/accepted/coupled-model.cjs'),f=require('../browser_eos_backend/accepted/coupled-fixtures.cjs'),engine=require('../../../engine.js'),data=require('../../../properties.json'),load=loader(),b=load('coupled-model.cjs'),rows=[];
for(const kind of ['cold','warm']){
 const run=(factory,e)=>{const attempts=[],m=factory(e,{trace:true,timestepGrowth:'failure-aware'},v=>attempts.push(v)),s=m.create(f.fixture(kind)),records=[m.record(s)];for(const t of [.0001,.0005,.001])records.push(m.advance(s,t-s.seconds));return {state:s,records,attempts};};
 const direct=run(a.createCoupledModel,engine.createEngine(data)),wrapped=run(b.createCoupledModel,load('engine.js').createEngine(load('properties.json')));assert(same(direct,wrapped),'literal-package numerical identity');
 rows.push({fixture:kind,exactDirectNodeAndWrappedParity:true,state:exact(direct.state),records:exact(direct.records),audits:direct.records.map(auditRecord),observerSHA256:createHash('sha256').update(JSON.stringify(exact(direct.attempts))).digest('hex')});
}
writeFileSync(new URL('./evidence/node-baseline.json',import.meta.url),JSON.stringify({passed:true,runtime:process.version,rows},null,2)+'\n');console.log('direct accepted sources / literal package exact parity');
