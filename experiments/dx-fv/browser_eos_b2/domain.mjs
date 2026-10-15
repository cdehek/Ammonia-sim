// Exact accepted A1 domain assertions reused by A2. Only module/factory and PT
// interfaces are supplied. Both selected A2 configurations retain their options.
import {loadEOS} from '../browser_eos_backend/loader.mjs';
import {createAdapter} from '../browser_eos_backend/adapter.mjs';
import {withPT} from './adapter-pt.mjs';
export async function domain(catalog,choice){
 const selected={thermalJacobian:choice==='exact-aware'?'exact':'finite-difference',timestepGrowth:'failure-aware'};
 const eos=await loadEOS('build44'),em={exports:{}};new Function('module','exports',catalog.sources['../../engine'])(em,em.exports);
 const guard=em.exports.createEngine(JSON.parse(catalog.sources['../../properties.json'])),adapter=withPT(createAdapter(eos,guard),eos,guard),cache={};let report;
 const select=m=>{if(m.exports.createCoupledModel){const f=m.exports.createCoupledModel;m.exports={...m.exports,createCoupledModel:(engine,options={},observer)=>f(engine,{...options,...selected},observer)};}};
 class BrowserModule{
  constructor(){this.exports={};this.require=require;this.paths=[];}
  _compile(source,filename){new Function('module','exports','require','__dirname',source)(this,this.exports,this.require,'accepted');if(filename.endsWith('coupled-model.cjs'))select(this);}
 }
 function require(name){
  if(name==='node:assert/strict')return globalThis.b2assert;
  if(name==='node:path')return {join:(...p)=>p.join('/')};
  if(name==='node:module')return BrowserModule;
  if(name==='node:fs')return {readFileSync:p=>catalog.sources[p.split('/').pop()],writeFileSync:(p,text)=>{report=JSON.parse(text);}};
  if(name==='../../engine')return {createEngine:()=>adapter};
  const key=name.startsWith('./')?name.slice(2):name;
  if(key.endsWith('.json'))return JSON.parse(catalog.sources[key]);
  if(cache[key])return cache[key].exports;if(!catalog.sources[key])throw Error('Missing accepted import '+key);
  const m=new BrowserModule();cache[key]=m;m._compile(catalog.sources[key],key);return m.exports;
 }
 const prefix=`const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),Module=require('node:module');const {createEngine}=require('../../engine'),data=require('../../properties.json');const {createCoupledModel}=require('./coupled-model.cjs'),{fixture}=require('./coupled-fixtures.cjs');const report={acceptedCommit:'be9eb35a4ddf5098e685182f8104685127c6a6ee',cases:[]};`;
 const code=prefix+catalog.domain.functions+'\ntry{'+catalog.domain.text+'}catch(error){report.passed=false;report.failure={message:error.message,stack:error.stack};}\nfs.writeFileSync("capture",JSON.stringify(report));';
 const start=performance.now();
 try{new Function('require','module','__dirname',code)(require,{paths:[]},'accepted');return {choice,selected,PTInterface:'B2 isolated PT mapping; original B1 PH/DU unchanged',report,counts:adapter.counts,init:eos.init,linearMemory:eos.memory(),elapsedMS:performance.now()-start};}finally{eos.dispose();}
}
