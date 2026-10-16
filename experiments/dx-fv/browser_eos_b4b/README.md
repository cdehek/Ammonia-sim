# Research B4B: vapor PT/cache consistency

**FOCUSED REPAIR PASS. Full backend qualification remains pending.**

Isolated branch `research/browser-eos-b4b-vapor-cache-repair-20261016`, based on
exact B4A `94f77bb062b75ffebf17a1c9758d11c1adc61711`.
No production selection, UI/Live Plant change, merge or deployment.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), the pre-implementation
[ALGORITHM.md](ALGORITHM.md), [exact patch](pt-cache-consistency.patch),
[BUILD.md](BUILD.md) and [the Mechanic’s Report](MECHANICS_REPORT.md).

| Evidence / tool | Purpose |
|---|---|
| `evidence/native-primary-gate.json`, `focused-gate.json` | Exact vapor, B4A liquid and B1 gates under original budgets |
| `native-*.json`, `*-focused.json` | Original 86 inputs and 344 signed probes, physical references, independent DT and canonical inventories |
| `trace-*-results.json`, `trace-*.jsonl`, `trace-audit.json` | Actual final density increments, termination, cache fill and commit coordinates, including fixed original B3 PT input |
| `scientific-audit.json` / `audit.py` | Independent native/browser EOS, phase-aware exclusions, original normalized numerical comparisons, lifecycle and limited A2 audit |
| `lifecycle-*.json`, `*-lifecycle.json` | 47 fresh/reused PH/PT/DU cases per backend/runtime, derivatives and equilibrium checks |
| `native-*-full-vle.json` | Alternate saturation path and all preserved inverse errors |
| `35bar-fixed-inventories.json`, `*-35bar-fixed-inventories.json` | Identical fixed inventories across control/candidate; native 124 and each browser 42; raw inverse and strict guard behavior |
| `*-A2-*.json`, `accepted-a2-verification.json` | Unchanged accepted dependency closure, original scientific assertions, startup/disturbance/reversal and zero-exchange trials |
| `performance-summary.json`, `*-cost.json`, `performance-native-*.json` | Matched native/browser/worker timing, initialization, memory and responsiveness |
| `diagnostic-parity.json`, diagnostic full matrices | Instrumented logging-off/on versus uninstrumented property equivalence |
| `provenance.json`, `native-binaries.json`, `build-versions.json` | Source, patch, native/archive/JS/WASM and compiler identities |
| `source-stage-*.json`, `dependency-verification.json` | All source hashes and exact nine dependency digests |
| `historical-*-hash-verification.json`, `rebuilt-*-equivalence.json` | Previous experimental source/binary verification and rebuilt control equality |
| `preservation-start.json`, `refs-before.txt`, preservation/final audits | All 1,102 starting tracked files and protected remote heads |
| `setup-attempts.json` | Preserved setup/harness issues and their disposition |

`controlA` is the B4A backend (B1 44-bit plus liquid classification). Initial
native/control browser measurements use preserved B4A binaries. The separate
rebuilt control is scientifically identical over all complete focused rows;
performance/browser-fixed-inventory runs use its distinct archived WASM.
`candidateB` adds only the PT commit patch. Version strings alone do not identify
these experiments; use the artifact hashes. Native diagnostic builds add logging
only. Browser cache verification uses independent DT/derivative comparisons;
there is no claim of instrumented WASM internal execution traces.

All input bits, perturbations, mass/internal-energy inventories and budgets are
preserved. Upper-quality extrapolation, 35-bar inverse/support failures and the
research loader’s rejected-PT exception cleanup remain explicitly unresolved.
The full option/reference qualification matrix and physical iPad testing remain
future gates. Stop here for engineering review and explicit approval.
