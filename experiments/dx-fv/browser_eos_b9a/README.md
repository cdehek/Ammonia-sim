# B9A compact-worker research

**B9A COMPACT-WORKER FEASIBILITY PASS. Operator integration NO-GO.**

Exact start B9 b1a65c9365879d6e97eff649e56371df3907e86e; isolated branch
research/browser-eos-b9a-compact-worker-optimization-20261017. All additions are
under this directory. Accepted A2 be9eb35a4ddf5098e685182f8104685127c6a6ee and all
historical sources remain byte-identical. Pre-optimization design commit c95a931.

A uses untouched B9 full diagnostics. B uses compact ordinary messages with the
same complete diagnostic generation and cumulative worker history. C keeps the
same generation with four recent endpoint scopes and explicit expiration. Worker
retains scientific authority. Explicit diagnostics do not reconstruct physics.

Read ENGINEERING_REPORT.md, PERFORMANCE_AND_MEMORY.md, SCIENTIFIC_PARITY_MATRIX.md,
FAILURE_AND_LIFECYCLE_MATRIX.md and MECHANICS_REPORT.md. Contracts are in
COMPACT_SNAPSHOT_CONTRACT.md, snapshot-schema.json and WORKER_PROTOCOL_REVIEW.md.
Evidence includes full M/U/V/thermal ledgers, original traces/work counts,
original/compact C1 failures, cache/lifecycle, actual browsers, startup and memory.
Tracker status is available as CSV, JSON and Excel. B7 execution is deferred.

From repository root, using Python with Playwright 1.62.0, psutil and openpyxl:

```sh
timeout 420 python3 experiments/dx-fv/browser_eos_b9a/setup-browsers.py
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/build.py
timeout 30 node experiments/dx-fv/browser_eos_b9a/node-baseline.mjs
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage baseline --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage attribution --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage parityB --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage parityC --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage failure --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage lifecycle --tag=-reproduce
timeout 300 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage benchmark --tag=-reproduce
timeout 180 python3 experiments/dx-fv/browser_eos_b9a/run-browser.py --stage startup --tag=-reproduce
timeout 240 python3 experiments/dx-fv/browser_eos_b9a/memory-lifecycle.py --tag=-reproduce
timeout 180 python3 experiments/dx-fv/browser_eos_b9a/run-retrieval.py --tag=-reproduce
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/analyze.py
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/write-reports.py
timeout 120 python3 experiments/dx-fv/browser_eos_b9a/audit.py
```

Runner refuses to overwrite an existing receipt: select a new tag. Analysis uses
retained final receipts by name; change selection explicitly to analyze a new
campaign. Memory script accepts --tag to preserve existing receipts. Retrieval script also
refuses existing receipts; use its --tag option for reproduction. All browser work is
sequential. Static preview: serve repository root with python3 -m http.server and
open /experiments/dx-fv/browser_eos_b9a/index.html. No deployed website or production
UI is changed. Runtime/provenance and failed-attempt notes are retained.

No full qualification, sustained real-time, EOS repair, production integration,
merge/deployment or physical iPad claim. Stop for explicit engineering review.
