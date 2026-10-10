'use strict';
// Stage 2A: five cells only. Historical fluid and Stage 1 thermal factories stay untouched.
const C = require('./conservation.cjs');
const {connectionFlow} = require('./hydraulics.cjs');
const {createThermodynamics} = require('./thermodynamics.cjs');
const {fixture} = require('./spatial-fixtures.cjs');
const {createThermalConfig} = require('./thermal-geometry.cjs');
const {normalize:normalizeThermal, ANCHOR_K} = require('./thermal-network.cjs');
const Time = require('./time-control.cjs');
const {coupledNewton} = require('./coupled-implicit.cjs');
const clone = x => JSON.parse(JSON.stringify(x));
const sum = a => a.reduce((s,v) => s+v,0);
const positive = (v,label) => { if (!Number.isFinite(v) || v<=0) throw Error(`Positive ${label} required.`); };
const fields = (o,allowed) => { if (!o || typeof o!=='object' || Array.isArray(o) || Object.keys(o).some(k=>!allowed.includes(k))) throw Error('Unsupported coupled configuration/patch field.'); };

function createCoupledModel(engine, options={}, observeAttempt=null) {
  if(observeAttempt!==null&&typeof observeAttempt!=='function')throw Error('Optional diagnostic observer must be a function.');
  fields(options,['method','adaptive','maxStep','minStep','relativeTolerance','massAbsoluteKg','energyAbsoluteKJ','pressureAbsoluteBar','enthalpyAbsoluteKJkg','eventStepSeconds','temperatureAbsoluteK','temperatureScaleK','nonlinearTolerance','thermalResidualK','maxIterations','maxAttempts','trace']);
  const settings = {...Time.adaptiveDefaults,temperatureAbsoluteK:1e-4,temperatureScaleK:50,
    nonlinearTolerance:1e-11,thermalResidualK:1e-12,maxIterations:30,maxAttempts:100000,trace:false,...options};
  for (const key of ['maxStep','minStep','relativeTolerance','massAbsoluteKg','energyAbsoluteKJ','pressureAbsoluteBar','enthalpyAbsoluteKJkg','eventStepSeconds','temperatureAbsoluteK','temperatureScaleK','nonlinearTolerance','thermalResidualK']) positive(settings[key],key);
  if (settings.maxStep<settings.minStep || !['tr-bdf2','backward-euler'].includes(settings.method) || typeof settings.adaptive!=='boolean' || typeof settings.trace!=='boolean' || !Number.isInteger(settings.maxIterations) || settings.maxIterations<1 || !Number.isInteger(settings.maxAttempts) || settings.maxAttempts<1) throw Error('Invalid coupled numerical settings.');
  const thermo = createThermodynamics(engine), order = settings.method==='tr-bdf2' ? 2 : 1;
  function fluidCall(fn, section, stage) {
    try { return fn(); } catch (cause) {
      cause.evidence = {...cause.evidence,source:'refrigerant',section,stage}; throw cause;
    }
  }
  function coordinates(c,i) { return fluidCall(()=>thermo.ph(c.pressureGuess,(c.internalEnergyKJ+100*c.pressureGuess*c.volumeM3)/c.massKg),i,'coordinates'); }
  function recover(c,i) { return fluidCall(()=>thermo.recover(c),i,'canonical-recovery'); }
  function temperatures(spec, energies, stage) {
    return energies.map((e,i) => {
      const t = ANCHOR_K+e/spec.thermal.nodes[i].capacityKJK;
      if (!Number.isFinite(t) || t<spec.thermal.domainK[0] || t>spec.thermal.domainK[1]) throw Object.assign(Error('Coupled thermal state outside supported domain.'), {
        faultKind:'domain',evidence:{source:'thermal',node:spec.thermal.nodes[i].id,stage,temperatureK:t,domainK:spec.thermal.domainK}
      });
      return t;
    });
  }
  function patchSpec(spec, patch) {
    fields(patch,['inlet','outlet','airLoadKW']);
    const next = clone(spec);
    for (const key of ['inlet','outlet']) if (patch[key]!==undefined) {
      fields(patch[key],['p','h']); thermo.ph(patch[key].p,patch[key].h); next.fluid[key]=clone(patch[key]);
    }
    if (patch.airLoadKW!==undefined) {
      if (!Number.isFinite(patch.airLoadKW)) throw Error('Finite external air load required.');
      next.thermal.loadsKW.air=patch.airLoadKW;
    }
    return next;
  }
  function create(config={}) {
    fields(config,['sectionCount','initial','inlet','outlet','thermal','refrigerantConductanceKWK','sealed','schedule']);
    if ((config.sectionCount??5)!==5) throw Error('Stage 2A permits five refrigerant sections only.');
    if (config.sealed!==undefined && typeof config.sealed!=='boolean') throw Error('Boolean sealed fixture flag required.');
    const fluid = fixture(5,{totalHeatKW:0});
    if (config.initial!==undefined) fluid.initial=clone(config.initial);
    if (!Array.isArray(fluid.initial) || fluid.initial.length!==5) throw Error('Five initial PH states required.');
    for (const key of ['inlet','outlet']) if (config[key]!==undefined) { fields(config[key],['p','h']); fluid[key]=clone(config[key]); }
    if (config.sealed) fluid.connections=fluid.connections.map(f=>({...f,closed:true}));
    // Only finite-air topology is authorized; geometry/material closures stay Stage 1 defaults.
    const input = config.thermal||{};
    fields(input,['tubeProfileK','finProfileK','airInitialK','airLoadKW','energyReferenceK','domainK']);
    const thermal = normalizeThermal(createThermalConfig({sectionCount:5,tubeProfileK:273.15,finProfileK:273.15,airInitialK:278.15,airLoadKW:1,...input}));
    const conductance = config.refrigerantConductanceKWK??.60;
    if (![0,.60].includes(conductance)) throw Error('Only approved 0.60 kW/K or zero-exchange verification is supported.');
    const spec = {fluid,thermal,conductancesKWK:fluid.volumeFractions.map(v=>v*conductance),
      conductanceDescription:'Effective uncalibrated constant tube-to-bulk-refrigerant conductance; radial/film resistance unresolved; no additional wall resistance.',schedule:clone(config.schedule||[])};
    if (!Array.isArray(spec.schedule)) throw Error('Array schedule required.');
    let previous = 0;
    for (const event of spec.schedule) {
      fields(event,['seconds','patch']);
      if (!Number.isFinite(event.seconds) || event.seconds<=previous) throw Error('Strictly increasing positive schedule times required.');
      patchSpec(spec,event.patch); previous=event.seconds;
    }
    const cells=fluid.initial.map((v,i)=>{fields(v,['p','h']);return fluidCall(()=>thermo.initialize(v.p,v.h,fluid.totalVolumeM3*fluid.volumeFractions[i]),i,'initial');});
    for (const key of ['inlet','outlet']) thermo.ph(fluid[key].p,fluid[key].h);
    const energies=thermal.nodes.map(n=>n.capacityKJK*(n.initialK-ANCHOR_K));
    temperatures(spec,energies,'initial'); cells.forEach(recover);
    return {model:'isolated-five-section-coupled-dx-stage2a',spec,cells,energies,initialCells:clone(cells),initialEnergies:[...energies],seconds:0,scheduleIndex:0,
      ledger:{faces:fluid.connections.map(()=>({massKg:0,energyKJ:0})),tubeRefrigerantKJ:Array(5).fill(0),thermalLinksKJ:thermal.links.map(()=>0),thermalNodesKJ:energies.map(()=>0),airLoadKJ:0,boundaryMassKg:0,boundaryEnthalpyKJ:0},
      acceptedSteps:0,rejectedSteps:0,accuracyRejectedSteps:0,eventRejectedSteps:0,domainRejectedSteps:0,attemptedResidualEvaluations:0,attemptedIterations:0,attemptedLinearSolves:0,
      nextStepSeconds:settings.maxStep,minAcceptedStepSeconds:null,maxAcceptedStepSeconds:0,lastTimeError:null,lastResidual:null,events:[],boundaryEvents:[],trace:[],rejectionTrace:[],stop:null};
  }
  function evaluate(spec, states, energies) {
    const t=temperatures(spec,energies,'rate'),ix=new Map(spec.thermal.nodes.map((n,i)=>[n.id,i]));
    const nodes=[thermo.ph(spec.fluid.inlet.p,spec.fluid.inlet.h),...states,thermo.ph(spec.fluid.outlet.p,spec.fluid.outlet.h)];
    const faces=spec.fluid.connections.map((f,i)=>{const m=f.closed?0:connectionFlow(nodes[i],nodes[i+1],f);return C.flux(m,m>=0?nodes[i]:nodes[i+1]);});
    const thermalRates=spec.thermal.nodes.map(n=>spec.thermal.loadsKW[n.id]||0);
    const links=spec.thermal.links.map(l=>{
      const from=ix.get(l.from),to=ix.get(l.to),q=l.conductanceKWK*(t[from]-t[to]);
      thermalRates[from]-=q; thermalRates[to]+=q; return q;
    });
    const tubeRefrigerant=states.map((v,i)=>{
      const tube=ix.get(`tube-${i}`),q=spec.conductancesKWK[i]*(t[tube]-(v.T+273.15));
      thermalRates[tube]-=q; return q;
    });
    return {faces,links,tubeRefrigerant,thermalRates,airLoad:spec.thermal.loadsKW.air||0,fluidRates:C.assemble(faces,tubeRefrigerant)};
  }
  function blend(terms) {
    const array = key => terms[0][1][key].map((_,i)=>sum(terms.map(([w,v])=>w*v[key][i])));
    return {faces:terms[0][1].faces.map((_,i)=>({massKgS:sum(terms.map(([w,v])=>w*v.faces[i].massKgS)),energyKW:sum(terms.map(([w,v])=>w*v.faces[i].energyKW))})),
      links:array('links'),tubeRefrigerant:array('tubeRefrigerant'),thermalRates:array('thermalRates'),airLoad:sum(terms.map(([w,v])=>w*v.airLoad))};
  }
  function solveStage(s, dt, known, weight, guess, work) {
    const fluidScales=s.cells.flatMap(c=>[Math.max(.01,c.massKg),Math.max(1,Math.abs(c.internalEnergyKJ))]);
    const variables=s.cells.flatMap((_,section)=>[{kind:'pressure',section},{kind:'enthalpy',section}]).concat(s.spec.thermal.nodes.map(n=>({kind:'thermal-energy',capacityKJK:n.capacityKJK})));
    const initial=guess.states.flatMap(v=>[v.p,v.h]).concat(guess.energies.map((e,i)=>e-s.energies[i]));
    if(work.diagnostics)work.diagnosticContext={startSeconds:s.seconds,stageSeconds:dt,stageWeight:weight,
      labels:s.cells.flatMap((_,i)=>[`refrigerant-${i}:mass`,`refrigerant-${i}:energy`]).concat(s.spec.thermal.nodes.map(n=>n.id+':energy')),
      physicalScales:fluidScales.concat(s.spec.thermal.nodes.map(n=>n.capacityKJK*settings.thermalResidualK/settings.nonlinearTolerance)),
      thermalCapacitiesKJK:s.spec.thermal.nodes.map(n=>n.capacityKJK)};
    // A thermal-column probe leaves PH unchanged. Cache exact PH pairs within
    // this stage only; never reuse properties across changed coordinates/stages.
    const properties=new Map();
    const solved=coupledNewton(x=>{
      const states=s.cells.map((_,i)=>{
        const key=`${x[2*i]}:${x[2*i+1]}`;
        if(!properties.has(key))properties.set(key,fluidCall(()=>thermo.ph(x[2*i],x[2*i+1]),i,'implicit-PH'));
        return properties.get(key);
      });
      const cells=states.map((v,i)=>({...C.inventory(v,s.cells[i].volumeM3),volumeM3:s.cells[i].volumeM3,pressureGuess:v.p}));
      const energies=s.energies.map((e,i)=>e+x[10+i]);
      const endpoint=evaluate(s.spec,states,energies),integratedRate=blend([...known,[weight,endpoint]]),rates=C.assemble(integratedRate.faces,integratedRate.tubeRefrigerant);
      const residual=cells.flatMap((c,i)=>[(c.massKg-s.cells[i].massKg-dt*rates[i].massKgS)/fluidScales[2*i],(c.internalEnergyKJ-s.cells[i].internalEnergyKJ-dt*rates[i].energyKW)/fluidScales[2*i+1]])
        // Nonlinear thermal closure has its own absolute K budget. The adaptive
        // 50 K scale is not a license to leave tiny exchanges unresolved forever.
        .concat(energies.map((_,i)=>(x[10+i]-dt*integratedRate.thermalRates[i])/(s.spec.thermal.nodes[i].capacityKJK*settings.thermalResidualK/settings.nonlinearTolerance)));
      return {residual,states,cells,energies,endpoint,integratedRate};
    },initial,variables,settings,work);
    const recovered=solved.value.cells.map(recover);
    recovered.forEach((v,i)=>{
      const ph=solved.value.states[i];
      if (Math.abs(v.p-ph.p)>1e-6 || Math.abs(v.h-ph.h)>1e-4 || Math.abs(v.T-ph.T)>1e-4) throw Object.assign(Error('Canonical M/U/V recovery disagrees with stage PH coordinates.'),{faultKind:'solver',evidence:{section:i,pressureDifference:v.p-ph.p,enthalpyDifference:v.h-ph.h,temperatureDifference:v.T-ph.T}});
    });
    temperatures(s.spec,solved.value.energies,'stage-acceptance');
    return {...solved.value,error:solved.error};
  }
  function trial(s, dt, work={evaluations:0,iterations:0,linearSolves:0}) {
    positive(dt,'trial interval');
    const previous={states:s.cells.map(coordinates),energies:s.energies};
    s.cells.forEach(recover); const t=temperatures(s.spec,s.energies,'trial-initial');
    // An outward derivative at an exact support boundary has no valid positive
    // interval. Detect it before a tiny residual can fall below Newton tolerance.
    const direction=evaluate(s.spec,previous.states,s.energies).thermalRates;
    const outward=t.findIndex((v,i)=>(v===s.spec.thermal.domainK[0]&&direction[i]<0)||(v===s.spec.thermal.domainK[1]&&direction[i]>0));
    if(outward>=0)throw Object.assign(Error('Thermal trajectory points outward at the supported boundary.'),{faultKind:'domain',evidence:{source:'thermal',node:s.spec.thermal.nodes[outward].id,stage:'initial-direction',temperatureK:t[outward],rateKS:direction[outward]/s.spec.thermal.nodes[outward].capacityKJK}});
    if (order===1) return solveStage(s,dt,[],1,previous,work);
    const initial=evaluate(s.spec,previous.states,s.energies),gamma=2-Math.sqrt(2),a=1/(2*(2-gamma)),b=(1-gamma)/(2-gamma);
    const stage=solveStage(s,gamma*dt,[[.5,initial]],.5,previous,work);
    const end=solveStage(s,dt,[[a,initial],[a,stage.endpoint]],b,stage,work);
    end.error=Math.max(stage.error,end.error); return end;
  }
  function errorEstimate(s, coarse, fine) {
    const fluid=Time.estimate(coarse,fine,{cells:s.cells,states:s.cells.map(coordinates)},order,settings);
    const thermal=Math.max(...fine.energies.map((e,i)=>Math.abs(e-coarse.energies[i])/(2**order-1)/s.spec.thermal.nodes[i].capacityKJK/(settings.temperatureAbsoluteK+settings.relativeTolerance*settings.temperatureScaleK)));
    return Math.max(fluid,thermal);
  }
  function commit(s, piece, dt, start) {
    for (const e of Time.crossings(s.cells.map(coordinates),piece.states,engine.sat)) s.events.push({...e,seconds:start+dt*Math.abs(e.left)/(Math.abs(e.left)+Math.abs(e.right)),bracketStartSeconds:start,bracketEndSeconds:start+dt});
    const r=piece.integratedRate;
    r.faces.forEach((f,i)=>{s.ledger.faces[i].massKg+=dt*f.massKgS;s.ledger.faces[i].energyKJ+=dt*f.energyKW;});
    r.tubeRefrigerant.forEach((q,i)=>{s.ledger.tubeRefrigerantKJ[i]+=dt*q;});
    r.links.forEach((q,i)=>{s.ledger.thermalLinksKJ[i]+=dt*q;});
    r.thermalRates.forEach((q,i)=>{s.ledger.thermalNodesKJ[i]+=dt*q;});
    s.ledger.airLoadKJ+=dt*r.airLoad;
    s.ledger.boundaryMassKg+=dt*(r.faces[0].massKgS-r.faces.at(-1).massKgS);
    s.ledger.boundaryEnthalpyKJ+=dt*(r.faces[0].energyKW-r.faces.at(-1).energyKW);
    s.cells=piece.cells; s.energies=piece.energies; s.acceptedSteps++; s.lastResidual=piece.error;
    s.minAcceptedStepSeconds=s.minAcceptedStepSeconds===null?dt:Math.min(s.minAcceptedStepSeconds,dt);s.maxAcceptedStepSeconds=Math.max(s.maxAcceptedStepSeconds,dt);
  }
  function applyBoundary(s,patch,scheduled) {
    const next=patchSpec(s.spec,patch);
    s.spec=next;s.nextStepSeconds=Math.min(.05,settings.maxStep);
    s.boundaryEvents.push({seconds:s.seconds,scheduled,patch:clone(patch)});
  }
  function domainEvidence(s,dt,cause) {
    const evidence={originalCause:cause.message,nonlinearResidual:cause.nonlinearResidual??null,trial:cause.evidence||cause.domainCause?.evidence||null,confirmed:false};
    // An exact boundary with an outward derivative already establishes that
    // no positive interval is supported. Recheck that proof at the accepted
    // state independently of the retry floor; arbitrary PH probes do not qualify.
    if(cause.evidence?.source==='thermal'&&cause.evidence.stage==='initial-direction') {
      const t=temperatures(s.spec,s.energies,'exact-boundary-confirmation');
      const r=evaluate(s.spec,s.cells.map(coordinates),s.energies);
      const i=s.spec.thermal.nodes.findIndex(n=>n.id===cause.evidence.node);
      if(i>=0&&((t[i]===s.spec.thermal.domainK[0]&&r.thermalRates[i]<0)||(t[i]===s.spec.thermal.domainK[1]&&r.thermalRates[i]>0))) {
        return {...evidence,confirmed:true,source:'thermal',node:s.spec.thermal.nodes[i].id,
          confirmation:'exact-boundary-outward-direction',temperatureK:t[i],rateKS:r.thermalRates[i]/s.spec.thermal.nodes[i].capacityKJK};
      }
    }
    // A branch-aware Newton failure need not encounter an unsupported PH probe.
    // At exhausted small intervals independently test the conserved direction,
    // regardless of the numerical failure label; evidence alone decides domain.
    if (dt>1e-6) return evidence;
    const r=evaluate(s.spec,s.cells.map(coordinates),s.energies),t=temperatures(s.spec,s.energies,'domain-evidence');
    evidence.thermalDirection=t.map((v,i)=>({node:s.spec.thermal.nodes[i].id,temperatureK:v,rateKS:r.thermalRates[i]/s.spec.thermal.nodes[i].capacityKJK}));
    const crossing=evidence.thermalDirection.find(v=>v.temperatureK+dt*v.rateKS<s.spec.thermal.domainK[0] || v.temperatureK+dt*v.rateKS>s.spec.thermal.domainK[1]);
    if (crossing) { evidence.confirmed=true;evidence.source='thermal';evidence.node=crossing.node; }
    evidence.refrigerantDirection=[];
    s.cells.forEach((c,i)=>{
      try { recover({...c,massKg:c.massKg+dt*r.fluidRates[i].massKgS,internalEnergyKJ:c.internalEnergyKJ+dt*r.fluidRates[i].energyKW},i); }
      catch (e) { evidence.refrigerantDirection.push({section:i,kind:e.faultKind||'solver',message:e.message});if(e.faultKind==='domain'){evidence.confirmed=true;evidence.source='refrigerant';evidence.section=i;} }
    });
    return evidence;
  }
  function advance(s,duration) {
    positive(duration,'advance duration');if(s.stop)return record(s);
    const target=s.seconds+duration;if(!Number.isFinite(target)||target<=s.seconds)throw Error('Invalid or unresolved target time.');
    let dt=s.nextStepSeconds,attempts=0;
    while(s.seconds<target) {
      const event=s.spec.schedule[s.scheduleIndex];
      if(event&&event.seconds===s.seconds){applyBoundary(s,event.patch,true);s.scheduleIndex++;dt=s.nextStepSeconds;continue;}
      const boundary=Math.min(target,event?.seconds??Infinity),remaining=boundary-s.seconds;dt=Math.min(dt,remaining);
      if(++attempts>settings.maxAttempts){s.stop={kind:'solver',seconds:s.seconds,message:'Coupled attempt budget exhausted.',evidence:{maxAttempts:settings.maxAttempts}};break;}
      const work={evaluations:0,iterations:0,linearSolves:0};
      if(observeAttempt)work.diagnostics=[];
      const diagnosticStartSeconds=s.seconds,diagnosticTrialSeconds=dt;
      let pieces,error=0,reason=null,diagnosticFailure=null;
      try {
        const coarse=trial(s,dt,work);pieces=[[coarse,dt]];
        if(settings.adaptive){
          const half=trial(s,dt/2,work),fine=trial({...s,cells:half.cells,energies:half.energies},dt/2,work);
          error=errorEstimate(s,coarse,fine);if(!Number.isFinite(error))throw Error('Nonfinite coupled temporal error.');
          pieces=[[half,dt/2],[fine,dt/2]];
          const crossings=[...Time.crossings(s.cells.map(coordinates),half.states,engine.sat),...Time.crossings(half.states,fine.states,engine.sat)];
          if(error>1)reason='accuracy';else if(crossings.length&&dt/2>settings.eventStepSeconds)reason='event';
        }
      } catch(cause) {
        diagnosticFailure={kind:cause.faultKind||'solver',message:cause.message};
        s.rejectedSteps++;if(cause.faultKind==='domain'||cause.domainCause)s.domainRejectedSteps++;
        if(settings.trace)s.rejectionTrace.push({seconds:s.seconds,trialSeconds:dt,kind:cause.faultKind||'solver',message:cause.message,nonlinearResidual:cause.nonlinearResidual??null,evidence:clone(cause.evidence||cause.domainCause||{})});
        const next=dt/2;
        if(next<settings.minStep||s.seconds+next===s.seconds){
          const evidence=domainEvidence(s,dt,cause);
          s.stop={kind:evidence.confirmed?'domain':'solver',seconds:s.seconds,attemptedStepSeconds:dt,message:cause.message,evidence};break;
        }
        dt=next;continue;
      } finally {
        s.attemptedResidualEvaluations+=work.evaluations;s.attemptedIterations+=work.iterations;s.attemptedLinearSolves+=work.linearSolves;
        // Detached diagnostic data cannot change candidates or numerical settings.
        // Observer errors propagate outside the solver rather than becoming probes.
        if(observeAttempt)observeAttempt({startSeconds:diagnosticStartSeconds,trialSeconds:diagnosticTrialSeconds,failure:diagnosticFailure,
          temporalError:error,rejectionReason:reason,evaluations:work.evaluations,iterations:work.iterations,
          linearSolves:work.linearSolves,events:work.diagnostics});
      }
      if(reason){
        s.rejectedSteps++;if(reason==='accuracy')s.accuracyRejectedSteps++;else s.eventRejectedSteps++;
        if(settings.trace)s.rejectionTrace.push({seconds:s.seconds,trialSeconds:dt,kind:reason,error});
        const next=reason==='event'?Math.min(dt/2,2*settings.eventStepSeconds):dt*Time.factor(error,order,false);
        if(next<settings.minStep||s.seconds+next===s.seconds){s.stop={kind:'accuracy',seconds:s.seconds,attemptedStepSeconds:dt,message:'Coupled temporal tolerance cannot be met above minimum step.',evidence:{error,reason}};break;}
        dt=next;continue;
      }
      const start=s.seconds;let offset=0;
      // Prepare both halves against detached ledgers/events. Even an unexpected
      // exception while preparing the second half cannot install the first half.
      const accepted={...s,ledger:clone(s.ledger),events:[...s.events]};
      for(const [piece,h]of pieces){commit(accepted,piece,h,start+offset);offset+=h;}
      Object.assign(s,accepted);
      s.seconds=dt===remaining?boundary:start+dt;s.lastTimeError=error;
      if(settings.trace)s.trace.push({startSeconds:start,endSeconds:s.seconds,trialSeconds:dt,error});
      dt=Math.min(settings.maxStep,settings.adaptive?dt*Time.factor(error,order,true):settings.maxStep);s.nextStepSeconds=dt;
    }
    if(!s.stop){const e=s.spec.schedule[s.scheduleIndex];if(e&&e.seconds===s.seconds){applyBoundary(s,e.patch,true);s.scheduleIndex++;}}
    return record(s);
  }
  function update(s,patch) {if(s.stop)throw Error('Stopped coupled state is frozen.');applyBoundary(s,patch,false);return record(s);}
  function record(s) {
    const sections=s.cells.map(recover),t=temperatures(s.spec,s.energies,'record'),initial=C.totals(s.initialCells),totals=C.totals(s.cells),q=sum(s.ledger.tubeRefrigerantKJ);
    const massResidualKg=totals.massKg-initial.massKg-s.ledger.boundaryMassKg;
    const refrigerantEnergyResidualKJ=totals.internalEnergyKJ-initial.internalEnergyKJ-s.ledger.boundaryEnthalpyKJ-q;
    const thermalChange=sum(s.energies.map((e,i)=>e-s.initialEnergies[i]));
    const thermalEnergyResidualKJ=thermalChange-s.ledger.airLoadKJ+q;
    const sectionResiduals=s.cells.map((c,i)=>({massKg:c.massKg-s.initialCells[i].massKg-s.ledger.faces[i].massKg+s.ledger.faces[i+1].massKg,
      energyKJ:c.internalEnergyKJ-s.initialCells[i].internalEnergyKJ-s.ledger.faces[i].energyKJ+s.ledger.faces[i+1].energyKJ-s.ledger.tubeRefrigerantKJ[i]}));
    const nodes=s.spec.thermal.nodes.map((n,i)=>({id:n.id,capacityKJK:n.capacityKJK,temperatureK:t[i],energyKJ:s.energies[i]+n.capacityKJK*(ANCHOR_K-s.spec.thermal.energyReferenceK),energyChangeKJ:s.energies[i]-s.initialEnergies[i],residualKJ:s.energies[i]-s.initialEnergies[i]-s.ledger.thermalNodesKJ[i]}));
    const current=evaluate(s.spec,s.cells.map(coordinates),s.energies),last=sections.at(-1),diagnostic=v=>({p:v.p,h:v.h,temperatureK:v.T+273.15,phase:v.phase,quality:v.x,wet:v.wet,superheatK:v.superheatK});
    let outlet;
    try {outlet={supported:true,...diagnostic(thermo.ph(s.spec.fluid.outlet.p,current.faces.at(-1).massKgS>=0?last.h:s.spec.fluid.outlet.h))};}
    catch(cause){outlet={supported:false,message:cause.message};}
    return clone({model:s.model,seconds:s.seconds,sectionCount:5,sections,nodes,terminal:diagnostic(last),outlet,totals,sectionResiduals,
      massResidualKg,refrigerantEnergyResidualKJ,thermalEnergyResidualKJ,combinedEnergyResidualKJ:refrigerantEnergyResidualKJ+thermalEnergyResidualKJ,
      ledger:s.ledger,fluxes:current,settings,conductancesKWK:s.spec.conductancesKWK,conductanceDescription:s.spec.conductanceDescription,
      energyReferenceK:s.spec.thermal.energyReferenceK,acceptedSteps:s.acceptedSteps,rejectedSteps:s.rejectedSteps,accuracyRejectedSteps:s.accuracyRejectedSteps,eventRejectedSteps:s.eventRejectedSteps,domainRejectedSteps:s.domainRejectedSteps,
      attemptedResidualEvaluations:s.attemptedResidualEvaluations,attemptedIterations:s.attemptedIterations,attemptedLinearSolves:s.attemptedLinearSolves,
      minAcceptedStepSeconds:s.minAcceptedStepSeconds,maxAcceptedStepSeconds:s.maxAcceptedStepSeconds,lastTimeError:s.lastTimeError,lastResidual:s.lastResidual,
      events:s.events,boundaryEvents:s.boundaryEvents,trace:s.trace,rejectionTrace:s.rejectionTrace,stop:s.stop});
  }
  return {create,trial,advance,update,record,settings};
}
module.exports={createCoupledModel};
