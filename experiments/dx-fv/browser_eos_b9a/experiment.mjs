export async function run(stage,args={}){
 if(stage==='startup')return (await import('./startup.mjs')).run();
 if(stage==='workload')return (await import('./benchmark.mjs')).workload(args.mode,args.fixture,args);
 if(stage==='lifecycle')return (await import('./lifecycle.mjs')).run();
 if(stage==='failure')return (await import('./failure-tests.mjs')).run();
 if(stage==='baseline')return (await import('../browser_eos_b9/experiment.mjs')).parity();
 if(stage==='parityB')return compactParity('B');
 if(stage==='parityC')return compactParity('C');
 if(stage==='attribution')return (await import('./attribution.mjs')).worker();
 throw Error('Unknown stage '+stage);
}
export async function compactParity(mode='B'){
 const {Client}=await import('./client.mjs'),{same,assert,exact}=await import('./values.mjs'),{compact}=await import('./snapshot.mjs');const results=[];
 for(const fixture of ['cold','warm']){const c=new Client(mode,{test:true});try{
 const initial=await c.request('initialize',{fixture});assert(initial.success);const snapshots=[initial.result.compact];
 for(const duration of [.0001,.0004,.0005]){const r=await c.request('advance',{duration});assert(r.success,JSON.stringify(r.error));snapshots.push(r.result.compact);const sr=await c.request('snapshot');assert(sr.success&&same(sr.result.compact,r.result.compact),'original record cadence');}
 const proof=await c.request('testEvidence');assert(proof.success);
 const d=await c.request('diagnosticsDetail',{version:snapshots.at(-1).acceptedVersion});assert(d.success&&d.result.available);assert(same(compact(d.result.record,d.result.state),snapshots.at(-1)),'compact projection');
 const copy=d.result.state.cells[0].massKg;d.result.state.cells[0].massKg=-1;const d2=await c.request('diagnosticsDetail',{version:snapshots.at(-1).acceptedVersion});assert(d2.result.state.cells[0].massKg===copy,'detached diagnostic state');
 results.push({fixture,mode,passed:true,snapshots:exact(snapshots),proof:proof.result,diagnosticRecord:exact(d2.result.record),diagnosticState:exact(d2.result.state),insideOwnerExactParity:true});await c.dispose();}finally{c.terminate();}}
 return {passed:true,results};
}
