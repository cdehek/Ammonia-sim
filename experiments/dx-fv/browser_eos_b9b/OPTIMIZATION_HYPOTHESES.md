# Future optimization hypotheses — none implemented

These are requests for future scientific design and engineering review. B9B
changes no accepted numerical work. Ranking weighs measured opportunity and
equivalence risk, rather than suggesting that every expensive calculation is
unnecessary. Timings and source attribution are in `BROWSER_PERFORMANCE_MATRIX.md`
and `evidence/cpu-attribution.json`; all observed work is retained in B9B.

## 1. Stage-local reuse of immutable table-backed boundary PH results

1. **Measured bottleneck:** residual/property evaluation. Each residual calls
   `model.evaluate`, which requests BOTH fixed boundary PH states again. That is
   5,828 cold and 15,420 warm boundary PH evaluations in residuals alone, before
   initial rates and recording. The existing section PH cache does not cover them.
2. **Operation:** accepted `coupled-model.cjs`, `evaluate` boundary `thermo.ph`
   calls; original `engine.inverse` performs a 38-iteration inverse on the
   superheated outlet boundary. The inlet is a mixture-table calculation.
3. **Potential redundancy:** during one original stage the exact `spec` boundary
   p/h pairs and table implementation do not change. The resulting properties
   appear identical across all Newton/FD/line-search evaluations of that stage.
4. **Equivalence obligation:** prove deterministic exact binary64 results, no
   consumer mutation/aliasing, identical validation and refusal meaning for this
   exact table engine. Restrict lifetime to the stage and exact boundary identity.
   A mutable, stateful, injected or experimental backend cannot inherit this proof.
5. **Phase risk:** retaining a boundary result must not bypass a changed boundary,
   support check or branch decision. Keep all section phase checks unchanged.
6. **Signed-FD risk:** only boundaries remain fixed during probes. Never reuse a
   perturbed section property, collapse signs, round keys or omit any probe.
7. **Convergence risk:** exact residual arrays and Newton/line-search decisions
   must remain identical, including failures. Changed evaluation ordering or
   refusal timing is a stop condition until independently justified.
8. **Conservation risk:** preserve shared face/donor arithmetic and all ledgers;
   do not regroup additions or replace canonical inventories.
9. **Rollback risk:** keep cached ownership detached from accepted state and
   discarded trials. No cache entry may turn a refused operation into success.
10. **Independent tests:** direct original versus candidate full state, every
    residual/FD/line-search/stage/proposal/record, exact PH inputs/results and
    canonical references; boundary edits, flow reversal, support edges, rejected
    steps and original C1 synthetic failures. If a refusing backend invalidates
    purity, leave that configuration unchanged rather than weakening its contract.
11. **Browsers:** Chromium and desktop WebKit bit-exact original fixtures plus
    failure/rollback tests and interleaved uninstrumented timing, with original
    reporting cadence. Node is supplementary. No iPad claim.
12. **Upside:** at most 2×(residuals−stages) = 5,720 / 15,180 residual-boundary PH
    calls could be removed if both are retained once per stage. This is a call
    bound, not a speedup forecast; cache setup, required checks and failure scope
    reduce the attainable benefit. The outlet inverse makes this worth review.
13. **Smallest milestone:** separately authorize a table-only, isolated stage
    boundary reuse design/prototype, prove exact equivalence first, then measure.
    Do not merge it into accepted A2 or extend the horizon as part of that study.
14. **Stop:** any changed original value, branch, acceptance, refusal, rollback,
    diagnostic meaning, unsupported-state handling or inconclusive purity proof.

## 2. Reuse saturation intermediates within one genuine engine PH operation

1. **Measured bottleneck:** sampled table-property work and directly counted
   nested saturation. Public counters miss these lexical calls.
2. **Operation:** `engine.inverse` calculates `sat(p)` and then calls `statePX`
   or `statePT`, which calculates `sat(p)` again at that exact pressure.
3. **Potential redundancy:** no intervening mutation of table data or p occurs
   within the synchronous accepted operation.
4. **Equivalence obligation:** the existing computed saturation object must yield
   identical fields and branches, with the same support validation and no exposed
   alias mutation. Preserve every interpolation expression and operation ordering.
5. **Phase:** saturation endpoint thresholds, epsilon comparisons and original
   quality behavior must remain exact; no new clamp or endpoint repair.
6. **Signed FD:** each PH call remains independent and retains the exact perturbed
   p/h. No reuse across probes or pressure coordinates.
7. **Convergence:** all original residual arrays and decisions must match.
8. **Conservation:** unchanged state density/enthalpy and inventory arithmetic.
9. **Rollback:** no cross-call cache and no mutation surviving a refused call.
10. **Independent tests:** original table PH/PT/PX branches, all support edges,
    exact inputs around saturation and signed-zero identities, direct and
    canonical recovery references, original scientific budgets and complete
    supported/failure fixture parity. Do not attempt a new CoolProp qualification.
11. **Browsers:** Chromium/WebKit exact property sequences and scientific
    decisions, failure receipts and matched uninstrumented controls.
12. **Upside:** potentially one lexical saturation calculation per genuine PH
    inverse; no measured isolated CPU duration for that private duplicate. Public
    `engine.sat` timing cannot serve as its exact cost. No speedup estimate.
13. **Smallest milestone:** one private single-operation intermediate-reuse proof
    and isolated prototype, separately authorized. This is a smaller possible
    follow-up if boundary reuse cannot preserve its failure contract.
14. **Stop:** any altered endpoint, result bits, validation/refusal or call-level
    side-effect assumption that cannot be proved for the exact table engine.

## 3. Avoid rebuilding a fixed thermal topology index on every rate evaluation

1. **Measured bottleneck:** residual construction is substantial after property
   work, but the individual `new Map` allocation cost is not isolated.
2. **Operation:** `model.evaluate` constructs eleven node-ID/index pairs and a Map
   each time; link lookups then repeat fixed topology relationships.
3. **Potential redundancy:** node order and link endpoints remain fixed for the
   same spec. Boundary patches clone specs, so lifetime/identity needs proof.
4. **Equivalence obligation:** identical index values and iteration order;
   preserve link subtraction/addition order and all energy expressions.
5. **Phase:** no property or phase logic touched.
6. **Signed FD:** every original residual/probe still executes with current
   energies; only immutable index metadata could be shared.
7. **Convergence:** bit-exact arrays and decisions, no reordered residual assembly.
8. **Conservation:** all signed link transfers and ledgers remain identical.
9. **Rollback:** immutable metadata only; no shared mutable rate/energy arrays.
10. **Independent tests:** geometry/node order, original spec cloning/patches,
    every original residual/flux/ledger and rollback; cache invalidation at every
    spec replacement, including schedules and manual changes.
11. **Browsers:** same exact Chromium/WebKit fixtures/failures and matched timing.
12. **Upside:** unquantified. Containing `model.evaluate` time also includes
    boundary properties and thermal/flow calculations; it is not a Map cost.
13. **Smallest milestone:** allocation-focused passive investigation first. Do not
    implement this solely from a count of 11-entry maps.
14. **Stop:** no meaningful measured allocation contribution, changed ordering,
    aliasing, invalidation or any scientific/failure difference.

## 4. Dense linear-system temporary allocation organization

1. **Measured bottleneck:** `solveLinear` has a small measured cost relative to
   the containing solves. O(n³) alone is not evidence of dominance at n=21.
2. **Operation:** fresh augmented matrix rows and correction array per solve in
   `implicit.cjs`, called 130 / 345 times.
3. **Potential redundancy:** storage allocation might be reusable; elimination,
   pivot selection and every floating-point arithmetic operation remain required.
4. **Equivalence obligation:** same values, loop order, pivots and rounding;
   original input matrix/rhs must remain unmodified and unaliased.
5. **Phase:** no direct phase change, but corrections influence later phase probes.
6. **Signed FD:** preserve all columns and signed derivative values exactly.
7. **Convergence:** correction vectors, line-search candidates and failures exact.
8. **Conservation:** exact correction/residual equivalence before physical checks.
9. **Rollback:** fully reset scratch storage after exceptions; no trial owns a
   reference reused by a later solve or accepted state.
10. **Independent tests:** pivot ties, singular matrices, residual/backward-error
    checks and original Newton/failure/canonical/conservation reference tests.
11. **Browsers:** Chromium/WebKit exact correction and science/failure parity,
    actual allocation observations and matched timing.
12. **Upside:** bounded by its small containing measured cost; no justified
    numerical speedup estimate. Low priority.
13. **Smallest milestone:** allocation profiling only if the higher-ranked
    property opportunity has been resolved or rejected.
14. **Stop:** altered pivot/correction bits, scratch aliasing, failure changes or
    an allocation contribution too small to justify scientific review cost.

Recommended next action is hypothesis 1's narrow **equivalence design and isolated
prototype**, subject to explicit engineering review. If its failure semantics
cannot be preserved, stop it and review hypothesis 2. No reduced Newton budget,
larger time step, approximate memoization, phase shortcut or thermal-setting
change is recommended. Required FD, error-estimation and rejection work is not
classified as redundant. Operator integration remains NO-GO.
