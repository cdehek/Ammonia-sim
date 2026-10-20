# Measured solver performance

All times above 0.001 s are UNQUALIFIED RESEARCH. No longer-duration scientific qualification is claimed.

Representative canonical r1 interval receipts (wall/CPU in milliseconds):

| Fixture | Accepted interval s | Requested Δt | Actual Δt | Wall ms | CPU ms | Substeps | Rejects | Residuals | Corrections |
|---|---|---|---|---|---|---|---|---|---|
| cold | 0→0.0001 | 0.0001 | 0.0001 | 40.88 | 82.83 | 4 | 1 | 1250 | 56 |
| cold | 0.0001→0.0005 | 0.0004 | 0.0004 | 38.04 | 78.93 | 8 | 0 | 1102 | 49 |
| cold | 0.0005→0.001 | 0.0005 | 0.0005 | 18.91 | 30.68 | 4 | 0 | 562 | 25 |
| cold | 0.001→0.002 | 0.001 | 0.001 | 19.22 | 34.86 | 4 | 0 | 562 | 25 |
| cold | 0.002→0.005 | 0.003 | 0.003 | 14.39 | 15.81 | 6 | 0 | 898 | 40 |
| cold | 0.005→0.01 | 0.005 | 0.005 | 16.27 | 16.26 | 6 | 0 | 898 | 40 |
| warm | 0→0.0001 | 0.0001 | 0.0001 | 161.5 | 239.8 | 10 | 3 | 3502 | 157 |
| warm | 0.0001→0.0005 | 0.0004 | 0.0004 | 112.7 | 157.1 | 12 | 0 | 2302 | 103 |
| warm | 0.0005→0.001 | 0.0005 | 0.0005 | 125.6 | 189.8 | 12 | 0 | 1884 | 84 |
| warm | 0.001→0.002 | 0.001 | 0.001 | 91.84 | 136.3 | 10 | 0 | 2010 | 90 |
| warm | 0.002→0.005 | 0.003 | 0.003 | 103.7 | 138.9 | 12 | 0 | 2500 | 112 |
| warm | 0.005→0.01 | 0.005 | 0.005 | 290.7 | 396.2 | 30 | 5 | 7182 | 321 |

| Fixture | Three total advance wall samples ms | Median wall s / simulated s | Median CPU s / simulated s | Observed profile / median canonical |
|---|---|---|---|---|
| cold | 147.7, 187.2, 171.3 | 17.13 | 30.59 | 1.06 |
| warm | 886, 980.7, 927.1 | 92.71 | 132 | 1.053 |

Ratios are measured total advance time divided by 0.01 accepted physical seconds. They are not repeated-one-second benchmark measurements. The 0.005→0.01 s interval costs 3.253, 6.849, 4.89 wall s/s cold and 58.15, 56.25, 58.27 warm. Output clipping, initialization dynamics and JIT warmup make whole-probe and late-window rates differ substantially. All three runs have identical scientific work counts and state/attempt hashes.

Canonical advance includes original accepted diagnostic generation, commit/record and sparse observer progress output. Observer callbacks cost 2.386 ms cold and 19.3 ms warm in representative r1. Construction, table import and full receipt encoding/compression are excluded from advance timing. Whole child/supervisor execution takes much longer because the research stream serializes full states and many diagnostic events. Do not present that serialization cost as property or integrator time.

Primary observed replay adds nested timing wrappers. Its total is 181.6 ms cold and 976.1 warm. Primary observed time is about 6% cold and 5% warm above canonical median. Earlier lightweight timing-only replays are retained separately; short-run variation must not be interpreted as a scientific speedup. This is measurement perturbation of timing, not decisions; exact hash equality passes. The primary observed replay includes public-property range accounting; earlier timing-only replays are also retained.

Representative maximum sampled RSS is 233.0 MiB cold and 365.5 MiB warm; sampled heap used is 99.0 / 131.4 MiB. These include rich diagnostics and serialization, not just 21 unknowns. No long-duration memory stability is demonstrated. Diagnostic histories/attempt arrays and trace grow with work; B9D retains attempts in its worker. Such retention needs an explicit later design before long sessions.

Worker transport and UI rendering: no fresh browser measurement here. Retained B11 Chromium/WebKit commissioning evidence contains historical service/roundtrip/render measurements, revalidated as saved evidence only. They are not mixed into Node solver timing. Browser scheduling or transfer/dispatch residuals cannot be attributed to science. B12 owner reports responsive physical iPad review; that is not an instrumented throughput benchmark.

Desktop Chrome/Edge implication: keep synchronous scientific computation in a worker and deliver bounded accepted snapshots so controls remain responsive. This harness demonstrates finite solver work on a cloud CPU, not performance of an ordinary desktop or the owner's laptop. Benchmark nominated desktop hardware and current browser versions separately before committing a UI pacing target. No browser-dependent scientific branch is added.
