import {Client} from './client.mjs';import {same,assert} from './values.mjs';
export async function run(){const rows=[];
 for(let round=0;round<3;round++)for(const mode of [['A','B','C'],['C','A','B'],['B','C','A']][round])for(const fixture of ['cold','warm']){
 const c=new Client(mode);try{assert((await c.request('initialize',{fixture})).success);let a;for(const duration of [.0001,.0004,.0005]){a=await c.request('advance',{duration});assert(a.success);}
 const before=await c.request('diagnostics');const commands=mode==='A'?['diagnostics','snapshot']:['diagnosticsSummary','diagnosticsDetail','snapshotCompact'];const samples=[];
 for(const type of commands){const r=await c.request(type,type.startsWith('diagnostics')&&type!=='diagnostics'?{version:a.acceptedVersion}:{});assert(r.success);if(type==='diagnosticsDetail')assert(r.result.available&&r.result.state&&r.result.acceptedVersion===a.acceptedVersion);
 samples.push({type,clock:r.clock,acceptedVersion:r.acceptedVersion,serviceMS:r.timing.serviceMS,roundtripMS:r.clientTiming.roundtripMS,clientPostMS:r.clientTiming.postMS,clientHandlingMS:r.clientTiming.handlingMS,jsonEstimateBytes:new TextEncoder().encode(JSON.stringify(r.result)).length,scope:r.result.scope??'original B9 cumulative/record',attemptCount:r.result.attempts?.length??null});}
 const after=await c.request('diagnostics');assert(same(before.result.counts,after.result.counts)||(mode==='A'&&commands.includes('snapshot')),'compact retrieval must add no property work');rows.push({round,mode,fixture,samples,compactRetrievalAddsNoPropertyCalls:mode!=='A'});assert((await c.dispose()).success);
 }finally{c.terminate();}}
 return {passed:true,rows,scopeDifference:'A diagnostics are cumulative attempts; B/C detail is final endpoint original record/attempts plus current full state. Do not treat these as identical retrieval work.'};}
