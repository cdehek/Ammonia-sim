'use strict';
// Execute byte-identical accepted assertion blocks independently. A failing block
// stays FAIL, with its partial report; subsequent blocks are separate executions.
// Only module dependency injection selects the B1 backend and accepted options.
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),crypto=require('node:crypto');
const [acceptedRoot,output,kind='coupled-test',choice='fd-aware',only='all',build='build44']=process.argv.slice(2);
const acorn=require(process.env.B2_ACORN||'/workspace/b2-runtime/node_modules/acorn');
const base=path.resolve(acceptedRoot),dir=path.join(base,'experiments/dx-fv');
const selected={...(choice.startsWith('exact')?{thermalJacobian:'exact'}:{}),...(choice.endsWith('aware')?{timestepGrowth:'failure-aware'}:{})};
const source=fs.readFileSync(path.join(dir,kind+'.cjs'),'utf8'),ast=acorn.parse(source,{ecmaVersion:'latest',locations:true});
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
async function main(){
 const realEngine=require(path.join(base,'engine.js')).createEngine(require(path.join(base,'properties.json')));
 const {backend}=await import('./node-eos.mjs');
 const counts={ph:0,sat:0,stateMVU:0};
 const counted={...realEngine,counts};for(const key of Object.keys(counts))counted[key]=(...args)=>{counts[key]++;return realEngine[key](...args);};
 const {eos,adapter}=build==='table'?{eos:{init:null,memory:()=>null,dispose(){}},adapter:counted}:await backend(build,realEngine);
 const enginePath=require.resolve(path.join(base,'engine.js'));
 require.cache[enginePath].exports={createEngine:()=>adapter};
 const modelPath=require.resolve(path.join(dir,'coupled-model.cjs')),original=require(modelPath);
 const wrap=(e,o={},observer)=>original.createCoupledModel(e,{...o,...selected},observer);
 require.cache[modelPath].exports={...original,createCoupledModel:wrap};
 const report={kind,choice,build,runtime:process.version,acceptedCommit:'be9eb35a4ddf5098e685182f8104685127c6a6ee',sourceSHA256:hash(source),selected,init:eos.init,blocks:[]};
 const save=()=>fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 const run=(text,overrides={})=>{const m=new Module(path.join(dir,kind+'.cjs'),module);m.filename=path.join(dir,kind+'.cjs');m.paths=module.paths;const req=m.require.bind(m);m.require=id=>Object.hasOwn(overrides,id)?overrides[id]:req(id);m._compile(text,m.filename);};
 let blocks;
 if(kind==='coupled-test'){
  const fn=ast.body.find(n=>n.type==='FunctionDeclaration'&&n.id.name==='verification');
  const prefix=source.slice(0,fn.start),statements=fn.body.body;
  const start=statements.findIndex(n=>n.type==='BlockStatement');
  const setup=source.slice(statements[0].start,statements[start].start);
  blocks=statements.slice(start).filter(n=>!source.slice(n.start,n.end).startsWith('report.passed=')).flatMap((n,i)=>{
   const text=source.slice(n.start,n.end);
   if(n.type==='ForOfStatement'&&source.slice(n.right.start,n.right.end)==='cases()')return ['cold','warm','load-step','feed-step','heat-reversal'].map(name=>({id:'operating-'+name,node:n,text,caseName:name,prefix,setup}));
   return [{id:'block-'+i,node:n,text,prefix,setup}];
  });
 }else blocks=[{id:'complete',node:{loc:{start:{line:1}}},text:source}];
 for(const b of blocks){
  if(only!=='all'&&b.id!==only)continue;
  const item={id:b.id,line:b.node.loc.start.line,assertionTextSHA256:hash(b.text),status:'RUNNING'};report.blocks.push(item);save();
  const temp=output+'.'+b.id+'.partial.json';
  const before={...adapter.counts},t=performance.now();
  try{
   if(kind==='coupled-test'){
    const capture=`fs.writeFileSync(${JSON.stringify(temp)},JSON.stringify(report));`;
    const code=b.prefix+'\ntry{\n'+b.setup+'\n'+b.text+'\nreport.passed=true;\n}catch(error){report.passed=false;report.failure={activeCase,message:error.message,stack:error.stack,lastAcceptedRecord:lastRecord};}\n'+capture;
    const overrides=b.caseName?{'./coupled-fixtures.cjs':{...require(path.join(dir,'coupled-fixtures.cjs')),cases:()=>require(path.join(dir,'coupled-fixtures.cjs')).cases().filter(c=>c.name===b.caseName)}}:{};
    run(code,overrides);item.result=JSON.parse(fs.readFileSync(temp));item.status=item.result.passed?'PASS':'FAIL';
   }else{
    const argv=process.argv;process.argv=[argv[0],path.join(dir,kind+'.cjs'),temp];
    try{run(b.text);item.result=JSON.parse(fs.readFileSync(fs.existsSync(temp)?temp:temp+'.failure.json'));item.status=item.result.passed?'PASS':'FAIL';}finally{process.argv=argv;}
   }
  }catch(error){item.status='FAIL';item.error=error.stack;}
  item.elapsedMS=performance.now()-t;item.propertyCalls=Object.fromEntries(Object.keys(before).map(k=>[k,adapter.counts[k]-before[k]]));item.linearMemory=eos.memory();
  const message=item.error||item.result?.failure?.message||'';
  if(message.includes('engine.statePT is not a function')){item.status='BLOCKED';item.missingInterface='statePT(p_bar,T_C)';}
  save();console.log(JSON.stringify({id:item.id,status:item.status,elapsedMS:item.elapsedMS,message}));
 }
 eos.dispose();report.completed=true;report.propertyCalls=adapter.counts;save();
}
main().catch(e=>{console.error(e);process.exitCode=1;});
