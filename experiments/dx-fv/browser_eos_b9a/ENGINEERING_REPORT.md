# B9A engineering decision

**B9A COMPACT-WORKER FEASIBILITY PASS**

All four bounded engineering gates PASS. Compact presentation and explicit
versioned diagnostics preserve original accepted-table science and failure
semantics in Chromium and desktop WebKit. This is an isolated research result.

| Required decision | Result |
|---|---|
| Scientific parity | PASS |
| Failure/rollback | PASS |
| Responsiveness improvement demonstrated | YES — real-button latency tails; no uniform frame-smoothness claim |
| Physics throughput improvement demonstrated | INCONCLUSIVE |
| Startup improvement demonstrated | INCONCLUSIVE |
| Memory improvement demonstrated | INCONCLUSIVE — estimated cache payload smaller; physical memory unresolved |
| Further isolated research | GO |
| Operator-workstation integration | NO-GO |

| Gate | Evidence |
|---|---|
| 1 Baseline/attribution verified — PASS | Exact clean B9 start, 2545 historical hashes, fourteen A2 Git identities, literal package, original main/worker reproduction; pre-edit design c95a931; real component timers and overhead pairs |
| 2 Compact scientific parity — PASS | Both original fixtures/checkpoints; direct full state/record/attempt comparisons inside each compact worker, original property counts/budgets; timed full-state hash guards |
| 3 Failure/lifecycle integrity — PASS | Original C1 subset, exact rollback, failure detail/replay, proven thermal exits, version expiration, stale/duplicate/stop/dispose/restart/crash/navigation/cache stress |
| 4 Browser decision — PASS | Three matched interleaved rounds in both browsers; service/property/diagnostic/copy/transport/startup/input/frame and coarse memory evidence, explicit limitations |

**Remaining primary bottleneck: solver/property evaluation**, with material
secondary diagnostic copying and transport. Instrumented original residual work
consumes most of the containing advance; exported property calls are substantial.
The observer push is negligible at available resolution. Private diagnostic event
construction is not independently isolated, so no exact diagnostic-generation
percentage is claimed. Timing wrappers have measurable overhead and are absent
from headline runs. Complete diagnostics are generated in every mode.

How much improvement comes from communication? A→B median RTT−service−hash falls
8.75 ms Chromium and 4.00 ms WebKit across commands; ordinary advance JSON estimates
fall ~1.34 MB→2.4 KB. End-to-end advance sums improve in the measured samples
(see per-fixture distributions), but numerical work remains identical and solver
throughput does not consistently improve. Do not convert payload ratios into a
speedup. The original uninstrumented .001-s workload still consumes roughly
64–235 ms in the initial attribution pairs, plus transport/copying; this is heavy
early-time work, not a sustained real-time result. Browser scheduling remains a
secondary concern: WebKit compact frame gaps reach 247/241 ms.

Mode B removes routine full-state/attempt transport and duplicate full-response
cache copies while retaining original full diagnostic generation in worker
ownership. Mode C only bounds recent endpoint retention; it does not reduce
observer generation or qualify a reduced-audit run. The short four-endpoint
benchmark cannot establish long-duration retention behavior. Full-detail cached
responses remain expensive; cache count is bounded, byte footprint is not.

No startup optimization was adopted: no persistent/preloaded worker, moved factory
cost, reused mutated state or source/table change. Separate startup probes provide
component evidence but differ from normal static-worker loading. Physical memory
remains coarse/unresolved despite lower estimated cached result bytes.

Next milestone: separately authorized **scientific performance profiling** of
unchanged residual/property workloads, beginning with sampling and exact work
attribution; do not modify Newton/TR-BDF2 under B9A. A narrow separate WebKit UI
scheduling study should address frame tails. Any future longer run needs explicit
byte-budgeted diagnostic/cache retention with fault preservation first. B7
compatibility execution was deferred; artifacts/cleanup identities are preserved.
All historical backend, phase, long-duration, nine-section and device blockers
remain. No EOS repair, acceptance relaxation, production/UI/Live Plant edit,
merge, deployment, full A2 campaign or iPad testing. Stop for engineering review.
