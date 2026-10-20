import fs from'node:fs';import zlib from'node:zlib';import{createHash}from'node:crypto';
import{same,exact,assert,auditRecord}from'../browser_eos_b9/values.mjs';import{loader}from'./control-bundle.mjs';
const E=new URL('./evidence/',import.meta.url);import{readReceipt}from'./receipts.mjs';export const read=readReceipt;
const digest=x=>createHash('sha256').update(JSON.stringify(exact(x))).digest('hex');
const [left,right]=process.argv.slice(2);if(!left||!right)throw Error('supply receipt names');
const a=read(left),b=read(right),builds=JSON.parse(fs.readFileSync(new URL('build-manifest.json',E))).builds,sources={};
for(const [key,rows]of [['left',a],['right',b]]){const h=rows.find(r=>r.type==='header');if(h.variant.includes('candidate'))assert(h.buildSHA256,'candidate source receipt required');if(h.buildSHA256)assert(h.buildSHA256===builds[h.variant].sha256,'source build mismatch');sources[key]={variant:h.variant,sha256:h.buildSHA256||builds[h.variant].sha256};}
const ca=a.filter(r=>r.type==='checkpoint'),cb=b.filter(r=>r.type==='checkpoint');assert(ca.length===cb.length,'checkpoint count');
for(let i=0;i<ca.length;i++){
 assert(same(ca[i].seconds,cb[i].seconds),'clock');assert(same(ca[i].science,cb[i].science),'state/record');assert(ca[i].scienceHash===cb[i].scienceHash,'science hash');assert(ca[i].attemptsHash===cb[i].attemptsHash,'attempt hash');assert(digest(ca[i].science)===ca[i].scienceHash,'rehash science');auditRecord(ca[i].science.record);auditRecord(cb[i].science.record);
}
const restore=rows=>{const x=rows.find(r=>r.type==='attempts').attempts;for(const a of x)for(const e of a.events)if(e.type==='iteration'&&!Object.hasOwn(e,'context'))e.context=undefined;return x;};
const attempts=restore(a);assert(same(attempts,restore(b)),'full attempts');assert(digest(attempts)===ca.at(-1).attemptsHash,'attempt reconstruction');
const matrices=[];let active;for(const a of attempts)for(const e of a.events){if(e.type==='iteration'&&e.status==='active')active={residual:e.residual,j:Array.from({length:21},()=>Array(21))};if(e.type==='derivative'&&e.outcome==='used'){assert(active,'base');for(let i=0;i<21;i++)active.j[i][e.column]=(e.residual[i]-active.residual[i])/e.step;if(e.column===20)matrices.push(digest(active.j));}}
const da=a.find(r=>r.type==='diagnostics'),db=b.find(r=>r.type==='diagnostics');let diagnostics=false,conservation=null;
if(da.matrices.length&&db.matrices.length){
 for(const key of ['matrices','captures','examples','commits','temporals','controllers'])assert(same(da[key],db[key]),'scientific diagnostic '+key);
 assert(same(matrices,da.matrices),'actual matrices vs independent derivative reconstruction');diagnostics=true;
 const load=loader(),engine=load('table-only.cjs').createTableEngine(),thermo=load('thermodynamics.cjs').createThermodynamics(engine),model=load('coupled-model.cjs').createCoupledModel(engine,{trace:true,timestepGrowth:'failure-aware'}),init=ca[0].science.state,max={mass:0,fluid:0,thermal:0,combined:0,sectionMass:0,sectionEnergy:0,node:0};
 for(const c of da.commits){
  const r=model.record({...structuredClone(init),cells:c.cells,energies:c.energies,ledger:c.ledger,seconds:c.seconds,lastResidual:c.error});const v=auditRecord(r);
  for(const k of ['mass','fluid','thermal','combined'])max[k]=Math.max(max[k],Math.abs(v[k]));for(const s of v.sections){max.sectionMass=Math.max(max.sectionMass,Math.abs(s.massKg));max.sectionEnergy=Math.max(max.sectionEnergy,Math.abs(s.energyKJ));}for(const n of v.nodes)max.node=Math.max(max.node,Math.abs(n.independent),Math.abs(n.residual));
  const f=init.spec.fluid,states=[thermo.ph(f.inlet.p,f.inlet.h),...c.states,thermo.ph(f.outlet.p,f.outlet.h)];for(let i=0;i<c.endpoint.faces.length;i++){const x=c.endpoint.faces[i];assert(Math.abs(x.energyKW-x.massKgS*(x.massKgS>=0?states[i].h:states[i+1].h))<1e-10,'signed donor energy');}
 }
 conservation={passed:true,acceptedHalfStates:da.commits.length,max,thresholds:{massKg:1e-8,energyKJ:1e-6},allElevenThermalNodesAndSignedDonors:true};
}
const header=a.find(r=>r.type==='header');let historical=[];
if(header.schedule==='original'||header.fixture==='warm'){
 const path=new URL('../browser_eos_b14/evidence/canonical-'+header.fixture+(header.schedule==='original'?'-r1':'-'+header.schedule)+'.jsonl.gz',import.meta.url),old=zlib.gunzipSync(fs.readFileSync(path)).toString().trim().split('\n').map(JSON.parse).filter(r=>r.type==='checkpoint');
 for(let i=0;i<ca.length;i++){assert(ca[i].scienceHash===old[i].scienceHash&&ca[i].attemptsHash===old[i].attemptsHash,'B14 retained scientific baseline');historical.push(ca[i].seconds);}
 if(header.fixture==='warm'&&header.schedule==='original'){
  const e=ca.at(-1).science.state.events[0],oldEvent=JSON.parse(fs.readFileSync(new URL('../browser_eos_b14/evidence/transition-bracket.json',import.meta.url))).event;assert(same(e,oldEvent),'B14 transition event exact');
 }
}
const result={passed:true,left,right,sources,fixture:header.fixture,schedule:header.schedule,checkpoints:ca.map(r=>({seconds:r.seconds,scienceHash:r.scienceHash,attemptsHash:r.attemptsHash})),historicalB14Checkpoints:historical,allScientificObjectsBitExact:true,originalAttemptsBitExact:true,independentFullJacobianReconstructions:matrices.length,actualMatricesAndCorrectionsCompared:diagnostics?da.captures.linear.length:0,completeResidualObjectsCompared:diagnostics?da.captures.residual.length:0,acceptedHalfStepsAndTemporalDecisionsCompared:diagnostics,conservation,counts:diagnostics?{control:da.pressureCounts,candidate:db.pressureCounts}:null};
fs.writeFileSync(new URL('equivalence-'+left+'--'+right+'.json',E),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({...result,checkpoints:result.checkpoints.length}));
