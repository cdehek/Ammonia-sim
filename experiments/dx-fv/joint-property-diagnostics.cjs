'use strict';
// Observational property tests and a short immutable accepted-source replay.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),Module=require('node:module'),crypto=require('node:crypto');
const {createEngine}=require('../../engine'),data=require('../../properties.json');
const {createTemperatureEngine}=require('./saturation-temperature.cjs');
const Model=require('./coupled-model.cjs');
const [mode,input,output]=process.argv.slice(2),root=path.resolve(__dirname,'../..');
assert.match(process.version,/^v22\./);assert.ok(['properties','legacy','conditioning'].includes(mode));
assert.ok(!path.resolve(output).startsWith(root+path.sep));
const base=createEngine(data),candidate=createTemperatureEngine(base,data,'pchip-log-pressure'),before=JSON.stringify(data);
const report={diagnosticOnly:true,runtime:process.version,mode,passed:false};
function capture(fn){try{return {success:true,state:fn()};}catch(e){return {success:false,kind:e.faultKind||null,message:e.message};}}
if(mode==='conditioning'){
  const rows=JSON.parse(fs.readFileSync(input,'utf8')).points;
  report.points=['liquid-p0.3029893712344606-sc1.0','liquid-p1.0-sc0.1','saved-five-linear-0'].map(name=>{
    const row=rows.find(r=>r.name===name),p=row.p,out={name,p,derivatives:[]};
    for(const [label,e] of [['original',base],['pchip',candidate]]){
      const T=e.ph(p,row.h).T;
      for(const delta of [1e-6,3e-7]){
        const a=e.statePT(p-delta,T,'liquid'),b=e.statePT(p+delta,T,'liquid');
        out.derivatives.push({interpolation:label,deltaBar:delta,T,
          rhoPressureSlopeAtFixedTKgM3Bar:(b.rho-a.rho)/(2*delta),hPressureSlopeAtFixedTKJkgBar:(b.h-a.h)/(2*delta)});
      }
    }
    return out;
  });
}else if(mode==='properties'){
  const points=JSON.parse(fs.readFileSync(input,'utf8')).points;
  report.points=points.map(point=>{
    const a=capture(()=>base.ph(point.p,point.h)),b=capture(()=>candidate.ph(point.p,point.h));
    assert.equal(a.success,b.success);
    if(!a.success)return {...point,originalPH:a,candidatePH:b};
    const withoutT=v=>{const out={...v};delete out.T;return out;};assert.deepEqual(withoutT(a.state),withoutT(b.state));
    const V=.003/5,M=a.state.rho*V,U=M*a.state.h-100*point.p*V;
    const am=capture(()=>base.stateMVU(M,V,U,point.p)),bm=capture(()=>candidate.stateMVU(M,V,U,point.p));
    if(am.success&&bm.success)assert.deepEqual(withoutT(am.state),withoutT(bm.state));
    const me=point.eos.rho*V,ue=me*point.eos.u;
    return {...point,originalPH:a,candidatePH:b,tableInventory:{massKg:M,internalEnergyKJ:U,volumeM3:V},
      originalRecovery:am,candidateRecovery:bm,
      EOSInventoryTableRecovery:capture(()=>base.stateMVU(me,V,ue,point.p)),
      originalSaturation:base.sat(point.p),candidateSaturation:candidate.sat(point.p)};
  });
}else{
  const e=path.resolve(input),reference=JSON.parse(fs.readFileSync(path.join(e,'liquid-five-linear.json'),'utf8')).run;
  function compiled(filename,source,overrides={}){
    const full=path.join(__dirname,filename),m=new Module(full,module);m.filename=full;m.paths=module.paths;
    const normal=m.require.bind(m);m.require=id=>overrides[id]||normal(id);m._compile(source,full);return m.exports;
  }
  const modelSource=fs.readFileSync(path.join(e,'legacy-model-source.cjs'),'utf8'),implicitSource=fs.readFileSync(path.join(e,'legacy-implicit-source.cjs'),'utf8');
  const legacy=compiled('coupled-model.cjs',modelSource,{'./coupled-implicit.cjs':compiled('coupled-implicit.cjs',implicitSource)});
  const m=legacy.createCoupledModel(base,reference.settings),s=m.create(reference.config),initial=m.record(s),rows=[];
  assert.deepEqual(initial,reference.initial);
  for(const time of [.001,.01,.05,.1])rows.push(m.advance(s,time-s.seconds));
  assert.deepEqual(rows,reference.rows);
  report.acceptedSHA='be9eb35a4ddf5098e685182f8104685127c6a6ee';report.legacyExactlyReproducesLiquidTrajectory=true;
  report.initial=initial;report.rows=rows;
  const blob=source=>crypto.createHash('sha1').update('blob '+Buffer.byteLength(source)+'\0'+source).digest('hex');
  report.gitBlobs={model:blob(modelSource),implicit:blob(implicitSource)};
  report.currentModelDifferent=fs.readFileSync(path.join(__dirname,'coupled-model.cjs'),'utf8')!==modelSource;
  assert.equal(createTemperatureEngine(base,data,'linear'),base);
}
assert.equal(JSON.stringify(data),before);report.passed=true;
fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({passed:true,mode,points:report.points?.length,legacyExactlyReproducesLiquidTrajectory:report.legacyExactlyReproducesLiquidTrajectory}));
