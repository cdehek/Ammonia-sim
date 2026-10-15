# B2 reproduction

Experimental research only. Assessment: **BLOCKED**. Read ENGINEERING_REPORT.md,
SUITE_RESULTS.md, QUALIFICATION_MATRIX.md and MECHANICS_REPORT.md together.
LIQUID_COUNTEREXAMPLE.md gives the exact failing liquid probes;
SCIENTIFIC_RESULTS.md separates conservation, frozen-EOS and fresh-table results.
No production integration, new EOS patch, device-site deployment or hosting work.

Use the delivered B2 branch, whose parent checkpoint is
`ef1562ae1680fccf3323391e9ec83788c5ae1e69`. Keep the original evidence untouched.
All original source30/source44/official assets are reused by relative import.
Do not rebuild or replace them to replay B2. Their hashes are pinned in B1 and
rechecked by the final integrity audit.

## Runtime

The exact observed runtime, browser/dependency hashes and native revisions are
in `evidence/environment.json`. Python Playwright **1.62.0** launches Chromium
revision 1234 (151.0.7922.34) and WebKit revision 2336 (WPE 26.5). The B1-reported
1.62.1 Python pin was unavailable from the package index; B2 does not pretend to
have installed it. Browser revisions match B1. Node is 22.23.3. Native references
are CoolProp 8.0.0 / 7.2.0 with their recorded source revisions, numpy 2.3.5 and
scipy 1.16.2. The accepted fresh-trajectory generator's separate numpy 2.5.3 pin
must remain unchanged if that currently unexecuted gate is later run.

Example isolated setup outside Git:

```bash
python -m venv /workspace/b2-runtime/python
/workspace/b2-runtime/python/bin/pip install playwright==1.62.0 CoolProp==8.0.0 numpy==2.3.5 scipy==1.16.2
python -m venv /workspace/b2-runtime/python72
/workspace/b2-runtime/python72/bin/pip install CoolProp==7.2.0 numpy==2.3.5
PLAYWRIGHT_BROWSERS_PATH=/workspace/b2-runtime/browsers /workspace/b2-runtime/python/bin/python -m playwright install chromium webkit
cp experiments/dx-fv/browser_eos_b2/runtime-package.json /workspace/b2-runtime/package.json
cp experiments/dx-fv/browser_eos_b2/runtime-package-lock.json /workspace/b2-runtime/package-lock.json
npm ci --prefix /workspace/b2-runtime --cache /workspace/b2-runtime/npm-cache
```

The npm lock resolves acorn 8.15.0, assert 2.1.0, esbuild 0.25.12 and node
22.23.3. No npm install is needed in the research repository.
The committed assertion shim is generated from `import assert from 'assert/';
globalThis.b2assert=assert.strict;`, with a browser process polyfill banner.
ASSERT_NOTICES.md preserves its notices. It is not shipped to the application.

Linux WebKit needs local missing shared libraries. Download the four Debian
packages identified by filename/SHA256 in environment.json, verify hashes, and
extract with `dpkg-deb -x` under `/workspace/b2-runtime/sysroot`; do not modify the
host to reproduce this run. The recorded launcher selects minibrowser-wpe and
prepends that local sysroot. Chromium uses its ordinary Playwright launcher.
Loopback socket permission is necessary. There is no remote server/deployment.

## Fresh output and exact input replay

Run commands from the repository root. Choose a new, nonexistent evidence path:

```bash
export B2_EVIDENCE=/tmp/ammonia-b2-replay-unique
mkdir "$B2_EVIDENCE"
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b2-runtime/browsers
export EOS_WEBKIT_EXECUTABLE=/workspace/b2-runtime/webkit-local.sh
B2=experiments/dx-fv/browser_eos_b2
P8=/workspace/b2-runtime/python/bin/python
P72=/workspace/b2-runtime/python72/bin/python
NODE22=/workspace/b2-runtime/node_modules/node/bin/node

# inputs.json is already preserved with exact binary64 bits. Optional prepare.py
# must use native 8.0 and must reproduce those bytes; never regenerate B1 inputs.
"$P8" "$B2/run-phase.py"
"$P8" "$B2/native.py"
"$P72" "$B2/native.py"
"$P8" "$B2/forensics.py"
PXFLASH_DIRECT_EOS=0 "$P8" "$B2/forensics.py"
"$P72" "$B2/forensics.py"
"$P8" "$B2/analyze-cache.py"
"$P8" "$B2/run-boundary.py"
"$P8" "$B2/boundary-reference.py"
"$P8" "$B2/analyze-boundary-derivatives.py"
"$P72" "$B2/analyze-boundary-derivatives.py"
"$P8" "$B2/run-initialization.py"
B2_INIT_DETAIL=1 B2_INIT_BUILDS=build44 "$P8" "$B2/run-initialization.py"
"$P8" "$B2/analyze-phase.py"
"$P8" "$B2/run-b1-regressions.py"
"$P8" "$B2/run-native-regressions.py"
"$P72" "$B2/run-native-regressions.py"
"$P8" "$B2/analyze-regressions.py"
```

Do not rerun a raw writer into historical output. Several runners deliberately
skip completed files; use a fresh output directory to obtain newly executed tests.
Derived summaries can be regenerated from their corresponding raw evidence.
The negative-quality canonical regression is expected to fail with this preserved
candidate. A file being produced successfully is not a scientific pass.

## Accepted suite

Extract the exact accepted repository outside the working tree:

```bash
mkdir /workspace/b2-runtime/accepted
# Omit if this exact snapshot is already extracted.
git archive be9eb35a4ddf5098e685182f8104685127c6a6ee | tar -x -C /workspace/b2-runtime/accepted
"$NODE22" "$B2/catalog.cjs" /workspace/b2-runtime/accepted /workspace/b2-runtime/catalog.json
# Optional partial-progress persistence, in a separate terminal with the same
# B2_EVIDENCE. It listens only on loopback; final results do not require it.
# "$P8" "$B2/progress-server.py"
"$P8" "$B2/run-browser-suite.py"
# Each original assertion block is an independent execution; failed blocks stay
# failed. B2_BROWSERS=chromium or webkit selects one engine. B2_ONLY selects an
# exact catalog ID. B2_CONTRACTS_ONLY=1 excludes the operating groups for scheduling.
"$NODE22" "$B2/run-suite.cjs" /workspace/b2-runtime/accepted "$B2_EVIDENCE/table-coupled-test-fd-aware.json" coupled-test fd-aware all table
"$NODE22" "$B2/run-suite.cjs" /workspace/b2-runtime/accepted "$B2_EVIDENCE/node-controls-fd-aware.json" coupled-controls fd-aware
GIT_DIR="$PWD/.git" "$NODE22" "$B2/run-roadmap.cjs" /workspace/b2-runtime/accepted rules "$B2_EVIDENCE/a2-rules.json"
GIT_DIR="$PWD/.git" "$NODE22" "$B2/run-roadmap.cjs" /workspace/b2-runtime/accepted domain "$B2_EVIDENCE/a2-domain-fd-aware.json" fd-aware
GIT_DIR="$PWD/.git" "$NODE22" "$B2/run-roadmap.cjs" /workspace/b2-runtime/accepted domain "$B2_EVIDENCE/a2-domain-exact-aware.json" exact-aware
"$P8" "$B2/audit-science.py"
"$P8" "$B2/audit-terminal.py"
```

Both domain commands are expected to preserve 33 completed cases followed by the
missing statePT interface error. Their full suite status is BLOCKED, not passed.
For the completed, separate minimum PT interface experiment, use new filenames:

```bash
B2_PT_INTERFACE=1 GIT_DIR="$PWD/.git" "$NODE22" "$B2/run-roadmap.cjs" /workspace/b2-runtime/accepted domain "$B2_EVIDENCE/a2-domain-pt-fd-aware.json" fd-aware
B2_PT_INTERFACE=1 GIT_DIR="$PWD/.git" "$NODE22" "$B2/run-roadmap.cjs" /workspace/b2-runtime/accepted domain "$B2_EVIDENCE/a2-domain-pt-exact-aware.json" exact-aware
"$P8" "$B2/run-domain.py"
"$P8" "$B2/write-results.py"
"$P8" "$B2/write-science-summary.py"
```

The catalog and several historical launchers deliberately use the recorded
`/workspace/b2-runtime` path. Use that path or explicitly review all path changes
as harness changes. Full table auxiliary verification is more work than the five
fresh operating groups used here: the saved table file records where execution
was stopped, and individual completed groups remain valid comparisons.
The exact accepted `coupled-test`, `coupled-controls`, `coupled-domain-test`,
`coupled-browser`, roadmap harnesses and two independent audit sources are copied
verbatim here for review; execution dependencies come from the accepted archive.
The catalog retains assertion text hashes/source lines. The browser harness uses
a plain-module loader and strict assertions; no test assertion is rewritten.
Node's file-backed adapter only allows the original B1 loader to fetch local WASM.

The delivered ledger lists all additional accepted configurations, original
smoke/ancestor/observer/fresh-reference paths that were not executed. Do not infer
that the commands above complete those gates. The exploratory adaptive-BE methods
mode remains outside the accepted A2 gate and retains its historical limitations.

## Serial cost and offline checks

First stop every scientific numerical/browser worker. These are focused matched
workloads, not additional full qualification:

```bash
"$P8" "$B2/run-performance.py"
"$P8" "$B2/run-coupled-cost.py"
python "$B2/run-offline.py" package /workspace/b2-runtime/offline-package-new
"$P8" "$B2/run-offline.py" smoke /workspace/b2-runtime/offline-package-new
"$P8" "$B2/run-offline.py" smoke /workspace/b2-runtime/offline-package-new --origin-only
"$P8" "$B2/analyze-performance.py"
```

The original B1 standalone worker/property workload is byte-identical. The new
coupled timing worker uses accepted physical cold/warm/reversal fixtures through
0.2 s, one warmup and three measured repetitions. Source transfer and WASM init
are outside that coupled timer; adapter support-guard calls and record construction
are inside. Page timer gaps measure responsiveness while the worker is busy.
Page CDP heap, worker-exposed JS heap and WASM linear memory are different scopes;
none measures total iPad memory. Physical Safari remains NOT RUN.

The first Chromium30 property timing overlapped a short independent audit and is
preserved under evidence/performance-overlap. Its isolated repeat is the reported
measurement. The resulting order and reason are recorded there. No raw timing
was overwritten or counted twice.

Two small native diagnostics were originally captured interactively and are
preserved as JSON, rather than claimed as commands run by the launchers:
`phase-boundary-sensitivity.json` evaluates
`-rho_f**2*(1/rho_g-1/rho_f)/(h_g-h_f)` from native PQ endpoints and compares it
with the independently rooted liquid rho_h; `upper-boundary-native-DU.json`
forms the original PH inventory at the saved 35-bar state and evaluates native
DU at that exact rho/u. Both are reference-only; neither changes model properties.

No local artifact is published. Offline-context and origin-disabled outcomes are
reported separately; a network interception/emulation failure is not relabeled as
successful offline operation.

## Integrity and review

`final-audit.py` checks the delivery branch and all 609 protected B1 file hashes,
accepted suite/dependency bytes, input transport, engine equivalence, stable native
roots, preserved canonical failures and independent completed scientific audits.
An integrity pass is explicitly not a backend qualification pass.
Raw execution logs and the generated third-party notice bundle retain their
original trailing whitespace/terminal blank line. Authored-code whitespace checks
exclude those exact byte-preserved artifacts; no measurement text is trimmed.
`evidence/evidence-hashes.json` pins the final research files. Keep raw failures,
`harness-v1`, interrupted Node evidence and partial files when archiving a replay.

After all raw writers have stopped:

```bash
"$P8" "$B2/audit-catalog.py" /workspace/b2-runtime/catalog.json
"$P8" "$B2/final-audit.py"
```

The catalog audit verifies every supplied source/data string against accepted Git
objects and every completed assertion hash against the unchanged accepted text.
The final audit is specific to this delivery branch and its preserved evidence;
it intentionally asserts that the demonstrated canonical regression still fails.
For a fresh replay, review missing/incomplete entries rather than forcing the
delivery's expected completion counts onto a partial run.

Read SUITE_RESULTS.md and PERFORMANCE_RESULTS.md for actual completed outcomes.
Stop for engineering review; no new EOS patch or further milestone is authorized.
