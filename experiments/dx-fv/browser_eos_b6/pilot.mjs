import {loadEOS} from './candidate-diagnostic.mjs';
import {step} from './lifecycle.mjs';
export async function run(){const fixtures=await (await fetch('./experiments/dx-fv/browser_eos_b6/evidence/historical-rejected-pt.json')).json();const events=[],e=await loadEOS('candidateB',{events});try{return {rows:[step(e,fixtures[0].request,{candidate:true,expectReject:true,events}),step(e,{mode:'PT',args:[350000,300]},{candidate:true,events})],events};}finally{e.dispose();}}
