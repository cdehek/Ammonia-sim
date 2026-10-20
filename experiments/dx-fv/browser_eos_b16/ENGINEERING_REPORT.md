# B16-A0 final engineering report

**B16-A0 DESKTOP/WORKER READINESS PASS**. Independent integration recommendation: **CONDITIONAL GO** for a later separately authorized isolated research review. No integration or deployment occurred.

Start: exact B15 `eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35`, initially clean. Branch: `research/b16-desktop-worker-performance-20261020`. Design commit `20406db` preceded harness implementation. Final SHA is the delivered branch HEAD (a commit cannot embed itself). Initial/final byte/ref/PR receipts and completion remote-HEAD check bind delivery. All 4,057 historical tracked files, 312 B15 sealed files, A2 closure, B9C control, table and B12 scientific/workstation sources remain unchanged. PR #3 remains open at original head `d4422425750a1d3c4e432cc103ac42ead40b7cc6`, base/main `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`; protected remote refs/tags are reverified. No Cloudflare account/deployment/host modification occurs.

Scientific parity: PASS in actual Chromium module Workers across cold/warm × original/added/fine schedules, uninstrumented/observer modes. Complete state/record/attempt, full residual, Jacobian/RHS/Newton correction, temporal/controller/phase/ledger and failure semantics match exactly by runtime. 77,258 full residuals and 3,452 actual matrices/corrections compare per variant; conservation passes original thresholds. Raw NaN and numerical partial-progress semantics are retained, including initial harness-assumption failures and fresh passing rerun. Accepted checkpoints include 0/.0001/.0005/.001 s. Maximum solve .01 s; >.001 s remains UNQUALIFIED RESEARCH.

## Node wall results (ms; six pairs each)

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, fresh | 76.95 | 73.83 | 4.54 | 3.44 | 5/6 |
| warm, fresh | 475.94 | 420.65 | 10.61 | 49.93 | 6/6 |
| cold, 2 warmups | 69.72 | 60.01 | 12.69 | 8.66 | 5/6 |
| warm, 2 warmups | 439.04 | 389.27 | 11.68 | 51.18 | 6/6 |

Node CPU results and full dispersion are separate in `BENCHMARK_RESULTS.md`. B15's cold wall regression is not reproduced consistently here. Counters reproduce exactly 210/15,739 eligible cold/warm vapor inversions and 8,190/613,821 removed pressure brackets; no scientific source changed.

## Actual Chromium Worker compute results (ms; six pairs each)

| Case | Original median ms | Candidate median ms | Paired improvement % | Paired ms saved | Faster pairs |
|---|---:|---:|---:|---:|---:|
| cold, fresh | 81.90 | 76.70 | 6.83 | 5.60 | 6/6 |
| warm, fresh | 444.30 | 404.45 | 8.82 | 39.15 | 5/6 |
| cold, 2 warmups | 45.95 | 48.30 | -4.29 | -1.95 | 2/6 |
| warm, 2 warmups | 436.30 | 379.80 | 12.49 | 55.50 | 6/6 |

Warm improvements translate to real Worker compute and service latency on this host. Warmed Chromium cold has a small regression; fresh cold and Node wall differ. Ranges, all valid extremes, absolute savings and paired percentages are retained; there is no universal speedup or proven cold root cause. Property microbenchmarks show supported vapor/mixed benefits and near-zero two-phase gain, not a substitute for solver evidence. Added/fine and transition intervals are separately labeled exploratory.

Worker lifecycle/transport: original/candidate ready medians 9.80/10.00 ms; initial snapshot roundtrip 32.60/31.50 ms; ping 0.10/0.05 ms. Asset verification, import/table/create, service, clone/enqueue envelope, handler, text assignment, disposal/restart are separately retained. No exclusive serialization CPU or layout claim is made.

Independent main-thread heartbeat/synthetic DOM input/tool acknowledgements are measured through Worker startup/compute; fresh primary heartbeat max excess delay 21.20 ms, with no observed long tasks in those windows. This is minimal-harness evidence only. Twelve reset/history sessions show bounded attempts/snapshots and disposal reference dropping; coarse renderer/Node memory cannot establish worker allocation savings or hours-long stability. V8 optimization/inlining/deopt/GC and jitless receipts characterize uncertainty without causal overclaiming.

Host: Linux cloud, AMD EPYC 9V45 identification, two-CPU quota, 8 GiB limit; Node 24.19.0, Chromium 154.0.8037.57, Playwright 1.62.0. Desktop WebKit and actual Edge NOT TESTED (executables absent); Windows/macOS hardware and owner desktop NOT TESTED. The local owner ZIP's actual UI/download passed on this cloud host only. No public deployment is required.

Remaining limits: unknown real installation/usage distribution, cold/JIT/GC sensitivity, small one-host samples, unisolated allocation/clone/worker heap, minimal rather than full workstation UI, unqualified >.001 s science and original physical/calibration bounds. Recommendation: B17 target-device characterization and separate integration design review, keep exact B9C default/rollback, no candidate promotion without explicit future authorization. Working tree and matching pushed B16 remote HEAD are verified at delivery, after final commit. Stop for engineering review.
