# Actual benchmark results

All valid samples retained; no timing exclusions or outlier trimming. Six pairs per primary row, same runtime/options/inputs, AB/BA/BA/AB/AB/BA. Positive paired values mean candidate faster. Paired medians are not ratios of group medians. Fresh means fresh process/Worker JIT, not empty disk/network cache. Two warmups are untimed bounded model resets followed by a new measured model. All solver rows end at 0.01 s; >0.001 s is UNQUALIFIED RESEARCH.

## Node 24.19.0 engine wall time

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, fresh | 76.95 | 73.83 | 4.54 | 3.44 | 5/6 |
| warm, fresh | 475.94 | 420.65 | 10.61 | 49.93 | 6/6 |
| cold, 2 warmups | 69.72 | 60.01 | 12.69 | 8.66 | 5/6 |
| warm, 2 warmups | 439.04 | 389.27 | 11.68 | 51.18 | 6/6 |

CPU milliseconds are recorded separately. CPU paired results:

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, warmups=0 | 127.50 | 128.58 | -1.43 | -1.82 | 2/6 |
| warm, warmups=0 | 630.27 | 573.64 | 9.49 | 59.91 | 6/6 |
| cold, warmups=2 | 117.65 | 107.12 | 6.90 | 7.77 | 5/6 |
| warm, warmups=2 | 506.97 | 461.82 | 8.13 | 41.05 | 6/6 |

## Actual Linux Chromium 154 Web Worker compute wall time

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, fresh | 81.90 | 76.70 | 6.83 | 5.60 | 6/6 |
| warm, fresh | 444.30 | 404.45 | 8.82 | 39.15 | 5/6 |
| cold, 2 warmups | 45.95 | 48.30 | -4.29 | -1.95 | 2/6 |
| warm, 2 warmups | 436.30 | 379.80 | 12.49 | 55.50 | 6/6 |

Worker compute includes original model.advance and original record work, excludes asset/init, compact projection, message transport and main handler. Full state/record/attempt digests checked after timing match per pair. Same-runtime comparison only; exploratory Node and browser trajectories need not be bit-identical.

## Supported PH microbenchmarks — 20,000 calls per class

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| node-vapor | 296.67 | 230.08 | 22.44 | 66.59 | 6/6 |
| node-twoPhase | 8.97 | 9.15 | -2.46 | -0.22 | 2/6 |
| node-mixed | 151.01 | 118.79 | 21.22 | 32.00 | 6/6 |
| worker-vapor | 251.30 | 188.75 | 25.75 | 63.85 | 6/6 |
| worker-twoPhase | 7.20 | 7.20 | -0.00 | -0.00 | 1/6 |
| worker-mixed | 127.85 | 97.00 | 24.98 | 31.90 | 6/6 |

Each has 3,000 untimed calls; equal-count mixed is a research input sequence. Microbenchmark gains are not coupled-solver gains. Two-phase is an explicit near-zero-benefit control.

## Supplemental scopes and sensitivity

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| warm-transition-0.005-to-0.01-warmups0 | 153.10 | 139.60 | 7.73 | 11.65 | 5/6 |
| warm-transition-0.005-to-0.01-warmups2 | 153.35 | 128.95 | 13.84 | 21.00 | 6/6 |
| cold-added | 87.45 | 88.75 | -1.63 | -1.30 | 1/2 |
| warm-added | 427.75 | 379.75 | 11.19 | 48.00 | 2/2 |
| cold-fine | 98.10 | 95.65 | 2.07 | 2.45 | 1/2 |
| warm-fine | 444.85 | 384.50 | 13.52 | 60.35 | 2/2 |
| counters-cold | 85.60 | 84.54 | 0.19 | 0.12 | 3/6 |
| counters-warm | 711.82 | 571.82 | 18.43 | 128.58 | 6/6 |
| jitless-cold | 259.76 | 257.33 | 0.94 | 2.43 | 2/3 |
| jitless-warm | 1849.65 | 1666.48 | 10.18 | 187.91 | 3/3 |

Added/fine: two independent pairs each, exploratory only. Jitless: three pairs each, a separate interpreter sensitivity run, not normal browser performance. Counters: six pairs each with perturbed code shape. Four traced V8 processes are separate observed samples with no primary-pair inference. Raw sample counts: 60 primary Node processes (48 solver, 12 PH), 24 counters-only, 12 jitless, four trace-observed; 64 Worker solver samples (48 primary, 16 supplemental), 12 Worker PH samples. Twelve bounded retention sessions and 24 packaged-UI validation samples are separate evidence, not primary timing substitutions. Every valid and failed setup/harness attempt remains retained.

## Range and dispersion

Ranges and IQRs below retain extremes. IQR is linearly interpolated over observed samples; these are descriptive small-sample statistics, not device-population confidence intervals. Raw pairs, all medians/ranges/IQRs and service/roundtrip statistics are in `evidence/analysis.json`.

| Case | Original ms range / IQR | Candidate ms range / IQR | Paired % range / IQR |
|---|---:|---:|---:|
| Node cold-warmups0-wallMS | 74.22–82.84 / 5.00 | 71.57–78.16 / 4.77 | -4.67–11.92 / 1.63 |
| Node cold-warmups0-cpuMS | 126.14–133.23 / 2.99 | 126.50–133.82 / 2.23 | -2.33–4.24 / 1.90 |
| Node warm-warmups0-wallMS | 466.30–501.82 / 14.00 | 413.22–442.74 / 16.89 | 5.67–16.54 / 4.26 |
| Node warm-warmups0-cpuMS | 619.99–655.77 / 22.22 | 567.43–586.77 / 1.08 | 5.79–12.48 / 3.84 |
| Node cold-warmups2-wallMS | 56.23–84.90 / 8.94 | 56.07–83.44 / 3.96 | -5.72–24.25 / 11.88 |
| Node cold-warmups2-cpuMS | 99.72–146.98 / 16.40 | 96.41–150.77 / 12.72 | -14.46–22.00 / 8.87 |
| Node warm-warmups2-wallMS | 436.83–464.16 / 3.86 | 382.70–402.36 / 6.61 | 7.89–15.85 / 2.40 |
| Node warm-warmups2-cpuMS | 482.16–549.73 / 9.19 | 431.71–482.68 / 16.67 | 4.66–16.04 / 9.09 |
| Worker cold-warmups0-computeMS | 74.00–142.20 / 4.42 | 71.80–81.30 / 2.12 | 1.62–42.83 / 5.86 |
| Worker cold-warmups0-serviceMS | 74.20–142.50 / 5.35 | 72.00–81.40 / 2.08 | 1.50–42.88 / 6.66 |
| Worker cold-warmups0-roundtripMS | 74.70–142.60 / 6.10 | 73.80–82.60 / 2.05 | 0.50–42.08 / 8.61 |
| Worker warm-warmups0-computeMS | 427.60–464.20 / 21.65 | 391.60–451.00 / 13.75 | -5.47–15.64 / 6.52 |
| Worker warm-warmups0-serviceMS | 427.80–464.30 / 21.65 | 391.70–451.00 / 13.83 | -5.42–15.64 / 6.54 |
| Worker warm-warmups0-roundtripMS | 428.00–464.50 / 21.63 | 391.80–451.30 / 13.43 | -5.44–15.65 / 6.40 |
| Worker warm-transition-0.005-to-0.01-warmups0 | 148.30–156.80 / 6.02 | 135.00–181.60 / 4.03 | -22.45–13.90 / 2.94 |
| Worker cold-warmups2-computeMS | 43.90–51.90 / 4.33 | 46.00–52.30 / 1.88 | -12.53–5.82 / 9.37 |
| Worker cold-warmups2-serviceMS | 44.30–52.00 / 4.53 | 46.20–52.40 / 1.90 | -11.74–6.00 / 9.76 |
| Worker cold-warmups2-roundtripMS | 44.40–52.20 / 4.68 | 46.60–52.50 / 1.97 | -12.16–6.35 / 9.22 |
| Worker warm-warmups2-computeMS | 407.00–446.70 / 12.10 | 359.00–406.70 / 15.57 | 5.29–16.88 / 6.53 |
| Worker warm-warmups2-serviceMS | 409.50–448.30 / 12.02 | 361.10–407.10 / 14.82 | 5.30–16.89 / 6.32 |
| Worker warm-warmups2-roundtripMS | 410.20–448.90 / 13.18 | 362.00–407.50 / 14.30 | 5.41–17.11 / 5.95 |
| Worker warm-transition-0.005-to-0.01-warmups2 | 143.60–162.90 / 6.75 | 125.70–144.00 / 4.60 | 10.45–20.54 / 4.61 |
| Worker cold-added | 82.50–92.40 / 4.95 | 85.90–91.60 / 2.85 | -4.12–0.87 / 2.49 |
| Worker warm-added | 422.10–433.40 / 5.65 | 374.20–385.30 / 5.55 | 8.72–13.66 / 2.47 |
| Worker cold-fine | 90.80–105.40 / 7.30 | 94.10–97.20 / 1.55 | -3.63–7.78 / 5.71 |
| Worker warm-fine | 436.20–453.50 / 8.65 | 380.30–388.70 / 4.20 | 10.89–16.14 / 2.63 |
| node-vapor | 290.74–305.19 / 10.90 | 227.19–237.66 / 2.40 | 18.26–25.42 / 3.72 |
| node-twoPhase | 8.75–9.18 / 0.14 | 8.84–10.52 / 0.42 | -17.28–3.74 / 5.20 |
| node-mixed | 150.35–156.89 / 3.52 | 117.22–121.91 / 2.69 | 19.35–25.29 / 3.69 |
| worker-vapor | 244.00–276.50 / 8.77 | 182.80–206.50 / 5.52 | 15.44–30.89 / 2.09 |
| worker-twoPhase | 7.10–7.20 / 0.07 | 7.10–7.70 / 0.30 | -7.04–0.00 / 5.21 |
| worker-mixed | 126.00–131.80 / 3.45 | 95.10–97.40 / 1.12 | 23.02–26.10 / 2.00 |
| counters-cold | 78.17–88.52 / 3.82 | 80.32–92.81 / 6.11 | -8.87–4.97 / 9.31 |
| counters-warm | 689.74–777.22 / 26.64 | 550.37–623.86 / 40.17 | 11.70–27.21 / 7.85 |
| jitless-cold | 244.44–271.46 / 13.51 | 255.33–267.19 / 5.93 | -4.45–1.57 / 3.01 |
| jitless-warm | 1845.02–1903.84 / 29.41 | 1657.11–1677.72 / 10.31 | 9.30–12.47 / 1.59 |
