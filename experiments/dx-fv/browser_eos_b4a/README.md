# B4A — controlled liquid phase-classification repair

**FOCUSED REPAIR PASS. Full backend qualification remains pending.**

Branch: `research/browser-eos-b4a-liquid-phase-repair-20261015`.
Parent checkpoint: `4e1295be9493d8bce4ca35ee0cf61accb7465226`.
Execution crossed UTC midnight on October 15–16, 2026; the requested branch name
is retained. Everything added is isolated in this directory.

* [Engineering report](ENGINEERING_REPORT.md)
* [🔧 Ammonia Lab — The Mechanic’s Report](MECHANICS_REPORT.md)
* [Algorithm recorded before editing](ALGORITHM.md), [exact patch](liquid-classification.patch)
* [Gate scope and retained failures](GATE_SCOPE.md)
* [Build and reproduction instructions](BUILD.md)
* [B4B prerequisites and full qualification gates](B4B_PREREQUISITES.md)

`evidence/summary.json` is the derived final ledger. `focused-gate.json` retains
all liquid canonical failures, including the three unchanged full-VLE 35-bar
inverse exceptions, separately from supported-liquid eligibility. They are not
passing recoveries. The vapor PT/cache and upper-Q band defects remain unresolved.

The exact B3 57-case matrix is reused verbatim. `inputs.json` records the 86 base
inputs actually exercised: B3's 57, B1's saved liquid fixture, twelve stable
liquid/mixture/vapor states and sixteen one-ULP endpoint neighbors. Every base
retains the original four signed probes; B3 inputs are not rounded or moved.

Evidence locations:

* `preservation-start.json`, `accepted-a2-verification.json`,
  `dependency-verification.json`, source-stage manifests and `provenance.json`:
  exact source/checkpoint/tool/binary identities and preservation checks.
* `historical-control.json`, `native-control44*.json`, `native-liquid44*.json`:
  native before/after PH, independently converged DT roots, stability, signed
  probes, requested-coordinate residuals and separate A/B/C inventories.
* `chromium-*-focused.json`, `webkit-*-focused.json`: returned PH and fresh DT,
  saturation distances, original probes, A/B/C inventories and adapter errors.
* `focused-gate.json`: independent native reevaluation of browser states/probes,
  physical phase classifications and original normalized mass/energy comparisons.
* `original-budget-ledger.json`, `endpoint-continuity.json`: explicit original
  component-budget comparisons and endpoint ULP density continuity.
* `endpoint-rounding-preimplementation.json`, `saturation-reference-8.0.0.json`:
  ULP investigation and independent displaced-seed coexistence solutions.
* `extra-native-*.json`: shared PS/PU callers and unchanged invalid/domain cases.
* `full-vle-35bar-fixed-inventory-control.json`: identical-input DU comparison.
* `trace-superanc.jsonl`, `trace-full-vle.jsonl`, `diagnostic-parity.json`:
  observed corrected dispatch/evaluation count and logging-on/off equality.
* `*-A2-*.json`: original zero-exchange trial and bounded accepted A2 fixtures.
* `performance-*.json`, `*-performance.json`: bounded matched timing, WASM
  initialization, observed memory and exceptions. Linux desktop engines only.
* Setup/build logs and `setup-attempts.json`: unsuccessful attempts retained.

Native `.so.xz` files and distinct WASM builds are under `artifacts/` and
`vendor/{control44,liquid44}`. Upstream embedded version strings do not identify
the experiment: use directory identities and SHA256 manifests. Licensing notices
are retained under `vendor/notices` and `vendor/LICENSE-CoolProp.txt`; the copied
`THIRD_PARTY-B1.md` describes historical B1 names, with its authoritative links
remaining in [B1's original notice](../browser_eos_backend/vendor/THIRD_PARTY.md).

No production property engine, UI, Live Plant, accepted solver, EOS coefficient,
fluid data, reference convention, input, perturbation or numerical budget is
modified. No merge, deployment, migration, full A2 campaign or B4B correction.
Stop for engineering review and explicit approval.
