# Research B9B — solver/property performance forensics

**B9B PERFORMANCE FORENSICS PASS.** The accepted table-backed five-section model
is unchanged. Its short startup cost is attributed to nonlinear residual/property
work, with a measured existing cache and a narrow future boundary-reuse hypothesis.
This milestone implements no numerical optimization. Operator integration NO-GO.

Start: `355db28d853817e1931295d6ec2f007876d53f90`; accepted A2:
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. Branch:
`research/browser-eos-b9b-solver-property-profiling-20261017`.
The pre-instrumentation design was independently committed as `5fae85a`.

Read ENGINEERING_REPORT.md for gates/decision, MECHANICS_REPORT.md for practical
meaning, PROFILING_DESIGN.md for the frozen design, NONLINEAR_WORK_CENSUS.md,
PROPERTY_EVALUATION_AUDIT.md, JACOBIAN_AND_LINE_SEARCH_COST.md,
COLD_VS_WARM_DIFFICULTY.md, INSTRUMENTATION_OVERHEAD.md,
BROWSER_PERFORMANCE_MATRIX.md and OPTIMIZATION_HYPOTHESES.md for findings.
TIMING_OVERLAP_AND_LIMITATIONS.md, FAILURE_AND_ROLLBACK.md and
SCIENTIFIC_CONTRACTS_AND_BLOCKERS.md preserve scope and obligations.

Raw evidence contains both actual browsers, original service reproduction,
matrix/validation/failure receipts, original and nested property/cache counters,
all original attempts, complete state/records, sampled stacks and Node reference.
scientific-parity.json, nonlinear-census.json, adaptive-proposal-reconstruction.json,
cpu-attribution.json and performance-summary.json are the machine-readable results.
milestone-status.json/csv/xlsx support the Laboratory tracker; no external sheet
or operator workstation was changed. Failed/superseded receipts remain labeled.

Reproduction from repository root (use explicit process timeouts):

```sh
# Read-only source checks / deterministic observational build
python experiments/dx-fv/browser_eos_b9b/build.py
python experiments/dx-fv/browser_eos_b9b/verify-copy.py
# Browser setup writes only /workspace/b9-runtime, requires network
timeout 420 python experiments/dx-fv/browser_eos_b9a/setup-browsers.py
# Each stage refuses to overwrite existing evidence. For a rerun, move prior
# B9B outputs to a labeled B9B receipt directory; never overwrite frozen history.
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 300 python experiments/dx-fv/browser_eos_b9b/run-browser.py --stage baseline
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 300 python experiments/dx-fv/browser_eos_b9b/run-browser.py --stage passive
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 300 python experiments/dx-fv/browser_eos_b9b/run-browser.py --stage matrix
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 300 python experiments/dx-fv/browser_eos_b9b/run-browser.py --stage validation
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 300 python experiments/dx-fv/browser_eos_b9b/run-browser.py --stage failure
timeout 60 node experiments/dx-fv/browser_eos_b9b/run-node.mjs
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 60 python experiments/dx-fv/browser_eos_b9b/reconstruct-proposals.py
timeout 120 python experiments/dx-fv/browser_eos_b9b/analyze.py
python experiments/dx-fv/browser_eos_b9b/write-reports.py
python experiments/dx-fv/browser_eos_b9b/preservation.py
```

Network-enabled execution is needed for localhost browser servers in a sandbox
that isolates networking. Node is supplemental. No CoolProp compilation or EOS
modification is required or permitted. Stop after isolated commit/push for explicit
engineering review; do not automatically implement an optimization.
