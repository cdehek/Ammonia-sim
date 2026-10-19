# Research B9C — exact stage-local boundary PH reuse

**B9C EXACT BOUNDARY PH REUSE PASS**. Performance improvement measured: **YES**.
Original table only; isolated prototype; operator integration **NO-GO**.
No merge, deployment, production UI, Live Plant, accepted A2 or EOS change.

Read ENGINEERING_REPORT.md, BOUNDARY_PH_EQUIVALENCE_DESIGN.md,
SOURCE_DIFF_AND_HASH_AUDIT.md and the scientific/failure/performance matrices.
The independent pre-implementation design commit is
36b118b30e44613f1c7ac9ca615aa61c949a88c2, based on exact B9B
ec2df3f9ee3efd7faef3d129282ad1dd7bdc896f. The canonical C2 correction inherited
from B8 is recorded in evidence/gate0.json; no protected ref was changed.

## Reproduction

Use Python 3, Playwright 1.62.0, openpyxl 3.1.5, Node 24 and the pinned browser setup. Network is
needed only for repository/browser setup; the harness serves local files. Read
the managed-environment proxy instructions before network setup. No EOS rebuild.
Run from repository root, writing NEW receipt names/directories when reproducing
so that committed evidence is not overwritten. Each browser command has an outer
bounded timeout; per-worker timeout is 90 s.

```sh
python3 experiments/dx-fv/browser_eos_b9c/build.py
python3 experiments/dx-fv/browser_eos_b9c/verify-source.py
timeout 420 python3 experiments/dx-fv/browser_eos_b9/setup-browsers.py
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b9-runtime/browsers
timeout 300 python3 experiments/dx-fv/browser_eos_b9c/run-browser.py --stage parity
timeout 300 python3 experiments/dx-fv/browser_eos_b9c/run-browser.py --stage regressions
timeout 180 python3 experiments/dx-fv/browser_eos_b9c/run-browser.py --stage c1
timeout 90 python3 experiments/dx-fv/browser_eos_b9c/analyze.py
timeout 300 python3 experiments/dx-fv/browser_eos_b9c/run-browser.py --stage timing
python3 experiments/dx-fv/browser_eos_b9c/analyze.py --performance
python3 experiments/dx-fv/browser_eos_b9c/write-reports.py
```

run-browser refuses existing stage receipts. For a new run, use a fresh isolated
worktree and archive the committed B9C stage receipts into a separate B9C-owned
subdirectory before running; never alter historical B9/B9A/B9B evidence. The
immutable original baseline remains read-only. gate0.py is intentionally restricted
to the starting B9B HEAD; final preservation.py uses the starting SHA and hashes.

Evidence encoding uses f64 hexadecimal binary64 tags, including NaN/signed zero;
equality never converts them to toleranced decimal values. Primary performance
samples contain exact science hashes, settings and original work counters. Raw
diagnostic ledgers contain the actual property requests and results. Extra
regressions retain hashes of complete residual/linear/stage data and full original
state/records/observer events. Source manifests and diagnostic patches make those
different evidence sizes explicit. No phase/physics acceptance is inferred from
timing or a compact property vector.

milestone-status.csv/json/xlsx are local tracker-compatible artifacts. No external
tracker, PR comment or message is posted. Protected refs and PR #3 receipts are
local research evidence. Stop for engineering review after the authorized branch
push and final clean-tree/preservation checks.
