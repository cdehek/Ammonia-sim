# Performance and responsiveness

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
| chromium main | 21.60 | 5.30 | 7.20 | 82.85 / 196.10 / 196.80 | 94.40 / 196.80 |
| chromium worker | 41.50 | 33.60 | 35.20 | 10.00 / 18.20 / 30.30 | 18.70 / 58.60 |
| webkit main | 20.00 | 7.00 | 7.50 | 95.50 / 181.00 / 187.00 | 113.00 / 187.00 |
| webkit worker | 55.50 | 35.50 | 38.00 | 12.00 / 15.00 / 39.00 | 15.00 / 39.00 |

Heartbeat targets 10 ms; WebKit commonly rounds to 12 ms. A delayed callback is
assigned to the phase with largest overlap between its start/end and recorded
phase spans, so main-thread blocking is not mislabeled as the next phase.
Percentiles are descriptive nearest-rank observations, with unequal sample counts
because workers allow more callbacks. Phase and pooled samples are retained.

| Engine / mode | Cold per-advance median ms | Warm per-advance median ms | Cold simulated s / wall s | Warm simulated s / wall s |
|---|---:|---:|---:|---:|
| chromium main | 36.15 | 76.15 | 0.00952 | 0.00394 |
| chromium worker | 36.65 | 94.30 | 0.00860 | 0.00321 |
| webkit main | 30.50 | 82.00 | 0.00901 | 0.00368 |
| webkit worker | 40.50 | 84.50 | 0.00625 | 0.00271 |

Throughput uses .001 s divided by SUM of the three original advance service times
for each run, then reports the median. It excludes deliberate heartbeat sampling
gaps, record requests and message roundtrip. It is short startup physics, not
long-duration real-time capability. The table reports each measured engine/fixture tradeoff; no intrinsic speedup
is claimed from these short startup workloads.

| Engine / mode | Automation input median / p95 / max ms | Browser input timestamp median / p95 / max ms | Record median ms | DOM render median ms |
|---|---|---|---:|---:|
| chromium main | 43.30 / 176.57 / 220.20 | 40.55 / 170.00 / 212.40 | 0.20–0.20 | 0.05 |
| chromium worker | 2.29 / 90.63 / 210.82 | 0.40 / 87.70 / 207.60 | 0.20–0.30 | 0.00 |
| webkit main | 47.78 / 159.45 / 230.42 | 46.00 / 148.00 / 229.00 | 0.00–0.00 | 0.00 |
| webkit worker | 4.62 / 57.62 / 158.26 | 1.00 / 54.00 / 156.00 | 0.00–0.50 | 0.00 |

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
| chromium | 7.85 | 27.50 / 34.70 | 0.45 | 5.20 |
| webkit | 5.00 | 24.00 / 40.00 | 1.00 | 8.00 |

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
| chromium main | 417.00 | 398.60 |
| chromium worker | 427.60 | 22.80 |
| webkit main | 743.00 | 731.00 |
| webkit worker | 886.00 | 40.00 |

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
