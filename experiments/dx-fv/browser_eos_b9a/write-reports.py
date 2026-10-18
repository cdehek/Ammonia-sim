"""Generate review reports from retained evidence; no browser or scientific execution."""
import csv,gzip,hashlib,json,math,statistics
from pathlib import Path
from openpyxl import Workbook
B=Path(__file__).resolve().parent;E=B/'evidence'
def read(n):
 p=E/n;return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def write(n,s):
 replacements={
 '8.15 ms Chromium and 4 ms WebKit':f"{P['chromium']['modes']['A']['communication']['rttMinusServiceAndHashMS']['median']-P['chromium']['modes']['B']['communication']['rttMinusServiceAndHashMS']['median']:.2f} ms Chromium and {P['webkit']['modes']['A']['communication']['rttMinusServiceAndHashMS']['median']-P['webkit']['modes']['B']['communication']['rttMinusServiceAndHashMS']['median']:.2f} ms WebKit",
 '238/242 ms':f"{P['webkit']['modes']['B']['frameIntervalsMS']['max']:.0f}/{P['webkit']['modes']['C']['frameIntervalsMS']['max']:.0f} ms",
 '17.90→4.22 ms':f"{P['chromium']['modes']['A']['automationInputMS']['p95']:.2f}→{P['chromium']['modes']['B']['automationInputMS']['p95']:.2f} ms",
 '16.21→11.75 ms':f"{P['webkit']['modes']['A']['automationInputMS']['p95']:.2f}→{P['webkit']['modes']['B']['automationInputMS']['p95']:.2f} ms",
 }
 for old,new in replacements.items():s=s.replace(old,new)
 (B/n).write_text(s.strip()+'\n')
def f(x):return f'{x:.2f}'
def triple(d):return '/'.join(f(d[k]) for k in ['median','p95','max']) if d else 'unavailable'
P=read('performance-summary.json');T=read('attribution-summary.json');S=read('scientific-audit.json')
for engine in ['chromium','webkit']:
 for fixture in ['cold','warm']:
  assert P[engine]['modes']['A']['fixtures'][fixture]['perAdvancePropertyCounts']==P[engine]['modes']['B']['fixtures'][fixture]['perAdvancePropertyCounts']==P[engine]['modes']['C']['fixtures'][fixture]['perAdvancePropertyCounts']
 for n in [f'failure-{engine}-fault-preserved.json.gz',f'lifecycle-{engine}.json.gz',f'startup-{engine}-receiver-fixed.json.gz']:
  d=read(n);assert d['passed'] and d['result']['passed']
 assert read(f'memory-{engine}.json')['passed']
perf=['# Performance, attribution and memory','',
'Final headline measurements use `benchmark-*-reviewed.json.gz` only. Three sequential interleaved rounds per engine, orders A/B/C, C/A/B, B/C/A; 12 sessions and 36 original advances per mode/engine. Original cold/warm fixtures, .0001/.0004/.0005 requested advances, checkpoints 0/.0001/.0005/.001 s, full original record cadence, settings and complete diagnostic generation are identical. Actual Chromium 151.0.7922.34 and desktop WPE WebKit 26.5; Playwright 1.62.0. Not physical Safari/iPad.', '',
'Fresh context per mode block. Every session/restart creates a fresh worker and original state. OS/network/module download caches are uncontrolled; labels mean fresh worker/model, never cold machine or sustained throughput. Hash verification runs after service timing, inside each worker, and is measured separately. Payload-size serialization is after heartbeat sampling. No JSON scientific transport. Mode A delegates to untouched B9 service; the B9A worker wrapper adds the same scientific hash guard used by compact modes.', '',
'| Engine/mode | New-session init median ms | Warm fresh-worker restart median ms | First renderable median ms | Input automation median/p95/max ms | Physics heartbeat median/p95/max ms | Frame median/p95/max ms |',
'|---|---:|---:|---:|---|---|---|']
for e in P:
 for m,r in P[e]['modes'].items():perf.append(f"| {e} {m} | {f(r['sessionInitRoundtripMS']['cold-session']['median'])} | {f(r['sessionInitRoundtripMS']['warm-restart']['median'])} | {f(r['firstRenderMS']['median'])} | {triple(r['automationInputMS'])} | {triple(r['heartbeatByPhaseMS']['physics'])} | {triple(r['frameIntervalsMS'])} |")
perf+=['','Input is an independent automation task clicking the actual fixed acknowledgement button approximately every 50 ms. Automation includes browser/driver delivery; event timestamp latency is a separate distribution in performance-summary.json. Samples are descriptive, unequal in number, nearest-rank p95; no confidence intervals or population guarantee. Phase assignment uses largest elapsed overlap, not callback-time labels. Frame intervals omit only the first timestamp in each session. WebKit compact frame maxima of 238/242 ms remain; input improvement does not establish uniformly smooth rendering.','',
'| Engine/mode | Original advance median ms | Cold sum median ms | Warm sum median ms | Cold simulated s/wall s | Warm simulated s/wall s | Advance RTT median ms |','|---|---:|---:|---:|---:|---:|---:|']
for e in P:
 for m,r in P[e]['modes'].items():
  a,b=r['fixtures']['cold'],r['fixtures']['warm'];perf.append(f"| {e} {m} | {f(r['advanceMS']['median'])} | {f(a['originalAdvanceSumMS']['median'])} | {f(b['originalAdvanceSumMS']['median'])} | {a['simulatedSecondsPerSolverWallSecond']['median']:.6f} | {b['simulatedSecondsPerSolverWallSecond']['median']:.6f} | {f(r['advanceRoundtripMS']['median'])} |")
perf+=['','Original advance includes trial/retry/commit and the mandatory final original record; it is not pure solver time. Throughput is .001 simulated seconds divided by SUM of the three original advance times, then median across sessions. End-to-end advance throughput is separately retained in JSON, including hash evidence overhead. Results do not demonstrate robust physics acceleration: some small medians improve, others regress; no numerical work is removed. No real-time or sustained capability is shown.','',
'| Engine/mode | Median advance JSON estimate bytes | Median RTT−service−hash ms | Previous response post median/p95/max ms | Cache copy median ms | Projection median ms |','|---|---:|---:|---|---:|---:|']
for e in P:
 for m,r in P[e]['modes'].items():perf.append(f"| {e} {m} | {r['payloadJSONEstimateBytes']['advance']['median']:.0f} | {f(r['communication']['rttMinusServiceAndHashMS']['median'])} | {triple(r['communication']['previousResponsePostMS'])} | {f(r['cacheCopyMS']['median']) if r['cacheCopyMS'] else 'original unsplit'} | {f(r['projectionMS']['median']) if r['projectionMS'] else 'control display extraction'} |")
perf+=['','These byte counts are estimates from detached result JSON, not wire or heap sizes. postMessage measures synchronous clone/enqueue, not isolated network transit. RTT residual includes cache cloning, dispatch, queues and handling; one-way upper bounds use realm clocks and may contain small negative rounding samples. The original A service has no isolated cache timer; full-response microbenchmarks below are not substituted as exact service components. No authoritative buffer is transferred. Main handling, DOM mutation, next-frame bounds, heartbeat phases, disposal, request post and hash timing all have separate distributions in performance-summary.json.','',
'For A→B, median combined communication overhead falls by 8.15 ms Chromium and 4 ms WebKit across measured commands. This is an observed combined-boundary saving, not an allocation of each millisecond to clone versus scheduling. The median advance payload falls from ~1.34 MB to ~2.4 KB; no throughput multiplier is inferred from that ratio. C does not provide a consistent additional benefit over B on this four-endpoint workload.','',
'## Pre-optimization component attribution','',
'Three interleaved uninstrumented/instrumented pairs per fixture, before compact implementation. Export wrappers and original residual callback delegate exactly once; full scientific values/attempts/property counts agree. Nested inclusive times overlap and must not be summed. Timers have material overhead.','',
'| Engine/fixture | Uninstrumented / instrumented advance sum median ms | Residual inclusive ms | Newton inclusive ms | engine.ph ms | engine.sat ms | engine.stateMVU ms | Attempt clone microbenchmark ms | Cache clone microbenchmark ms | Bit-tag / full comparison serialization microbenchmark ms |','|---|---|---:|---:|---:|---:|---:|---:|---:|---|']
for e in T:
 for fixture,a in T[e].items():
  c=a['inclusiveCostMS'];mi=a['microbenchmarkMS'];perf.append(f"| {e}/{fixture} | {f(a['uninstrumentedAdvanceSumMS']['median'])}/{f(a['instrumentedAdvanceSumMS']['median'])} | {f(c['residualInclusive']['median'])} | {f(c['NewtonInclusive']['median'])} | {f(c['engine.ph']['median'])} | {f(c['engine.sat']['median'])} | {f(c['engine.stateMVU']['median'])} | {f(mi['attemptClone']['median'])} | {f(mi['cacheClone']['median'])} | {f(mi['bitTag']['median'])}/{f(mi['fullComparisonSerialization']['median'])} |")
perf+=['','The observer callback push itself is at or below timer resolution; original event/record construction occurs outside that callback. Residual callbacks contain original thermodynamic and thermal calculations, but not the following Newton diagnostic event construction. The original solver/property/residual work therefore remains a major measured cost even without transport. Private FD/line-search loops, trial accounting, retry and atomic commit cannot be separately timed through public exports without editing source; exact original diagnostic event/work counts are retained instead. No isolated cost is claimed for those private loops.','',
'Newton timings include diagnostics and wrapper overhead. Original diagnostic construction is not independently isolated; Newton-minus-residual is not claimed as pure diagnostics. Thermodynamics PH/recovery and linear solve costs, callback costs, table/model initialization and all microbenchmark samples are in attribution-summary.json. Internal lexical sat calls inside engine.ph are included in PH and are not separately counted by exported sat timers. Full state cloning is ~0–0.1 ms at available timer resolution; large attempt arrays cost ~7–26 ms per microbenchmark clone. Expensive bit-tag/serialization is research evidence work outside the model advance, not thermodynamic solver work.','',
'Primary remaining bottleneck: **solver/property evaluation**, with material secondary diagnostic copying/transport. Evidence does not support diagnostic generation as the primary cause. Early-time nonlinear work is heavy and unchanged; no observation establishes all long-duration behavior.','',
'## Initialization investigation','',
'Separate startup-*-receiver-fixed.json.gz probes use 18 new workers per engine with three interleaved mode rounds and fresh-worker restarts. Script entry, dependency import/fetch/evaluation, scientific import, table parse/engine, model factory/create, initial record, receipt, DOM and next-frame upper bounds are separately recorded where interfaces permit. The dynamic bootstrap probe differs from the static normal worker; its import/evaluation boundary includes fetch/dependency work and is not pure CPU module evaluation. Normal-worker headline startup remains creation-to-first receipt/render above. No factory work is moved outside the measured interval. No persistent worker, shared mutable table, preloaded session or reused state is introduced.','']
for e in ['chromium','webkit']:
 rows=read(f'startup-{e}-receiver-fixed.json.gz')['result']['rows'];perf+=['| '+e+' mode | Script entry median ms | Dependency import/eval median ms | Creation→receipt median ms |','|---|---:|---:|---:|']
 for m in ['A','B','C']:
  rr=[r for r in rows if r['mode']==m];perf.append(f"| {m} | {statistics.median(r['creationToScriptStartMS'] for r in rr):.2f} | {statistics.median(r['serviceModuleImportAndEvaluationMS'] for r in rr):.2f} | {statistics.median(r['creationToReceiptMS'] for r in rr):.2f} |")
 perf+=['']
perf+=['A exposes table parsing plus engine construction together, and model factory/create together. B/C split table parse, engine, factory and create; component distributions remain in raw probe rows and normal matched initialization summaries. Module evaluation of the literal scientific registry is inside scientific import. No unsupported isolated table-only number is invented for A. Startup improvement is **INCONCLUSIVE**.','',
'## Bounded memory/cache investigation','',
'Three disposal/recreation cycles per mode/engine, first cycle fills exactly 256 response entries after the original .001 s physics workload, including eight explicit full-diagnostic requests. Exhausted advance refuses without changing .001 s; dispose remains possible. Actual navigation/pagehide during pending work creates a new uninitialized page. Detailed retrieval timing and bytes are retained in memory-*.json.','',
'| Engine/mode | Estimated cached result JSON bytes, stress cycle | RSS page-ready / active-full-cache / first-disposed / third-disposed MiB |','|---|---:|---|']
for e in ['chromium','webkit']:
 d=read(f'memory-{e}.json')
 for m in ['A','B','C']:
  cyc=next(c for c in d['cycles'] if c['mode']==m and c['cycle']==0);obs={r['label']:r['summedBrowserChildRSSBytes']/2**20 for r in d['observations'] if r['mode']==m};perf.append(f"| {e} {m} | {cyc['result']['approximateCacheJSONBytes']} | {' / '.join(f(obs[k]) for k in ['page-ready','0-active-cache','0-disposed','2-disposed'])} |")
perf+=['','The compact ordinary cache reduces this estimated payload sum by about 7.1 MB, but explicit full diagnostics dominate remaining cached bytes. JSON estimates omit requests, object/allocator overhead and initial response; they are not live graph measurements. RSS sums browser-child processes and double-counts shared pages. Heap is coarse Chromium-only page data; worker heap is unavailable. Garbage collection/high-water/process changes prevent a unique worker-memory or leak conclusion. Physical memory improvement is **INCONCLUSIVE**. Cache/evidence references are dropped and workers actually terminated; no immediate RSS-return promise follows.','',
'Mode B keeps cumulative observer history, so its generation/retention is still unbounded by simulation horizon; the authorized horizon here is tiny. Mode C caps endpoint evidence to four recent accepted versions, but attempts/bytes within one command are not hard-byte bounded. Neither mode solves arbitrary long-run diagnostic memory. The 256-entry cache also bounds count, not bytes; full-detail requests remain expensive. No production suitability follows.','',
'## Decision','',
'Communication and real-button latency tails improve; solver throughput, startup and physical-memory improvement are not established robustly. Further isolated research GO, operator integration NO-GO. Next: profile original residual/property workloads without changing Newton/TR-BDF2; separately test UI scheduling for WebKit frame tails. If extending duration is later authorized, require a byte-budgeted diagnostic-retention design first.']
perf+=['','## Explicit diagnostic API retrieval','',
'Additional retrieval-*.json.gz samples use three interleaved rounds and both frozen fixtures. B/C commands add no property calls. A cumulative diagnostics and B/C endpoint detail have different scopes and are not equal-work performance comparisons. All numbers below are service/roundtrip medians, with size estimates from detached JSON.','',
'| Engine/mode | Command | Service median ms | Roundtrip median ms | Payload estimate median bytes |','|---|---|---:|---:|---:|']
for e in ['chromium','webkit']:
 d=read(f'retrieval-{e}.json.gz');assert d['passed']
 for m in ['A','B','C']:
  rr=[s for r in d['rows'] if r['mode']==m for s in r['samples']]
  for command in sorted({r['type'] for r in rr}):
   ss=[r for r in rr if r['type']==command];perf.append(f"| {e} {m} | {command} | {statistics.median(r['serviceMS'] for r in ss):.2f} | {statistics.median(r['roundtripMS'] for r in ss):.2f} | {statistics.median(r['jsonEstimateBytes'] for r in ss):.0f} |")
write('PERFORMANCE_AND_MEMORY.md','\n'.join(perf))
write('SCIENTIFIC_PARITY_MATRIX.md','''# Scientific parity

PASS in actual Chromium and desktop WebKit. `scientific-audit.json` independently
compares B/C worker-owned evidence against untouched B9 main/worker controls.
Direct Node versus literal packaging also passes. No compact value reconstructs
scientific state.

| Engine | Fixture | A/B/C checkpoint clocks s | Final half-steps/rejections | Original PH/SAT/MUV counts |
|---|---|---|---|---|
| Chromium | cold | 0/.0001/.0005/.001 | 16/1 | 8476/9261/445 |
| Chromium | warm | 0/.0001/.0005/.001 | 34/3 | 22072/23752/940 |
| WebKit | cold | 0/.0001/.0005/.001 | 16/1 | 8476/9261/445 |
| WebKit | warm | 0/.0001/.0005/.001 | 34/3 | 22072/23752/940 |

Exact bits cover every original state field: all five M/U/V/pressure guesses,
recovered p/T/h/rho/u/phase/quality/wet, eleven thermal energies and temperatures,
all fluid/thermal fluxes and ledgers, counters, trial/FD/line-search histories,
settings, proposal/growth state, clock, schedule and event lists. Each compact
worker executes a separate unchanged B9 control and compares direct authoritative
state/record and original attempt arrays INSIDE its owning worker. C changes
retention only, with zero observer or physical-work count differences. Timed
runs additionally hash full state/record against B9's exact per-engine fixtures
inside the worker, outside service timing; every timed property-call vector
matches across A/B/C.

Original per-section and total mass <1e-8 kg, energy <1e-6 kJ, signed independent
thermal budgets, residual <=1e-11 and temporal acceptance <=1 pass at each point.
Original thermal closure 1e-12 K and all numerical settings are unchanged.
Cross-engine original limits pass separately in scientific-audit.json; engines
are not presumed bit-identical. Natural event lists are empty in these short
fixtures; scheduled long-time events and arbitrary phase crossings are not newly
qualified. Presentation mutation tests and detailed retrieval leave authoritative
state unchanged. Scientific-contract audit retains all inherited restrictions.

Use parityB/C-*-record-cadence.json.gz and baseline-*-export-fixed.json.gz.
Earlier compact parity receipts precede the extra original record-request cadence
and are superseded, not pooled. No sustained or complete A2 qualification.
''')
write('FAILURE_AND_LIFECYCLE_MATRIX.md','''# Failure, diagnostics and lifecycle

PASS for the bounded required subset in both actual engines. Final failure
receipts: failure-*-fault-preserved.json.gz. Lifecycle receipts: lifecycle-*.json.gz;
cache stress/navigation: memory-*.json. The unchanged original C1/B6 subset and
B9 exact/reference rollback tests are also rerun in main and worker.

| Test | Result |
|---|---|
| Original nonzero-exchange supported control | Exact accepted match and original ledgers |
| Transient synthetic property refusal | Two original rejected trials, halvings, recovery to .0011 s |
| Persistent inverse-recovery-failure | Numerical stop, physical exit unproved, original 20 attempts/19 halvings/floor |
| Synthetic returned-but-unqualified boundary | boundary-unresolved retained as numerical, never proven excursion |
| Original Newton/TR-BDF2/signed FD/line search | Unchanged source; Newton 30 and minStep 1e-9 |
| Every rejected trial | Exact physical bits and original cells/energies/ledger references in worker |
| Failed accepted-state record | Refusal with recordFailure, no returned property state, immediate current fault, prior display stale |
| Genuine independent 200/400 K outward exit | Original independent recheck proves thermal domain stop; exact rollback |
| Diagnostic detail after failure | Correct requested version, complete current attempts and safe fault evidence |
| Repeat command after stop | Explicit refusal; complete current fault history remains retained |
| Cached failed command | Same error/result/clock; no second solve or downgrade |
| Duplicate advance, pending and completed | Single execution; M/U/V/events/property counters unchanged on replay |
| Altered duplicate, order, stale version | Explicit refusal before physics |
| Equal-version stale response | Cannot clear newer relevant fault or install older display |
| Old/replaced session | Ignored; no pending callback installs new-session data |
| Diagnostic expiration | Explicit unavailable/expired with retained versions; no invented trace |
| Eight-pending bound | Ninth request rejected locally |
| 256-response exhaustion | New work refused, sequence consumed, disposal still succeeds |
| Scheduling stop during advance | Original synchronous advance completes before stop acknowledgement |
| Dispose after work/failure | Acknowledged last clock; cache/evidence/model references dropped; worker terminated |
| Fresh restart | Exact original initial state; no mutated state reused |
| Crash/module fetch failure/termination | Pending rejects; last received state only, in-flight acceptance unknown |
| Actual navigation/unmount | pagehide destroys worker; new page uninitialized |

Synthetic C1 evidence is failure-handling evidence, not natural EOS reachability.
Numerical refusal never becomes successful refrigerant recovery or a physical
trip. The table-backend identity is retained; test-only C1 scenario arguments and
proof explicitly identify the unchanged C1 error-handling factory and synthetic
injection. Test commands are disabled in ordinary sessions. Native B7 execution
is deferred; original B6 cleanup/B7 artifacts are hash verified, not requalified.

The disposal response itself may be cached as a small tombstone; prior scientific
cache entries are cleared. A diagnostic entry for an already stopped version is
pinned by refusing new advance commands; an empty attempt list cannot overwrite
its fault history. Emergency termination is destruction, never solver rollback.
''')
write('WORKER_PROTOCOL_REVIEW.md','''# Protocol, ownership and diagnostic retrieval

Protocol 1 retains unique session/worker/backend/request identity, strict command
sequence, clock, acceptedVersion, status, explicit success/refusal and safe error.
B/C add mode and diagnosticScope; A delegates original semantics untouched.
Worker owns original conserved state and solver. Presentation and evidence are
detached and cannot be applied as state. No authoritative ArrayBuffer transfer.

| Command | Supported boundary |
|---|---|
| initialize | Original package/engine/factory/create/record, one session |
| advance | Same original advance and complete diagnostic generation; compact response in B/C |
| snapshot | Same original model.record cadence as B9; compact B/C response |
| snapshotCompact | Projection of retained current original record; no invented model API |
| diagnosticsSummary(version) | Requested endpoint availability/counts/fault; explicit expiration |
| diagnosticsDetail(version) | Detached original record/attempts; full state only if current |
| diagnostics | Cumulative B history; C discloses four recent endpoint scopes |
| stop | Scheduling latch at original synchronous boundary; not physical trip |
| dispose | Clear ownership/cache/evidence then terminate |
| testEvidence | Only test-enabled sessions; in-owner reference parity/rollback proofs |

Detail requests require an explicit integer version. Envelope clock/version are
current owner metadata; result clock/version explicitly identify requested
historic evidence. Historic full scientific state is not retained and is returned
as null with stateScope; current state is cloned only on explicit detail retrieval.
Expired endpoint records return available:false, reason:unavailable/expired. They
do not silently substitute a newer version. A later refusal at the same accepted
version replaces that endpoint's status/evidence with current failure information.

B retains cumulative original attempts in worker ownership plus four endpoint
record/attempt scopes. C generates identical original diagnostics but retains four
recent endpoint scopes, discarding expired history explicitly. Observer remains
enabled, trace:true; no acceptance/check/FD/line-search/property call is skipped.
Generation is not optimized. Four endpoints are a count bound, not a byte bound.

Duplicate IDs use bit-exact original content comparison. Up to 256 detached
responses are cached, no eviction/reexecution: identical replay returns original
outcome; altered content refuses. Exhaustion consumes valid sequence and refuses
new work; dispose exempt. Client bounds eight pending requests; 30-s deadline
loses/terminates disposable session with unknown in-flight acceptance. No retry
with a new ID after an uncertain advance. Cache hits cannot mutate authority.

Display acceptance checks session, worker, backend, pending request/type/sequence,
then monotonic acceptedVersion AND sequence. New refusal immediately marks prior
readings stale and stores current fault. Older same-version snapshots cannot clear
it. The panel also ignores older display-sequence results. Successful command
receipt is distinct from numerical status; a returned record with stop is displayed
as numerical-stop or physical-domain-stop, not running. No live Error, pointer,
module handle or native exception ownership crosses the safe diagnostic envelope.

Source review: the original observer is optional, receives freshly constructed
work diagnostics and its return is unused. Callback exceptions propagate outside
probe classification. Diagnostic records contain copied residual/state scalars
and context arrays, not authoritative conserved objects. B/C only push evidence;
neither disables observer nor changes settings. Source remains literal. The
instrumented attribution loader wraps exported call boundaries before dependent
modules evaluate, delegates exactly once and passes exact full-work comparison.
''')
write('ENGINEERING_REPORT.md','''# B9A engineering decision

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
8.15 ms Chromium and 4 ms WebKit across commands; ordinary advance JSON estimates
fall ~1.34 MB→2.4 KB. End-to-end advance sums improve in the measured samples
(see per-fixture distributions), but numerical work remains identical and solver
throughput does not consistently improve. Do not convert payload ratios into a
speedup. The original uninstrumented .001-s workload still consumes roughly
64–235 ms in the initial attribution pairs, plus transport/copying; this is heavy
early-time work, not a sustained real-time result. Browser scheduling remains a
secondary concern: WebKit compact frame gaps reach 238/242 ms.

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
''')
write('MECHANICS_REPORT.md','''# Mechanic’s Report

The old worker sends a laboratory notebook with every gauge reading: refrigerant
inventory, thermal ledgers, thousands of Newton derivative/line-search records
and full model state. An operator needs a small set of honest readings, not that
whole notebook on every refresh. The compact view carries five section pressures,
temperatures, masses and energies, coil-metal/air temperatures, clock and fault
status. Detailed evidence stays available by accepted-state version.

Changing the gauge face cannot change how much ammonia or energy is in a section.
The worker keeps the exact original mass, internal energy and volume and performs
the same accepted property, conservation and numerical checks. Display values
never rebuild or update refrigerant inventory. Wet is the modeled bulk indication,
not a compressor protection or safe-suction signal.

Smaller messages improved measured button-response tails in both browsers.
Chromium A→B automation p95 went 17.90→4.22 ms; WebKit 16.21→11.75 ms. It did not
make the underlying physics reliably faster. WebKit still had long frame gaps.
The main remaining expense is the original nonlinear/property work, with extra
cost from laboratory trace copying and traffic. This .001-second workload says
nothing about sustained real-time plant simulation.

When an ammonia property calculation refuses, the model keeps its last accepted
inventory, follows the original retries/halvings and reports the actual numerical
fault. A failed accepted-state record is unavailable; the panel marks the older
reading stale. Only independently proven modeled thermal exits keep their distinct
physical-domain meaning. Less diagnostic traffic cannot make an unresolved fluid
state valid. Synthetic fault tests prove handling, not natural EOS reachability.

The worker is **not ready for operator-workstation integration**. Exact tested
science and useful communication savings justify more isolated engineering work;
remaining frame behavior, startup/memory uncertainty and scientific qualification
gaps still require review. No plant alarm, valve, receiver level, compressor
measurement or safety trip has been invented.
''')
write('MECHANICS_REPORT.md',(B/'MECHANICS_REPORT.md').read_text())
write('NEXT_MILESTONE_RECOMMENDATION.md','''# Prioritized next milestone

1. GO for separately authorized profiling of the unchanged accepted solver/property
   and residual workload. Isolate intrinsic property work from validation/caching
   and instrumentation overhead; preserve exact inputs/decisions. No Newton,
   TR-BDF2, tolerance, phase or EOS change is authorized here.
2. Investigate WebKit presentation scheduling and byte-budgeted evidence/cache
   retention as separate narrow architecture questions. Retain current failure
   evidence and explicit expiration before any longer workload is proposed.
3. Preserve the accepted-model/backend qualification backlog. Inventory existing
   evidence before authorizing missing full/long-duration A2 or physical-device
   qualification. Do not repeat a full campaign by default.

Operator-workstation integration NO-GO. Do not automatically start any item.
B7 optional execution deferred. Original B5A/B7 unresolved endpoints, DP cases,
35-bar refusals, inward hazards and exact-inventory phase certification remain
unresolved. No EOS repair is selected from communication results.
''')
write('EXECUTION_NOTES.md','''# Execution notes and retained failed attempts

- Workspace had no checkout. Initial clone without sandbox network permission
  failed at proxy; the supported network-enabled tool call succeeded. No proxy,
  network policy or credential bypass. Clean detached exact B9 was recorded.
- Browser setup reused B9's pinned six local Debian packages and Playwright
  Chromium/WebKit downloads, extracted under /workspace/b9-runtime; no host install.
- Design/audit commit c95a931 precedes attribution code and compact implementation.
  Attribution completed in both engines before compact implementation. Its decision
  receipt retains the evidence-based choice. B passed before C execution; C never
  disabled observer or diagnostic generation.
- baseline-chromium.json.gz failed exporting already-executed parity because the
  B9A values re-export was missing. Both baseline-*-export-fixed receipts pass.
- Original compact parity passed, then full B9 extra record-request cadence and
  original cumulative property-count comparisons were added. Use record-cadence
  receipts. No numerical options or frozen workload changed.
- benchmark-chromium-sealed.json.gz failed a hash encoding guard: B used object
  key order state/record instead of B9 record/state. Direct full-value parity
  passed independently. Corrected encoding-fixed campaign passes both engines;
  it is superseded by final matched results, not pooled.
- Final failure-history review found new advance after a stopped model could
  overwrite its retained endpoint with empty attempts. The protocol now refuses
  that command, preserving complete fault history. failure-*-retained-stop passes.
  Final matched campaign follows this fix; no accepted solver source changed.
- The separate startup bootstrap initially installed its message receiver after
  awaiting dynamic import; the first message could be lost and the 30-s deadline
  fired. Failed startup-chromium receipt remains. The separate probe now installs
  the receiver first and queues import; both receiver-fixed receipts pass.
- Only experiment.mjs's extra startup dispatch and analyze.py's receipt
  selection changed after timed-source-manifest-retention-fixed. Measured workload,
  worker, client, projection and panel are unchanged. A subsequent refusal-envelope
  review additionally preserves the current numerical fault on altered-duplicate
  refusal. Both fault-preserved failure receipts pass; the reviewed matched campaign
  follows this fix and is sealed by benchmark-source-manifest-reviewed.json. Later reports/build/
  audit/startup-probe files do not alter the measured path.
- All failed/superseded receipts remain. No scientific mismatch, swallowed
  numerical error, acceptance relaxation or protected-source edit was observed.
  Private function costs remain explicitly unisolated; memory remains coarse.
- B7 execution deferred. Existing scientific artifact hashes including compressed
  native archive identities were verified; no CoolProp build or EOS modification.
- Per-command 30 s deadlines; scientific stages 240 s, matched campaign 300 s,
  startup 180 s, memory 240 s, setup 420 s, direct Node 30 s, build/audit 120 s.
  Timeouts never alter physical input or numerical acceptance.
''')
write('README.md','''# B9A compact-worker research

**B9A COMPACT-WORKER FEASIBILITY PASS. Operator integration NO-GO.**

Exact start B9 b1a65c9365879d6e97eff649e56371df3907e86e; isolated branch
research/browser-eos-b9a-compact-worker-optimization-20261017. All additions are
under this directory. Accepted A2 be9eb35a4ddf5098e685182f8104685127c6a6ee and all
historical sources remain byte-identical. Pre-optimization design commit c95a931.

A uses untouched B9 full diagnostics. B uses compact ordinary messages with the
same complete diagnostic generation and cumulative worker history. C keeps the
same generation with four recent endpoint scopes and explicit expiration. Worker
retains scientific authority. Explicit diagnostics do not reconstruct physics.

Read ENGINEERING_REPORT.md, PERFORMANCE_AND_MEMORY.md, SCIENTIFIC_PARITY_MATRIX.md,
FAILURE_AND_LIFECYCLE_MATRIX.md and MECHANICS_REPORT.md. Contracts are in
COMPACT_SNAPSHOT_CONTRACT.md, snapshot-schema.json and WORKER_PROTOCOL_REVIEW.md.
Evidence includes full M/U/V/thermal ledgers, original traces/work counts,
original/compact C1 failures, cache/lifecycle, actual browsers, startup and memory.
Tracker status is available as CSV, JSON and Excel. B7 execution is deferred.

From repository root, using Python with Playwright 1.62.0, psutil and openpyxl:

```sh
timeout 420 python3 experiments/dx-fv/browser_eos_b9a/setup-browsers.py
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/build.py
timeout 30 node experiments/dx-fv/browser_eos_b9a/node-baseline.mjs
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage baseline --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage attribution --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage parityB --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage parityC --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage failure --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage lifecycle --tag=-reproduce
timeout 300 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage benchmark --tag=-reproduce
timeout 180 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage startup --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/memory-lifecycle.py --tag=-reproduce
timeout 180 python3 experiments/dx-fv/browser_eos_b9a/run-retrieval.py --tag=-reproduce
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/analyze.py
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/write-reports.py
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/audit.py
```

Runner refuses to overwrite an existing receipt: select a new tag. Analysis uses
retained final receipts by name; change selection explicitly to analyze a new
campaign. Memory script accepts --tag to preserve existing receipts. Retrieval script also
refuses existing receipts; use its --tag option for reproduction. All browser work is
sequential. Static preview: serve repository root with python3 -m http.server and
open /experiments/dx-fv/browser_eos_b9a/index.html. No deployed website or production
UI is changed. Runtime/provenance and failed-attempt notes are retained.

No full qualification, sustained real-time, EOS repair, production integration,
merge/deployment or physical iPad claim. Stop for explicit engineering review.
''')
status=dict(classification='B9A COMPACT-WORKER FEASIBILITY PASS',gates={str(i):'PASS' for i in range(1,5)},scientificParity='PASS',failureRollback='PASS',responsivenessImprovement='YES',physicsThroughputImprovement='INCONCLUSIVE',startupImprovement='INCONCLUSIVE',memoryImprovement='INCONCLUSIVE',furtherIsolatedResearch='GO',operatorWorkstationIntegration='NO-GO',remainingPrimaryBottleneck='Solver/property evaluation',secondaryBottlenecks=['Diagnostic copying','Message transport','Browser scheduling/rendering'],B7Execution='DEFERRED',completeA2Qualification=False)
(B/'milestone-status.json').write_text(json.dumps(status,indent=2)+'\n')
rows=[['item','status','qualification']]+[[k,json.dumps(v) if isinstance(v,(dict,list)) else str(v),'Bounded B9A research only'] for k,v in status.items()]
with (B/'milestone-status.csv').open('w',newline='') as out:csv.writer(out).writerows(rows)
w=Workbook();s=w.active;s.title='B9A status'
for row in rows:s.append(row)
s.freeze_panes='A2';s.auto_filter.ref=s.dimensions;s.column_dimensions['A'].width=40;s.column_dimensions['B'].width=75;s.column_dimensions['C'].width=40;blockers=w.create_sheet('Inherited B8 blockers')
with (E/'inherited-B8-issue-priorities.csv').open(newline='') as source:
 for row in csv.reader(source):blockers.append(row)
blockers.freeze_panes='A2';blockers.auto_filter.ref=blockers.dimensions
w.save(B/'milestone-status.xlsx')
print('Generated B9A review reports and CSV/JSON/Excel tracker')
