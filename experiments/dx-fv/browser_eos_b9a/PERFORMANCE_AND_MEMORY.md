# Performance, attribution and memory

Final headline measurements use `benchmark-*-reviewed.json.gz` only. Three sequential interleaved rounds per engine, orders A/B/C, C/A/B, B/C/A; 12 sessions and 36 original advances per mode/engine. Original cold/warm fixtures, .0001/.0004/.0005 requested advances, checkpoints 0/.0001/.0005/.001 s, full original record cadence, settings and complete diagnostic generation are identical. Actual Chromium 151.0.7922.34 and desktop WPE WebKit 26.5; Playwright 1.62.0. Not physical Safari/iPad.

Fresh context per mode block. Every session/restart creates a fresh worker and original state. OS/network/module download caches are uncontrolled; labels mean fresh worker/model, never cold machine or sustained throughput. Hash verification runs after service timing, inside each worker, and is measured separately. Payload-size serialization is after heartbeat sampling. No JSON scientific transport. Mode A delegates to untouched B9 service; the B9A worker wrapper adds the same scientific hash guard used by compact modes.

| Engine/mode | New-session init median ms | Warm fresh-worker restart median ms | First renderable median ms | Input automation median/p95/max ms | Physics heartbeat median/p95/max ms | Frame median/p95/max ms |
|---|---:|---:|---:|---|---|---|
| chromium A | 36.85 | 33.85 | 34.95 | 2.34/24.38/68.88 | 10.00/19.30/26.00 | 16.70/16.70/16.80 |
| chromium B | 39.95 | 35.80 | 36.65 | 2.16/4.41/7.24 | 10.00/14.80/23.90 | 16.70/16.70/16.80 |
| chromium C | 38.60 | 36.00 | 38.30 | 2.02/5.13/6.25 | 10.00/17.90/23.00 | 16.70/16.80/16.80 |
| webkit A | 42.50 | 30.50 | 32.50 | 3.22/12.82/24.90 | 12.00/14.00/29.00 | 16.00/19.00/228.00 |
| webkit B | 56.00 | 33.00 | 35.50 | 2.76/9.99/25.74 | 12.00/13.00/34.00 | 16.00/20.00/247.00 |
| webkit C | 51.00 | 32.00 | 34.00 | 2.73/9.63/25.02 | 12.00/14.00/24.00 | 16.00/19.00/241.00 |

Input is an independent automation task clicking the actual fixed acknowledgement button approximately every 50 ms. Automation includes browser/driver delivery; event timestamp latency is a separate distribution in performance-summary.json. Samples are descriptive, unequal in number, nearest-rank p95; no confidence intervals or population guarantee. Phase assignment uses largest elapsed overlap, not callback-time labels. Frame intervals omit only the first timestamp in each session. WebKit compact frame maxima of 247/241 ms remain; input improvement does not establish uniformly smooth rendering.

| Engine/mode | Original advance median ms | Cold sum median ms | Warm sum median ms | Cold simulated s/wall s | Warm simulated s/wall s | Advance RTT median ms |
|---|---:|---:|---:|---:|---:|---:|
| chromium A | 57.60 | 104.75 | 291.85 | 0.009547 | 0.003426 | 79.55 |
| chromium B | 64.60 | 102.75 | 255.15 | 0.009741 | 0.003919 | 65.80 |
| chromium C | 59.05 | 91.60 | 262.15 | 0.010920 | 0.003815 | 60.30 |
| webkit A | 63.00 | 121.00 | 299.50 | 0.008321 | 0.003342 | 81.00 |
| webkit B | 67.00 | 108.50 | 314.00 | 0.009226 | 0.003186 | 69.00 |
| webkit C | 69.00 | 124.00 | 290.50 | 0.008141 | 0.003442 | 72.00 |

Original advance includes trial/retry/commit and the mandatory final original record; it is not pure solver time. Throughput is .001 simulated seconds divided by SUM of the three original advance times, then median across sessions. End-to-end advance throughput is separately retained in JSON, including hash evidence overhead. Results do not demonstrate robust physics acceleration: some small medians improve, others regress; no numerical work is removed. No real-time or sustained capability is shown.

| Engine/mode | Median advance JSON estimate bytes | Median RTT−service−hash ms | Previous response post median/p95/max ms | Cache copy median ms | Projection median ms |
|---|---:|---:|---|---:|---:|
| chromium A | 1336772 | 9.05 | 0.80/11.70/15.50 | original unsplit | control display extraction |
| chromium B | 2408 | 0.30 | 0.00/0.10/0.20 | 0.00 | 0.10 |
| chromium C | 2408 | 0.30 | 0.00/0.10/0.30 | 0.00 | 0.10 |
| webkit A | 1345674 | 4.00 | 1.00/10.00/14.00 | original unsplit | control display extraction |
| webkit B | 2397 | 0.00 | 0.00/2.00/4.00 | 0.00 | 0.00 |
| webkit C | 2397 | 1.00 | 0.00/1.00/1.00 | 0.00 | 0.00 |

These byte counts are estimates from detached result JSON, not wire or heap sizes. postMessage measures synchronous clone/enqueue, not isolated network transit. RTT residual includes cache cloning, dispatch, queues and handling; one-way upper bounds use realm clocks and may contain small negative rounding samples. The original A service has no isolated cache timer; full-response microbenchmarks below are not substituted as exact service components. No authoritative buffer is transferred. Main handling, DOM mutation, next-frame bounds, heartbeat phases, disposal, request post and hash timing all have separate distributions in performance-summary.json.

For A→B, median combined communication overhead falls by 8.75 ms Chromium and 4.00 ms WebKit across measured commands. This is an observed combined-boundary saving, not an allocation of each millisecond to clone versus scheduling. The median advance payload falls from ~1.34 MB to ~2.4 KB; no throughput multiplier is inferred from that ratio. C does not provide a consistent additional benefit over B on this four-endpoint workload.

## Pre-optimization component attribution

Three interleaved uninstrumented/instrumented pairs per fixture, before compact implementation. Export wrappers and original residual callback delegate exactly once; full scientific values/attempts/property counts agree. Nested inclusive times overlap and must not be summed. Timers have material overhead.

| Engine/fixture | Uninstrumented / instrumented advance sum median ms | Residual inclusive ms | Newton inclusive ms | engine.ph ms | engine.sat ms | engine.stateMVU ms | Attempt clone microbenchmark ms | Cache clone microbenchmark ms | Bit-tag / full comparison serialization microbenchmark ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| chromium/cold | 75.50/99.70 | 89.50 | 95.20 | 30.50 | 2.90 | 0.70 | 10.00 | 9.60 | 64.40/68.30 |
| chromium/warm | 231.30/265.40 | 235.10 | 246.90 | 118.90 | 7.90 | 7.20 | 25.70 | 25.30 | 174.90/204.40 |
| webkit/cold | 64.00/75.00 | 61.00 | 69.00 | 29.00 | 4.00 | 1.00 | 7.00 | 7.00 | 40.00/44.00 |
| webkit/warm | 235.00/242.00 | 212.00 | 230.00 | 132.00 | 6.00 | 5.00 | 19.00 | 18.00 | 108.00/125.00 |

The observer callback push itself is at or below timer resolution; original event/record construction occurs outside that callback. Residual callbacks contain original thermodynamic and thermal calculations, but not the following Newton diagnostic event construction. The original solver/property/residual work therefore remains a major measured cost even without transport. Private FD/line-search loops, trial accounting, retry and atomic commit cannot be separately timed through public exports without editing source; exact original diagnostic event/work counts are retained instead. No isolated cost is claimed for those private loops.

Newton timings include diagnostics and wrapper overhead. Original diagnostic construction is not independently isolated; Newton-minus-residual is not claimed as pure diagnostics. Thermodynamics PH/recovery and linear solve costs, callback costs, table/model initialization and all microbenchmark samples are in attribution-summary.json. Internal lexical sat calls inside engine.ph are included in PH and are not separately counted by exported sat timers. Full state cloning is ~0–0.1 ms at available timer resolution; large attempt arrays cost ~7–26 ms per microbenchmark clone. Expensive bit-tag/serialization is research evidence work outside the model advance, not thermodynamic solver work.

Primary remaining bottleneck: **solver/property evaluation**, with material secondary diagnostic copying/transport. Evidence does not support diagnostic generation as the primary cause. Early-time nonlinear work is heavy and unchanged; no observation establishes all long-duration behavior.

## Initialization investigation

Separate startup-*-receiver-fixed.json.gz probes use 18 new workers per engine with three interleaved mode rounds and fresh-worker restarts. Script entry, dependency import/fetch/evaluation, scientific import, table parse/engine, model factory/create, initial record, receipt, DOM and next-frame upper bounds are separately recorded where interfaces permit. The dynamic bootstrap probe differs from the static normal worker; its import/evaluation boundary includes fetch/dependency work and is not pure CPU module evaluation. Normal-worker headline startup remains creation-to-first receipt/render above. No factory work is moved outside the measured interval. No persistent worker, shared mutable table, preloaded session or reused state is introduced.

| chromium mode | Script entry median ms | Dependency import/eval median ms | Creation→receipt median ms |
|---|---:|---:|---:|
| A | 7.55 | 5.35 | 35.30 |
| B | 7.35 | 4.70 | 37.70 |
| C | 6.00 | 6.15 | 32.50 |

| webkit mode | Script entry median ms | Dependency import/eval median ms | Creation→receipt median ms |
|---|---:|---:|---:|
| A | 9.00 | 2.00 | 34.50 |
| B | 7.00 | 2.00 | 31.50 |
| C | 8.50 | 1.50 | 32.50 |

A exposes table parsing plus engine construction together, and model factory/create together. B/C split table parse, engine, factory and create; component distributions remain in raw probe rows and normal matched initialization summaries. Module evaluation of the literal scientific registry is inside scientific import. No unsupported isolated table-only number is invented for A. Startup improvement is **INCONCLUSIVE**.

## Bounded memory/cache investigation

Three disposal/recreation cycles per mode/engine, first cycle fills exactly 256 response entries after the original .001 s physics workload, including eight explicit full-diagnostic requests. Exhausted advance refuses without changing .001 s; dispose remains possible. Actual navigation/pagehide during pending work creates a new uninitialized page. Detailed retrieval timing and bytes are retained in memory-*.json.

| Engine/mode | Estimated cached result JSON bytes, stress cycle | RSS page-ready / active-full-cache / first-disposed / third-disposed MiB |
|---|---:|---|
| chromium A | 27338502 | 385.57 / 538.56 / 503.91 / 518.01 |
| chromium B | 20217052 | 393.37 / 533.22 / 515.78 / 518.71 |
| chromium C | 20217196 | 393.75 / 532.15 / 514.79 / 518.09 |
| webkit A | 27348458 | 364.15 / 497.64 / 493.44 / 453.07 |
| webkit B | 20223931 | 361.11 / 490.02 / 487.77 / 434.76 |
| webkit C | 20224058 | 346.57 / 497.57 / 495.56 / 446.83 |

The compact ordinary cache reduces this estimated payload sum by about 7.1 MB, but explicit full diagnostics dominate remaining cached bytes. JSON estimates omit requests, object/allocator overhead and initial response; they are not live graph measurements. RSS sums browser-child processes and double-counts shared pages. Heap is coarse Chromium-only page data; worker heap is unavailable. Garbage collection/high-water/process changes prevent a unique worker-memory or leak conclusion. Physical memory improvement is **INCONCLUSIVE**. Cache/evidence references are dropped and workers actually terminated; no immediate RSS-return promise follows.

Mode B keeps cumulative observer history, so its generation/retention is still unbounded by simulation horizon; the authorized horizon here is tiny. Mode C caps endpoint evidence to four recent accepted versions, but attempts/bytes within one command are not hard-byte bounded. Neither mode solves arbitrary long-run diagnostic memory. The 256-entry cache also bounds count, not bytes; full-detail requests remain expensive. No production suitability follows.

## Decision

Communication and real-button latency tails improve; solver throughput, startup and physical-memory improvement are not established robustly. Further isolated research GO, operator integration NO-GO. Next: profile original residual/property workloads without changing Newton/TR-BDF2; separately test UI scheduling for WebKit frame tails. If extending duration is later authorized, require a byte-budgeted diagnostic-retention design first.

## Explicit diagnostic API retrieval

Additional retrieval-*.json.gz samples use three interleaved rounds and both frozen fixtures. B/C commands add no property calls. A cumulative diagnostics and B/C endpoint detail have different scopes and are not equal-work performance comparisons. All numbers below are service/roundtrip medians, with size estimates from detached JSON.

| Engine/mode | Command | Service median ms | Roundtrip median ms | Payload estimate median bytes |
|---|---|---:|---:|---:|
| chromium A | diagnostics | 17.85 | 55.20 | 4418516 |
| chromium A | snapshot | 0.50 | 1.60 | 23018 |
| chromium B | diagnosticsDetail | 4.45 | 13.65 | 1057165 |
| chromium B | diagnosticsSummary | 0.00 | 0.40 | 211 |
| chromium B | snapshotCompact | 0.10 | 0.50 | 2322 |
| chromium C | diagnosticsDetail | 4.50 | 15.20 | 1057147 |
| chromium C | diagnosticsSummary | 0.05 | 0.30 | 193 |
| chromium C | snapshotCompact | 0.10 | 0.35 | 2322 |
| webkit A | diagnostics | 13.50 | 36.50 | 4419689 |
| webkit A | snapshot | 1.00 | 1.50 | 23006 |
| webkit B | diagnosticsDetail | 2.50 | 9.00 | 1066173 |
| webkit B | diagnosticsSummary | 0.00 | 0.00 | 211 |
| webkit B | snapshotCompact | 0.00 | 0.50 | 2323 |
| webkit C | diagnosticsDetail | 3.50 | 9.00 | 1066155 |
| webkit C | diagnosticsSummary | 0.00 | 0.00 | 193 |
| webkit C | snapshotCompact | 0.00 | 0.00 | 2323 |
