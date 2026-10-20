# Cold performance: bounded evidence, unresolved cause

B15's five-of-six cold regression is not a stable universal result in B16. Node wall timing improves on this host; Chromium changes sign between fresh and warmed-engine strata. Warmed Chromium cold median regression is -1.95 ms saved (negative means lost), -4.29%, candidate faster in 2/6. Its paired range includes both signs. This small sample supports a real engineering tradeoff to retain, but not a statistically firm general cold penalty or a proven causal root cause.

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, fresh | 76.95 | 73.83 | 4.54 | 3.44 | 5/6 |
| warm, fresh | 475.94 | 420.65 | 10.61 | 49.93 | 6/6 |
| cold, 2 warmups | 69.72 | 60.01 | 12.69 | 8.66 | 5/6 |
| warm, 2 warmups | 439.04 | 389.27 | 11.68 | 51.18 | 6/6 |
| Chromium cold, fresh | 81.90 | 76.70 | 6.83 | 5.60 | 6/6 |
| Chromium warm, fresh | 444.30 | 404.45 | 8.82 | 39.15 | 5/6 |
| Chromium cold, 2 warmups | 45.95 | 48.30 | -4.29 | -1.95 | 2/6 |
| Chromium warm, 2 warmups | 436.30 | 379.80 | 12.49 | 55.50 | 6/6 |

## Confirmed workload and ownership

Advance-only original schedule, initialization excluded, no additional checkpoint records. Frozen observer context probe matches original/candidate science and property distributions. Counts below are Node observations; separate Chromium diagnostic receipts include initialization/additional record observations and can follow a different exploratory adaptive path.

| Fixture | PH calls | Eligible vapor holders | Other PH (mixture here) | PH outside implicit stages | PH in finite-difference columns | Boundary cache hit/miss | Section cache hit/miss |
|---|---:|---:|---:|---:|---:|---:|---:|
| cold | 5,028 | 210 (4.18%) | 4,818 | 837 | 2,318 | 10,340/420 | 22,373/3,987 |
| warm | 17,416 | 15,739 (90.37%) | 1,677 | 2,365 | 8,606 | 38,148/1,236 | 82,461/14,439 |

Cold pressure brackets 27,324 → 19,134 (8,190 removed); warm 764,565 → 150,744 (613,821 removed). All 38 bisections and 40 branch interpolations per successful eligible vapor PH remain unchanged. Cold column PH calls are mixture calls; vapor work is concentrated in other stage/trial/record work. Existing stage caches mean many residual section requests hit cached thermodynamic states; property calls are not uniformly distributed among residual coordinates. `context-counts.json` retains all contexts and cache counts, exactly equal by variant.

The cold candidate constructs 210 local holders during advance; two-phase returns before holder construction. Public PT has one forwarding closure per engine and an extra public call layer, while internal branch helpers carry an additional optional argument and ownership test. Source-level bracket-array construction is reduced, but machine-code allocation elimination is unknown. No per-inversion allocation profile was measured. Lower heap snapshots do not establish savings.

## Controls and interpretation

Uninstrumented primary cases use no inner lexical counters or scientific hashing. Six paired counters-only samples per fixture are separate; their cold paired median 0.19% does not isolate holder overhead, since instrumentation changes both code shape and runtime. Three no-optimizing-JIT pairs yield cold 0.94% and warm 10.18% median improvement. Disabling JIT is a sensitivity control, not causal decomposition or a recommended setting.

Fresh versus warmed Chromium changes the cold sign. Node fresh cold CPU is -1.43% paired while its wall time improves; CPU includes concurrent compiler/GC work and cannot be substituted for wall latency. Counterbalanced order, fresh ownership and exact counts rule out a deliberately different scientific workload, but do not remove scheduling/JIT/GC variability. The large fresh-cold pair remains included. Browser cache effects are shared controls, not experimentally isolated.

V8 traces show optimization/inlining/deoptimization and GC in both variants. They do not identify a unique candidate-only deoptimization responsible for cold timing, quantify exclusive fast-path overhead, or establish GC as the cause. No overlapping timer subtraction is used. The small vapor fraction makes fixed/code-shape overhead a plausible hypothesis, not a demonstrated explanation. The evidence is runtime/warmup-sensitive and too variable/small for a general root-cause claim. Keep the cold tradeoff visible and measure intended devices before a default decision. No frozen prototype is modified to improve these results.
