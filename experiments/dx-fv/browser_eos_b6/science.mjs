import {investigate} from '../browser_eos_b2/phase.mjs';
import {createAdapter,errorJSON,pack} from '../browser_eos_b5b_c1/adapter.mjs';
import {createAdapter as historicalAdapter} from '../browser_eos_backend/adapter.mjs';
const ok=(v,m)=>{if(!v)throw Error(m);};
const equal=(a,b,m)=>ok(JSON.stringify(a)===JSON.stringify(b),m);
const read=async p=>await(await fetch(new URL(p,import.meta.url))).json();
export async function science(loadControl,loadCandidate,engine){
 const historical=await read(`../browser_eos_b4c/evidence/${engine}-candidateB-focused.json`),native=await read('../browser_eos_b4c/evidence/native-candidateB.json');
 const ids=['B1-liquid-precision','B1-vapor-regression','approach-30298.937123458254-liquid-0.001','diagnostic-quality-band-799999.9981754856-hg-9.9e-10'];
 const requests=native.rows.filter(r=>ids.includes(r.request.id)).map(r=>r.request);ok(requests.length===4,'four inherited scientific controls');
 const a=await loadControl('candidateB'),b=await loadCandidate('candidateB');
 try{
  const control=investigate(a,requests),candidate=investigate(b,requests);equal(control,candidate,'scientific bit identity control/candidate');
  for(const r of candidate.rows){const old=historical.rows.find(o=>o.id===r.id),projected=Object.fromEntries(Object.keys(r).map(k=>[k,old[k]]));equal(r,projected,'historical focused scientific row exact');}
  const recovery=[];
  for(const row of candidate.rows)for(const [sample,z]of [['base',row.base],...row.probes.map(p=>[p.axis+':'+p.step,p.output])]){
   ok(z,'supported scientific sample');const V=.003/5,M=z.state.rho*V,U_kJ=M*(z.h/1000)-100*(z.p/1e5)*V;
   const q={mode:'DU',args:[M/V,(U_kJ/M)*1000]},c=a.evaluate(q),s=b.evaluate(q);equal(pack(c),pack(s),'DU control/candidate exact');
   const canonical={p:s.p-z.p,h:s.h-z.h,T:s.T-z.state.T},normalized={mass:Math.abs((s.rho-M/V)*V)/Math.max(.01,M),energy:Math.abs((s.u-(U_kJ/M)*1000)*M/1000)/Math.max(1,Math.abs(U_kJ))};
   ok(Math.abs(canonical.p)<=.1&&Math.abs(canonical.h)<=.1&&Math.abs(canonical.T)<=1e-4,'original canonical limits');ok(normalized.mass<=1e-11&&normalized.energy<=1e-11,'original nonlinear scale');
   recovery.push({id:row.id,sample,input:pack({M,V,U_kJ}),DU:pack(s),canonical,normalized});
  }
  const phase=[];
  for(const q of [{mode:'PQ',args:[350000,0]},{mode:'PQ',args:[350000,1]},{mode:'PQ',args:[350000,.4]},{mode:'PT',args:[350000,250]},{mode:'PT',args:[350000,300]},{mode:'SAT',args:[350000,0]}]){const c=a.evaluate(q),s=b.evaluate(q);equal(pack(c),pack(s),'phase controls exact');phase.push({request:q,state:pack(s)});}
  const nativeComparisons=[];
  for(const row of candidate.rows){const n=native.rows.find(r=>r.request.id===row.id).base.PH.values,s=row.base.state;const diff={p:s.p-n.p,h:s.h-n.h,T:s.T-n.T};ok(Math.abs(diff.p)<10&&Math.abs(diff.h)<50&&Math.abs(diff.T)<.01,'original standalone native/browser limits');nativeComparisons.push({id:row.id,native:n,browser:s,diff,reference:'unchanged archived B4C native actual execution; independent DT/reference qualification remains inherited'});}
  return {passed:true,control,candidate,recovery,phase,nativeComparisons,originalScientificBudgets:{canonical:{p:.1,h:.1,T:1e-4},standaloneStrict:{p:10,h:50,T:.01},normalizedMassEnergy:1e-11,independentReferenceResolution:{p:1e-5,energy:1e-8}},noNewIndependentReferenceResolutionClaim:true};
 }finally{a.dispose();b.dispose();}
}
export async function c1(loadControl,loadCandidate,engine,fixture){
 const text=async p=>await(await fetch(new URL(p,import.meta.url))).text();
 const mod={exports:{}};new Function('module','exports',await text('../../../engine.js'))(mod,mod.exports);const guard=mod.exports.createEngine(await read('../../../properties.json'));
 const a=await loadControl('candidateB'),b=await loadCandidate('candidateB'),ca=createAdapter(a,guard),cb=createAdapter(b,guard),rows=[];
 try{
  const failures=(await read('../browser_eos_b5/evidence/original-failures.json')).rows.filter(r=>r.runtime===engine),originalC1=await read(`./evidence/c1-original-${engine}-subset.json`);
  const decode=v=>{const d=new DataView(new ArrayBuffer(8));d.setBigUint64(0,BigInt('0x'+v));return d.getFloat64(0);};
  for(const f of failures){const x=Object.fromEntries(Object.entries(f.fixedInput.bits).map(([k,v])=>[k,decode(v)]));
   const q={mode:'DU',args:[x.rho,x.u]},controlRaw=pack(a.evaluate(q)),raw=pack(b.evaluate(q));equal(raw,controlRaw,'seven DU bits');
   let controlError,error,state;try{ca.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){controlError=errorJSON(e);}try{state=cb.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){error=errorJSON(e);}
   ok(!state&&error&&error.faultKind==='solver','seven remain failed');equal(error,controlError,'C1 classification exact');equal(error,originalC1.rows.find(r=>r.key===f.fixedKey).error,'historical C1 diagnostic unchanged');
   equal(pack(b.evaluate({mode:'PH',args:f.originalPHInput})),pack(a.evaluate({mode:'PH',args:f.originalPHInput})),'originating PH exact');rows.push({key:f.fixedKey,input:f.fixedInput,raw,error});
  }
  ok(rows.length===7,'original seven count');
  const hazards=(await read('../browser_eos_b5/evidence/fixed-inputs.json')).filter(r=>['webkit-ledger-69','webkit-ledger-76'].includes(r.key)),falseAcceptance=[];
  for(const f of hazards){const x=f.input.values,raw=pack(b.evaluate({mode:'DU',args:[x.rho,x.u]}));equal(raw,pack(a.evaluate({mode:'DU',args:[x.rho,x.u]})),'hazard raw unchanged');const state=pack(cb.stateMVU(x.M,x.V,x.U_kJ,35));equal(state,pack(ca.stateMVU(x.M,x.V,x.U_kJ,35)),'hazard state unchanged');falseAcceptance.push({key:f.key,raw,state,qualificationBlocker:true,certified:false});}
  // Harness-only forced dispatch: the requested C1 DU call encounters a REAL
  // rejected PT operation. Label the dispatch injection; never claim it is DU physics.
  const injected=createAdapter({evaluate(q){if(q.mode==='DU')return b.evaluate(fixture.request);return b.evaluate(q);}},guard);
  const x=Object.fromEntries(Object.entries(failures[0].fixedInput.bits).map(([k,v])=>[k,decode(v)]));
  function ptFailure(){let e;try{injected.stateMVU(x.M,x.V,x.U_kJ,35);}catch(z){e=z;}ok(e?.faultKind==='solver'&&e.evidence.propertyFailure.reason==='inverse-recovery-failure','PT C1 fail closed');ok(e.evidence.propertyFailure.physicalTrajectoryExit==='unproved'&&e.evidence.propertyFailure.rawCoordinates===null,'no fabricated raw state');return e;}
  function boundaryFailure(){try{cb.stateMVU(x.M,x.V,x.U_kJ,35);}catch(e){return e;}throw Error('boundary expected');}
  const ptError=errorJSON(ptFailure());
  const names=['thermodynamics.cjs','coupled-model.cjs','coupled-implicit.cjs','failure-contract.cjs','conservation.cjs','hydraulics.cjs','linear.cjs','nonlinear.cjs','phase-events.cjs','thermal.cjs','time-control.cjs','transport.cjs','trbdf2.cjs'];
  // Exact dependency names come from B6's extraction receipt, not guessed aliases.
  const manifest=await read('./evidence/c1-harness-provenance.json'),sources={},controlSources={};
  for(const name of manifest.candidateFiles)sources[name]=await text('../browser_eos_b5b_c1/a2/'+name);
  for(const name of manifest.controlFiles)controlSources[name]=await text('../browser_eos_backend/accepted/'+name);
  const am={exports:{}};new Function('module','exports',await text('./a2-subset.cjs'))(am,am.exports);
  const a2=[];for(const [label,realFailure]of [['original-boundary',boundaryFailure],['actual-PT-dispatch-injection',ptFailure]]){
   a2.push({label,result:am.exports.runA2({sources,controlSources,engine:cb,tableEngine:guard,realFailure})});
  }
  return {passed:true,rows,falseAcceptance,ptError,ptDispatchInjection:true,actualRejectedRequest:fixture.request,nativeDetailsFabricated:false,a2};
 }finally{a.dispose();b.dispose();}
}
