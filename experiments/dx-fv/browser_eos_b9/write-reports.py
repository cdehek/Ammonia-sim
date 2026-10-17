"""Generate report tables from audited observations. Timeout 30s."""
import csv,json
from pathlib import Path
B=Path(__file__).resolve().parent;E=B/'evidence'
p=json.loads((E/'performance-summary.json').read_text());s=json.loads((E/'scientific-audit.json').read_text());f=json.loads((E/'failure-lifecycle-audit.json').read_text())
def fmt(v):return f'{v:.2f}'
def text(n,s):(B/n).write_text(s)
parity='# Scientific parity matrix\n\nWithin each actual browser, main and worker use the same fourteen-file accepted package, fixtures, numerical settings, duration requests and reporting cadence. Full scientific values use binary64 bit tags. No per-section failure is averaged away.\n\n| Engine | Fixture | Checkpoints | Final accepted half-steps | Rejections | PH / SAT / MUV calls | Result |\n|---|---|---:|---:|---:|---|---|\n'
for engine,rows in s['sameEngine'].items():
 for r in rows:
  c=r['propertyCalls'];parity+=f"| {engine} | {r['fixture']} | 0/.0001/.0005/.001 s | {r['acceptedSteps'][-1]} | {r['rejectedSteps'][-1]} | {c['ph']} / {c['sat']} / {c['stateMVU']} | exact state/record/attempt parity |\n"
parity+='''
`parity-*-serialized.json.gz` contains all full state/record/attempt comparisons,
not just hashes. `scientific-audit.json` supplies section/aggregate/node and
independent signed thermal budgets. `node-baseline.json` independently verifies
direct original CommonJS versus the literal package. Timed runs check every
record/state against `frozen-browser-scientific-hashes.json` before completion.

| Scientific quantity | Same-engine result |
|---|---|
| Each section M/U/V, pressure guess | exact bits; volumes retained |
| Each recovered p/T/h/rho/u/phase/quality/wet/superheat | exact bits/values |
| Tube/fin/finite-air energies and temperatures | exact bits |
| Inlet/outlet signed fluxes; thermal links and refrigerant heat | exact bits |
| Section/total refrigerant and thermal ledgers | exact bits; original budgets pass |
| Newton iterations/residuals/FD/line-search; TR-BDF2 stages | complete observer attempts exact |
| Accepted steps, rejected counts, clocks and proposal history | exact values |
| Phase/boundary events, order/values, records and final state | exact values |
| Record after advance | exact original record; no state mutation |

Both short fixtures have EMPTY physical phase/boundary event lists. This proves
transport retains the observed ordering, not coverage of natural crossings,
scheduled 15/30-s events or every future physical event. Original event and
atomic commit code stays byte-identical. C1 tests independently retain accepted
event/clock history across refusals and test thermal outward-boundary proof.

Cross-engine values are not presumed bit-identical. The original accepted
coupled-browser limits are reapplied in `scientific-audit.json`. Maximum observed
cross-engine differences are '''
parity+=', '.join(f"{k}={max(r['differences'][k] for r in s['crossEngine']):.12g}" for k in ['pBar','hKJkg','fluidK','thermalK'])+'. All pass original limits. No full/long-duration A2 qualification follows.\n'
text('SCIENTIFIC_PARITY_MATRIX.md',parity)
perf='''# Performance and responsiveness

The worker materially improves main-thread responsiveness for the tested whole
five-section workloads. It does not make the calculations consistently faster.
All numbers below are actual local Chromium 151.0.7922.34 and desktop WPE WebKit
26.5 observations; none is a physical iPad forecast.

Final evidence is `benchmark-*-sealed.json.gz`, not the superseded preliminary
runs. Three interleaved matched rounds per engine use M/W, W/M, M/W order, never
simultaneous control/candidate physics. Each mode block has a fresh browser
context/page; each original fixture gets a new session and a warm restart. There
are 12 sessions and 36 advances per mode/engine. Every run uses 0/.0001/.0005/.001 s,
identical original settings, full diagnostic cadence, independent conservation
checks and its engine's frozen scientific hashes. UI renders actual accepted
snapshots and an independent automation task clicks the real acknowledgement
button during work.

Cold-session labels mean a new model session. Only the FIRST cold fixture in each
fresh mode page also has cold JS realm/import; the warm fixture's cold session
uses an already imported main module. Every replacement worker is a fresh JS
realm, even on warm restart. OS asset cache is warm/ uncontrolled; no cold-machine,
network download, JIT-steady-state or sustained throughput claim is made. Page
startup is outside per-command timing. Worker construction is separately sampled.

| Engine / mode | Init new-session median ms | Warm restart median ms | First renderable median ms | Physics heartbeat median / p95 / max ms | All-phase heartbeat p95 / max ms |
|---|---:|---:|---:|---|---|
'''
for engine,modes in p.items():
 for mode,x in modes.items():
  h=x['heartbeatByLargestOverlapMS']['physics'];a=x['allHeartbeatMS'];perf+=f"| {engine} {mode} | {fmt(x['initializationRoundtripMS']['cold-session']['median'])} | {fmt(x['initializationRoundtripMS']['warm-restart']['median'])} | {fmt(x['initializationComponentsMS']['firstRenderableMS']['median'])} | {fmt(h['median'])} / {fmt(h['p95'])} / {fmt(h['max'])} | {fmt(a['p95'])} / {fmt(a['max'])} |\n"
perf+='''
Heartbeat targets 10 ms; WebKit commonly rounds to 12 ms. A delayed callback is
assigned to the phase with largest overlap between its start/end and recorded
phase spans, so main-thread blocking is not mislabeled as the next phase.
Percentiles are descriptive nearest-rank observations, with unequal sample counts
because workers allow more callbacks. Phase and pooled samples are retained.

| Engine / mode | Cold per-advance median ms | Warm per-advance median ms | Cold simulated s / wall s | Warm simulated s / wall s |
|---|---:|---:|---:|---:|
'''
for engine,modes in p.items():
 for mode,x in modes.items():
  a=x['fixtures']['cold'];b=x['fixtures']['warm'];perf+=f"| {engine} {mode} | {fmt(a['advanceMS']['median'])} | {fmt(b['advanceMS']['median'])} | {a['throughputSimulatedSecondsPerWallSecond']['median']:.5f} | {b['throughputSimulatedSecondsPerWallSecond']['median']:.5f} |\n"
perf+='''
Throughput uses .001 s divided by SUM of the three original advance service times
for each run, then reports the median. It excludes deliberate heartbeat sampling
gaps, record requests and message roundtrip. It is short startup physics, not
long-duration real-time capability. The table reports each measured engine/fixture tradeoff; no intrinsic speedup
is claimed from these short startup workloads.

| Engine / mode | Automation input median / p95 / max ms | Browser input timestamp median / p95 / max ms | Record median ms | DOM render median ms |
|---|---|---|---:|---:|
'''
for engine,modes in p.items():
 for mode,x in modes.items():
  a=x['automationInputRoundtripMS'];b=x['browserInputTimestampLatencyMS'];rec=[v['recordMS']['median'] for v in x['fixtures'].values()];perf+=f"| {engine} {mode} | {' / '.join(fmt(a[k]) for k in ['median','p95','max'])} | {' / '.join(fmt(b[k]) for k in ['median','p95','max'])} | {min(rec):.2f}–{max(rec):.2f} | {fmt(x['renderMS']['median'])} |\n"
perf+='''
Worker input maxima still reach about 211/158 ms in Chromium/WebKit. Raw frame
evidence retains desktop WebKit startup/frame gaps up to 330 ms main / 354 ms
worker in the sealed run; worker execution does not guarantee smooth presentation.
Frame summaries exclude only the first per-session RAF timestamp (not an interval
between two callbacks); raw data retains it, including a negative Chromium
startup timestamp. Large later frame delays remain. Long-task API observations
are recorded where exposed; WebKit availability differs. Export/verification
formatting is outside the measured scientific interval; input clicks span that
work too, helping expose remaining stalls rather than hiding them.

## Initialization and transport

`performance-summary.json` preserves separate distributions for worker creation,
JS scientific import, table parsing/engine construction, model construction,
first valid state/record and first renderable snapshot. First valid scientific
state occurs after construction, before original record generation. Table mode
has no WASM fetch, compilation or CoolProp factory: those fields are inapplicable,
not zero-cost WASM measurements. Optional B7 init components remain separate.

Request postMessage cost, previous response postMessage cost, client handling,
service time, record time and RTT-minus-service are retained. One-way dispatch
and queue estimates use worker/main performance.timeOrigin+now and are upper
bounds, not isolated clone timings. Coarse clock rounding yields a few -0.1/-1-ms
estimates; raw negatives are retained, not clamped. The main-thread control also
clones its adapter boundary, ensuring the same detached scientific payload.

| Engine worker | Median RTT-minus-service ms | p95 / max ms | Median response post ms | p95 response post ms |
|---|---:|---|---:|---:|
'''
for engine,modes in p.items():
 x=modes['worker']['communicationMS'];r=x['roundtripMinusServiceUpperBoundMS'];q=x['previousWorkerPostMS'];perf+=f"| {engine} | {fmt(r['median'])} | {fmt(r['p95'])} / {fmt(r['max'])} | {fmt(q['median'])} | {fmt(q['p95'])} |\n"
perf+='''
Record JSON size estimates are about 9.5–11.9 KB. Full research advances also
transport exact accepted state and large observer traces; evidence bit-tag sizes
are separately recorded and are NOT structured-clone wire sizes. Browsers expose
no exact wire-size API here. No scientific input is reconstructed from JSON sizes.
Diagnostic copying, caching and structured-clone overhead are included in service
and roundtrip boundaries. FIFO/backpressure is bounded; current full diagnostic
payloads are unsuitable as a production rendering protocol.

## Supported/error sequence and lifecycle

Three additional interleaved rounds execute the SAME unchanged five-section C1
supported/transient/persistent/thermal sequence in each mode, with actual C1
wrapper synthetic faults and worker-internal rollback checks. This is synthetic
fault handling, not a naturally occurring plant EOS excursion.

| Engine / mode | Full C1 sequence median ms | Heartbeat max ms |
|---|---:|---:|
'''
for engine,modes in f['errorSequenceTiming'].items():
 for mode,x in modes.items():perf+=f"| {engine} {mode} | {fmt(x['sequenceMS']['median'])} | {fmt(x['heartbeatMS']['max'])} |\n"
perf+='''
## Memory and engineering decision

Table mode has no native state or WASM linear memory. `memory-*.json` observes
three main sessions followed by three worker sessions and actual navigation with
pending work. Summed browser-child RSS is coarse and double-counts shared pages;
it is not unique per-worker memory. Chromium page-ready/main-third-disposed/
worker-third-disposed observations are about 383.5/463.4/475.0 MiB; WebKit about
349.2/455.1/490.3 MiB. Worker creation/disposal does not immediately return the
whole process footprint. Chromium's page heap API remains a coarse 10 MB;
WebKit and worker-thread heap APIs are unavailable. No forced GC or leak proof.
Growth/high-water behavior remains an integration concern, not proof of a leak.

Optional unchanged B7 factories show 22,544,384 -> 56,360,960 bytes linear memory;
tested property operations remain at 56,360,960. Explicit Embind deletion and
native catch bookkeeping are separate evidence from that high-water size.

**GO for continued isolated worker research:** median/p95 interaction and physics
heartbeat improvements are material, with exact tested science. Startup, lower
throughput, diagnostic-copy cost and memory are acceptable for this bounded
investigation. **NO-GO FOR FURTHER INTEGRATION of this harness:** residual frame/
input stalls, non-real-time bounded throughput, coarse/high memory observations
and scientific qualification gaps do not support an operator-workstation change.
Gate 4 PASS means adequate evidence for that decision, not production readiness.
'''
text('PERFORMANCE_AND_RESPONSIVENESS.md',perf)
