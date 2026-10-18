# B9B pre-instrumentation measurement design

Starting checkpoint: B9A `355db28d853817e1931295d6ec2f007876d53f90`.
Accepted A2: `be9eb35a4ddf5098e685182f8104685127c6a6ee`. Only additive B9B files.
This design is committed independently before profiling implementation.

## Frozen science and evidence levels

Use the fourteen Git-verified accepted dependency files and untouched B9 literal
bundle. Never load later root coupled solver files. The engine is the accepted
table engine, not B7 CoolProp. Fixtures are original cold/warm with .60 kW/K
exchange, open flows and original inventories, geometry and boundaries. Options
remain `trace:true,timestepGrowth:'failure-aware'`; thermal Jacobian remains its
original finite-difference default. No alternative numerical setting is planned.
Checkpoints: 0/.0001/.0005/.001 s; requested advances: .0001/.0004/.0005 s.
Initial record and one additional original snapshot record after each advance
preserve B9/B9A cadence. No longer or easier trajectory is permitted.

* Level A: original unmodified execution, exact B9 bundle, original observer and
  public property counter. This is the authoritative scientific/performance
  control. Timing covers model advance, including its mandatory original record;
  extra endpoint recording, state copying, verification and transport are timed
  separately. Also reproduce original B9 service worker workload.
* Level B: bounded Chromium CPU sampling through CDP on original worker execution
  if available. Preserve raw profiles and source positions, sample intervals,
  sampled stacks and unmatched samples. Test desktop WebKit capability; absence
  of a supported external sampler is a documented limitation, not sampled data.
  Node inspector provides additional diagnostic evidence only.
* Level C: exported function wrappers delegate once with identical receivers,
  inputs, returns and thrown objects. Original observer events give solve IDs,
  iteration, signed FD and line-search outcomes without added evaluations. If
  those cannot resolve cache/private work, generate an isolated diagnostic copy
  with a complete exact diff. Insert only observation statements; never modify
  an existing expression, branch, cache decision, state or numerical rule. Such
  a copy is profiling-only and is not accepted A2. Stop any investigation needing
  changes to accepted source logic.

## Bounded matrix and overhead controls

Actual Chromium and desktop WebKit run sequentially, without competing physics
or compilation. Three rounds per engine/fixture in predeclared order:
original, pass-through wrappers, instrumented diagnostics, original again.
Each session has a fresh loader/model and original inputs; reuse browser process
within a round only. Runtime JIT/OS cache state is uncontrolled and disclosed;
first round and first advances remain visible. No repeated horizon inside a
single state. Separately sample one fresh original session per fixture/engine
where supported, bracketed by original controls. Bound each worker to 30 s,
browser campaign to 300 s and setup to 420 s. No favorable-sample searching.
Report all samples, median, min/max, first-use outliers and paired overhead;
three rounds do not support population confidence intervals.

Record engine binary/version, Node/Playwright/protocol versions, timer resolution,
initial hash, checkpoint hashes, accepted time, requests, actual property counts,
original attempts, stage/iteration counts, growth proposals, rejection causes,
accepted half-steps and final state. Worker timing is separate from RTT/startup.
Public property counts are not CPU attribution and exclude lexical nested calls.

## Exact census and selective attribution

Per advance/attempt/solve reconstruct initial residual, all actual FD probes by
pressure/enthalpy/thermal column, used/branch-rejected/failed probe, line-search
factor/outcome, Jacobian assemblies, linear solves, stage completion, canonical
recovery, post-solve verification, recording and commit events. Reconcile residual
count = initial calls + FD probes + line-search candidates; explain any mismatch.
TR-BDF2 error control tries coarse and two half trials, each normally two stages.
Do not equate discarded coarse estimates or safety-preserving retries to waste.

Audit actual PH Map scope/key/lifetime; count residual PH requests, hits, misses,
real engine calls, nested saturation and independent M/U/V recovery. Preserve
exact keys and every failure. Trace repetition within/across residuals, iterations
and stages without implementing any reuse. Characterize the table inverse,
interpolation, validation and temporary allocations. A new cache is prohibited.

Exported timers and selective diagnostic-copy timers are inclusive. Never add
Newton/residual/property durations. A synchronous nested timer stack may assign
exclusive wrapper time only by subtracting directly nested measured children;
timer overhead remains inside that accounting. Otherwise report overlap and
unmeasured remainder explicitly. Sampling leaf/stack attribution is distinct
from inclusive elapsed timers; samples outside marked advances are excluded.
Linear solves are measured, not presumed dominant from O(n^3) at n=21. Detailed
thermal/fluid/normalization attribution is limited to actual observable boundaries.

## Validity, failure and stop rules

Within-engine require exact binary64 parity against original controls and saved
B9 hashes for all checkpoints, all state/record fields and original observer
attempts. Compare profiling metadata separately. Also hash original public
property input/output/throw sequence in diagnostic validation, without added calls.
Original decisions, settings, ledgers, phases, canonical recovery and budgets must
agree. Reject changed science or work; heavily instrumented time never estimates
intrinsic cost. Node does not replace either browser or physical Safari/iPad.

Reuse unchanged C1/B6/B9 bounded supported, transient/persistent synthetic failure,
record refusal, numerical stop, exact reference/bit rollback and independently
proven outward 200/400 K tests. Persistent case retains 20 attempts/19 halvings,
1e-9 minimum and original fault classification. Instrumentation must not repair a
refusal or convert it into a proven exit; worker termination is not rollback.

Classify costs as required numerical work, potentially redundant (precise future
equivalence obligation), diagnostic/presentation overhead or uncertain. Propose
at most five future hypotheses with all science/phase/FD/convergence/conservation/
rollback/reference/browser tests, justified upside and stop conditions. Implement
none. Retain all inherited backend, phase/topology, long-duration, nine-section,
production and physical-device blockers. Gates and final classification follow
the user contract; incomplete evidence requires PARTIAL or BLOCKED, never a
manufactured PASS. Commit/push only B9B, audit protected history/refs/PR #3 and stop
for explicit engineering review. Operator integration remains NO-GO.
