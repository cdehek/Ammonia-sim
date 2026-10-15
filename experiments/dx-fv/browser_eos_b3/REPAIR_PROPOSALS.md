# B4 candidates — proposals only

No candidate below is implemented in B3. The historical B1 44-bit variant is
reproduced as a control; it is not a new B3 correction. All accepted equations,
Newton/TR-BDF2 options, signed probes, budgets, support rules and fixtures remain
unchanged. Final source evidence and confidence are in ENGINEERING_REPORT.md.

| Candidate and exact affected path | Conceptual correction and expected behavior | Risks and PH/DU implications | Evidence/tests required before acceptance |
|---|---|---|---|
| Thermodynamic PH classification: `HelmholtzEOSMixtureBackend.cpp::p_phase_determination_pure_or_pseudopure`, both superancillary and full-VLE quality branches | Distinguish uncertainty in saturation endpoints from a physically permissible quality. Resolve an h below the liquid bound with a stable homogeneous liquid solve; an h above the vapor bound with stable vapor. Restrict equilibrium lever calculations to physically justified coexistence. | Blindly replacing the tolerance with a strict zero can turn saturation rounding into branch chatter. Near the critical point the latent heat collapses and Q becomes ill conditioned; metastable roots and melting limits require explicit handling. Do not normalize inventory or silently move requested P/h. Correct PH density should remove the demonstrated corrupted-inventory cause, but does not establish global DU reliability. | Exact saved base and both signed probes; independent liquid/vapor DT roots and saturation checks; endpoints and physical crossings, both signs around Q=0/1, normal pressures and critical/triple-region coverage appropriate to declared support. Verify both source paths and H/S/U-at-P callers. |
| Out-of-range quality dispatch: same paths, before `1/(Q/rhoV+(1-Q)/rhoL)` | Never use an extrapolated equilibrium volume merely because Q is numerically close to [0,1]. A physically justified homogeneous fallback is a possible part of the classifier, after validating the endpoint uncertainty. | Clipping Q would substitute a saturation inventory for the specified liquid state and would not preserve the PH contract. Rejecting every such state would deny valid supported inputs. A fallback must prove root stability and original-coordinate residuals; it must not mask a failing flash. | Demonstrate continuous same-phase behavior on stable branches, correct one-sided coexistence behavior and explicit treatment of phase crossings. Compare independently reconstructed PH and DU inventories with unchanged budgets. A tolerance-only repair is not justified by B3. |
| PT cache synchronization: `Solvers.cpp::Householder4`, `HelmholtzEOSMixtureBackend.cpp::SolverTPResid::call` and `solver_rho_Tp`, `FlashRoutines.cpp::PT_flash` | Ensure committed density, cached derivative coordinates, pressure and caloric properties describe the same final DT state. Possible designs include final residual evaluation or a consistent backend state commit/cache invalidation after the density solver. | Re-evaluating a generic residual can affect all Householder4 callers, cost and side effects. Backend-level invalidation may change outer PH bracketing and warm/cold paths. Near criticality, a small density correction can amplify residuals. Choose the narrowest verified source owner; do not assume changing the generic solver is sufficient. | Capture final trial, increment, termination, cache fill and PT assignment, then compare fresh DT at returned coordinates. Test public PT separately from PH, warm/cold and reused/fresh states, both precisions, native and browser. Extend to other Householder4 callers if that generic routine changes. |
| Final state verification: PH/PT and DU return boundaries | Validate actual EOS pressure and energy at committed coordinates, alongside specified-coordinate getters. Fail explicitly or retry through a separately justified existing flash path when a state is inconsistent. | Getter echoes and stale caches cannot be their own independent verification. Mixtures require phase-aware equilibrium checks rather than a homogeneous residual at averaged density. A residual gate alone does not provide a convergent recovery and must not suppress failures. Additional cost needs measurement after scientific correctness. | Independent homogeneous evaluations on stable single-phase branches; equilibrium evaluations on two-phase branches; original canonical M/U/V compatibility, actual source input bits and failure/rollback contracts. No new budget chosen simply to admit a failure. |

These concepts preserve the accepted model contract only if implemented entirely
inside a separately reviewed property backend and qualified without changing
requested P/h, conservation accounting, solver tolerances, perturbations or
domain support. They may alter returned phase labels and remove erroneous
branches, which requires explicit backend regression review. B3 does not select
a final algorithm, a replacement tolerance, or an optimum number of bits.

## Proposed B4 acceptance gates

1. Approve a narrowly scoped corrective source change against a pinned upstream
   revision, with a separate decision for the liquid classifier and vapor cache.
   Review both phase-selection paths and every shared H/S/U caller affected.
2. Preserve the exact B3 failure/probe bits. Demonstrate stable, converged liquid
   roots for subcooled inputs, physically bounded equilibrium states and stable
   vapor roots; do not require smooth homogeneous derivatives across boiling.
3. Require original PH versus M/U/V recovery differences at or below 0.1 Pa,
   0.1 J/kg and 1e-4 K, and original standalone value budgets (strictly below
   10 Pa, 50 J/kg, .01 K). Independently certify reference roots at 1e-5 Pa and
   1e-8 J/kg; these are diagnostic root-resolution limits, not newly approved
   universal backend error budgets.
4. Assess signed-probe inventory contamination against the existing normalized
   nonlinear scale 1e-11, preserving its mass/energy scales. Require independent
   PH/PT consistency rather than accepting a getter echo or a favorable slope.
5. Prove correct recovery of both physical and historical PH-derived inventories.
   Do not redefine a fixed inventory to recover a preferred pressure. Characterize
   the native 7.2 high-pressure failures separately from the candidate's behavior.
6. Verify native/source/browser agreement, logging-on/off equivalence, all four
   artifact identities, endpoint sensitivity and supported-domain boundaries.
   Resolve or explicitly gate recovered numerical overshoots at 35 bar without
   silently relaxing the accepted support guard.
7. Requalify the complete accepted five-section A2 contracts through the repaired
   backend: mass <1e-8 kg, energy <1e-6 kJ, fluid norm <=1e-11, thermal closure
   <=1e-12 K, canonical compatibility, original temporal/refinement/frozen-reference
   budgets, phase events, support stops and exact rollback. Complete previously
   unexecuted B2 option/reference coverage. No enlarged probes or suppressed tests.
8. After the scientific gates pass, assess performance, longer supported runs,
   physical Safari/iPad and deployment compatibility in separately authorized
   scope. Passing this finite B3 sample cannot establish global phase accuracy.

Stop for engineering review and explicit approval before any corrective B4 work.
