# B4B algorithm decision — before functional source modification

Starting checkpoint: 94f77bb062b75ffebf17a1c9758d11c1adc61711.
Pinned CoolProp: ae81610e7d23efc57f9d051c8e70a4d66e87537f.
Control execution: evidence/native-controlA.json, using the verified original
B4A liquid44 library, reproduces the original bits and stale-cache discrepancies.
The B3 report, proposals, captured probes-trace44.jsonl, B4A report, algorithm,
patch and B4B prerequisites have been reviewed. No broader defect is authorized.

## Selected operation and scope

In FlashRoutines::PT_flash's pure/pseudopure homogeneous density branch, save T,
solve density with the existing solver and original pressure, then commit the
returned density and saved T with update_DmolarT_direct. Retain _Q=-1.
This existing backend operation runs pre_update (clear cached elements, restore
gas constant/reducing state), assigns density/T, calculates EOS pressure, and runs
post_update(false). Derivatives are subsequently filled lazily at those committed
coordinates. No target pressure is installed as an EOS answer. No extra flash,
phase selection, numerical iteration or acceptance budget is introduced.

The same operation already follows solver_rho_Tp in update_TP_guessrho and in
mixture PT's homogeneous selection paths. The change is restricted to the missing
commit in pure/pseudopure PT; the critical-point shortcut and mixture paths remain
unchanged. It is shared by PT calls from homogeneous H/S/U-pressure inversion,
including PH; this can alter the outer root because it now sees consistent energy.
Pseudo-pure and non-ammonia fluids are shared-source consequences requiring future
qualification. This experiment only certifies its focused supported ammonia tests.

## Mechanism

Householder4 evaluates f(x) and three derivatives, increments x, then can exit
using old fval or relative dx. SolverTPResid::call uses update_DmolarT_direct at
the evaluated density; derivative calls fill the residual Helmholtz cache there.
solver_rho_Tp returns the incremented coordinate. Old PT_flash assigns only rho.
post_update rewrites delta/tau but does not clear derivatives. calc_hmolar and
calc_umolar use explicit final coordinates with cached alpha derivatives from
the previous coordinate. _p also remains the previous residual's EOS pressure.
AbstractState::clear clears CachedElements and bulk coordinates; pre_update also
restores reducing state. update_DmolarT_direct preserves the selected phase and
rebuilds the state without invoking another phase classifier.

## Alternatives considered

* Generic final residual evaluation or altered Householder termination affects
  unrelated callers and acceptance behavior. Neither is necessary for this defect.
* A final residual evaluation in solver_rho_Tp requires handling every early,
  fallback and phase-specific return, and broadens side effects for callers that
  already commit correctly. Its density-selection checks remain out of scope.
* Clearing selected derivatives manually risks omitting pressure/caloric/ideal
  derivative caches. Calling clear alone destroys coordinates and requires a
  duplicated partial rebuild. The existing complete commit is easier to audit.
* Restoring requested pressure after invalidation would create an input echo;
  instead pressure is evaluated from EOS at returned density/T.

## Gates and resource limits

Checkpoint/reproduction: 30 min; native/WASM setup/build: 60 min; focused science,
browser and compatibility: 60 min. Individual builds <=900 s, property campaigns
<=180 s, limited A2 <=300 s. Preserve partial outputs on deadlines. At most two
compiler jobs per build. No full B2 or global A2 qualification rerun.

First require original vapor PH/PT, independent DT p/h/u, reference root,
cache-coordinate trace, original canonical .1 Pa/.1 J/kg/1e-4 K limits and local
normalized energy scale <=1e-11. Then B4A liquid and B1 exact probes; stop downstream
compatibility if either primary fails. Reference roots retain 1e-5 Pa/1e-8 J/kg
resolution. Two-phase checks use coexistence endpoints/lever rules, never impose
homogeneous continuity across boiling. Preserve input bits, signed probes,
normalization, upper-Q and 35-bar failure records, and all original tracked files.

Only after these gates: supported lifecycle matrix, bounded accepted A2 fixtures,
native/Chromium/WebKit timing/memory and work counts. No production selection,
UI/Live Plant change, merge, deployment, full qualification or physical iPad claim.
