# Research B9 — worker-first five-section browser physics

**B9 WORKER-FIRST FEASIBILITY PASS.** Four bounded architecture gates pass in
actual Chromium and desktop WebKit. **GO for continued isolated research;
NO-GO FOR FURTHER INTEGRATION of this harness.** No backend/production qualification.
Stop for engineering review and explicit approval.

Start: `d5c7d01264639ebed39d1442222d5bf5c44fe848` (B8).
Branch: `research/browser-eos-b9-worker-first-architecture-20261017`.
Accepted A2: `be9eb35a4ddf5098e685182f8104685127c6a6ee`.
Pre-implementation design commit: `81e43e4`.
Delivery SHA: `git rev-parse origin/research/browser-eos-b9-worker-first-architecture-20261017`.

Read [engineering findings](ENGINEERING_REPORT.md), [mechanic’s report](MECHANICS_REPORT.md),
[architecture](WORKER_ARCHITECTURE_DESIGN.md), [protocol](WORKER_PROTOCOL.md),
[ownership](MESSAGE_OWNERSHIP.md), [source/bundle audit](SOURCE_AND_BUNDLE_AUDIT.md),
[scientific parity](SCIENTIFIC_PARITY_MATRIX.md), [failures/rollback](FAILURE_AND_ROLLBACK_MATRIX.md),
[performance](PERFORMANCE_AND_RESPONSIVENESS.md), [scientific contracts](SCIENTIFIC_CONTRACT_AUDIT.md),
and [execution limitations](EXECUTION_NOTES.md).

Frozen original cold/warm fixtures use nonzero exchange and open flow, default
original numerics plus trace/failure-aware growth, with checkpoints
0/.0001/.0005/.001 simulated seconds. Main/worker share the exact accepted closure.
No CoolProp DP dependency, EOS replacement, source repair, clamp, budget change,
production/operator UI change, merge, deployment or hosting edit.

## Local reproduction

Use Linux with recorded Python Playwright 1.62.0, psutil, Node and Git. Browser
runtime/setup is outside Git in `/workspace/b9-runtime`; scientific source/output
is only here. Existing archived B6/B7 assets remain in their original directories.
All commands below run from repository root. Permission to access localhost and
normal browser child processes is required in a sandbox. Do not disable TLS/proxy
or modify the network policy to obtain it.

```sh
timeout 420 python experiments/dx-fv/browser_eos_b9/setup-browsers.py
timeout 30 python experiments/dx-fv/browser_eos_b9/build.py
timeout 40 node experiments/dx-fv/browser_eos_b9/node-baseline.mjs
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 240 python experiments/dx-fv/browser_eos_b9/run-browser.py --stage parity --tag=-repro
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 240 python experiments/dx-fv/browser_eos_b9/run-browser.py --stage c1 --tag=-repro
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 120 python experiments/dx-fv/browser_eos_b9/run-browser.py --stage lifecycle --tag=-repro
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 300 python experiments/dx-fv/browser_eos_b9/run-browser.py --stage benchmark --tag=-repro
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 180 python experiments/dx-fv/browser_eos_b9/run-browser.py --stage errorsbench --tag=-repro
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 120 python experiments/dx-fv/browser_eos_b9/run-browser.py --stage b7 --tag=-repro
PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers timeout 120 python experiments/dx-fv/browser_eos_b9/memory-lifecycle.py --tag=-repro
timeout 120 python experiments/dx-fv/browser_eos_b9/analyze.py
timeout 120 python experiments/dx-fv/browser_eos_b9/audit.py
```

Run browser stages sequentially, preserving table parity before downstream work.
The runner refuses to overwrite an existing tag: use another unique repro tag.
`analyze.py` audits ORIGINAL milestone receipts; it intentionally does not relabel
new reproduction measurements as the archived campaign. Node/build output should
remain byte-identical on the recorded runtime. Reproduction output is B9-only;
do not commit it automatically. Fresh scientific hashes may differ across engines
or runtime versions; use the original contracts for cross-engine comparisons.

For manual inspection only, run a bounded local server:

```sh
timeout 600 python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/experiments/dx-fv/browser_eos_b9/`. Select main/worker,
original cold/warm, initialize, advance the frozen checkpoints, stop or dispose.
No unsupported compressor/valve controls exist. The UI offers only accepted table
physics. B7 appears solely in separate, explicitly unqualified test evidence.

## Evidence index

- `starting-files-sha256.json`, `checkpoint.json`, `start-audit.json`, reviewed report/source manifests: preservation and exact starting source/fixture identities.
- `source-bundle-manifest.json`, `frozen-fixtures.json`, `node-baseline.json`: packaging and frozen inputs/settings.
- `parity-*-serialized.json.gz`, `scientific-audit.json`, `frozen-browser-scientific-hashes.json`: complete original state/record/attempts, budgets, events and timed-run exact checks.
- `c1-*.json.gz`, `lifecycle-*-final.json.gz`, `lifecycle-*-backpressure.json.gz`, `lifecycle-*-cache-bound.json.gz`, `failure-lifecycle-audit.json`: original floor/halving, exact internal rollback, failures, sequencing and lifecycle.
- `benchmark-*-sealed.json.gz`, `performance-summary.json`, `errorsbench-*.json.gz`, `memory-*.json`: final timings, heartbeat/frame/input distributions, transport and bounded memory observations.
- `b7-*-phase-getter.json.gz`, `b7-subset-audit.json`: optional supported property/qualified-liquid subset and expected refusals, never full EOS-backed A2.
- `browser-runtime.json`, `browser-install.log`: actual executable/package provenance.
- `remote-before.tsv`, `remote-prepush.tsv`, `pr3-before.json`, `pr3-prepush.json`, `final-preservation.json`, `delivery-manifest-sha256.json`: delivery preservation; postpush receipts are separate to avoid a commit self-reference.
- `milestone-status.json` and `.csv`: Excel-tracker-compatible status and engineering decision.

Superseded/failed evidence is retained, never pooled into headline numbers. All
unresolved blockers remain listed in SCIENTIFIC_CONTRACT_AUDIT.md and the engineering
report. Desktop browser measurements do not establish iPadOS Safari behavior.

Delivery sealing includes a committed post-first-push ref/PR/artifact audit. The
last postpush clean/SHA receipt is separate because embedding it would change the
commit it identifies. `verify-delivery.py` rechecks historical files, B9 seal,
protected refs, PR metadata, ancestry and additive-only scope with explicit
receipt paths; use `--require-clean` for the final check.
