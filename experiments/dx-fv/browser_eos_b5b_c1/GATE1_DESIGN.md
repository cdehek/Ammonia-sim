# C1 pre-implementation scientific contract review

Decision: **Gate 1 PASS**, for the narrow intervention below. This document is
committed before functional implementation. It authorizes no thermodynamic or
numerical-budget change. The C1 branch starts at exact B5B commit
`26df10c1f486b60978646e9c8819fc0054cb9465`; A2 is
`be9eb35a4ddf5098e685182f8104685127c6a6ee`.

Reviewed: all six required B5B reports, B5 failure matrix/report, B5A Gate B
feasibility/report, B4C loader, historical adapter, accepted thermodynamics,
Newton, coupled model, time control, conservation and accepted domain tests.
Preservation receipts bind every starting file and all remote heads, including
PR #3, all research artifacts and twelve accepted dependency snapshots. No
functional code was written before this decision.

## Ownership and complete failure path

| Owner (paths relative to experiments/dx-fv) | Historical behavior / information loss | C1 intervention |
|---|---|---|
| `browser_eos_b4c/vendor/candidateB` CoolProp JS/WASM | Raw getters or exception; no inventory/trajectory proof | Import exact historical artifacts. No build, source or loader edits. |
| `browser_eos_b4c/loader.mjs::evaluate` | Decodes exception into new Error; finite check; existing exception cleanup has separate rejected-PT defect | Outer research wrapper records exact request bits and original observed message/status. Cannot recreate discarded native exception details. Never changes cleanup. |
| `browser_eos_backend/adapter.mjs::stateMVU` | Receives M,V,U, unused guess. Reconstructs rho/u, obtains raw DU, then convert; on refusal loses raw evidence | Isolated wrapper delegates to this byte-identical function, captures raw requests/results on its call stack, throws typed failure. Never returns raw rejected state. No inferred PH provenance. |
| `adapter::convert` | Table PH guard can throw unlabeled; sat fails domain; temperature envelope fails domain; successful phase/density/u only after these gates | Same code, same comparisons and order. Wrapper identifies failing support stage from call trace, scopes DU refusal C/solver; numerical exception B/solver. |
| `adapter::sat` | Explicit p outside .3–35 bar throws domain before EOS | Direct explicit sat/PH request remains E/domain, input scope, physical exit unproved. In recovery context it remains refusal with C/solver. |
| accepted `thermodynamics.cjs::ph` | Explicit PH guard domain. Catch defaults untyped PH exception to domain. Derives wet/superheat only after success | Isolated copy labels explicit guard E; defaults unknown property error to B/solver and retains structured diagnostics. `recover` scopes any subsequent saturation error to recovery. |
| accepted `coupled-model.cjs::fluidCall` | Adds source/section/stage by spreading evidence | Keep existing fields and diagnostic envelope, adding lineage without overwriting underlying operation. |
| accepted `coupled-implicit.cjs` Newton | Signed FD branch handling; failed derivative throws last cause. Line search remembers only last domain, losing solver property failures; may otherwise learn from genuine nonlinearResidual | Isolated copy retains last property cause plus diagnostic probe records. Attach it to failed line search without inventing or altering residual. Prevent property refusal from teaching nonlinear-failure growth. All probes, branch rules, Newton budgets unchanged. |
| coupled `advance` catch | Rejects every exception; dt/2; traces evidence; finite genuine Newton residual can teach A2 growth; property errors don't supply one | Preserve exact retry, counters, floors and halving. Carry propertyCause to trace, observer and final stop. |
| coupled `domainEvidence` | Rechecks exact thermal outward direction; at dt<=1e-6 computes accepted-state rates and conserved refrigerant direction. Any recovery error domain currently confirms exit | For typed property failures require independent evidence: a property refusal carries `physicalTrajectoryExit:unproved`, so cannot satisfy refrigerant proof. Preserve historical untyped table-backend behavior outside C1's typed adapter scope. Thermal proof code stays byte-identical. If evidence gathering itself fails, retain unconfirmed diagnostic, do not throw away original failure or fabricate proof. |
| coupled detached commit / rollback | Both half-step commits prepared against detached ledger/events before installation; rejected trial never writes physical state | No changes to commit, accepted identity, ledger arithmetic, events, TR-BDF2, trial construction or rollback. |
| coupled `record`, initialization, boundary edits | Records re-evaluate accepted properties; may throw. Initialization may fail; patch validates before mutation | Preserve refusal: if accepted-state re-evaluation fails, throw with diagnostic and retained stop; never use raw failure to populate sections. Record failure is explicitly tested, never returned as a successful state. Retain outlet failure diagnostic. |

Raw numerical evidence is represented as numbers plus binary64 bits, not an
alternate state return. The wrapper has no certificate API, no pressure enclosure
and no general runtime ability to detect the saved inward-recovery hazards.

## Five distinct outcomes and compatibility

| Class / reason | Evidence required; available / missing | Compatible kind | State / accepted trial / physical stop | Retry and rollback |
|---|---|---|---|---|
| A `confirmed-domain-exit` | Accepted A2 independently rechecked thermal boundary and outward rate, or original independently justified domain evidence. Property layer lacks trajectory, rate and accepted identity. A label or tiny EOS sign is insufficient. | domain at caller proof only | No rejected state; no trial acceptance; protective stop allowed only after proof | Existing reject/halve/floor and exact accepted rollback |
| B `inverse-recovery-failure` | Observed raw exception, nonfinite/phase/numerical refusal. Retain actual observed status and any residual. No native exception details beyond loader information can be invented. | solver | No / no / no from this failure | Original dt/2, numerical stop if persistent, exact rollback |
| C `boundary-unresolved` | Raw recovery returned but complete operation fails support. Inventory available; originating PH, certified exact-inventory pressure and physical proof missing. Two/five mechanisms require offline evidence. | solver | No / no / no from refusal | Same retry/floor, unresolved numerical stop, exact rollback |
| D supported success | Unchanged adapter gates pass; every original property, canonical, nonlinear, phase, conservation and trial criterion still applies. Runtime numeric support is not an exact-inventory certificate. | none | Candidate property only; A2 still decides trial; no exit claim | Ordinary original path; known mathematical inward hazards remain blockers |
| E `explicit-unsupported-input` | Exact explicit PH/sat request violates strict support/guard, or independently established input unsupported. MVU cannot reconstruct arbitrary original PH input. | domain for direct input; solver when refusal occurs inside recovery | No / no / no automatic trajectory stop | Reject initialization/edit without installation; reject trials and exact rollback; caller needs separate A proof |

E takes precedence over apparent inward recovery when the explicit request is
actually supplied. No MVU-origin field is invented. The runtime does **not**
label the seven by fixture identity, microscopic pressure gap or offline root.
All seven runtime refusals are C; the report joins independent immutable B5B
evidence for the two numerical wrong-side and five representation mechanisms.

## Preservation argument and implementation boundary

Only additions under `browser_eos_b5b_c1` are permitted. Copy all twelve accepted
dependencies and compare every byte to the accepted Git objects before any edit.
Functional diffs are limited to error classification/transport in the three
copies named above and wrappers around the historical adapter/loader. Produce
full unified patches and a hash manifest. No EOS changes. No new top-level
faultKind. No new physical proof issuer or refrigeration protection rule.

Hard maximum remains exactly 3,500,000 Pa, strict .3–35 bar comparisons, floor
195.495 K, table bounds, 30 K subcool / 250 K superheat and thermal 200–400 K.
No epsilon, band, clipping, rounding change, input substitution or success fallback.
Canonical <=.1 Pa / <=.1 J/kg / <=1e-4 K; normalized fluid mass/energy 1e-11;
standalone <10 Pa / <50 J/kg / <.01 K; conservation <1e-8 kg / <1e-6 kJ;
thermal closure 1e-12 K; minStep 1e-9; Newton 30, FD, halving/attempt budgets,
hydraulics, thermal transport, phase events and reference rules stay unchanged.

The independently rechecked thermal protection is sufficient to test a genuine
modeled exit using existing accepted evidence. No accepted refrigerant proof
can be obtained merely by renaming a DU failure. C1 cannot qualify physical
refrigerant crossings at nanopa or certify exact-boundary acceptance.

## Gate 2 verification plan (bounded)

Replay both engines' seven original bit inventories and two saved inward controls
against exact B4C WASM and historical adapter versus wrapper. Compare all raw
bits, budgets, strict refusal and no fabricated proof/state. Replay saved PH
boundary triplets, meaningful interior/exterior and phase cases; explicit E
must refuse even when the separately constructed MVU later returns inward.
Run focused B1/B4A/B4B/B4C controls including actual signed FD/cache cases.
Exercise actual accepted A2 with matched supported calls and synthetic faults,
and real preserved browser refusals injected at a property call, not a mock
solver. Exercise retry/halving to original floor, exact rollback using original
JSON comparison, retained stops, independent thermal outward recheck, false
proof, initialization/edit/record and detached commit failure. Compare supported
control/candidate accepted values and original conservation budgets.
Use actual archived native libraries without rebuilding. Verify async/worker,
fresh/reused and stale error behavior, matched bounded timings and linear memory.
Omissions are failures of scope/verification, never converted to qualification.

Both saved mathematical inward controls are **qualification blockers** unless
a general numerical certification method is implemented; no such research is
authorized here. Gate B endpoints, Gate A browser, rejected-PT loader cleanup,
complete backend/A2 and physical iPad qualification remain separate limitations.
