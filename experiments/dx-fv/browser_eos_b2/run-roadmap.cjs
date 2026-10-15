'use strict';
// Run the accepted A2 harness itself with its original four selections. Only
// createEngine is injected. No source replacements, including compiled probes.
const path=require('node:path');
const [acceptedRoot,mode,output,...args]=process.argv.slice(2);
async function main(){
 const root=path.resolve(acceptedRoot),p=require.resolve(path.join(root,'engine.js'));
 const guard=require(p).createEngine(require(path.join(root,'properties.json')));
 const {backend}=await import('./node-eos.mjs');const {eos,adapter}=await backend('build44',guard);
 const engine=process.env.B2_PT_INTERFACE==='1'?(await import('./adapter-pt.mjs')).withPT(adapter,eos,guard):adapter;
 require.cache[p].exports={createEngine:()=>engine};
 process.on('beforeExit',()=>require('node:fs').writeFileSync(path.resolve(output)+'.backend.json',JSON.stringify({PTInterface:process.env.B2_PT_INTERFACE==='1',counts:engine.counts,linearMemory:eos.memory(),init:eos.init},null,2)+'\n'));
 process.argv=[process.argv[0],path.join(root,'experiments/dx-fv/roadmap-a2.cjs'),mode,path.resolve(output),...args];
 require(process.argv[1]);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
