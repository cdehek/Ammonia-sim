# Browser runtime and memory results

These are new B2 desktop observations. Physical Safari/iPad is **NOT RUN**.
Serial matched 30/44 measurements are separate from concurrent scientific campaign elapsed times.

| Engine | Build | Median init ms (3 contexts) | PH liquid / vapor / two-phase µs | DU liquid / vapor / two-phase µs | Peak observed WASM MiB | Page maximum timer gap ms |
|---|---|---:|---|---|---:|---:|
| chromium | build30 | 2759.20 | 165.899 / 146.027 / 7.458 | 50.465 / 41.694 / 53.376 | 53.75 | 52.80 |
| chromium | build44 | 2844.70 | 151.506 / 184.783 / 14.934 | 36.681 / 29.547 / 59.888 | 53.75 | 115.20 |
| webkit | build30 | 3326.00 | 93.905 / 142.045 / 12.267 | 39.809 / 46.296 / 34.153 | 53.75 | 246.00 |
| webkit | build44 | 3786.00 | 176.802 / 211.864 / 9.874 | 37.811 / 49.801 / 35.311 | 53.75 | 226.00 |

Each property state returns the same seven fields; three timed rounds per physical region. Group calls/failures, min/max latency, sustained epochs, error recovery, startup components and heap scopes are retained in performance-summary.json and raw files. Fresh contexts may reuse browser/compiler/OS caches. WebKit reverses build order. The first Chromium30 measurement overlapped a brief independent audit and remains under performance-overlap; its isolated repeat is reported here. The recorded order is Chromium30 (archived), Chromium44, WebKit44, WebKit30, then the isolated Chromium30 repeat.

| Engine | Build | Original fixture through 0.2 s | Median solver ms (3 repeats) | Accepted half-steps | Rejected trials | Iterations | PH / sat / MUV public calls | Completed target |
|---|---|---|---:|---:|---:|---:|---|---|
| chromium | build30 | cold | 2052.300 | 52 | 6 | 519 | 33256 / 72022 / 1450 | True |
| chromium | build30 | warm | 10044.600 | 158 | 20 | 1868 | 118843 / 254641 / 4465 | True |
| chromium | build30 | heat-reversal | 1813.700 | 56 | 3 | 372 | 21844 / 49083 / 1405 | True |
| chromium | build44 | cold | 1998.800 | 52 | 6 | 519 | 33256 / 72022 / 1450 | True |
| chromium | build44 | warm | 9944.100 | 158 | 20 | 1820 | 115891 / 248737 / 4465 | True |
| chromium | build44 | heat-reversal | 1763.700 | 56 | 3 | 370 | 20639 / 46673 / 1405 | True |
| webkit | build30 | cold | 1869.000 | 52 | 6 | 519 | 33256 / 72022 / 1450 | True |
| webkit | build30 | warm | 9380.000 | 158 | 20 | 1868 | 118843 / 254641 / 4465 | True |
| webkit | build30 | heat-reversal | 1779.000 | 56 | 3 | 372 | 21844 / 49083 / 1405 | True |
| webkit | build44 | cold | 2559.000 | 52 | 6 | 519 | 33256 / 72022 / 1450 | True |
| webkit | build44 | warm | 13808.000 | 158 | 20 | 1820 | 115891 / 248737 / 4465 | True |
| webkit | build44 | heat-reversal | 1923.000 | 56 | 3 | 370 | 20639 / 46673 / 1405 | True |

The coupled timer includes original model creation, advances/records and the adapter/table support guard; WASM initialization, input transfer and JSON output are outside it. One warmup precedes three measured repetitions. These short startup workloads are cost measurements, **not full scientific trajectories** and contain no 15/30 s disturbance. They preserve original solver options and physics.

| Engine | Fixture | Median cost 44 / 30 | Both targets complete |
|---|---|---:|---|
| chromium | cold | 0.9739 | True |
| chromium | warm | 0.9900 | True |
| chromium | heat-reversal | 0.9724 | True |
| webkit | cold | 1.3692 | True |
| webkit | warm | 1.4721 | True |
| webkit | heat-reversal | 1.0809 | True |

Ratios are descriptive for these matched workloads; three repeats do not establish universal cost or an optimal precision setting. Scientific qualification timings include source transfer, assertions and diagnostic/persistence overhead and were collected with competing workers; they are not controlled backend speed ratios.

WASM linear memory is not total browser or device memory. Page CDP heap excludes the worker; worker performance.memory is nonstandard and can be unavailable. Heap snapshots after a worker terminates may include uncollected harness data. No total iPad memory or physical-device responsiveness is inferred.

Offline results are separate for browser offline-context emulation and an origin returning 503. Local service-worker/worker execution is not a physical-device test or hosted deployment.

| Scope | Chromium30 page JS used / allocated MiB | Chromium44 page JS used / allocated MiB |
|---|---:|---:|
| Standalone after worker | 2.061 / 3.434 | 2.024 / 3.184 |
| Coupled after worker | 10.824 / 11.738 | 10.821 / 11.738 |

Worker JS heap is unavailable in both engines; WebKit page heap is NOT MEASURED. These page-only values must not be added to WASM memory and called a total browser footprint.
All coupled repetitions reach the 0.2 s target with repeatable work counts: **True**. Failed/missing rows, if present, remain explicit in the summary.

**offline-context.json**
- chromium: 4/4 backend workers completed; preparation error=None; origin requests blocked (cumulative within this mode)=5; backend/page failures=[].
- webkit: 0/4 backend workers completed; preparation error=None; origin requests blocked (cumulative within this mode)=5; backend/page failures=['Page.goto: WebKit encountered an internal error'].

**offline-origin-only.json**
- chromium: 4/4 backend workers completed; preparation error=None; origin requests blocked (cumulative within this mode)=4; backend/page failures=[].
- webkit: 4/4 backend workers completed; preparation error=None; origin requests blocked (cumulative within this mode)=8; backend/page failures=[].

Chromium passes both offline experiments. WebKit passes the origin-disabled cache replay but **FAILS offline-context emulation** during fresh navigation with an internal error (all four builds). The successful origin-disabled result is a different experiment and does not clear that compatibility gate. Neither result qualifies actual Safari airplane-mode/device behavior.

Long-duration memory growth, hour-scale cost and actual iPad Safari remain **NOT RUN** because earlier scientific gates fail. No hosting or Cloudflare changes were made.
