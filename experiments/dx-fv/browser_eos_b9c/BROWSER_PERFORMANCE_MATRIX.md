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
