import {writeFileSync} from 'node:fs';import {gzipSync} from 'node:zlib';import {Session} from 'node:inspector';import {createRequire} from 'node:module';
import {run,seal} from './profile.mjs';import {same,assert} from '../browser_eos_b9/values.mjs';
const require=createRequire(import.meta.url),F=require('../browser_eos_backend/accepted/coupled-model.cjs'),fixtures=require('../browser_eos_backend/accepted/coupled-fixtures.cjs'),engine=require('../../../engine.js'),data=require('../../../properties.json');
const result={runtime:process.version,platform:process.platform,arch:process.arch,referenceOnly:true,runs:[]};
for(const fixture of ['cold','warm']){
 const control=await seal(run('original',fixture,{sequence:true})),candidate=await seal(run('instrumented',fixture,{sequence:true}));assert(same(control.science,candidate.science),'Node instrumented parity');assert(control.sequenceHash===candidate.sequenceHash,'Node property sequence');
 const attempts=[],model=F.createCoupledModel(engine.createEngine(data),{trace:true,timestepGrowth:'failure-aware'},a=>attempts.push(a)),state=model.create(fixtures.fixture(fixture)),records=[model.record(state)];
 for(const duration of [.0001,.0004,.0005]){records.push(model.advance(state,duration));model.record(state);}
 assert(same(state,control.science.rows.at(-1).state)&&same(records,control.science.rows.map(r=>r.record))&&same(attempts,control.science.attempts),'direct Node / literal package parity');
 const session=new Session();session.connect();const post=(method,params={})=>new Promise((resolve,reject)=>session.post(method,params,(err,r)=>err?reject(err):resolve(r)));
 await post('Profiler.enable');await post('Profiler.setSamplingInterval',{interval:500});await post('Profiler.start');const sampled=await seal(run('original',fixture));const profile=await post('Profiler.stop');session.disconnect();
 writeFileSync(new URL('./evidence/cpu-node-'+fixture+'.json',import.meta.url),JSON.stringify(profile));
 const after=await seal(run('original',fixture));assert(same(after.science,control.science)&&same(sampled.science,control.science),'Node repeated original parity');
 result.runs.push(control,candidate,sampled,after);
}
writeFileSync(new URL('./evidence/node.json.gz',import.meta.url),gzipSync(JSON.stringify(result)));console.log('Node direct/literal/diagnostic property-sequence and scientific parity PASS');
