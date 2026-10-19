# Browser performance and resources

PASS for measurement/characterization, without a real-time threshold. Fresh B10 and B11 samples use the same host, browser versions, 1440×1000 viewport, original playback plus trusted tool/schematic input and exactly three A2 intervals. Two sequential rounds per browser/fixture, order reversed in round 2. Fresh contexts retain natural browser/OS caches; “cold fixture” describes the physical initial condition, not a guaranteed empty OS cache.

Milliseconds are median [min–max], n. Compute is the sum of worker timing.advanceMS across the original three intervals; it excludes asset loading and includes original model work. Tool and readiness roundtrips include automation/actionability/render scheduling.

| Browser | Fixture | Artifact | Navigation to original ready | Lazy A2 panel | First accepted/rendered t=0 | Three-advance compute | Tool switch during compute |
|---|---|---|---|---|---|---|
| chromium | cold | B10 | 236.18 [214.49–257.87], n=2 | 172.87 [171.27–174.47], n=2 | 72.70 [72.20–73.20], n=2 | 124.45 [120.20–128.70], n=2 | 46.31 [45.70–46.92], n=2 |
| chromium | cold | B11 | 226.55 [224.70–228.40], n=2 | 211.63 [204.28–218.99], n=2 | 73.45 [67.80–79.10], n=2 | 119.40 [115.00–123.80], n=2 | 51.94 [48.00–55.89], n=2 |
| chromium | warm | B10 | 230.30 [228.04–232.56], n=2 | 228.32 [218.29–238.36], n=2 | 73.35 [67.00–79.70], n=2 | 447.65 [437.40–457.90], n=2 | 342.50 [294.39–390.62], n=2 |
| chromium | warm | B11 | 248.01 [247.46–248.55], n=2 | 205.54 [191.99–219.09], n=2 | 78.95 [77.00–80.90], n=2 | 463.15 [407.50–518.80], n=2 | 261.77 [152.77–370.77], n=2 |
| webkit | cold | B10 | 593.58 [563.41–623.75], n=2 | 1305.28 [1240.76–1369.80], n=2 | 194.50 [136.00–253.00], n=2 | 169.00 [156.00–182.00], n=2 | 740.82 [738.98–742.66], n=2 |
| webkit | cold | B11 | 592.93 [588.93–596.92], n=2 | 1161.09 [1145.71–1176.46], n=2 | 141.50 [129.00–154.00], n=2 | 136.50 [128.00–145.00], n=2 | 602.73 [580.04–625.41], n=2 |
| webkit | warm | B10 | 639.05 [581.40–696.69], n=2 | 1116.99 [1113.44–1120.54], n=2 | 129.00 [124.00–134.00], n=2 | 620.50 [580.00–661.00], n=2 | 307.97 [286.90–329.04], n=2 |
| webkit | warm | B11 | 557.25 [557.23–557.27], n=2 | 1118.31 [1115.37–1121.25], n=2 | 125.50 [123.00–128.00], n=2 | 604.50 [539.00–670.00], n=2 | 335.84 [322.70–348.98], n=2 |

| Browser | Artifact | Worker creation | Bundle hash/fetch | Module/owned table | Model create/record | Original initialize UI | Dispose | Restart to rendered t=0 |
|---|---|---|---|---|---|---|---|
| chromium | B10 | 0.30 [0.20–0.30], n=4 | 16.90 [13.70–18.10], n=4 | 31.55 [27.40–33.70], n=4 | 6.25 [5.40–7.40], n=4 | 151.29 [115.72–173.77], n=4 | 7.91 [6.94–8.85], n=4 | 59.90 [56.40–70.20], n=4 |
| chromium | B11 | 0.35 [0.20–0.40], n=4 | 16.95 [16.00–18.80], n=4 | 31.55 [29.40–37.70], n=4 | 6.30 [5.00–7.70], n=4 | 130.42 [126.85–170.00], n=4 | 5.14 [5.06–7.53], n=4 | 60.45 [55.50–84.00], n=4 |
| webkit | B10 | 0.50 [0.00–1.00], n=4 | 24.50 [15.00–32.00], n=4 | 81.50 [75.00–148.00], n=4 | 8.50 [7.00–11.00], n=4 | 5154.54 [4892.60–6081.56], n=4 | 12.03 [10.70–25.14], n=4 | 174.00 [155.00–191.00], n=4 |
| webkit | B11 | 1.00 [0.00–1.00], n=4 | 21.00 [19.00–23.00], n=4 | 74.50 [71.00–100.00], n=4 | 8.50 [7.00–9.00], n=4 | 5060.90 [4703.33–5317.18], n=4 | 12.41 [7.56–33.03], n=4 | 137.50 [102.00–187.00], n=4 |

| Browser | Artifact | Main heartbeat gaps | rAF gaps | Trusted event acknowledgement | DOM render | Browser/driver RSS MiB after solve |
|---|---|---|---|---|---|---|
| chromium | B10 | 10.00 [1.00–279.00], n=260 | 16.70 [16.60–250.00], n=143 | 1.00 [0.00–3.90], n=16 | 0.70 [0.00–4.70], n=56 | 786.48 [765.10–805.88], n=4 |
| chromium | B11 | 10.00 [0.70–341.70], n=260 | 16.70 [16.50–316.60], n=139 | 1.00 [0.70–7.10], n=16 | 0.60 [0.00–3.00], n=56 | 792.36 [769.46–798.93], n=4 |
| webkit | B10 | 12.00 [1.00–422.00], n=731 | 85.00 [1.00–289.00], n=103 | 2.00 [1.00–39.00], n=16 | 1.00 [0.00–5.00], n=56 | 868.41 [861.15–878.16], n=4 |
| webkit | B11 | 12.00 [2.00–398.00], n=705 | 61.00 [1.00–285.00], n=103 | 3.00 [1.00–9.00], n=16 | 1.00 [0.00–5.00], n=56 | 875.36 [863.23–882.63], n=4 |

## Observed packaging differences

B11 minus matched B10 medians below are observations from two samples per fixture, not causal estimates or guarantees. Positive deltas mean additional observed time/resource use.

- chromium: cold-fixture navigation -9.63 ms; lazy panel +38.77 ms; first accepted/rendered initialization +0.75 ms; warm three-advance compute +15.50 ms; tool-switch median -66.32 ms; coarse after-solve RSS median +5.88 MiB.
- webkit: cold-fixture navigation -0.65 ms; lazy panel -144.19 ms; first accepted/rendered initialization -53.00 ms; warm three-advance compute -16.00 ms; tool-switch median -69.50 ms; coarse after-solve RSS median +6.95 MiB.

Raw performance-{browser}.json preserves every sample, worker projection/service/delivery/roundtrip time, startup navigation entries, original model-call time, trusted-event pending counts, frames/heartbeat, coarse Chromium heap (WebKit may be null), RSS process observations and disposal timer state. B10/B11 scientific snapshot cores match exactly in each pair. Main-thread delays/tool roundtrips are real; event acknowledgement starts at the browser timestamp and omits actionability waiting. DOM timing is not display scanout. Negative transfer estimates from timer resolution, if present, are retained.

No scientific assets are compressed/rebuilt at runtime; no new worker/page/service worker/cache exists. The packaged B9D formatter dependency is about 3 KB; the scientific bundle is present once. Original embedded properties and scientific owned tables intentionally remain independent, as in B10. RSS includes shared browser/driver pages and cannot isolate worker memory or establish leaks. Matched sample variation is too small a campaign for causal scheduling or memory conclusions; inspect the tables for startup/compute/switch outliers. The package introduces no new startup failure in supported origins and no additional asset download dependency. No stable nonlinear speedup or sustained real-time performance is claimed.

Historical B10 warm compute medians were about 610 ms Chromium and 1,004 ms desktop WebKit. They are context, not thresholds for this host. Use the matched rows above. Only .001 simulated seconds is computed; wall-clock time and UI stalls remain material limitations, especially on WebKit. Physical iPad resource behavior awaits owner review.
