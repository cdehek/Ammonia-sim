# Instrumentation overhead and GC observations

Primary builds have no lexical counts, B14 hooks or scientific hashes. Heavy diagnostic times are excluded from speed estimates. Eight supplemental clean processes provide one count-only and one no-inner-timer observation per engine/fixture, all with identical physical checksums.

| Fixture/variant | Count-only / primary median advance | No-inner-timer process ms | Primary median process ms |
|---|---:|---:|---:|
| cold/control | 1.360 | 302.76 | 241.27 |
| cold/candidate | 1.130 | 260.83 | 272.48 |
| warm/control | 1.451 | 1082.47 | 1114.17 |
| warm/candidate | 1.364 | 990.53 | 980.90 |


Single observations include natural JIT/runtime variation; these are sensitivity estimates, not causal overhead or intervals. No-inner-timer process wall includes startup/init; compare it only to primary process wall. Do not subtract these differences from advance time or add nested scopes.

Primary PerformanceObserver arrays were empty at disconnect, not evidence of zero GC. Four separately bounded final-version `--trace-gc-nvp` logs give perturbed whole-process indicators:

* cold/control: 32 process-wide GC events, 27.10 ms summed pauses, largest 3.90 ms.
* cold/candidate: 32 process-wide GC events, 27.40 ms summed pauses, largest 4.30 ms.
* warm/control: 102 process-wide GC events, 53.60 ms summed pauses, largest 4.10 ms.
* warm/candidate: 89 process-wide GC events, 56.80 ms summed pauses, largest 10.50 ms.

These include initialization/record and tracing overhead. Allocated bytes and exclusive advance GC attribution are unestablished. Source construction counts show 39 fewer pressure-bracket arrays plus one holder per eligible call, and one public PT wrapper per engine. JIT may eliminate source allocations. Preliminary v1 traces are explicitly prefixed and excluded here.
