# Matched bounded integration measurements

PASS for characterization, without a speed/FPS threshold or continuous-operation claim. All samples are in performance-{browser}.json. Two sequential rounds per frozen cold/warm fixture/browser compare A original pinned workstation, B B10 inactive, C A2 initialized/idle, D A2 computing while original playback/UI operates, E bare B9D, plus bare B9C. Scientific D/E snapshot cores match exactly; bare B9C matches saved same-engine full science. No unrelated scientific workload is attributed to UI overhead. Units below are milliseconds, median [min–max], n.

| Browser | Fixture | D worker three-advance compute sum | E bare B9D sum | Bare B9C sum |
|---|---|---|---|---|
| chromium | cold | 170.00 [162.90–177.10], n=2 | 127.75 [121.50–134.00], n=2 | 90.60 [87.40–93.80], n=2 |
| chromium | warm | 610.20 [562.90–657.50], n=2 | 389.70 [389.10–390.30], n=2 | 408.35 [389.10–427.60], n=2 |
| webkit | cold | 383.00 [250.00–516.00], n=2 | 209.00 [207.00–211.00], n=2 | 117.50 [95.00–140.00], n=2 |
| webkit | warm | 1004.00 [994.00–1014.00], n=2 | 588.50 [566.00–611.00], n=2 | 508.50 [478.00–539.00], n=2 |

| Browser | Fixture | Worker creation | First accepted + rendered t=0 | Source import + owned table | Model create + record |
|---|---|---|---|---|---|
| chromium | cold | 0.30 [0.30–0.30], n=2 | 88.60 [84.50–92.70], n=2 | 37.60 [36.50–38.70], n=2 | 6.00 [4.80–7.20], n=2 |
| chromium | warm | 1.35 [0.20–2.50], n=2 | 106.80 [86.40–127.20], n=2 | 40.30 [36.70–43.90], n=2 | 11.70 [8.90–14.50], n=2 |
| webkit | cold | 3.50 [1.00–6.00], n=2 | 233.50 [229.00–238.00], n=2 | 142.50 [140.00–145.00], n=2 | 10.00 [10.00–10.00], n=2 |
| webkit | warm | 2.50 [1.00–4.00], n=2 | 212.50 [201.00–224.00], n=2 | 137.50 [130.00–145.00], n=2 | 11.00 [10.00–12.00], n=2 |

| Browser | Fixture | Case | 10-ms heartbeat gaps | rAF gaps | Trusted input acknowledgement |
|---|---|---|---|---|---|
| chromium | cold | A | 10.00 [1.70–425.40], n=60 | 16.70 [16.60–400.00], n=24 | 0.90 [0.50–1.30], n=4 |
| chromium | cold | B | 10.00 [3.40–433.20], n=59 | 16.70 [16.60–416.70], n=24 | 0.90 [0.50–1.20], n=4 |
| chromium | cold | C | 10.00 [2.10–10.20], n=32 | 16.70 [16.60–16.70], n=17 | unavailable |
| chromium | cold | D | 10.00 [1.20–292.90], n=123 | 16.70 [16.50–266.70], n=66 | 1.50 [0.80–2.20], n=8 |
| chromium | cold | E | 10.00 [2.40–14.80], n=33 | 16.70 [16.60–16.80], n=18 | unavailable |
| chromium | warm | A | 10.00 [0.80–418.40], n=59 | 16.70 [16.60–383.40], n=25 | 1.00 [0.60–1.00], n=4 |
| chromium | warm | B | 10.00 [0.30–445.30], n=60 | 16.70 [16.60–433.30], n=23 | 0.95 [0.70–1.50], n=4 |
| chromium | warm | C | 10.00 [2.50–10.80], n=32 | 16.70 [16.60–16.80], n=17 | unavailable |
| chromium | warm | D | 10.00 [0.80–348.00], n=184 | 16.70 [16.60–333.30], n=93 | 1.15 [0.20–1.80], n=8 |
| chromium | warm | E | 10.00 [1.40–18.50], n=87 | 16.70 [16.60–16.80], n=51 | unavailable |
| webkit | cold | A | 12.00 [0.00–527.00], n=261 | 19.00 [1.00–820.00], n=18 | 3.00 [2.00–3.00], n=4 |
| webkit | cold | B | 12.00 [1.00–480.00], n=262 | 19.00 [1.00–791.00], n=18 | 1.00 [1.00–2.00], n=4 |
| webkit | cold | C | 12.00 [1.00–13.00], n=29 | 16.00 [9.00–18.00], n=20 | unavailable |
| webkit | cold | D | 12.00 [0.00–712.00], n=371 | 98.50 [1.00–369.00], n=50 | 3.00 [2.00–22.00], n=8 |
| webkit | cold | E | 12.00 [0.00–55.00], n=43 | 36.00 [6.00–83.00], n=19 | unavailable |
| webkit | warm | A | 12.00 [5.00–548.00], n=252 | 18.00 [1.00–773.00], n=19 | 2.00 [2.00–4.00], n=4 |
| webkit | warm | B | 12.00 [5.00–486.00], n=258 | 20.00 [1.00–797.00], n=17 | 2.00 [2.00–3.00], n=4 |
| webkit | warm | C | 12.00 [1.00–19.00], n=27 | 16.00 [7.00–22.00], n=19 | unavailable |
| webkit | warm | D | 12.00 [0.00–502.00], n=390 | 98.00 [1.00–330.00], n=53 | 3.00 [2.00–6.00], n=8 |
| webkit | warm | E | 12.00 [0.00–47.00], n=91 | 16.00 [4.00–90.00], n=55 | unavailable |

Scientific computation time is measured inside unchanged model.advance, with original record/observer/diagnostic work. Startup separates worker construction, hash-verifying fetch, import/owned table, model/create record and first rendered accepted state. The t=0 reading is initialization, not an accepted advance. Projection, service/transport, delivery, DOM rendering, original initialization, navigation and tool-switch roundtrips, dispose/restart, all frame/input outliers and memory observations are retained separately in raw receipts. Transfer includes clone/dispatch/scheduling, not an isolated memcpy benchmark. Main-thread render timing measures DOM work, not display scanout.

D intentionally includes original playback and trusted tool/schematic interactions during the same .001-s A2 workload. Its end-to-end interaction roundtrip is therefore not a pure UI overhead subtraction from bare E. CPU scheduling, allocation/JIT/GC and message cadence are not independently attributed. Cold bridge overhead remains an investigation item; no new optimization or scientific shortcut is made. The clocks stay independent. Warm work can take about one second for only .001 simulated seconds, and observed scheduling/input/frame outliers are real limitations. The interface acknowledges input while the worker computes; this does not establish sustained real-time refrigeration or physical iPad performance.

Observed limitations in these samples: D's three-advance compute sums reach 657.5 ms in Chromium and 1014 ms in WebKit. WebKit original-model initialization UI roundtrips take 5.26–5.84 seconds in A/B even though the model-create call itself takes 3–4 ms. D tool-switch roundtrips reach 777.57 ms, a WebKit heartbeat gap reaches 712 ms, and an original-baseline rAF gap reaches 820 ms. Trusted event acknowledgement reaches 22 ms in D; that interval starts at the browser event timestamp and does not include all automation or user waiting. The tool-switch roundtrip is a more complete measured interaction cost. These are material responsiveness limits, not steady frame or input guarantees.

Transfer/dispatch estimates subtract page and worker timestamps and include scheduling/clone work. Small negative samples (-0.1 ms Chromium, -1 ms WebKit) reflect cross-context clock/timer resolution; they are retained as measurement uncertainty, not negative physical transport. No values are clamped to improve the result.

RSS totals cover this runner's browser/driver descendants and may count shared pages; Chromium heap data is coarse main-page information and WebKit may provide null. They are observations, not isolated worker heap or long-duration leak certification. Disposal/restart and bounded timer cleanup are independently tested. Performance runs are sequential after other test jobs; earlier busy-host integration timings are not pooled into these matched results.

## Original versus inactive B10 startup

A is the exact original; B has the research tool available without loading it. Original model creation is measured by a test-only observer around the unchanged create API. Roundtrips include browser automation/action/render scheduling.

| Browser | Fixture bracket | Case | Navigation roundtrip | Original model creation | Initialize UI roundtrip | Tool switch roundtrip |
|---|---|---|---|---|---|---|
| chromium | cold | A | 281.64 [256.25–307.03], n=2 | 2.35 [2.20–2.50], n=2 | 176.20 [172.71–179.69], n=2 | 116.95 [114.87–119.03], n=2 |
| chromium | cold | B | 270.09 [268.08–272.10], n=2 | 2.25 [2.10–2.40], n=2 | 197.61 [191.67–203.54], n=2 | 114.09 [108.64–119.55], n=2 |
| chromium | warm | A | 261.16 [259.22–263.10], n=2 | 2.40 [2.30–2.50], n=2 | 178.56 [169.19–187.94], n=2 | 108.47 [106.79–110.14], n=2 |
| chromium | warm | B | 262.60 [256.38–268.82], n=2 | 2.45 [2.20–2.70], n=2 | 174.27 [173.50–175.03], n=2 | 113.00 [109.96–116.03], n=2 |
| webkit | cold | A | 652.20 [650.01–654.38], n=2 | 3.50 [3.00–4.00], n=2 | 5326.60 [5260.37–5392.82], n=2 | 646.98 [640.39–653.57], n=2 |
| webkit | cold | B | 804.56 [759.36–849.77], n=2 | 4.00 [4.00–4.00], n=2 | 5596.21 [5352.32–5840.11], n=2 | 679.62 [657.78–701.46], n=2 |
| webkit | warm | A | 727.82 [641.18–814.45], n=2 | 3.00 [3.00–3.00], n=2 | 5482.33 [5301.89–5662.77], n=2 | 638.76 [635.13–642.40], n=2 |
| webkit | warm | B | 781.67 [750.75–812.58], n=2 | 3.00 [3.00–3.00], n=2 | 5474.90 [5335.70–5614.10], n=2 | 654.41 [647.64–661.18], n=2 |

## Advance and message costs

Per accepted requested interval, not per internal adaptive half-step. Bare B9D uses its unchanged UI, while D includes the actual workstation. Values below retain browser timer resolution, including measured zeros.

| Browser | Fixture | Case | Advance compute | Projection | Worker service | Transfer/dispatch | Request roundtrip |
|---|---|---|---|---|---|---|---|
| chromium | cold | D | 72.05 [18.30–78.70], n=6 | 0.00 [0.00–0.30], n=6 | 72.15 [18.60–78.90], n=6 | 0.10 [0.00–0.20], n=6 | 73.85 [19.70–80.80], n=6 |
| chromium | cold | E | 50.85 [15.80–63.50], n=6 | 0.10 [0.00–0.10], n=6 | 51.00 [15.80–63.60], n=6 | 0.15 [-0.10–0.40], n=6 | 52.10 [17.20–64.80], n=6 |
| chromium | warm | D | 167.00 [140.40–337.10], n=6 | 0.10 [0.00–0.10], n=6 | 167.10 [140.50–337.20], n=6 | 3.20 [0.30–281.80], n=6 | 171.15 [141.80–554.80], n=6 |
| chromium | warm | E | 114.50 [83.80–196.80], n=6 | 0.10 [0.00–0.10], n=6 | 114.55 [83.90–197.10], n=6 | 0.25 [0.10–0.30], n=6 | 115.70 [84.70–197.90], n=6 |
| webkit | cold | D | 96.50 [39.00–358.00], n=6 | 0.00 [0.00–1.00], n=6 | 96.50 [39.00–359.00], n=6 | 0.00 [0.00–803.00], n=6 | 107.00 [42.00–1166.00], n=6 |
| webkit | cold | E | 47.50 [16.00–154.00], n=6 | 0.00 [0.00–0.00], n=6 | 47.50 [16.00–154.00], n=6 | 2.50 [0.00–7.00], n=6 | 55.00 [19.00–169.00], n=6 |
| webkit | warm | D | 256.50 [198.00–549.00], n=6 | 0.00 [0.00–0.00], n=6 | 257.50 [198.00–550.00], n=6 | 0.50 [0.00–334.00], n=6 | 263.50 [202.00–874.00], n=6 |
| webkit | warm | E | 144.50 [112.00–346.00], n=6 | 0.00 [0.00–0.00], n=6 | 144.50 [112.00–346.00], n=6 | 0.00 [-1.00–1.00], n=6 | 146.50 [114.00–359.00], n=6 |

## Panel operations

Roundtrips include trusted automation scheduling where applicable; render is measured DOM work for all bounded updates in the session. Restart includes creation through the first accepted rendered initialization reading.

| Browser | Fixture | Lazy panel open | Tool switch during compute | DOM render | Dispose | Restart to rendered t=0 |
|---|---|---|---|---|---|---|
| chromium | cold | 185.82 [176.07–195.58], n=2 | 42.97 [42.26–43.67], n=2 | 0.80 [0.00–5.20], n=28 | 6.56 [5.15–7.97], n=2 | 80.85 [76.80–84.90], n=2 |
| chromium | warm | 221.37 [212.17–230.57], n=2 | 196.41 [193.88–198.94], n=2 | 1.00 [0.00–3.40], n=28 | 8.81 [8.71–8.90], n=2 | 79.80 [76.00–83.60], n=2 |
| webkit | cold | 1277.57 [1201.03–1354.10], n=2 | 621.06 [464.55–777.57], n=2 | 2.00 [0.00–35.00], n=28 | 25.96 [8.41–43.51], n=2 | 363.00 [337.00–389.00], n=2 |
| webkit | warm | 1223.65 [1197.15–1250.16], n=2 | 311.30 [281.28–341.31], n=2 | 2.00 [0.00–5.00], n=28 | 14.40 [9.55–19.24], n=2 | 221.50 [181.00–262.00], n=2 |

## Memory observations

Browser/driver descendant RSS totals in MiB, median [min–max], n. These may count shared memory multiple times and include the browser shell and automation driver; they are not isolated JavaScript heap measurements. Raw receipts also retain coarse Chromium heap values and each process observation.

| Browser | Fixture | Case | Descendant RSS MiB |
|---|---|---|---|
| chromium | cold | C | 680.28 [671.55–689.01], n=2 |
| chromium | cold | D | 739.40 [731.12–747.67], n=2 |
| chromium | cold | E | 606.03 [598.54–613.52], n=2 |
| chromium | warm | C | 688.05 [677.89–698.22], n=2 |
| chromium | warm | D | 758.13 [746.50–769.77], n=2 |
| chromium | warm | E | 613.98 [601.59–626.37], n=2 |
| webkit | cold | C | 767.18 [737.86–796.51], n=2 |
| webkit | cold | D | 800.87 [773.25–828.48], n=2 |
| webkit | cold | E | 597.52 [572.46–622.58], n=2 |
| webkit | warm | C | 767.73 [748.17–787.28], n=2 |
| webkit | warm | D | 807.85 [784.19–831.50], n=2 |
| webkit | warm | E | 606.14 [584.19–628.09], n=2 |
