# Native trace and browser guard schema

`trace-on.jsonl` contains an input marker followed by native event objects.
Each marker includes its exact fixed-ledger key, fixture ID, rho/u and phase-path
setting. Within a marker block the reused update runs first, then an independent
fresh update. The two sequences have identical outputs. There are 250 markers.
The trace is native source execution, never a WASM-internal trace.

Each event has `event,a,b,c,d`. Event names encode the argument meaning. Unused
trailing fields are zero. Units are native molar SI unless stated otherwise:

| Event | a, b, c, d |
|---|---|
| `DU_entry_rhomolar_umolar_config` | input mol/m³, input J/mol, ENABLE_SUPERANCILLARIES, other parameter enum |
| `legacy_enter_rhomolar_umolar` | restored input mol/m³, J/mol |
| `satD_attempt_i_omega_maxiter_rho` | attempt index, damping, max iterations, specified mol/m³ |
| `satD_seed_T_rhoL_rhoV_omega` | ancillary seed K, liquid mol/m³, vapor mol/m³, damping |
| `satD_eval_T_rhoL_rhoV_iter` | evaluated K, liquid mol/m³, vapor mol/m³, iteration index |
| `satD_residual_r0_r1_pL_pV` | negative reduced pressure/chemical-potential residuals, liquid Pa, vapor Pa |
| `satD_step_dtau_ddelta_omega` | solved tau increment, density-coordinate increment, configured damping |
| `satD_advanced_T_error_pError` | advanced local K, prior residual norm, prior relative pressure error |
| `satD_exit_Tadvanced_TL_TV_error` | local advanced K, actual SatL K, actual SatV K, termination residual norm |
| `legacy_phase_value_satValue_satT_satRho` | requested caloric J/mol, saturation getter J/mol, saturation K, mol/m³ |
| `legacy_dispatch_two_phase` | specified mol/m³, requested J/mol |
| `legacy_two_phase_bracket` | lower K, upper K, Brent absolute setting, max iterations |
| `legacy_two_phase_residual_T_Qo_Qd_diff` | evaluated K, caloric quality, density quality, their difference |
| `legacy_two_phase_return_Treturn_Tstate_Qd` | returned Brent K, actual final state K, density-derived Q |
| `legacy_homogeneous_seed_Tmin_Tmax` | initial K, lower K, upper K |
| `DU_homogeneous_residual_T_rho_eos_target` | evaluated K, mol/m³, EOS J/mol, target J/mol |
| `SA_interval` | interval index, lower K, upper K, specified mol/m³ |
| `SA_two_phase_residual_T_Qo_Qd_diff` | evaluated K, caloric Q, density Q, difference |
| `SA_commit_T_Q` | committed K, computed Q before the unchanged inherited fast-path acceptance |
| `Brent_entry_a_b_t_maxiter` | bracket a, bracket b, absolute t, max iterations |
| `Brent_stop_boundary_a/b` | selected coordinate, residual, t |
| `Brent_stop_machine_residual` | coordinate, residual, machine epsilon |
| `Brent_stop_scaled_residual` | coordinate, residual, 2*epsilon*abs(coordinate) |
| `Brent_stop_loop_m_tol_fb` | final half-bracket m, tol, residual fb |
| `Brent_return_b_fb_iter_threshold` | returned coordinate b, residual fb, iteration index, scaled threshold |
| `Brent_return_a_fa_iter_t` | returned coordinate a, residual fa, iteration index, absolute t |

Generic Brent events include supporting saturation calls as well as the DU
quality residual. Associate the correct call with bracket/caller events and
its returned temperature. The final stop/return immediately before
`legacy_two_phase_return...` is the relevant quality-residual solve in the seven
original failures. Native event totals are diagnostic evaluation counts, not
all labeled Newton iterations.

The source patch adds logging and stores an existing once-evaluated comparison
in a local variable of the same CoolPropDbl type. It adds no EOS residual
calls, modifies no update argument and changes no branch/termination condition.
Logging parity is exact for all raw science outputs/errors, not timings.
Original source files and binary hashes allow independent review.

`*-diagnostics.json:guardTraces` captures actual browser adapter control flow.
A wrapper delegates the exact EOS request and table guard call, records their
results, and lets the original adapter throw. The original seven sequences are
DU call -> table PH guard pass -> strict sat pressure error. Error stacks locate
`adapter.mjs:8`; counts show one sat attempt but no SAT EOS call. Originating
PH acceptance is separately captured, including any Pa/bar and J/kJ round trip.
No adapter code was edited and no native trace is represented as browser-internal
solver execution.
