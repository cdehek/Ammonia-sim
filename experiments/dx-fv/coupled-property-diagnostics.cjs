'use strict';
// Measure canonical recovery separately from PH inversion. No engine edits.
const fs=require('node:fs'),assert=require('node:assert/strict');
const engine=require('../../engine').createEngine(require('../../properties.json'));
const {createThermodynamics}=require('./thermodynamics.cjs'),thermo=createThermodynamics(engine);
const diagnostics=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const points=[{p:3.5,h:500},{p:3.65,h:1650},{p:3.5,h:engine.sat(3.5).hf-20},
 ...diagnostics.failedNewtonAttempts.slice(0,30).flatMap(v=>v.states.map(({p,h})=>({p,h})))];
const rows=points.map(({p,h})=>{
 const ph=thermo.ph(p,h),cell=thermo.initialize(p,h,.003/5),state=thermo.recover(cell);
 const row={p,h,phase:ph.phase,pressureDifferenceBar:state.p-ph.p,enthalpyDifferenceKJkg:state.h-ph.h,
  temperatureDifferenceK:state.T-ph.T,densityResidual:state.densityResidual,specificEnergyResidualKJkg:state.energyResidual};
 assert.ok(Math.abs(row.pressureDifferenceBar)<1e-6&&Math.abs(row.enthalpyDifferenceKJkg)<1e-4&&Math.abs(row.temperatureDifferenceK)<1e-4);
 return row;
});
const report={stage:'2A-R',runtime:process.version,passed:true,
 PH:{iterations:38,maxVaporSearchWidthK:250,quantizationWidthK:250/2**38,maxLiquidSearchWidthK:30,liquidQuantizationWidthK:30/2**38,
  measuredAnalyticInverseErrorK:diagnostics.propertyResolution.maximumMeasuredAnalyticInverseErrorK},
 canonicalRecovery:{densityOffsetIterations:32,maxVaporOffsetQuantizationWidthK:250/2**32,maxLiquidOffsetQuantizationWidthK:30/2**32,
  specificEnergyStoppingToleranceKJkg:1e-7,warmPressureIterations:10,fallbackPressureBisections:48,
  maxTemperatureDifferenceK:Math.max(...rows.map(v=>Math.abs(v.temperatureDifferenceK))),rows},
 interpretation:'The PH 38-step inversion is evaluated inside failed Newton residuals. Canonical M/U/V recovery occurs after stage convergence and has distinct density-offset/energy inversion tolerances; these failures happen before that acceptance recovery. Quantization widths are resolution estimates, not universal error bounds or a proof that 1e-12 K thermal closure is impossible.'};
fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:true,PH:report.PH,canonicalMaxTemperatureDifferenceK:report.canonicalRecovery.maxTemperatureDifferenceK}));
