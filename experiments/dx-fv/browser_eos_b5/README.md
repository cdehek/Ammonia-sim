# Ammonia Simulation Laboratory — B5 forensics

**ROOT CAUSE CONFIRMED. Diagnostic only; no functional repair or backend qualification.**

Branch `research/browser-eos-b5-35bar-inverse-forensics-20261016`, parent exact
B4C `3622000309cacdd35aaaebbb805ae40d27c75603`. Delivery SHA is the commit
containing this directory (`git rev-parse HEAD`). No merge or deployment.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), the
[original failure matrix](FAILURE_MATRIX.md),
[repair proposals and future A2 gates](REPAIR_PROPOSALS.md),
[reproduction instructions](BUILD.md), [trace schema](TRACE_SCHEMA.md), and
[🔧 The Mechanic’s Report](MECHANICS_REPORT.md).

| Evidence under `evidence/` | Purpose |
|---|---|
| `checkpoint.json`, `starting-file-hashes.json`, `refs-before.txt`, `preservation-verification.json`, `provenance.json` | Exact clean start; 1,557 protected files, 1,782 inherited source files, binaries, wheels, dependencies and accepted A2 closure |
| `fixed-inputs.json`, `fixed-inventory.csv`, `original-failures.json`, `diagnosis.json` | All original exact inventories, bits, failure identities and per-failure scientific dispositions |
| `native-fixed-replay.json`, `native72-fixed-replay.json`, `*-fixed-replay.json`, `PH-native*.json` | Identical native8/B4C/B4B/7.2 inputs and Chromium/WebKit replay; current PH inventories separately labeled |
| `independent-fixed-references.json`, `high-precision-references.json`, `precision-audit.json` | Independent DT/coexistence roots, stability, 65/90-digit arithmetic verification and local seed checks |
| `trace-on.jsonl`, `trace-on-results.json`, `trace-off-results.json`, `rebuilt-uninstrumented.json`, `trace-audit.json`, `instrumentation/` | Actual native decisions, guesses, residuals, termination and logging parity; no WASM-internal trace claim |
| `pressure-error-attribution.json`, `reference-inventories.json`, `reference-inventory-recovery.json` | PH error versus inventory rounding versus inverse drift; separate new physical-reference inventories |
| `cross-path.json`, `inventory-sensitivity.json`, `boundary-sweep.json`, `*-diagnostics.json` | Fixed inventories on both native phase paths; labeled ULP/sweep diagnostics; browser guard execution stacks |
| `raw-DU-eos-audit.json`, `scientific-audit.json` | Fresh independent EOS, original canonical/nonlinear budgets, failures retained |
| `native-binaries.json`, build logs/caches/commands, `browser-libraries.json` | Exact diagnostic/rebuilt artifacts and runtime provenance |
| `trace-phase-only.jsonl`, `auditor-attempt.json`, setup logs | Earlier instrumentation stage and unsuccessful setup/auditor attempts retained |
| `final-preservation.json`, `refs-before-push.txt` | Final local preservation and protected remote head comparison |

The three new native archives are research controls/diagnostics only. Archived
B4C remains the accepted experimental candidate for this investigation; neither
a rebuilt nor instrumented library is presented as a functional correction.
All upstream notices remain in the unchanged B4C vendor directory.

The evidence audit passes. The seven native full-VLE exceptions and seven strict
browser rejections remain failures. No full A2 campaign or physical iPad test
was run. Stop for engineering review and explicit approval before corrective work.
