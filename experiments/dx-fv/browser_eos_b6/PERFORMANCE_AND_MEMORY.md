# Bounded performance and memory observations

Actual Chromium 154.0.8037.57 and desktop WPE WebKit 26.5 use the same verified
B4C WASM and JS in both variants. Node is 24.19.0, Python 3.12.14 and Playwright
1.62.0. `evidence/runtime.json` records executable digests, pinned Emscripten
build identity and the absence of a local emcc requirement. No compiler is run.

Eight explicit warm-up sequences precede three interleaved rounds per variant
and group. Each sample targets 35 ms and stops at 512 calls; some fast samples
hit the call cap first. Each call includes update/getters or actual error
handling. There are 30 samples per engine, twelve additional state factory/
delete samples per variant, and one worker run per variant. First module load,
first factory, fetch/instantiate timings, counts, checksums and actual failures
are retained in `gate-b-*-0.json`; summaries are independently recalculated.

Median microseconds per call, historical control → candidate:

| Engine | Supported PT | Rejected PT | PH | DU | Alternating |
|---|---:|---:|---:|---:|---:|
| Chromium | 18.36 → 14.26 | 71.14 → 48.05 | 92.84 → 84.95 | 30.08 → 28.52 | 38.67 → 35.16 |
| Desktop WebKit | 41.02 → 19.53 | 117.00 → 155.34 | 169.08 → 131.09 | 101.16 → 44.92 | 74.79 → 50.78 |

These short measurements do **not** establish a speedup. JIT/tiering, garbage
collection, timer resolution and order/warm-up effects are material, especially
after the fresh-module lifecycle matrix. The historical rejected path asserts
and fails cleanup; the candidate performs required catch adoption/destruction
and carries honest native-name diagnostics. These paths do different error work.
WebKit's rejected-call sample costs about 1.33 times control; that observation is
retained, without inventing a pass threshold or a simulator slowdown forecast.
There is no demonstrated added supported numerical work.

Median subsequent factory time is about 0.2 ms in Chromium and 1 ms in WebKit
for both variants. Median deletion reads 0 ms at available resolution: this means
below measurement resolution, not costless deletion. All 48 explicit factory/
delete samples across engines verify `isDeleted()`; lifecycle comparisons create
and delete further fresh states through the same API.

Workers execute 64 actual rejected/supported alternations plus PH/DU/PQ.
Control → candidate total latency, including worker load/init, is about
3088 → 2844 ms Chromium and 4781 → 6167 ms WebKit. Main-thread timer counts
are 599 → 568 and 499 → 627, respectively. Maximum observed heartbeat gaps are
31.3 → 8.7 ms Chromium and 222 → 367 ms WebKit. Timers continue, but the long
WebKit gaps preclude a smooth-response guarantee. These single matched worker
samples are observations, not physical Safari/iPad performance qualification.

Every timed sample retains actual expected errors and zero unexpected supported
failures. Candidate rejected paths retain the property refusal and show no
secondary assertion. WASM linear memory remains **56,360,960 bytes** in these
samples, including after deletion. An unchanged linear-memory size does not
prove absence of leaks: allocators reuse reserved memory and WASM does not
normally shrink it. Chromium JS heap observations are coarse and GC-dependent;
WebKit does not supply that heap API. No exact native allocation census or
long-duration browser-heap proof is claimed.

Ownership evidence instead rests on the pinned generated implementation,
read-only live-header observations (zero before adoption, one before end-catch),
matched callback order, no post-free reads, and the uncaught-exception counter
returning to zero after each candidate rejection. All tests are bounded; no
hours-long stress, unrestricted fuzzing or performance-based ownership inference
is used.
