'use strict';
// Interface-only observation: no coupled trial, advance, or campaign runs.
const fs=require('node:fs'),path=require('node:path');
const {createThermodynamics}=require('../browser_eos_backend/accepted/thermodynamics.cjs');
const rows=[];
for(const method of ['ph','recover'])for(const kind of [null,'solver','domain']){
 const error=Object.assign(Error('Diagnostic interface exception'),kind?{faultKind:kind}:{});
 const engine={ph(){throw error;},stateMVU(){throw error;}};
 const t=createThermodynamics(engine);
 try{method==='ph'?t.ph(35,1100):t.recover({massKg:1,volumeM3:.01,internalEnergyKJ:1000,pressureGuess:35});}
 catch(e){rows.push({method,injectedFaultKind:kind,observedFaultKind:e.faultKind??null,coupledCatchFallback:e.faultKind||'solver',scope:'Synthetic interface-only observation, no property state or trajectory proof'});}
}
fs.writeFileSync(path.join(__dirname,'evidence/propagation.json'),JSON.stringify({rows,simulationExecuted:false},null,2)+'\n');
console.log('six interface-only propagation observations; no simulation executed');
