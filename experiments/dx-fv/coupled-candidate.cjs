'use strict';
// Read the preserved candidate without checking out or changing any files.
const {execFileSync}=require('node:child_process'),{createRequire}=require('node:module');
const path=require('node:path'),crypto=require('node:crypto');
const CANDIDATE='aa9514b0338b6021d9afc4b9f47f88ebdde765da';
function candidateFactory(){
  const localRequire=createRequire(path.join(__dirname,'coupled-model.cjs'));
  const sources={};
  for(const name of ['coupled-implicit.cjs','coupled-model.cjs'])sources[name]=execFileSync('git',['show',`${CANDIDATE}:experiments/dx-fv/${name}`],{cwd:__dirname,encoding:'utf8'});
  function load(name){
    const module={exports:{}};
    new Function('module','exports','require',sources[name])(module,module.exports,ref=>ref==='./coupled-implicit.cjs'?load('coupled-implicit.cjs'):localRequire(ref));
    return module.exports;
  }
  return {create:load('coupled-model.cjs').createCoupledModel,commit:CANDIDATE,
    sourceSHA256:Object.fromEntries(Object.entries(sources).map(([name,s])=>[name,crypto.createHash('sha256').update(s).digest('hex')]))};
}
module.exports={candidateFactory,CANDIDATE};
