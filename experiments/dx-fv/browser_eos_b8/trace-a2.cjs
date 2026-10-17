'use strict';
// Observation only. Run under timeout 45s. No source transform or fault injection.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const B=__dirname,R=path.resolve(B,'../../..'),A=path.resolve(B,'../browser_eos_backend/accepted'),commit='be9eb35a4ddf5098e685182f8104685127c6a6ee';
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const verified=JSON.parse(fs.readFileSync(path.join(B,'evidence/start-audit.json'))).acceptedA2;
const files={},edges=[];
function visit(file){if(files[file])return;const p=file.startsWith('experiments/')?path.join(A,path.basename(file)):path.join(R,file),raw=fs.readFileSync(p);
 assert.equal(digest(raw),verified[file].sha256);files[file]={sha256:digest(raw),snapshot:path.relative(R,p)};
 if(file.endsWith('.cjs'))for(const match of raw.toString().matchAll(/require\(['"](\.\/[^'"]+)['"]\)/g)){const target=path.posix.join(path.posix.dirname(file),match[1]);edges.push({from:file,to:target});visit(target);}}
visit('experiments/dx-fv/coupled-model.cjs');visit('experiments/dx-fv/coupled-fixtures.cjs');visit('engine.js');visit('properties.json');
const {createCoupledModel}=require(path.join(A,'coupled-model.cjs')),{fixture}=require(path.join(A,'coupled-fixtures.cjs'));
const {createEngine}=require(path.join(R,'engine.js')),data=require(path.join(R,'properties.json'));
const bits=n=>{const b=Buffer.alloc(8);b.writeDoubleBE(n);return b.toString('hex');};
function run(observe){const actual=createEngine(data),calls=[],attempts=[];let stage='factory';
 const engine=observe?new Proxy(actual,{get(target,key){const value=target[key];if(typeof value!=='function')return value;
 return (...args)=>{const row={operation:key,stage,args,bits:args.map(bits),stack:new Error().stack.split('\n').slice(2,8).map(s=>s.replaceAll(R+'/',''))};calls.push(row);
 try{const out=Reflect.apply(value,target,args);row.outcome='returned';return out;}catch(e){row.outcome='threw';row.message=e.message;throw e;}};}}):actual;
 const model=createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'},observe?a=>attempts.push(a):null);
 stage='create';const state=model.create(fixture('cold'));stage='initial-record';const initial=model.record(state);stage='advance';const final=model.advance(state,.001);
 assert.equal(final.stop,null);assert.equal(state.seconds,.001);assert.equal(final.sectionCount,5);
 assert.ok(Math.abs(final.massResidualKg)<1e-8);assert.ok(Math.abs(final.combinedEnergyResidualKJ)<1e-6);
 stage='final-record';assert.deepEqual(model.record(state),final);
 return {state,initial,final,calls,attempts};}
try{const plain=run(false),traced=run(true);assert.deepEqual(traced.state,plain.state);assert.deepEqual(traced.initial,plain.initial);assert.deepEqual(traced.final,plain.final);
 const counts={};for(const r of traced.calls)counts[r.operation]=(counts[r.operation]||0)+1;
 assert.deepEqual(Object.keys(counts).sort(),['ph','sat','stateMVU']);
 const events=traced.attempts.flatMap(a=>a.events),out={passed:true,runtime:process.version,acceptedCommit:commit,scope:'One cold five-section scenario, nonzero heat/flow, .001 s. Not a qualification run. Public engine calls only; internal lexical calls characterized statically.',files,edges,config:fixture('cold'),durationSeconds:.001,settings:traced.final.settings,exactObservationParity:true,stateSHA256:digest(JSON.stringify(traced.state)),recordSHA256:digest(JSON.stringify(traced.final)),counts,calls:traced.calls,attempts:traced.attempts,derivativeEvents:events.filter(e=>e.type==='derivative').length,lineSearchEvents:events.filter(e=>e.type==='line-search').length,record:traced.final};
 const raw=Buffer.from(JSON.stringify(out,null,2)+'\n'),zipped=require('node:zlib').gzipSync(raw,{mtime:0});
 fs.writeFileSync(path.join(B,'evidence/a2-trace.json.gz'),zipped);
 const {calls:omitCalls,attempts:omitAttempts,...summary}=out;summary.traceArtifact={file:'a2-trace.json.gz',sha256:digest(zipped),uncompressedSHA256:digest(raw),publicCallRows:out.calls.length,attempts:out.attempts.length};
 fs.writeFileSync(path.join(B,'evidence/a2-trace-summary.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify({passed:true,counts,derivativeEvents:out.derivativeEvents,lineSearchEvents:out.lineSearchEvents,attempts:out.attempts.length}));
}catch(e){fs.writeFileSync(path.join(B,'evidence/a2-trace-failure.json'),JSON.stringify({message:e.message,stack:e.stack},null,2)+'\n');throw e;}
