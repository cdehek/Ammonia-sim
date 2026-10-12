'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const data=require('../../properties.json'),{createEngine}=require('../../engine');
const {createPchip,createTemperatureEngine,createSaturationCoupledModel}=require('./saturation-temperature.cjs');
const output=process.argv[2],root=path.resolve(__dirname,'../..');
assert.match(process.version,/^v22\./);assert.ok(output&&!path.resolve(output).startsWith(root+path.sep));
const before=JSON.stringify(data),base=createEngine(data),candidate=createTemperatureEngine(base,data,'pchip-log-pressure'),curve=createPchip(data);
assert.equal(createTemperatureEngine(base,data),base);assert.equal(createTemperatureEngine(base,data,'linear'),base);
assert.throws(()=>createTemperatureEngine(base,data,'unknown'));assert.equal(candidate.solve,undefined);
const report={runtime:process.version,method:'pchip-log-pressure',saturation:[],states:[],knots:curve.knots,unsupported:[],checks:[]};
const samePhysical=(a,b)=>{const x={...a},y={...b};delete x.T;delete y.T;assert.deepEqual(x,y);};
for(let i=0;i<data.p.length;i++){
  const p=data.p[i],a=candidate.sat(p);assert.equal(a.T,data.sat[i][0]);samePhysical(a,base.sat(p));
  assert.equal(candidate.satP(a.T),p);
  if(i===data.p.length-1)continue;
  const lo=Math.log(p),width=Math.log(data.p[i+1])-lo;let previous=-Infinity;
  for(let j=0;j<=32;j++){
    const q=j===0?p:j===32?data.p[i+1]:Math.exp(lo+width*j/32),t=curve.evaluate(q),a=base.sat(q),b=candidate.sat(q);
    assert.ok(b.T>=data.sat[i][0]-1e-12&&b.T<=data.sat[i+1][0]+1e-12&&b.T>=previous);
    assert.ok(t.derivativeLogPressure>0);samePhysical(a,b);previous=b.T;
    assert.ok(Math.abs(Math.log(candidate.satP(b.T)/q))<1e-13);
    report.saturation.push({p:q,baseline:a,candidate:b,derivativeLogPressure:t.derivativeLogPressure});
  }
  if(i>0){const p=data.p[i],left=curve.evaluate(p*(1-1e-10)),right=curve.evaluate(p*(1+1e-10));
    assert.ok(Math.abs(left.derivativeLogPressure-right.derivativeLogPressure)<1e-6);}
}
for(const p of [NaN,Infinity,0,data.p[0]*(1-1e-12),data.p.at(-1)*(1+1e-12)])assert.throws(()=>candidate.sat(p),e=>e.faultKind==='domain');
for(const T of [NaN,Infinity,data.sat[0][0]-1e-12,data.sat.at(-1)[0]+1e-12])assert.throws(()=>candidate.satP(T),e=>e.faultKind==='domain');
report.checks.push('Exact knots, dense interval monotonicity/no overshoot, positive slopes, C1 knots, inverse saturation and strict domain edges.');
const pressures=data.p.slice(0,-1).filter((_,i)=>i%4===0).flatMap(p=>[p,Math.sqrt(p*data.p[data.p.indexOf(p)+1])]);
pressures.push(35,3.5,3.65);
for(const p of pressures){
  for(const quality of [0,.01,.5,.99,1]){
    const a=base.statePX(p,quality),b=candidate.statePX(p,quality);samePhysical(a,b);assert.equal(b.T,candidate.sat(p).T);
    const ap=base.ph(p,a.h),bp=candidate.ph(p,a.h);samePhysical(ap,bp);assert.equal(bp.T,candidate.sat(p).T);
    report.states.push({kind:'two-phase',p,h:a.h,quality,baseline:ap,candidate:bp});
  }
  for(const kind of ['liquid','vapor'])for(const offset of (kind==='liquid'?[.001,.1,1,5,15,30]:[.001,.1,1,5,15,75,150,250])){
    let a;
    try{a=base.statePT(p,base.sat(p).T+(kind==='liquid'?-offset:offset),kind);}
    catch(e){assert.throws(()=>candidate.statePT(p,candidate.sat(p).T+(kind==='liquid'?-offset:offset),kind));report.unsupported.push({p,kind,offset,message:e.message});continue;}
    const targetT=candidate.sat(p).T+(kind==='liquid'?-offset:offset),b=candidate.statePT(p,targetT,kind);
    // Offset arithmetic can move the last bit; full PH and MUV non-T states
    // must nevertheless be exactly unchanged, without alternate inversions.
    for(const key of ['h','s','rho'])assert.ok(Math.abs(b[key]-a[key])<1e-10*Math.max(1,Math.abs(a[key])));
    assert.equal(b.T,targetT);assert.equal(b.phase,a.phase);
    const ap=base.ph(p,a.h),bp=candidate.ph(p,a.h),as=base.ps(p,a.s),bs=candidate.ps(p,a.s);
    samePhysical(ap,bp);samePhysical(as,bs);
    assert.ok(Math.abs(bp.T-ap.T-(candidate.sat(p).T-base.sat(p).T))<1e-12);
    const V=.003/5,M=ap.rho*V,U=M*ap.h-100*p*V;let am,bm;
    try{am=base.stateMVU(M,V,U,p);}catch(e){assert.throws(()=>candidate.stateMVU(M,V,U,p));report.unsupported.push({p,kind,offset,path:'native-MUV',message:e.message});}
    if(am){bm=candidate.stateMVU(M,V,U,p);samePhysical(am,bm);
      assert.ok(Math.abs(am.energyResidual)<1e-7&&Math.abs(am.densityResidual)<1e-7);
      assert.ok(Math.abs(bm.T-bp.T)<1e-4&&Math.abs(bm.h-bp.h)<1e-4&&Math.abs(bm.p-bp.p)<1e-6);}
    report.states.push({kind,p,h:a.h,offset,baseline:ap,candidate:bp,baselineRecovery:am,candidateRecovery:bm});
  }
}
for(const n of [5,9]){
  const m=createSaturationCoupledModel(base,data),a=m.create({sectionCount:n}),original=require('./coupled-model.cjs').createCoupledModel(base),b=original.create({sectionCount:n});
  assert.deepEqual(a,b);assert.deepEqual(m.record(a),original.record(b));
}
assert.equal(JSON.stringify(data),before);report.sampleHash=crypto.createHash('sha256').update(before).digest('hex');
report.checks.push('PH/PS/PX/PT/MUV temperature anchor consistency in supported liquid/vapor/two-phase states; identical non-T fields, inversions, phase definitions and default initial states.');
report.passed=true;fs.writeFileSync(output,JSON.stringify(report)+'\n');console.log(JSON.stringify({passed:true,saturationSamples:report.saturation.length,stateSamples:report.states.length,unsupported:report.unsupported.length}));
