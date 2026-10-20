# Exactly one recommended next experiment

**Recommend a narrowly scoped prototype of exact pressure-bracket reuse within a single vapor PH inversion.** Authorization is requested in the next milestone, not exercised by B14.

## Why this first

Warm 15,739 vapor PH calls each execute 40 branch interpolations, totaling 629,560 repeated pressure-location operations with unchanged p inside their own call. Source confirms every branch calls pBracket(p), repeating log(p), pressure-axis binary search and bracket-result construction. PH is a measured substantial inclusive scope (diagnostic median ~618 ms), while original B13 independently measured ~475.6 ms. The pressure-location fraction is unmeasured; neither value is promised savings. This identifies exact invariant work with a natural single-call owner, avoiding decisions about sharing across sections/stages/spec changes.

The candidate must preserve all 38 bisections, every offset lookup, interpolation operation/order, statePT/thermodynamic outputs, classification band, table/support bounds and exception behavior. A pressure bracket can be reused only after its original successful validation and only for the same exact p and owned immutable table during that inversion. No persistent cache, approximate match, quantization, table change, new stopping criterion or new backend is permitted by this proposal. Do not hoist calculations past domain checks or change refusal ordering. The ordinary two-phase path must remain untouched. This is an implementation plan for future review, not code in B14.

## Ranked candidates

| Rank | Candidate | Measured opportunity | Equivalence/proof and complexity | Phase/decision/conservation/refusal risk | Rollback |
|---|---|---|---|---|---|
| 1 | Single-inversion exact pressure-bracket reuse (D/C) | 40 repeated pressure searches per warm vapor PH; exact savings unknown within PH envelope | High likelihood of bit equality if all branch arithmetic/order retained; moderate proof/implementation, owned tables and failures mandatory | Low expected phase/decision/conservation risk only after exact proof; exception ordering needs deliberate tests | One isolated helper/path, no persistent state |
| 2 | Residual assembly/allocation reduction (B) | 19,380 residuals; repeated arrays/Map construction, 9,537 thermal probes rebuild unchanged fluid assembly | High for invariant topology lookup, moderate for broad rewrites; exclusive allocation cost unknown | Reassociation or alias changes can alter decisions/ledger; medium failure-scope proof | Small isolated source diff |
| 3 | Optional original exact thermal Jacobian columns (A) | 9,537 warm residual probes, median thermal column envelope ~218 ms | Lower likelihood of bit equality: analytic derivative need not equal finite difference binary64; scientific qualification likely, implementation easy but proof hard | Moderate/high Newton path/acceptance risk; conservation needs requalification if results differ | Existing option is easy to disable |
| 4 | Broader exact-input reuse across call sites (C) | 4,930 repeated warm PH inputs including initialization | Moderate proof: ownership, mutable outputs, changing spec, failed probes, stage lifetime; implementation moderate/high | Aliasing/stale cache could affect phase/refusal and decisions; conservation risk follows | New state must be removable and invalidated |
| 5 | Estimator/refinement investigation (E) | Extra transition rejections and schedule sensitivity established | Further science is useful, but changing estimator has no exact-equivalence presumption; complex independent qualification | High acceptance/event/trajectory risk; no current evidence authorizes relaxing accuracy | Separate diagnostic/qualified branch |

Ranking weighs proof and reversibility alongside measured opportunity. Candidate A has a larger direct residual-count opportunity than the narrow chosen prototype, but expected binary64 derivative differences make it a poor first exact-equivalence experiment. Candidate B is plausible but original allocation cost is unresolved. Candidate E remains a qualification question; timing coincidence does not justify changing the controller.

## Proposed controlled protocol

1. Start from the completed B14 branch in a new isolated authorized directory/branch. Preserve all protected source/package/ref/PR audits. First commit a design and exact-input ownership argument.
2. Compare original versus prototype on pinned tables: two-phase states, vapor just outside the 1e-8 band, every relevant pressure/superheat boundary, invalid/support inputs, aliasing and mutation isolation. Validate exception type/message/evidence and order; do not silently convert a refusal to a cache hit.
3. Replay cold/warm original B13 schedules and the two B14 sensitivity schedules, still no longer than .01 s without new authorization. Require bit-exact PH outputs, residuals, Jacobians, every original attempt/controller decision, accepted M/U/V, thermal energies, records, events/ledgers and stops. Replay genuine domain refusal, invalid update and external termination semantics.
4. Any numerical or scientific decision mismatch rejects the prototype as an exact-equivalence optimization. Do not relax the gate or rewrite fixtures; return for separate scientific qualification.
5. Only after proof, use bounded sequential process measurements to estimate actual pressure-location saving with light counters and a no-timer control. Separate counts, CPU/wall, instrument overhead, allocation/GC and serialization. Minimum reproducibility samples, desktop Chrome/Edge assessment later.
6. Keep prototype opt-in and independently removable. No merge/deployment until engineering review and separate approval.

Success would be demonstrated identical science plus measured work reduction, not a promised speedup. If pressure search is too small to matter, report the negative result and retain the original engine.
