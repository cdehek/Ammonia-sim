'use strict';
// Explicit research adapter only. No production engine/table or solver changes.
const {createCoupledModel}=require('./coupled-model.cjs');
function domain(message){throw Object.assign(Error(message),{faultKind:'domain'});}
function createPchip(data){
  const pressures=[...data.p],x=pressures.map(Math.log),y=data.sat.map(r=>r[0]),n=x.length;
  if(n<3||y.length!==n)throw Error('At least three aligned saturation knots required.');
  const h=[],d=[];
  for(let i=0;i<n-1;i++){
    h.push(x[i+1]-x[i]);d.push((y[i+1]-y[i])/h[i]);
    if(!(h[i]>0&&d[i]>0&&Number.isFinite(d[i])))throw Error('Strictly increasing finite saturation coordinates required.');
  }
  // Fritsch-Butland weighted harmonic interior slopes; shape-limited one-sided
  // three-point endpoint slopes. Same mathematical PCHIP rule as SciPy.
  const m=Array(n);
  for(let i=1;i<n-1;i++){
    const w1=2*h[i]+h[i-1],w2=h[i]+2*h[i-1];
    m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i]);
  }
  function edge(a,b,da,db){let z=((2*a+b)*da-a*db)/(a+b);
    if(Math.sign(z)!==Math.sign(da))z=0;
    else if(Math.sign(da)!==Math.sign(db)&&Math.abs(z)>3*Math.abs(da))z=3*da;
    return z;
  }
  m[0]=edge(h[0],h[1],d[0],d[1]);m[n-1]=edge(h[n-2],h[n-3],d[n-2],d[n-3]);
  function interval(p){
    if(!Number.isFinite(p)||p<pressures[0]||p>pressures[n-1])domain('Pressure outside immutable saturation table; extrapolation forbidden.');
    let lo=0,hi=n-1;while(hi-lo>1){const k=(lo+hi)>>1;if(pressures[k]<=p)lo=k;else hi=k;}
    return p===pressures[n-1]?n-2:lo;
  }
  function evaluate(p){
    const i=interval(p),w=(Math.log(p)-x[i])/h[i],w2=w*w,w3=w2*w;
    const temperatureC=p===pressures[i]?y[i]:p===pressures[i+1]?y[i+1]:
      (2*w3-3*w2+1)*y[i]+(w3-2*w2+w)*h[i]*m[i]+(-2*w3+3*w2)*y[i+1]+(w3-w2)*h[i]*m[i+1];
    const derivativeLogPressure=(6*w2-6*w)*y[i]/h[i]+(3*w2-4*w+1)*m[i]+(-6*w2+6*w)*y[i+1]/h[i]+(3*w2-2*w)*m[i+1];
    return {temperatureC,linearC:y[i]+(y[i+1]-y[i])*w,derivativeLogPressure,interval:i};
  }
  function pressure(T){
    if(!Number.isFinite(T)||T<y[0]||T>y[n-1])domain('Temperature outside immutable saturation table; extrapolation forbidden.');
    if(T===y[0])return pressures[0];if(T===y[n-1])return pressures[n-1];
    let lo=0,hi=n-1;while(hi-lo>1){const k=(lo+hi)>>1;if(y[k]<=T)lo=k;else hi=k;}
    if(T===y[lo])return pressures[lo];
    let left=x[lo],right=x[hi];for(let j=0;j<60;j++){const mid=(left+right)/2;if(evaluate(Math.exp(mid)).temperatureC<T)left=mid;else right=mid;}
    return Math.exp((left+right)/2);
  }
  return {evaluate,pressure,knots:pressures.map((p,i)=>({p,temperatureC:y[i],slope:m[i]}))};
}
function createTemperatureEngine(base,data,mode='linear'){
  if(mode==='linear')return base; // Default is the original engine object itself.
  if(mode!=='pchip-log-pressure')throw Error('Unsupported isolated saturation-temperature selection.');
  const curve=createPchip(data);
  function lift(state){const t=curve.evaluate(state.p);
    return {...state,T:state.x!==null&&state.x!==undefined?t.temperatureC:state.T+(t.temperatureC-t.linearC)};
  }
  const adapter={sat:p=>{const t=curve.evaluate(p);return {...base.sat(p),T:t.temperatureC};},
    satP:T=>curve.pressure(T),
    statePX:(p,q)=>{curve.evaluate(p);return lift(base.statePX(p,q));},
    ph:(p,h)=>{curve.evaluate(p);return lift(base.ph(p,h));},
    ps:(p,s)=>{curve.evaluate(p);return lift(base.ps(p,s));},
    stateDU:(...args)=>lift(base.stateDU(...args)),stateMVU:(...args)=>lift(base.stateMVU(...args)),
    statePT:(p,T,kind)=>{const t=curve.evaluate(p);if(!Number.isFinite(T))domain('Finite temperature required.');
      // Shift the branch's saturation anchor, retaining the native offset grid,
      // inversion and phase rule. Return exactly the requested temperature.
      return {...base.statePT(p,t.linearC+(T-t.temperatureC),kind),T};}
  };
  // Application-cycle closures capture their original private interpolation.
  // They are deliberately unavailable in this isolated coupled adapter.
  return Object.freeze(adapter);
}
function createSaturationCoupledModel(engine,data,options={},observer=null){
  const {saturationTemperature='linear',...solverOptions}=options;
  return createCoupledModel(createTemperatureEngine(engine,data,saturationTemperature),solverOptions,observer);
}
module.exports={createPchip,createTemperatureEngine,createSaturationCoupledModel};
