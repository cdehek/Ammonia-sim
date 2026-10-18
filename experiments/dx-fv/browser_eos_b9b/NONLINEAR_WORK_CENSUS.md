# Exact nonlinear-work census

Both browsers have the following identical counts for the unchanged frozen
startup workload. `evidence/nonlinear-census.json` contains per-engine, per-advance,
per-attempt, per-solve and per-TR-BDF2-trial data. Full original FD and line-search
events remain in the raw receipts. No work is inferred from elapsed time.

| Work over .001 s | Cold | Warm |
|---|---|---|
| Adaptive attempts | 9 | 20 |
| Accuracy rejections | 1 | 3 |
| TR-BDF2 trial integrations | 27 | 60 |
| Newton stages / initial residuals | 54 | 120 |
| Newton corrections / Jacobians | 130 | 345 |
| Residual evaluations | 2914 | 7710 |
| Pressure FD probes | 650 | 1725 |
| Enthalpy FD probes | 650 | 1725 |
| Thermal FD probes | 1430 | 3795 |
| Line-search candidates | 130 | 345 |
| Dense solves | 130 | 345 |
| Accepted half-steps | 16 | 34 |

Each attempted adaptive interval performs a coarse integration and two half
integrations. Each TR-BDF2 integration has a trapezoidal stage (weight .5) and a
final BDF2 stage (weight (1−γ)/(2−γ), γ=2−sqrt(2)). All 54 / 120 Newton stages
converge. Their initial guesses are original previous PH coordinates and thermal
energy increments; the second stage uses the first stage's original result.

Cold: 54 + 2,730 + 130 = **2,914** residual evaluations.
Warm: 120 + 7,245 + 345 = **7,710**. Each correction uses 21 FD columns and one
line-search candidate. There are zero branch-rejected or failed FD probes, zero
negative probes in these fixtures, and zero rejected line-search candidates.
All accepted factors are 1. This observation does not authorize removing signed
alternatives, shrink attempts or line-search checks from other trajectories.

The original exact thermal-Jacobian option is **not enabled**. The eleven thermal
columns remain finite differences, giving 1,430 / 3,795 thermal residual probes.
No alternative setting was run. No accepted scientific configuration is replaced.

There are 8 / 17 accepted interval installations and 16 / 34 accepted half-steps.
The accuracy-rejected intervals discard 2 / 6 successfully solved half-step
candidates. All 9 / 20 coarse integrations are error-estimator references, not
accepted inventory updates. They are required numerical work under this method.
The rejected attempts consume 22 / 69 corrections and 490 / 1,536 residuals.
Accepted interval attempts consume 108 / 276 corrections and 2,424 / 6,174 residuals.
There is no natural Newton-budget exhaustion or property refusal in either fixture.

`model.trial` source events identify every trial's original start/duration,
inclusive timing, property vector, cache requests/hits/misses and child stage IDs.
`model.solveStage` events identify every stage and its recovery/cache work; original
solve IDs reset within each adaptive attempt. `model.commit` records every half
commit and `state-install` the detached atomic install. Observer arrays preserve
all outcomes and exact trial/error histories. Stage events and original solves
are ordered identically and reconcile to the totals above.

Independent M/U/V recovery occurs five times during initialization, five per
TR-BDF2 trial, five after every converged stage and five per original record:
5 + 27×5 + 54×5 + 7×5 = **445** cold;
5 + 60×5 + 120×5 + 7×5 = **940** warm. No inverse recovery is hidden inside the
Newton residual itself. All recoveries finish their pressure warm start at the
first density evaluation in these fixtures; no pressure scan/bracket fallback
is needed. Warm density evaluation still performs its original 32-step inverse.

Seven original records are generated: initial, three mandatory advance records,
and three original snapshot records. Together they contribute 56 PH / 91 public
SAT / 35 MVU calls. Additional snapshots, cloning, hashes and transport are outside
the reported advance sums. The extra three records explain the 24/39/15 count
difference from B9A's earlier component-only attribution runs.

Per-advance requests and actual accepted increments are .0001/.0004/.0005 s,
ending exactly at .0001/.0005/.001 s. Original incoming/outgoing step proposals
are in the raw timing rows. `adaptive-proposal-reconstruction.json` reconstructs
every internal unclipped proposal using the unchanged Time.factor in the SAME
browser, checks every clipped attempted dt and final nextStepSeconds exactly,
and verifies that no nonlinear-failure ceiling is active. This is post-processing
of saved errors, with zero new model/property evaluations.

See `PROPERTY_EVALUATION_AUDIT.md` for requests versus actual calls, and
`JACOBIAN_AND_LINE_SEARCH_COST.md` for cost/overlap limitations.
