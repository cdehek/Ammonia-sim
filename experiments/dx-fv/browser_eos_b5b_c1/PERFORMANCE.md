# Bounded performance and lifecycle observations

Five interleaved 40-ms rounds per property group, at most 1000 calls/round.
Medians are elapsed time divided by calls, not pure EOS timing. Both sides use
the identical WASM. No performance acceptance threshold was invented.

| Engine | Group | Control ms/call | Candidate ms/call | Candidate/control |
|---|---|---:|---:|---:|
| chromium | success | 0.0777132 | 0.0795635 | 1.02 |
| chromium | rejected | 0.100251 | 0.17316 | 1.73 |
| webkit | success | 0.0740741 | 0.0900901 | 1.22 |
| webkit | rejected | 0.0798403 | 0.277778 | 3.48 |

Error-transport measurements use three 20-ms rounds (at most 10000 calls).
These are synthetic numerical errors at the real thermodynamics interface.

| Engine | Control ms/error | Candidate ms/error |
|---|---:|---:|
| chromium | 0.0584795 | 0.0638978 |
| webkit | 0.00406256 | 0.0105097 |

## Focused A2 and memory

| Runtime | Supported control / candidate ms | Retry control / candidate ms |
|---|---:|---:|
| native | 19164.1 / 7080.53 | 124.676 / 85.1216 |
| chromium | 1468.6 / 1616.6 | 21.6 / 26.1 |
| webkit | 10051 / 5252 | 62 / 65 |

A2 is a single paired sample, with substantial JIT/warm-up/order and native
FIFO bridge overhead. These numbers do not establish a speedup or a robust
regression rate. The failed retry controls preserve historical stop behavior;
the candidate changes only the justified stop classification and diagnostics.

| Engine | Linear memory before / after bytes | Worker elapsed ms | Main timer ticks |
|---|---:|---:|---:|
| chromium | 56360960 / 56360960 | 4408.6 | 831 |
| webkit | 56360960 / 56360960 | 8793 | 718 |

Worker elapsed includes startup, import, WASM initialization, transfer and
property calls. Main timers keep running during worker execution. Forty
alternating success/refusal calls and fresh/reused parity show no observed
stale error or rejected state contamination. Finite observations and heap
snapshots do not prove absence of memory leaks. WebKit heap metrics are
unavailable; native replay peak RSS is 118872 KiB.

The native bridge uses the preserved library through local buffered FIFOs.
Desktop WPE WebKit results do not establish physical iPad performance. No
long-duration campaign or production throughput qualification is claimed.
