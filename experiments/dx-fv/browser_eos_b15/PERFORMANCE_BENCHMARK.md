# Final corrected-candidate performance

| Final workload | Original median ms (range) | Candidate median ms (range) | Paired median improvement | Median paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| ph-vapor | 567.55 (542.41–593.78) | 424.10 (418.89–428.16) | 24.69% | 139.85 | 6/6 |
| ph-mixed | 286.23 (281.30–298.99) | 218.47 (215.39–230.76) | 23.82% | 67.64 | 6/6 |
| cold-advance | 145.44 (142.26–169.73) | 167.67 (139.15–177.82) | -2.51% | -4.11 | 1/6 |
| warm-advance | 1016.86 (916.60–1041.90) | 880.41 (797.20–895.24) | 13.41% | 137.56 | 6/6 |


Six paired measurements per row, fresh separate processes, order AB/BA/BA/AB/AB/BA. PH vapor/mixed windows are disjoint scopes in the same six process pairs; each contains 20,000 calls. Vapor pressures 3.5/3.65/4/6/12 bar, superheat enthalpy offsets .00001/.1/5/50/150 kJ/kg; mixed uses equal equilibrium/vapor inputs. Warmup: 3,000 calls per workload outside windows. Solver uses original seven-checkpoint schedule through 0.01 s, trace mode and lightweight attempt counting. No expensive hashing/lexical counters in primary windows. Identical environment/runtime/options/table/fixtures/resource limits; sequential execution, no concurrent campaign. All 36 primary and eight supplemental samples are retained in `timing-samples.json`.

* ph-vapor: paired improvement range 21.99–29.45%; empirical median 95% interval 23.28–27.56%.
* ph-mixed: paired improvement range 19.74–26.67%; empirical median 95% interval 20.87–25.48%.
* cold-advance: paired improvement range -22.49–3.09%; empirical median 95% interval -16.94–0.57%.
* warm-advance: paired improvement range 4.08–21.82%; empirical median 95% interval 6.38–18.88%.

Intervals are exact empirical resampling of six observed pairs, descriptive with weak small-sample inference. They are not guarantees about host populations or desktop hardware. Positive percentages mean faster; negative means slower. Group medians and paired median deltas are different statistics. Primary timing measures worker-independent compute including original record work, excluding load/init/receipt serialization; no input-to-service latency measured. Residual/Newton/accepted/rejected counts and physical checksums match per pair; source counters are separate.

cold: CPU median 253.14 → 270.47 ms; peak RSS median 67,734 → 67,716 KiB; heapUsed median 20.93 → 17.97 MB; model initialization 4.38 → 4.57 ms.

warm: CPU median 1335.47 → 1176.60 ms; peak RSS median 96,102 → 96,568 KiB; heapUsed median 25.59 → 19.54 MB; model initialization 5.54 → 5.13 ms.


Engine parse/freeze, model initialization, process wall, heap/RSS and GC indicators are recorded separately. Peak memory/heap samples do not prove per-call allocator savings. Count-only/no-inner-timer observations estimate sensitivity; separately traced GC processes perturb execution and cannot establish exclusive advance GC cost. Never add nested scopes.

Preliminary v1 data, including a 1199.20 ms vapor candidate outlier (1205.88 ms CPU) and cold regression, remain in `prototype-v1/`. V1 failed public extra-argument compatibility. The corrected source was measured afresh in both variants; no v1 outlier was selectively removed from a final-version sample set. Its unexplained timing variability remains a caution. No causal explanation or universal speedup is asserted. Windows/macOS desktop browser performance, Worker transport and long refrigeration operation are unmeasured.

See `performance-analysis.json`, all sample-level receipts, and [paired figure](figures/paired-wall-times.png) / [work count figure](figures/pressure-search-counts.png). Final figures use only final-version primary samples, without trimming.
