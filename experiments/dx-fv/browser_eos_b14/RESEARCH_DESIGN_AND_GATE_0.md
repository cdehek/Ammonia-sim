# B14-A0 research design and Gate 0

Design checkpoint: written and committed before diagnostic transformations or solves.
Baseline HEAD `eddb2e7add904238162ead68ef9e2c1b8874f04d`, exact B13 branch tip. Empty `git status --porcelain` was observed at detached baseline before creating `research/b14-phase-jacobian-diagnostics-20261019`. No AGENTS.md was found. All additions remain in this directory. No merge, deployment, historical regeneration or production change is permitted.

## Gate 0 evidence

`audit.py` verifies every B13 Git blob against checkout bytes, fourteen A2 closure files against pinned Git objects, B9C candidate/control/diagnostic bundles and isolated model, the B13 delivery seal, and the read-only B12 package verifier with its output redirected here. See `evidence/source-preservation.json`, `historical-files.json`, `artifact-audit.json`. Local and remote refs are recorded in `evidence/*refs-before.txt`; PR #3 identity in `pr3-before.json`. Runtime/resource receipts show Node 24.19.0, Linux x86_64, Xeon Platinum 8573C, 3 visible CPUs / 2 CPU quota, 8 GiB cgroup memory. GitHub API independently confirms baseline tree `d13d17d1c9986305074799900da1c097b926bf11`.

## Precise source functions

Use the original B9C literal registry, not current unpinned root research modules. `coupled-model.cjs` exports `createCoupledModel`; inner `trial` implements two TR-BDF2 stages, `advance` compares a coarse full trial with two half trials, `errorEstimate` takes maximum fluid/thermal error, `solveStage` builds the conservative residual and owns exact PH caches, `evaluate` assembles hydraulic and thermal rates, `commit` integrates ledgers and interpolates events, `record` recovers conserved state and audits closures. `time-control.cjs:estimate` checks mass/U/P/H for every section, `factor` supplies unchanged controller constants, `crossings` tests signed h−hf/hg. `coupled-implicit.cjs:coupledNewton` builds signed 21-column finite differences. `engine.js:inverse`, `branch`, `sat`, `statePT`, `statePX` implement bounded table inversion. `thermodynamics.cjs:ph/recover` derive physical properties. Accepted snapshots identify exact sources; B9C differs only in its authorized owned boundary PH cache.

## Observation-only plan

1. Canonical B9C runs with B13 schedule `[0.0001,0.0005,0.001,0.002,0.005,0.01]`, cold and warm, same original `{trace:true,timestepGrowth:'failure-aware'}`. Compare exact science/attempt hashes against saved B13, plus accepted A2 control through 0.001 s.
2. Generate an isolated in-memory diagnostic registry from pinned B9C using fail-closed unique anchors. Retain a patch and source hashes. Never modify arithmetic, decision expressions, settings, cache scope or original event structures. New observation functions copy inputs/results after calculation; never feed copies back.
3. At estimator return, copy coarse/fine states, inventories, thermal energies and initial values. Offline reproduce original left-to-right divisions and maximum over 31 terms (not a made-up 21-coordinate norm). Assert reconstructed binary64 error equals original. Record accepted/rejected attempt, original controller factor/proposal and actual next proposal.
4. At accepted `commit`, copy both half pieces and detached accepted ledger to retain actual phase states and section changes without extra solver property evaluations. Derive properties offline from a separate original engine. Distinguish accepted PH coordinates, canonical M/U/V recovery, event interpolation and finite-step uncertainty.
5. At each Jacobian column copy perturbation/sign/shrink/residual and hash full numerical Jacobian before linear solve. Inclusive timing/counters attribute property calls, cache requests, lexical interpolation to column and residual context. Count fixed 38-iteration PH branches; track exact repeated inputs only for diagnosis, no reuse. Bounded maps and event counts; fail if caps reached.
6. Compare full original state/record/attempt exact encodings at all requested times. A separate observation mode with only detached numerical captures checks residual/Jacobian hashes against timed instrumentation; original attempt events already carry derivative residuals. Timings are inclusive, never summed as disjoint shares.
7. Two additional warm schedules: add 0.00525/0.0055 and a finer 0.0051–0.0056 partition. Each has its own paired canonical replay. At common times use original tolerance scales as sensitivity metrics (maximum <=1 a stated comparison criterion, not a formal convergence proof); record raw physical differences. No schedule is assumed bit-identical to another.
8. Reuse the separately labeled B13 sealed domain-refusal/rollback and external-budget witness as baseline; replay compact domain witness with canonical/instrumented equality. Independent signed conservation audits on all accepted half pieces and output records.

## Budgets and stop rules

B13 cost indicates seconds rather than tens of seconds per 0.01 s Node run, so start with two paired canonical/profile runs. Separate Python supervisor, process group, initial 40 s wall / 40 s CPU, 512 MiB V8 heap, bounded file and in-memory observations, sequential heavy runs. No horizon exceeds 0.01 s. Stop campaign on unsupported probe, unexpected failure/refusal, conservation violation, numerical inequality or budget termination; retain last independently accepted snapshot. Repeats limited to three pairs if short-timing noise warrants them. No browser installation or deployment.

## Predeclared interpretation and deliverables

A rejection coinciding with phase change is correlation until term-level evidence, table structure and schedule comparisons support mechanism. Distinguish actual trajectory dynamics, scale sensitivity, constitutive kinks and output clipping. No algorithm/property optimization will be implemented. Allocation bytes/GC causality remain unknown unless independently measurable; source allocation counts may be lower-bound constructions, never precise heap attribution. Rank optional exact thermal columns, residual assembly, scoped exact reuse, PH work and estimator investigation; recommend exactly one subsequent authorized experiment with independent equivalence/rollback gates.

A diagnostic PASS requires all requested source/science/conservation gates and defensible attribution with honest uncertainty. PARTIAL if useful attribution/reproducibility remains unresolved; BLOCKED on integrity/resource barriers. Accepted scientific qualification stays 0.001 s; all longer runs are UNQUALIFIED RESEARCH.
