# Bounded responsiveness and lifecycle measurements

Actual primary display, original trace/observer generation, fresh workers. Milliseconds; all samples retained in shadow browser receipts. No startup/FPS threshold is invented. One sequential B9C→shadow→B9C bracket per fixture/browser is descriptive, not a population estimate or repeated B9C performance campaign.

| Browser | Fixture | Initialize + first t=0 snapshot RTT ms | Three original advance compute ms | B9C before / shadow / B9C after compute sum ms |
|---|---|---|---|---|
| chromium | cold | 56.70 | 37.10, 38.20, 12.40 | 66.30 / 87.70 / 73.30 |
| chromium | warm | 54.60 | 131.20, 89.30, 67.70 | 338.50 / 288.20 / 288.40 |
| webkit | cold | 107.00 | 54.00, 24.00, 13.00 | 86.00 / 91.00 / 83.00 |
| webkit | warm | 100.00 | 185.00, 107.00, 84.00 | 382.00 / 376.00 / 390.00 |

| Browser | Fixture | Transfer + dispatch | Render | 10-ms heartbeat gaps | rAF frame gaps | Trusted input acknowledgement |
|---|---|---|---|---|---|---|
| chromium | cold | 0.20 [0.00–2.70], n=4 | 0.60 [0.20–2.00], n=11 | 10.00 [2.70–27.30], n=32 | 16.70 [16.60–16.80], n=22 | 0.35 [0.30–1.20], n=4 |
| chromium | warm | 0.15 [0.10–0.20], n=4 | 0.50 [0.20–0.60], n=11 | 10.00 [2.90–25.50], n=54 | 16.70 [16.50–16.80], n=34 | 0.50 [0.30–0.80], n=4 |
| webkit | cold | 2.00 [1.00–4.00], n=4 | 1.00 [0.00–1.00], n=11 | 12.00 [3.00–32.00], n=31 | 15.00 [1.00–26.00], n=30 | 0.00 [0.00–2.00], n=4 |
| webkit | warm | 1.00 [1.00–1.00], n=4 | 1.00 [0.00–2.00], n=11 | 12.00 [10.00–19.00], n=53 | 16.00 [1.00–31.00], n=45 | 1.00 [1.00–2.00], n=4 |

Cells contain median [minimum–maximum], n. First accepted snapshot is the genuine initialized t=0 record, not a successful advance. Initialization components separate asset hash verification, module/owned-table construction and create+record. First-advance RTT, every per-command service/transfer/roundtrip sample, stop acknowledgement, disposal and fresh initialization remain in raw evidence. Transfer+dispatch uses correlated timeOrigin+performance.now across worker/window and includes clone, scheduling and message delivery; it is not an isolated network or memcpy benchmark. Render timing measures DOM projection execution; rAF measures delivered frame gaps, not physical display scanout. Input acknowledgement is trusted browser event timestamp to handler execution. Timing excludes test-only full scientific retrieval; primary display does not load diagnostic test bundles.

The worker retains the B9C algorithm and reduction in property work; exact scientific counters/checkpoint hashes remain original. Sparse timing brackets show JIT/loader/runtime variability and must not be read as guaranteed identical compute latency. The warm computation takes hundreds of milliseconds for only .001 simulated seconds; this is not real-time plant operation. The main event loop continues while it runs. Outliers above nominal 10-ms heartbeat / frame cadence are retained and shown; no smoothness or physical iPad guarantee follows. Stop queues behind synchronous work. Basic diagnostics are compact, while original full detail is test-only and can be expensive. No timing work removes record generation, observer, finite differences or conservation checks.

Disposal RTT / owner service ms: chromium: 13.50 / 0.10; webkit: 0.00 / 0.00. Fresh warm initialization after disposal recreates exact original state. This bounded evidence is not long-duration heap/leak qualification or device performance certification.

## Follow-up on measured compute overhead

The first primary brackets showed slower shadow sums than both flanking bare B9C samples. Three additional sequential control→B9C→shadow→B9C→control brackets per fixture/browser investigate that concern. They use unchanged .001-s workloads, retain all samples, compare every original control/candidate full science hash and shadow final state/record plus every original attempt diagnostic. Test-only pre-advance physical copies are outside compute timers; these follow-ups are separate from primary UI responsiveness samples.

| Browser | Fixture | Unoptimized accepted control ms | Bare B9C ms | Shadow ms | Median paired reduction versus control |
|---|---|---|---|---|---|
| chromium | cold | 129.05 [121.00–139.70], n=6 | 68.00 [57.60–87.20], n=6 | 90.00 [87.00–93.60], n=3 | 33.3% |
| chromium | warm | 480.55 [434.60–501.60], n=6 | 309.15 [294.90–423.10], n=6 | 326.80 [288.70–364.50], n=3 | 29.6% |
| webkit | cold | 172.00 [153.00–206.00], n=6 | 81.50 [67.00–92.00], n=6 | 109.00 [97.00–131.00], n=3 | 39.2% |
| webkit | warm | 582.50 [566.00–635.00], n=6 | 383.00 [337.00–402.00], n=6 | 370.00 [348.00–387.00], n=3 | 36.0% |

The bounded shadow retains a compute reduction versus unchanged accepted controls in every follow-up bracket. Cold shadow work is consistently slower than the bare B9C medians; warm observations overlap and vary. The cause is **OPEN**: message cadence, allocation/JIT/GC and scheduling are hypotheses, not demonstrated attribution. We do not claim unchanged wall time or zero bridge overhead. Main-thread worker separation and measured input/heartbeat responsiveness remain intact. This supports a bounded read-only feasibility result, with performance investigation required before a longer/continuous-operation claim. No numerical or property-work shortcut was introduced to improve this result.
