# Matched actual-browser performance

| Engine | Fixture | Control ms n=10, median [range] | Candidate ms n=5, median [range] | Median paired reduction | Decision |
|---|---|---|---|---|---|
| chromium | cold | 131.90 [121.70–148.70] | 69.10 [61.40–73.30] | 50.0% | meaningful improvement in all five matched brackets |
| chromium | warm | 480.55 [447.50–526.10] | 317.20 [296.80–325.40] | 35.0% | meaningful improvement in all five matched brackets |
| webkit | cold | 167.50 [149.00–213.00] | 77.00 [76.00–90.00] | 53.9% | meaningful improvement in all five matched brackets |
| webkit | warm | 597.00 [564.00–617.00] | 373.00 [347.00–404.00] | 37.7% | meaningful improvement in all five matched brackets |

Times are original three-advance sums to .001 simulated seconds, including all
retry/stage/commit and mandatory record work. Extra snapshot records, cloning,
hashing, JSON artifact export, communication, browser/worker startup and table
ownership construction are outside those advance timers. Original observer cadence
remains active. No heavy diagnostic wrappers/counters run in primary timing.

Five predeclared C→candidate→C brackets per fixture/engine; fixture order reverses
on alternating rounds. Workloads are strictly sequential, with fresh workers.
All samples and before/after variability remain in timing-*.json.gz and
performance-summary.json. Every timed scientific hash matches qualified control.
No outlier is removed. Ranges, sample standard deviations, paired deltas and raw
samples are reported; these sparse rounds do not establish population confidence
intervals or sustained throughput. A consistent bracket reduction is the stated
bounded improvement criterion, not an inferred speedup from call counts.

Construction and model create+initial-record times, per-advance values, extra
record generation and full request RTT are separate in the raw samples. RTT
includes research module loading, full evidence hashing and serialization; it is
not pure worker/main communication cost. A pure communication-only duration is
not isolated here. Stage/property/residual timings are separate DIAGNOSTIC passes
with explicitly measured overhead, never added as an exclusive CPU partition.

Chromium and desktop WPE WebKit versions, executable identities, user agents and
source hashes are recorded in raw receipts. No physical iPadOS Safari inference.
Main-page 10-ms heartbeat is measured during primary research requests. The minimal
harness has no operator input UI; real UI input responsiveness is NOT APPLICABLE.
Available page JS heap and whole-browser RSS observations are retained; WebKit
may lack performance.memory. RSS double-counts shared pages and does not identify
live cache bytes. All workers terminate and fresh sessions restart exactly.
Two boundary result objects per active stage are the only new retained values;
no evidence establishes long-duration leak freedom or operator readiness.

| Engine | Fixture | Mode | Owned table/factory ms | Create + initial record ms | Extra record sum ms | Research request RTT ms |
|---|---|---|---|---|---|---|
| chromium | cold | control | 18.70 | 3.30 | 0.40 | 400.35 |
| chromium | cold | candidate | 19.10 | 3.00 | 0.60 | 343.74 |
| chromium | warm | control | 18.55 | 5.45 | 1.65 | 986.62 |
| chromium | warm | candidate | 18.30 | 5.00 | 1.10 | 815.40 |
| webkit | cold | control | 46.00 | 4.00 | 1.00 | 422.38 |
| webkit | cold | candidate | 47.00 | 4.00 | 1.00 | 354.81 |
| webkit | warm | control | 46.50 | 7.00 | 1.00 | 1092.91 |
| webkit | warm | candidate | 44.00 | 6.00 | 2.00 | 892.04 |

These are separate per-mode medians, with fresh worker/loader/model sessions;
"warm" means the warm scientific fixture, not a warm OS/JIT cache. The ownership
setup is outside model-initialization and advance timers in BOTH modes.

| Engine | Page heap before | Page heap after | Process RSS before KiB | Process RSS after KiB | Heartbeat median ms | Heartbeat max ms |
|---|---|---|---|---|---|---|
| chromium | {'used': 10000000, 'total': 10000000} | {'used': 10000000, 'total': 10000000} | 385400 | 521964 | 10.00 | 15.30 |
| webkit | None | None | 299996 | 597068 | 12.00 | 69.00 |

Memory/heartbeat span all 30 timing requests per engine, both modes interleaved.
They cannot attribute retained bytes to one mode or prove leak freedom. Process
RSS includes shared pages; page heap excludes worker-owned heaps. No operator
input UI or communication-only microbenchmark is claimed.
