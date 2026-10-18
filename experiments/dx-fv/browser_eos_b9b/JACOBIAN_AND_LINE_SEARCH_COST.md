# Jacobian, residual, thermal and linear-algebra cost

The 21 coordinates are interleaved five p/h pairs followed by eleven thermal
energy increments. Residual rows are five normalized mass/energy pairs plus
eleven thermal closures. Pressure/enthalpy epsilon and signed shrink loops are
unchanged. The default FD thermal setting remains in force.

All 130 / 345 Jacobian assemblies fill all 21 columns: 650/1,725 pressure,
650/1,725 enthalpy and 1,430/3,795 thermal probes. Every derivative is used on
the first positive probe here. All 130 / 345 line searches accept factor 1 on
the first candidate. A line-search residual is never counted as Jacobian work.

The following are medians of three diagnostic ADVANCE sums in ms. They are
**inclusive, nested, instrumented elapsed intervals**, not an additive CPU budget:

| Engine | Fixture | Newton | Residual | PH | SAT public | MVU | Rates | Blend | Linear + diagnostics |
|---|---|---|---|---|---|---|---|---|---|
| chromium | cold | 156.40 | 136.90 | 44.60 | 5.30 | 1.80 | 80.70 | 25.20 | 7.50 |
| chromium | warm | 406.20 | 372.20 | 164.40 | 10.70 | 10.40 | 192.80 | 54.50 | 13.50 |
| webkit | cold | 143.00 | 128.00 | 51.00 | 2.00 | 1.00 | 82.00 | 18.00 | 5.00 |
| webkit | warm | 462.00 | 431.00 | 227.00 | 16.00 | 8.00 | 226.00 | 38.00 | 11.00 |

Rates include boundary PH, temperature/domain checks, flow/donor calculations,
tube/refrigerant heat, 15 tube/fin/air links and thermal rate assembly. Residuals
also contain cached section lookups, inventory construction, energy increments,
blended quadrature and normalized balance rows. Blend repeatedly constructs
small arrays and reduces the original stage weights in the original order.
Newton also contains matrix allocation/assembly, derivative differences,
norms, original diagnostic events, linear solution and correction/line search.
Public timers do not independently split every one of these private expressions.

`linearSolve` includes the original solve PLUS read-only matrix norms,
diagonal-range and backward-residual diagnostics in the wrapper. It is therefore
an upper containing interval in the diagnostic run, not pure elimination time.
Those diagnostics do not calculate a condition number: recorded `conditionNumber`
is null. Diagonal ranges are not condition numbers. No claim that warm matrices
are poorly conditioned is supported. All observed systems are 21×21 and solve.

The original Chromium sampler independently observes unchanged solveLinear:
6.49 ms cold and 10.61 ms warm sample-delta exposure at the solveLinear leaf;
all implicit.cjs leaves total 6.49 / 11.20 ms within 99.70 / 265.71 ms of sampled
advance exposure. Sampling is sparse and does not give exact CPU-cycle durations,
but it excludes the dense solve as the dominant measured browser cost here.
WebKit's containing timed intervals are also small relative to residual/Newton
intervals, with timer quantization and diagnostic overhead explicitly retained.

Each synchronous timer frame tracks measured child duration. The raw
`advanceExclusiveMS` subtracts directly nested timer intervals from the parent;
it remains an **instrumented wrapper remainder**, including unmeasured child
work, timer bookkeeping and allocation. For example Newton's remainder includes
matrix assembly, corrections and original diagnostics, and is not a pure
diagnostic-generation measurement. Rates' remainder combines physical arithmetic
and allocations. Exclusive wrapper remainders are not intrinsic CPU estimates.

Never add Newton + residual + PH + rates: each can contain another. Never
subtract a detached-copy microbenchmark as if it were an in-solver component.
Only the sampler's mutually exclusive leaf/source categories form a partition
of its explicitly included samples; unrooted GC/runtime samples cannot be
assigned to an advance and are excluded. No 100% whole-CPU pie is manufactured.

Required numerical work includes the observed finite differences, canonical
recovery, accuracy error estimation, conservation/domain checks and rejected
intervals. Potential redundancy concerns identical intermediates and temporary
organization, never skipping a branch-sensitive probe or changing tolerances.
