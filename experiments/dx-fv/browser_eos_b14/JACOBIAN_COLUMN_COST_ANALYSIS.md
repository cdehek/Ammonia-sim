# Jacobian column cost

Observed original schedule: cold 235 Jacobians / 4,935 derivative residuals; warm 867 / 18,207. Each build uses all 21 finite-difference columns. Every normal derivative uses first positive sign, shrink=0; no branch fallback, failed probe, skipped residual or optional exact column occurs. Full original residuals and actual numerical matrix hashes match canonical reconstruction exactly.

Perturbations remain P: `1e-7*max(1,abs(P))` bar; H: `1e-8*max(1,abs(h))` kJ/kg; thermal E: `capacityKJK*1e-6` kJ. The difference quotient divides by selected signed step, exactly as original, not by recomputed actual floating displacement. Raw original events preserve epsilon, selected step, actual displacement, sign, shrink, base and derivative residuals. `columns-*.json` gives ranges/counts and each detailed observed receipt associates per-column counts/times with stage and trial. Repeated runs retain compact column totals after equivalence verification.

| Column | Coordinate | Cold ms median [range] | Cold PH calls | Warm ms median [range] | Warm PH calls |
|---|---|---|---|---|---|
| 0 | pressure-0 | 12.94 [12.45, 14.90] | 235 | 61.89 [60.69, 81.78] | 867 |
| 1 | enthalpy-0 | 10.73 [10.12, 11.62] | 235 | 55.84 [54.71, 56.27] | 867 |
| 2 | pressure-1 | 10.25 [9.42, 10.29] | 231 | 64.69 [56.95, 65.01] | 859 |
| 3 | enthalpy-1 | 9.54 [9.50, 18.34] | 231 | 55.89 [54.99, 56.69] | 859 |
| 4 | pressure-2 | 10.96 [10.53, 11.99] | 231 | 58.45 [55.06, 74.66] | 859 |
| 5 | enthalpy-2 | 15.64 [10.39, 15.65] | 231 | 55.67 [55.48, 56.60] | 859 |
| 6 | pressure-3 | 10.41 [9.02, 11.17] | 231 | 54.66 [54.22, 56.63] | 859 |
| 7 | enthalpy-3 | 9.50 [9.18, 9.57] | 231 | 58.27 [54.84, 60.15] | 859 |
| 8 | pressure-4 | 9.76 [9.19, 10.82] | 231 | 55.54 [55.52, 60.84] | 859 |
| 9 | enthalpy-4 | 10.75 [9.80, 12.65] | 231 | 65.21 [60.79, 66.29] | 859 |
| 10 | tube-0 | 6.60 [6.08, 9.71] | 0 | 20.85 [18.78, 21.27] | 0 |
| 11 | fin-0 | 8.99 [6.22, 17.73] | 0 | 18.79 [17.93, 18.83] | 0 |
| 12 | tube-1 | 6.23 [6.00, 9.82] | 0 | 20.39 [18.62, 22.05] | 0 |
| 13 | fin-1 | 6.23 [5.83, 6.44] | 0 | 18.03 [17.64, 32.05] | 0 |
| 14 | tube-2 | 6.48 [6.33, 7.26] | 0 | 18.05 [17.38, 23.03] | 0 |
| 15 | fin-2 | 5.92 [5.60, 7.17] | 0 | 19.32 [18.58, 21.72] | 0 |
| 16 | tube-3 | 6.78 [5.83, 10.17] | 0 | 18.50 [17.46, 20.78] | 0 |
| 17 | fin-3 | 6.39 [5.81, 7.24] | 0 | 18.02 [17.20, 21.89] | 0 |
| 18 | tube-4 | 6.38 [6.15, 11.75] | 0 | 20.14 [17.83, 24.20] | 0 |
| 19 | fin-4 | 7.83 [7.04, 14.51] | 0 | 22.47 [18.31, 24.92] | 0 |
| 20 | air | 6.05 [5.96, 6.53] | 0 | 18.75 [17.61, 27.92] | 0 |

Timings are inclusive wall ms summed over that column across the entire run, n=3 separate processes. They include original derivative residual assembly, property work, original event recording and B14 accounting; ranges are empirical, not confidence intervals. Strong timing overhead means these are not exclusive production cost estimates. See [limitations](PERFORMANCE_MEASUREMENT_LIMITATIONS.md) and [figure](figures/jacobian-columns.png).

## What the counts establish

Each thermal column causes 235 cold / 867 warm residual evaluations and five cache hits per residual, with **zero section misses, zero PH calls and zero branch interpolations**. All eleven thermal columns together cause 2,585 cold / 9,537 warm derivative residuals and 12,925 / 47,685 section cache hits. Hydraulic faces and fluid inventories are nevertheless rebuilt with unchanged PH; thermal-rate networks and scaled residuals are recomputed for every probe.

P/H columns cause 2,350 / 8,670 derivative residuals, with 2,318 / 8,606 PH misses. Most probes need one section property; shared stage-cache keys also reuse identical PH across sections during the uniform initial iterations. This explains four fewer cold and eight fewer warm misses in columns 2–9 than their build counts. It is expected shared exact-pair reuse within the original stage, not an asymmetric derivative rule. Section 0 always misses on its own probes; after its transition, fewer of those misses invoke vapor inversion (23,360 branch operations per column, versus 34,360 for each other warm P/H column).

Median aggregate P/H column time across processes: cold 111.31 ms, warm 587.73 ms. Median thermal-column total: cold 84.90 ms, warm 218.27 ms. Thus individual P/H columns are typically more expensive, especially warm; thermal columns are numerous and still substantial through assembly. Thermal columns are not the PH cost center. No stable scientific column-order slowdown beyond these counts is established by noisy short timing samples.

The inclusive Jacobian timer starts after the original 21×21 array allocation and contains B14's actual-matrix hashing before the end timer. Matrix hashing is expensive observation work and is not the scientific finite-difference cost. Do not interpret the difference between Jacobian and summed column envelopes as original allocation time or exclusive overhead.
