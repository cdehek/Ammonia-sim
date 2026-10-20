# Workload realism and tradeoffs

The actual distribution of future ammonia installation conditions and operator requests is NOT established. The original cold/warm fixtures are illustrative, materially different property workloads. Cold has 4.18% eligible vapor PH calls during advance; warm 90.37%. This does not make warm representative of all industrial refrigeration. No plant duty cycle is fabricated.

The measured matrix includes both original fixtures, repeated independent starts, fresh and warmed JIT, original/added/fine schedules, a transition-bearing warm 0.005→0.01 s interval, supported vapor-dominant/two-phase-dominant/equal-count mixed PH sequences, and short reset/history sessions. All advances remain ≤0.01 s. Detailed paired absolute and relative results, sample counts and dispersion are in `BENCHMARK_RESULTS.md` / `analysis.json`.

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, fresh | 81.90 | 76.70 | 6.83 | 5.60 | 6/6 |
| warm, fresh | 444.30 | 404.45 | 8.82 | 39.15 | 5/6 |
| cold, 2 warmups | 45.95 | 48.30 | -4.29 | -1.95 | 2/6 |
| warm, 2 warmups | 436.30 | 379.80 | 12.49 | 55.50 | 6/6 |

Vapor/mixed property benefits do not translate directly to coupled solver gains. Two-phase PH shows near-zero gain, and warmed Chromium cold has a small median regression while warm improves. A cold slowdown is retained even where its absolute milliseconds are smaller than warm savings. Node/browser and JIT differences prevent a universal default conclusion. Transition-bearing interval timing is exploratory and can include both vapor and mixture work.

## Hypothetical planning scenarios only

Each scenario weights whole bounded cold/warm requests, combines matched pair-index absolute timings, then computes each pair's relative improvement. These are declared request-count mixes, not physical time, energy, plant operating distributions or operator usage evidence. There are six synthetic paired scenarios each; pairing index across separate cases adds another planning assumption. They are not new measured mixed solver sessions.

| Hypothetical request mix | Warmups | Cold request fraction | Median paired ms saved | Median paired improvement % |
|---|---:|---:|---:|---:|
| cold-heavy | 0 | 90% | 8.05 | 6.81 |
| balanced | 0 | 50% | 22.08 | 8.37 |
| warm-heavy | 0 | 10% | 35.74 | 8.76 |
| cold-heavy | 2 | 90% | 2.70 | 3.23 |
| balanced | 2 | 50% | 25.50 | 10.44 |
| warm-heavy | 2 | 10% | 49.50 | 12.24 |

A favorable scenario does not authorize integration or resolve the cold penalty. Retain the original as independently selectable control/default for any future review. Establish target-device behavior and intended research workloads before considering candidate opt-in policy.
