# Diagnostic overhead and limits

| Engine | Fixture | Mode | Primary median ms | Diagnostic ms (one pass) | Ratio |
|---|---|---|---|---|---|
| chromium | cold | control | 131.90 | 183.10 | 1.39× |
| chromium | cold | candidate | 69.10 | 95.80 | 1.39× |
| chromium | warm | control | 480.55 | 537.20 | 1.12× |
| chromium | warm | candidate | 317.20 | 362.90 | 1.14× |
| webkit | cold | control | 167.50 | 220.00 | 1.31× |
| webkit | cold | candidate | 77.00 | 154.00 | 2.00× |
| webkit | warm | control | 597.00 | 773.00 | 1.29× |
| webkit | warm | candidate | 373.00 | 505.00 | 1.35× |

The diagnostic path instruments actual public PH/SAT/MVU and lexical saturation/
inverse/branch operations, stage/trial/rate/record scopes, every residual result,
Jacobian/correction and logical boundary request. It stores values already
computed, adding no scientific property/residual calls. Timers and output data
are detached from numerical decisions. Function bodies are separately labeled
diagnostic artifacts with exact patches and hashes.

Diagnostic timers retain inclusive stage, residual, property-engine, rate and
record intervals. They overlap and include bookkeeping; they are not additive
or intrinsic exclusive CPU costs. Tiny intervals quantize at browser resolution.
The full residual-value SHA is calculated AFTER advance, before reduction to
raw residual arrays. Matrix/FD/Newton/stage equality is independent of timing.

Ratios compare one diagnostic run with primary matched medians, not a stable
overhead estimate or paired confidence interval. The initial overly detailed
artifact exports were manually terminated and superseded: they imposed excessive
protocol/serialization memory/time. They produced no scientific failure or usable
performance result. Final exports preserve complete fixed-workload property
ledgers and science, with full residual-value hashes plus raw residual/matrix/
stage evidence. Extra regressions retain complete science/observer data, component
hashes and logical boundary-result hashes with counts instead of duplicating all
large raw diagnostic arrays. Failed/superseded logs are retained explicitly.
No favorable timing sample selection followed those harness-only corrections.

| Engine | Fixture | Mode | Stage ms | Residual ms | PH ms | Public SAT ms | MVU ms | Record ms |
|---|---|---|---|---|---|---|---|---|
| chromium | cold | control | 176.10 | 157.10 | 89.20 | 7.00 | 1.60 | 2.20 |
| chromium | cold | candidate | 83.90 | 59.40 | 9.40 | 2.20 | 1.30 | 2.00 |
| chromium | warm | control | 500.40 | 457.40 | 317.90 | 15.30 | 23.50 | 3.50 |
| chromium | warm | candidate | 328.00 | 292.20 | 167.20 | 7.80 | 20.80 | 4.90 |
| webkit | cold | control | 211.00 | 195.00 | 119.00 | 6.00 | 2.00 | 5.00 |
| webkit | cold | candidate | 139.00 | 114.00 | 10.00 | 2.00 | 2.00 | 2.00 |
| webkit | warm | control | 712.00 | 659.00 | 522.00 | 17.00 | 44.00 | 7.00 |
| webkit | warm | candidate | 448.00 | 397.00 | 277.00 | 15.00 | 38.00 | 5.00 |

Stage/residual timers cover advance work. Property and record scopes cover the
full frozen workload, including initialization and extra records. These are
one-pass inclusive DIAGNOSTIC measurements with overhead, not primary medians.
