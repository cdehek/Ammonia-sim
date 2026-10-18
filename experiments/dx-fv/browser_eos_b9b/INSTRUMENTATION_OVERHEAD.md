# Overhead and validity

Three matched rounds per engine/fixture run original → pass-through → diagnostic
→ original, each a fresh worker/loader/model with original reporting cadence.
No physics workloads or compiler jobs overlap. The complete original state,
records, attempts and property vector agree in every run; dedicated validation
also hashes every public property's input/output/throw sequence exactly.

| Engine | Fixture | Original ms, n=6 | Pass-through ms, n=3 | Diagnostic ms, n=3 |
|---|---|---|---|---|
| chromium | cold | 106.15 [94.80–122.90] | 106.90 [90.10–113.60] | 169.30 [149.30–174.70] |
| chromium | warm | 305.90 [274.30–363.50] | 315.40 [312.80–330.10] | 445.90 [432.30–462.70] |
| webkit | cold | 139.50 [104.00–167.00] | 121.00 [112.00–124.00] | 154.00 [153.00–167.00] |
| webkit | warm | 314.50 [288.00–344.00] | 314.00 [303.00–375.00] | 509.00 [459.00–513.00] |

Numbers are three-advance sums for .001 simulated seconds; median [min–max].
There are six original and three runs of each wrapper mode per fixture/engine.
For each round, overhead uses the mean of its original before/after sums:

| Engine | Fixture | Pass-through Δ ms | Diagnostic Δ ms | Diagnostic / bracket range |
|---|---|---|---|---|
| chromium | cold | -3.30 | 64.50 | 1.395–1.633 |
| chromium | warm | 16.00 | 140.65 | 1.338–1.559 |
| webkit | cold | -14.00 | 15.00 | 0.978–1.392 |
| webkit | warm | -13.00 | 184.50 | 1.453–1.758 |

Δ columns are medians over three paired differences. Negative pass-through
deltas are observed variance/JIT/representation effects, not a speedup claim.
Exported pass-through wrapper indirection and JIT/scheduling effects can affect
this workload; their observed deviations remain explicit. Observed diagnostic differences range approximately -2.2–75.8% across the brackets. A negative difference is timing variability, not negative
instrumentation cost. The diagnostic mode includes fine timers,
context strings, an additional read-only Map.has, internal counters and matrix
readouts. Do not derive intrinsic performance from these diagnostic durations
or scale all components by one global overhead ratio.

Original before/after differences are material; all raw samples remain visible
in performance-summary.json. Fresh worker does not mean cold OS cache or a
steady-state JIT. The first round is retained. Three rounds and sparse samples
do not support population confidence intervals or stable platform rankings.

The best observed clock increments are about .1 ms Chromium / 1 ms WebKit;
some bounded resolution probes observe no tick and report null. Many fine
intervals quantize to zero. Zero recorded ms does not establish zero CPU cost.
Nested elapsed timers overlap; exclusive wrapper remainders remain instrumented.

Passive Chromium controls (profiler disabled) / sampled / control advance sums:

| Engine | Fixture | Before / passive / after ms |
|---|---|---|
| chromium | cold | 95.70 control / 117.20 sampled / 89.00 control |
| chromium | warm | 273.40 control / 306.50 sampled / 274.60 control |
| webkit | cold | 121.00 control |
| webkit | warm | 286.00 control |

Only one sampled session per Chromium fixture was predefined. The sampled/control differences and their bracketing variance do not establish
an exact sampler-overhead estimate. Controls retain debugger attachment/resume but
do not enable Profiler. The separate original matrix has no CDP attachment.
WebKit has no supported sampler in this harness; its row is an original control,
not passive CPU evidence. Node inspector is supplementary and separately saved.

The initial passive harness error and a subsequently discovered sampled-control
issue are preserved under failed/superseded filenames. They are excluded from
all final statistics. Corrected final passive receipts distinguish sampled and
unsampled controls explicitly. No scientific outcomes differed in superseded
successful runs; no favorable sample selection was used.
