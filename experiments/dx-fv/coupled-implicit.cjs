'use strict';
// Separate from the historical alternating-PH Newton implementation.
const {solveLinear} = require('./implicit.cjs');
const norm = r => Math.max(...r.map(Math.abs));
const region = s => s.x === null ? (s.phase.includes('liquid') ? 'liquid' : 'vapor') : 'mixture';

function coupledNewton(evaluate, initial, variables, settings, work) {
  if (variables.length !== initial.length) throw Error('One type is required per coupled variable.');
  const counted = x => { work.evaluations++; return evaluate(x); };
  const recorded=!!work.diagnostics;
  const solveId=recorded?(work.diagnosticSolveCount=(work.diagnosticSolveCount||0)+1):null;
  let x = [...initial], value, lastIteration=null;
  const recordIteration=(iteration,status)=>{
    const residual=[...value.residual],fluid=Math.max(...residual.slice(0,10).map(Math.abs)),thermal=Math.max(...residual.slice(10).map(Math.abs));
    const dominant=residual.reduce((best,v,i)=>Math.abs(v)>Math.abs(residual[best])?i:best,0);
    return {type:'iteration',solveId,iteration,status,residual,fluidNorm:fluid,thermalNorm:thermal,dominantIndex:dominant,
      states:value.states.map(s=>({p:s.p,h:s.h,T:s.T,phase:s.phase,x:s.x})),context:iteration===0?work.diagnosticContext:undefined};
  };
  try {
    value = counted(x);
    for (let iteration = 0; iteration <= settings.maxIterations; iteration++) {
      const error = norm(value.residual);
      if (!Number.isFinite(error)) throw Error('Nonfinite coupled nonlinear residual.');
      if(recorded){lastIteration=recordIteration(iteration,error<=settings.nonlinearTolerance?'converged':'active');work.diagnostics.push(lastIteration);}
      if (error <= settings.nonlinearTolerance) return {x, value, error};
      if (iteration === settings.maxIterations) break;
      work.iterations++;
      const jacobian = Array.from({length:x.length}, () => Array(x.length));
      for (let k = 0; k < x.length; k++) {
        const variable = variables[k];
        const epsilon = variable.kind === 'pressure' ? 1e-7*Math.max(1,Math.abs(x[k]))
          : variable.kind === 'enthalpy' ? 1e-8*Math.max(1,Math.abs(x[k]))
          : variable.kind === 'thermal-energy' ? variable.capacityKJK*1e-6 : NaN;
        if (!(epsilon > 0)) throw Error('Unsupported coupled variable type.');
        let candidate = null, step, lastCause = null;
        for (let shrink = 0; shrink < 12 && !candidate; shrink++) {
          for (const sign of [1,-1]) {
            step = sign*epsilon*2**(-shrink);
            const probe = [...x]; probe[k] += step;
            try {
              const next = counted(probe);
              const sameBranch=variable.section === undefined || region(value.states[variable.section]) === region(next.states[variable.section]);
              if(recorded)work.diagnostics.push({type:'derivative',solveId,iteration,column:k,kind:variable.kind,epsilon,step,shrink,outcome:sameBranch?'used':'branch-rejected'});
              if (sameBranch) {
                candidate = next; break;
              }
            } catch (cause) {
              if(recorded)work.diagnostics.push({type:'derivative',solveId,iteration,column:k,kind:variable.kind,epsilon,step,shrink,outcome:'probe-failed',message:cause.message,faultKind:cause.faultKind||'solver'});
              lastCause = cause;
            }
          }
        }
        if (!candidate) throw lastCause || Error('No coupled derivative within the constitutive branch.');
        for (let i = 0; i < x.length; i++) jacobian[i][k] = (candidate.residual[i]-value.residual[i])/step;
      }
      work.linearSolves++;
      const delta = solveLinear(jacobian, value.residual.map(r => -r));
      let accepted = false, lastDomain = null;
      for (let factor = 1; factor >= 2**-28; factor /= 2) {
        try {
          const nextX = x.map((v,k) => v+factor*delta[k]), next = counted(nextX);
          const nextError=norm(next.residual);
          if(recorded)work.diagnostics.push({type:'line-search',solveId,iteration,factor,previousError:error,nextError,outcome:nextError<error?'accepted':'not-reduced'});
          if (nextError < error) { x = nextX; value = next; accepted = true; break; }
        } catch (cause) {
          if(recorded)work.diagnostics.push({type:'line-search',solveId,iteration,factor,previousError:error,outcome:'probe-failed',message:cause.message,faultKind:cause.faultKind||'solver'});
          if (cause.faultKind === 'domain') lastDomain = cause;
        }
      }
      if (!accepted) throw Object.assign(Error('Coupled line search did not reduce the conservative residual.'), {
        faultKind:'solver', nonlinearResidual:error,
        domainCause:lastDomain ? {message:lastDomain.message,evidence:lastDomain.evidence} : null
      });
    }
    throw Object.assign(Error('Coupled nonlinear iteration budget exhausted.'), {faultKind:'solver',nonlinearResidual:norm(value.residual)});
  } catch(cause) {
    if(recorded)work.diagnostics.push({type:'solve-failed',solveId,message:cause.message,faultKind:cause.faultKind||'solver',
      nonlinearResidual:cause.nonlinearResidual??null,lastIteration,context:work.diagnosticContext});
    throw cause;
  }
}
module.exports = {coupledNewton};
