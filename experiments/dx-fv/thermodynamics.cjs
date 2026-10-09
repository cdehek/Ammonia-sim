'use strict';
const {inventory}=require('./conservation.cjs');
function createThermodynamics(engine){
 function ph(p,h){
  if(!Number.isFinite(p)||p<.3||p>35||!Number.isFinite(h)){const error=Error('Thermodynamic state outside the bounded property domain.');error.faultKind='domain';throw error;}
  let state,sat;try{state=engine.ph(p,h);sat=engine.sat(p);}catch(error){
   if(error.message.includes('Compressor discharge exceeds'))error.message='Section enthalpy exceeds the bounded property table (250 K superheat).';
   error.faultKind=error.faultKind||'domain';throw error;
  }
  return {...state,superheatK:Math.max(0,state.T-sat.T),wet:state.x!==null?state.x<1:state.phase.includes('liquid')};
 }
 function initialize(p,h,volumeM3){return {...inventory(ph(p,h),volumeM3),volumeM3,pressureGuess:p};}
 function recover(cell){
  const state=engine.stateMVU(cell.massKg,cell.volumeM3,cell.internalEnergyKJ,cell.pressureGuess);
  return {...state,superheatK:Math.max(0,state.T-engine.sat(state.p).T),wet:state.x!==null?state.x<1:state.phase.includes('liquid')};
 }
 return {ph,initialize,recover};
}
module.exports={createThermodynamics};
