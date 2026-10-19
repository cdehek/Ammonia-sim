import {project as originalProject} from './support/snapshot.mjs';
export {BACKEND,SOURCE,QUALIFICATION,INTERVALS} from './support/snapshot.mjs';
export function project(r,s,session,version){
 return {...originalProject(r,s,session,version),heatTransfer:{tubeRefrigerantKW:[...r.fluxes.tubeRefrigerant],totalTubeRefrigerantKW:r.fluxes.tubeRefrigerant.reduce((a,b)=>a+b,0),airLoadKW:r.fluxes.airLoad},numerics:{acceptedSteps:r.acceptedSteps,rejectedSteps:r.rejectedSteps,nextStepSeconds:s.nextStepSeconds,lastAcceptedInterval:s.trace.length?structuredClone(s.trace.at(-1)):null,minAcceptedStepSeconds:r.minAcceptedStepSeconds,maxAcceptedStepSeconds:r.maxAcceptedStepSeconds,lastTimeError:r.lastTimeError,lastResidual:r.lastResidual}};
}
