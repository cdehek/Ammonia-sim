# Ammonia Simulation Laboratory — research B4C

**FOCUSED REPAIR PASS. Full backend qualification remains pending.**

Isolated branch `research/browser-eos-b4c-upper-quality-repair-20261016`, starting
at exact B4B `d0d11d59756c4dc32bbfdb22a5975fd6f4527e05`.
The delivery SHA is the commit containing this directory; use `git rev-parse HEAD`
or the final delivery response. No production integration or deployment.

Read [the engineering report](ENGINEERING_REPORT.md), [the pre-edit algorithm](ALGORITHM.md),
[the exact two-condition patch](upper-quality-classification.patch),
[the original input inventory](UPPER_QUALITY_MATRIX.md), [reproduction instructions](BUILD.md),
and [🔧 Ammonia Lab — The Mechanic’s Report](MECHANICS_REPORT.md).

| Evidence | What it establishes |
|---|---|
| `preservation-start.json`, `historical-identities.json`, source-stage manifests | Exact B4B start, 1,313 original file hashes, inherited patches and binaries |
| `original-upper-quality-inventory.json`, `original-upper-quality-base-inputs.csv` | Original native/browser failures and original signed probes; no regenerated fixtures |
| `preimplementation-thermodynamics.json`, `preimplementation-decision.json` | Stable vapor roots, independent saturation paths, endpoint uncertainty, decision before source edits |
| `native-*.json`, `*-focused.json`, `focused-gate.json` | All 86 original base inputs and 344 original signed probes per runtime/build |
| `upper-quality-native-before-after.json`, `*-upper-quality-inventories.json`, `upper-quality-browser-physical-ledger.json` | Every unique invalid base/probe input, physical phase, EOS and canonical recovery |
| `boundary-gate.json`, `default-equilibrium-audit.json` | Both saturation paths, original diagnostic bands/endpoints, explicit physical crossings and known 35-bar exceptions |
| `shared-*.json`, `*-shared.json`, `cache-candidateB.json`, lifecycle results | PH/PS/PU, fresh/reused states, PT/DU lifecycle and independent derivatives |
| `trace-*.jsonl`, `trace-audit.json` | Actual native raw quality/dispatch, homogeneous work counts and logging parity |
| `35bar-fixed-inventories.json`, `*-35bar-fixed-inventories.json` | Exact fixed inventories, unchanged inverse errors and strict support guards |
| `A2-audit.json`, `*-A2-*.json`, `accepted-a2-verification.json` | Bounded accepted scientific compatibility and exact dependency closure |
| `performance-summary.json`, `performance-*`, `*-cost.json` | Matched additional B4C cost, worker response and memory, bounded A2 cost |
| `provenance.json`, `native-binaries.json`, `final-integrity.json` | Build/source/artifact identities and final preservation audit |
| `setup-attempts.json`, `boundary-gate-attempt1.json`, `*-contended-do-not-use.json` | Retained setup/auditor/timing mistakes and their disposition |

All JSON above is under `evidence/`. The unchanged archived B4B control is used
for exact scientific replay; separately rebuilt controls match every full row
and probe exactly and supply matched native/WASM timing. Source paths can alter
whole-binary hashes. `controlA` in B4C means B1+B4A+B4B; `candidateB` adds B4C.

35-bar inverse/support failures, rejected-PT loader cleanup assertions, complete
A2 qualification and real iPad testing remain outstanding. Stop for engineering
review and explicit approval before any subsequent milestone.
