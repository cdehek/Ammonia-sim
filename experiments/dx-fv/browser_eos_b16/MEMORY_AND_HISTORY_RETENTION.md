# Bounded memory/history observations

Twelve reset Worker sessions (six per variant, alternating cold/warm) each end at 0.01 s. After advance, 48 repeated latest-snapshot requests do not add model attempts or Worker snapshot versions. Worker history retains two accepted snapshots (init/final) in this scenario; maximum allowed is eight. Client display history stays at eight. Cold retains 17 attempts and warm 52 on this Chromium path; each fixture's count stays unchanged during latest requests. Dispose reports dropping those attempt/snapshot references and terminates the Worker. No physical session exceeds the authorized horizon.

Property-table memory: one deep-frozen scientific table per fresh Worker. The self-contained ~1.44 MB source asset is not its live heap size. Model state: five cells plus eleven energies, original accepted state/ledgers. Attempt history: bounded at 256. Worker command count: bounded at 128, no response cache. Serialized snapshots: compact projection, payload JSON-byte estimate in stats; actual structured-clone storage differs. Client histories/metrics and heartbeat arrays are bounded by session/request lifetime. Diagnostic hashing retains stream state instead of raw residual histories, though full failure receipts contain detailed original evidence.

| Fixture / variant (fresh Node) | End heap median MB | Max RSS median MiB | Recorded GC events median |
|---|---:|---:|---:|
| cold/control | 16.69 | 83.45 | 0 |
| cold/candidate | 16.82 | 82.71 | 0 |
| warm/control | 28.87 | 95.85 | 0 |
| warm/candidate | 32.44 | 97.15 | 0 |

Node snapshots include engine/table, model, retained attempts, parser/compiler/GC state and instrumentation scaffolding. Max RSS includes process/native memory; Node CPU/heap is not browser Worker memory. Lower post-run heap does not establish allocation savings or a leak fix. Per-object allocation bytes are not measured.

Chromium retention-session renderer performance.memory usedJSHeapSize observations range 1.74–3.95 MB. These are coarse browser-provided renderer readings with GC/quantization effects and harness instrumentation; they do not isolate Worker heap, table memory, native/renderer RSS or total browser memory. No Worker heap snapshot or long-session retained-object profile was collected. They cannot establish monotonic memory stability or per-inversion allocation differences.

Reference dropping is verified, immediate OS reclamation is not. Short reset sessions provide bounded history evidence only; they make no hours-long memory-stability claim. A later integration must audit its own observer/attempt/record/response history policies, since retaining records without caps could grow excessively even with this optimization. B16 does not rewrite historical workstation retention behavior.
