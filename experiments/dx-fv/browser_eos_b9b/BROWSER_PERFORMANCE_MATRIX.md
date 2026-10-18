# Actual browser performance and profiler limitations

Chromium **151.0.7922.34**, desktop WPE WebKit **26.5**, Playwright **1.62.0**;
Node **24.19.0** is an additional reference. The installed system Chromium 154
is not the measured browser. Launch paths, actual user agents, versions, binary
hashes, Node/V8/Python versions and protocol identity are retained in runtime.json
and passive-chromium.json.gz. No physical Safari/iPadOS inference is made.

| Engine | Fixture | Original ms, n=6 | Pass-through ms, n=3 | Diagnostic ms, n=3 |
|---|---|---|---|---|
| chromium | cold | 106.15 [94.80–122.90] | 106.90 [90.10–113.60] | 169.30 [149.30–174.70] |
| chromium | warm | 305.90 [274.30–363.50] | 315.40 [312.80–330.10] | 445.90 [432.30–462.70] |
| webkit | cold | 139.50 [104.00–167.00] | 121.00 [112.00–124.00] | 154.00 [153.00–167.00] |
| webkit | warm | 314.50 [288.00–344.00] | 314.00 [303.00–375.00] | 509.00 [459.00–513.00] |

Original timing is the authoritative unchanged advance computation boundary,
including trial/retry/acceptance/commit and mandatory record. It excludes extra
endpoint snapshots, detached state/attempt copies, exact hashes, transport and
browser startup. Initial/model times and per-command values remain in raw rows.
The harness's initializationMS begins after loader/table/engine creation and
includes model construction/create/initial record; it is not complete startup.
The unchanged original B9 worker service is separately reproduced in baseline
receipts, preserving import/factory/construction/service/RTT boundaries.

The research worker imports both original and unused diagnostic bundles. Thus
its startup/RTT also includes research module loading, large evidence copying,
bit tagging/hash work and delivery, and must not be sold as operator service
time or used to infer compilation-only cost. Worker model-advance timing and
original B9 service boundaries remain distinct. No startup optimization is tested.

Original detached state/attempt copy medians are 11.35/31.20 ms cold/warm Chromium
and 11.00/20.50 ms WebKit over the three endpoint copies. Extra original snapshot
record sums are 0.50/1.20 ms Chromium and 1.00/1.00 ms WebKit at available resolution.
These are actual outside-advance boundaries, not deductions from physical CPU.
Original diagnostic generation remains inside the solver and is not isolated as
a complete independent component. Display transport is not rebenchmarked here;
B9A's preserved evidence remains the secondary transport/copy reference.

## Original-source sampling

Chromium CDP Profiler requests 500 µs sampling on the dedicated original worker.
Raw cpu-chromium-*.json preserves call frames, source positions, samples and
timeDeltas. Only stacks containing accepted-bundle's advance function are used
for advance attribution; hashing, serialization and module startup are excluded.
The source range map is derived from exact accepted slices, not function names
alone. Anonymous frames retain their source file/line identity.

| Fixture | Advance samples | Engine stack samples | Weighted advance ms | Weighted engine ms | Engine weighted fraction |
|---|---|---|---|---|---|
| cold | 175 | 41 | 99.70 | 23.91 | 24.0% |
| warm | 432 | 205 | 265.71 | 123.40 | 46.4% |

For cold, coupled-model leaves total 53.21 ms, table engine 23.91 ms, coupled
Newton 7.91 ms and linear module 6.49 ms of sampled exposure. Warm: table engine
123.40 ms, coupled-model 104.27 ms, coupled Newton 15.87 ms and linear 11.20 ms.
MixRow/branch interpolation and the model's residual/quadrature arrays are visible
hot paths. The property stack is substantial but does not account for every
millisecond. The main supported ranking is **nonlinear residual/property work**,
then smaller linear/record/commit work, with separate diagnostic copying expense.

These are sample-delta-weighted stack exposure estimates, not exact exclusive
CPU cycles. Browser scheduling and lost/unrooted runtime/GC samples matter.
The cold profile has only 175 included samples; one profile per fixture cannot
establish stable percentages. No total-CPU 100% decomposition is claimed.

WebKit's Playwright `new_cdp_session` returns “CDP session is only available in
Chromium”. This establishes a limitation of the available automation interface,
not absence of every WebKit inspector/profiler in principle. No unsupported raw
inspector protocol is substituted. WebKit uses exact work counters and direct
instrumented boundary timings, with explicit overhead; no WebKit sampled stack
or private-function CPU percentage is asserted.

## Engine comparison and uncertainty

Both browsers execute identical operation counts and match their own saved
scientific baseline exactly. Their internal floating values are not assumed
cross-engine identical. Original medians differ, with overlapping scheduling/JIT
variability and coarse WebKit timing. Warm PH inclusive diagnostic medians are
164.40 ms Chromium / 227.00 ms WebKit; those values include observational counter
overhead and cannot establish a pure intrinsic property-engine ratio.

Node's warm reference uses 22,013 PH / 23,693 SAT / 940 MVU, one fewer Newton
correction than these browsers; cold matches their public count vector. Its
original, isolated-copy and direct-CommonJS references agree within Node, including
full original property sequences. Node timings/samples remain separate. Neither
Node nor desktop WebKit stands in for physical iPadOS Safari.

The full bounded workload is tiny startup only. No longer-duration throughput,
real-time capability, cooling-equipment calibration, speedup or device ranking
is extrapolated. All samples, significant spreads, profiler failures and limits
remain in the evidence rather than being replaced with favorable observations.
