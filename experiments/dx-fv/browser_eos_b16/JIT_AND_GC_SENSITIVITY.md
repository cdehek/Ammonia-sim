# JIT and GC sensitivity

Fresh and two-replay warmed-JIT cases are separate primary strata. The warmed model is newly created after untimed resets; no state crosses samples. Chromium cold flips from 6.83% to -4.29% paired improvement; warm remains beneficial, with all six warmed pairs faster. Node cold does not show the same wall-time regression. This demonstrates sensitivity, not proof that warmup explains most of B15's slowdown.

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| counters-cold | 85.60 | 84.54 | 0.19 | 0.12 | 3/6 |
| counters-warm | 711.82 | 571.82 | 18.43 | 128.58 | 6/6 |
| jitless-cold | 259.76 | 257.33 | 0.94 | 2.43 | 2/3 |
| jitless-warm | 1849.65 | 1666.48 | 10.18 | 187.91 | 3/3 |

Counters-only frozen sources perturb code shape and cannot be used as primary speed estimates. `--jitless` disables optimizing execution in separate Node processes, three counterbalanced pairs per case; no browser or deployment setting is changed. The limited three-pair result is descriptive.

Four observed processes run trace-opt, trace-deopt, trace-turbo-inlining, trace-file-names and trace-gc-nvp. Whole traces are retained compressed, bounded by process/CPU/output limits. Relevant function examples/counts and deoptimization reasons are in `jit-gc-trace-summary.json`. `pBracket`, `branch`, `inverse` and solver functions become hot and compile; the traces show Maglev and, in warm work, TurboFan activity. Inlining lines include decisions/candidates as well as actual inlining and are not all successful inlines. Generic wrong-map/type deoptimizations occur in both variants. No stable candidate-only causal mechanism is isolated.

| Observed process | Deoptimizations | GC events | Whole-process GC pause ms |
|---|---:|---:|---:|
| trace-candidate-cold.txt.gz | 8 | 30 | 18.10 |
| trace-candidate-warm.txt.gz | 27 | 89 | 30.90 |
| trace-control-cold.txt.gz | 8 | 30 | 28.60 |
| trace-control-warm.txt.gz | 24 | 101 | 41.90 |

These are single observed processes including startup, table parse/freeze, initialization and compute; trace output adds overhead. Whole-process pauses are not exclusive solver GC cost and are not subtracted from solver time. Primary Node receipts also retain timestamped PerformanceObserver GC events, memory and CPU; callbacks run after synchronous work and may straddle scope boundaries. Neither lower post-run heap nor fewer source arrays establishes allocator-byte savings, escape analysis, peak live memory, or GC causation. Per-allocation/per-function profiles and controlled target-browser compiler traces remain gaps.
