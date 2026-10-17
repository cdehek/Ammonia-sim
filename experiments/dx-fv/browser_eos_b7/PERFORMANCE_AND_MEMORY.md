# Actual rebuilt-WASM performance and memory

These are bounded desktop browser observations, not native forecasts, kernel-only costs, sustained production throughput or physical Safari/iPad results. Five short interleaved control/candidate rounds per workload/path use at least 60 ms each. No compiler or property campaign runs concurrently with the timing campaign. Warm-up, JIT tiering, timer granularity and host variability remain relevant. Raw sample ranges, calls/second and per-request return/refusal counts are preserved in `performance-*.json`; no speedup claim is based on an individual run.

Control and candidate use the same reviewed B6 lifecycle handling. They differ scientifically only by the exact Gate A patch. All qualification identities are explicit and hash-verified.

| Engine | Path | Workload | Control median µs/call | Candidate median µs/call | Outcome comparison |
|---|---|---|---:|---:|---|
| chromium | default | fresh-supported-state | 123.71 | 118.34 | Matched raw outcomes |
| chromium | default | genuine-mixture | 3.37 | 3.43 | Matched raw outcomes |
| chromium | default | homogeneous-liquid | 7.89 | 8.06 | Matched raw outcomes |
| chromium | default | homogeneous-vapor | 7.77 | 7.77 | Matched raw outcomes |
| chromium | default | original-resolved-liquids | 11.40 | 11.44 | Matched raw outcomes |
| chromium | default | original-unresolved-endpoints | 13.26 | 13.22 | Matched raw outcomes |
| chromium | default | rejected-PT | 16.93 | 17.10 | Matched raw outcomes |
| chromium | default | reused-supported-state | 7.75 | 7.71 | Matched raw outcomes |
| chromium | default | supported-PH-PT-DU | 22.52 | 22.75 | Matched raw outcomes |
| chromium | full VLE | fresh-supported-state | 114.91 | 114.07 | Matched raw outcomes |
| chromium | full VLE | genuine-mixture | 220.59 | 218.91 | Matched raw outcomes |
| chromium | full VLE | homogeneous-liquid | 8.06 | 7.85 | Matched raw outcomes |
| chromium | full VLE | homogeneous-vapor | 7.70 | 7.58 | Matched raw outcomes |
| chromium | full VLE | original-resolved-liquids | 226.22 | 36.10 | Different outcomes; ratio excluded |
| chromium | full VLE | original-unresolved-endpoints | 223.88 | 181.33 | Different outcomes; ratio excluded |
| chromium | full VLE | rejected-PT | 122.45 | 122.15 | Matched raw outcomes |
| chromium | full VLE | reused-supported-state | 7.57 | 7.55 | Matched raw outcomes |
| chromium | full VLE | supported-PH-PT-DU | 131.58 | 130.09 | Matched raw outcomes |
| webkit | default | fresh-supported-state | 197.37 | 213.52 | Matched raw outcomes |
| webkit | default | genuine-mixture | 3.47 | 3.49 | Matched raw outcomes |
| webkit | default | homogeneous-liquid | 8.67 | 8.60 | Matched raw outcomes |
| webkit | default | homogeneous-vapor | 8.29 | 8.44 | Matched raw outcomes |
| webkit | default | original-resolved-liquids | 11.63 | 11.60 | Matched raw outcomes |
| webkit | default | original-unresolved-endpoints | 13.91 | 14.59 | Matched raw outcomes |
| webkit | default | rejected-PT | 32.64 | 18.16 | Matched raw outcomes |
| webkit | default | reused-supported-state | 8.35 | 8.41 | Matched raw outcomes |
| webkit | default | supported-PH-PT-DU | 26.34 | 24.72 | Matched raw outcomes |
| webkit | full VLE | fresh-supported-state | 167.60 | 185.19 | Matched raw outcomes |
| webkit | full VLE | genuine-mixture | 310.88 | 338.98 | Matched raw outcomes |
| webkit | full VLE | homogeneous-liquid | 8.05 | 8.22 | Matched raw outcomes |
| webkit | full VLE | homogeneous-vapor | 7.92 | 8.03 | Matched raw outcomes |
| webkit | full VLE | original-resolved-liquids | 235.29 | 44.25 | Different outcomes; ratio excluded |
| webkit | full VLE | original-unresolved-endpoints | 245.90 | 202.70 | Different outcomes; ratio excluded |
| webkit | full VLE | rejected-PT | 181.82 | 188.68 | Matched raw outcomes |
| webkit | full VLE | reused-supported-state | 7.99 | 7.95 | Matched raw outcomes |
| webkit | full VLE | supported-PH-PT-DU | 181.82 | 192.31 | Matched raw outcomes |

Legacy resolved-liquid control calls fail while candidate calls return qualified liquid. Unresolved groups also change raw outcome mix because 162 returns. Those comparisons have **no speedup ratio**. Raw returned counts in the timing files do not certify physical phase, particularly for unresolved endpoints. Supported PH/PT/DU, genuine mixtures, repeated fresh/reused states and legitimate rejected PT are separately measured. Fresh timing includes allocation/disposal and the harness phase inspection; it is not pure EOS kernel cost. Apparent differences on unchanged paths, including variable WebKit rejected-PT timings, are descriptive short-run samples rather than evidence of an intrinsic algorithmic improvement.

## Initialization, workers and responsiveness

| Observation | Chromium | Desktop WebKit |
|---|---:|---:|
| Control median initialization ms | 1414.00 | 1636.00 |
| Candidate median initialization ms | 1424.10 | 1630.00 |
| Candidate median first factory ms | 1370.20 | 1507.00 |
| Maximum main-thread campaign heartbeat gap ms | 1505.20 | 1775.00 |
| Maximum worker campaign heartbeat gap ms | 76.80 | 94.00 |
| Control worker workload latency ms | 7034.20 | 8172.00 |
| Candidate worker workload latency ms | 7264.20 | 7828.00 |

Initialization has five samples per artifact and includes explicit JS/WASM integrity checks in the research loader. Worker latency has one bounded workload sample per artifact; it includes historical sequences, errors, allocation, synthetic controls and seven full-VLE cases. Their changed error/success mix precludes a speedup ratio. Worker main-thread heartbeats are independent from worker elapsed time.

**Responsiveness concern:** observed main-thread gaps of about 1.51/1.78 seconds occur in a campaign including synchronous factory work and synchronous sampling windows. Worker campaigns still record about 77/94 ms maximum gaps. This evidence does not establish smooth interaction or device responsiveness. Numerical correctness is a separate result.

## Memory and limits

All artifacts retain original unshared memory limits: initial 344 pages / 22,544,384 bytes; maximum 32,768 pages / 2 GiB; growth enabled. Actual first factory grows memory to **56,360,960 bytes**, which remains the observed size across main/worker and repeated property workloads. Stable linear-memory size is not a leak proof.

Chromium exposes only the coarse heap observation (10,600,000 bytes throughout sampled property rounds here); it does not account for all native/WASM allocation or prove an isolated per-module heap increment. WebKit exposes no equivalent API in this run. No forced-GC or long-duration leak claim is made. All created state objects are explicitly disposed; source-level catch ownership and actual lifecycle tests provide separate evidence.

No native-performance ratio is multiplied into browser/model cost. The bounded A2 timings remain in their actual scenario evidence and are not presented as a robust simulator speed comparison. Broader performance acceptance and physical-device measurements require separate work.
