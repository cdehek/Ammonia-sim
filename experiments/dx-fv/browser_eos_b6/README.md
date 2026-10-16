# Ammonia Simulation Laboratory — Research B6

**FOCUSED LOADER REPAIR PASS**. Gate A and Gate B pass for the isolated B6
`evaluate` interface with the pinned B4C JS/WASM. Legitimate rejected PT calls
still refuse; their handling no longer produces the secondary reference-count
assertion. Overall backend, complete A2 and physical iPad qualification remain
pending. Stop for engineering review; no next milestone or integration begins.

Branch: `research/browser-eos-b6-rejected-pt-loader-repair-20261016`.
Exact parent: `75e015fd3455e75fa85074e8748bc01eb8973624`.
Design commit: `6b1c69b82ed90ee113689f713cd10e31a089eef5`.
Complete pre-edit Gate A receipt: `183295983435deea4d59a926dac8b8d86666123c`.
Final delivery identity is branch HEAD / the delivery response.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md),
[ROOT_CAUSE_AND_REPAIR_DESIGN.md](ROOT_CAUSE_AND_REPAIR_DESIGN.md),
[OWNERSHIP_TRACE.md](OWNERSHIP_TRACE.md),
[MECHANICS_REPORT.md](MECHANICS_REPORT.md),
[PERFORMANCE_AND_MEMORY.md](PERFORMANCE_AND_MEMORY.md),
[EXECUTION_NOTES.md](EXECUTION_NOTES.md) and
[RESEARCH_BLOCKERS.md](RESEARCH_BLOCKERS.md).

Qualification calls **explicitly use `loadEOS('candidateB')`**. The historical
`controlA` default is preserved to avoid changing artifact selection; other
artifact choices receive no new B6 scientific qualification.

## Reproduction without overwriting saved evidence

Python 3.12.14, Playwright 1.62.0, system Chromium 154.0.8037.57 and Playwright
WebKit 2336 / WPE 26.5 were used. Node 24.19.0 checks syntax/actual WASM ABI;
no Emscripten installation or compilation is needed. Native controls use the
preserved B4C archive through ctypes, without a CoolProp wheel. Runtime hashes,
exact package URLs/digests, original build identity and reviewed sources are in
`evidence/runtime.json`, `setup-provenance.json` and `reviewed-source-index.json`.

Install WebKit outside the repository with
`PLAYWRIGHT_BROWSERS_PATH=/workspace/b6-browsers python -m playwright install webkit`.
On this host, the six Debian packages recorded in `setup-provenance.json` are
required for WPE. Download through the inherited proxy, verify every SHA256,
extract with `dpkg-deb -x` to a disposable directory, and place their shared
libraries in the isolated WebKit bundle's `minibrowser-wpe/sys/lib`. The preserved
WPE launcher text/identity is recorded in runtime evidence; it sets bundle bin,
lib, share and sys/lib paths and executes `bin/MiniBrowser`. GTK host warnings
do not establish WPE failure or success: actual browser calls must run.
Set `CHROMIUM_PATH` and `WEBKIT_PATH` to the usable executables when needed.
Loopback browser/child-process execution requires network-enabled execution in
this managed sandbox. No external browser results or mocks count as qualification.

From repository root, keep new outputs outside the saved evidence:

```sh
mkdir -p /tmp/b6-reproduction
# Full unchanged historical Gate A, two separate instances per engine:
timeout 180 python experiments/dx-fv/browser_eos_b6/replay.py --stage a --replicas 2 --output-dir /tmp/b6-reproduction
# Full candidate/control matrix and focused regressions, with final harness:
timeout 600 python experiments/dx-fv/browser_eos_b6/replay.py --stage b --replicas 1 --output-dir /tmp/b6-reproduction
# Bounded actual native scientific control:
B6_NATIVE_OUTPUT=/tmp/b6-reproduction/native.json timeout 45 python experiments/dx-fv/browser_eos_b6/native.py
```

The replay runner refuses to overwrite an output file. `pilot.py` and
`abi-check.py` also refuse overwrite and use saved-output names; run them in a
disposable copy, or relocate their output targets for an independent replay.
`prepare.py`, `implement.py` and `extract-c1.py` reproduce fixture/candidate/harness
construction; inspect them before running in a disposable copy. They write only
B6 files. `implement.py` requires the sealed Gate A ancestor. Never rerun an old
milestone's writer against protected historical evidence.

`verify-results.py` independently audits the saved delivery inputs and writes
B6 summaries. It joins the initial full lifecycle/performance run with corrected
science/C1 comparisons and final pointer-safe diagnostic checks; unsuccessful
attempts remain preserved. Full numerical values, original input bits and
original scientific limits are retained. Some intentionally nonfinite request
records use Python JSON Infinity/NaN extensions; do not read those full ledgers
with strict browser response.json(). The seven C1 error subsets are strict JSON
and preserve their source hashes.

For final preservation, take fresh read-only remote snapshots outside the tree:

```sh
git ls-remote --heads --tags origin > /tmp/b6-review-refs.tsv
git ls-remote origin refs/pull/3/head refs/pull/3/merge > /tmp/b6-review-pr3.tsv
python experiments/dx-fv/browser_eos_b6/audit.py --refs /tmp/b6-review-refs.tsv --pr3-refs /tmp/b6-review-pr3.tsv --clean --read-only
```

This checks exact ancestry/branch, all historical bytes, archived artifacts,
A2, scientific patches, protected remote heads and PR #3, clean status and the
B6 delivery manifest. A prepush receipt cannot embed its own eventual commit
SHA; the final post-push read-only receipt is retained outside the commit.

## Deliverable index

| Requirement | Files under this directory |
|---|---|
| Exact fixtures and historical control | `evidence/historical-rejected-pt.json`, `.csv`, `gate-a-{chromium,webkit}-{0,1}.json`, `gate-a-summary.json` |
| Original/raw/final exception and ownership trace | `OWNERSHIP_TRACE.md`, `generated-js-trace.json`, `wasm-abi.json`, pinned Emscripten sources and `setup-provenance.json` in evidence |
| Pre-edit decision and commit | `ROOT_CAUSE_AND_REPAIR_DESIGN.md`, `evidence/pre-edit-commit.json` |
| Isolated repair and observation-only copies | `loader.mjs`, `candidate-diagnostic.mjs`, `control-diagnostic.mjs`, `observe.mjs`, `evidence/loader-repair.diff`, instrumentation diffs |
| Actual Chromium/WebKit lifecycle and original six positions | `evidence/gate-b-*-0.json`, `lifecycle-matrix.json`, `verification.json` |
| Low/high interfaces, JS error distinctions, final ABI ownership | Gate A `interfaces`, full/corrected diagnostic sections, `evidence/gate-diagnostic-complete-*-0.json`, `abi-{chromium,webkit}.json` |
| Repetition, fresh/reused and terminal disposal | `lifecycle.mjs`, full Gate B lifecycle rows, matrix and ABI checks |
| Native/browser scientific comparison and unchanged signed probes | `native.py`, `evidence/native-controls.json`, `gate-corrected-*-0.json`, `scientific-audit.json` |
| C1 fail-closed / A2 subset | `science.mjs`, `a2-subset.cjs`, `extract-c1.py`, `evidence/c1-harness-provenance.json`, seven-error subsets, corrected comparisons |
| Worker, memory and performance | `worker.mjs`, `performance.mjs`, full Gate B worker/performance records, `evidence/performance-summary.json`, `PERFORMANCE_AND_MEMORY.md` |
| Original numerical-budget audit | `evidence/numerical-budget-audit.json`, `scientific-audit.json` |
| Preservation, dependencies and protected refs | `audit.py`, `evidence/checkpoint.json`, `starting-files-sha256.json`, `start-audit.json`, `final-preservation.json`, remote/PR3 snapshots, runtime/setup provenance, delivery manifest |
| Failed attempts and next scientific decision | `EXECUTION_NOTES.md`, retained initial logs/evidence, `RESEARCH_BLOCKERS.md` |

No protected loader, accepted dependency, C1 or C2/P1 file changes. No EOS or
support-domain change. No merge, deployment, UI/Live Plant or production action.
