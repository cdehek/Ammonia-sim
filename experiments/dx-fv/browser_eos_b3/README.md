# B3 — phase-decision forensics

Targeted diagnosis from exact B2 commit
`6a220dd6c94bff08e00e0107cfec71854166ede2`, on new branch
`research/browser-eos-b3-phase-forensics-20261015`. Read
[ENGINEERING_REPORT.md](ENGINEERING_REPORT.md),
[REPAIR_PROPOSALS.md](REPAIR_PROPOSALS.md), and
[MECHANICS_REPORT.md](MECHANICS_REPORT.md).

Everything added is isolated here. Original B1/B2 files, their artifacts and
accepted A2 sources remain byte-identical. There is no functional correction,
model/solver change, deployment, integration or merged branch.

## Evidence map

- `inputs.json`: preserved binary64 fixtures and labeled tolerance diagnostics.
- `evidence/preservation-start.json`: SHA256 of all 854 B2 starting files and
  checks of all 12 accepted A2 dependency snapshots against Git objects.
- `evidence/chromium-*.json`, `webkit-*.json`: exact original base and signed
  probes, repeat bits and paired physical/PH-derived inventories.
- `evidence/native-{wheel8,wheel72,source30,source44,diag30,diag44}.json`:
  native reproductions, independent homogeneous roots, stability quantities,
  canonical inventories and matching-version DT checks.
- `evidence/audit-browser-native*.json`: independent DT reevaluation of all
  browser snapshots, physical input classification, unchanged-probe derivative
  comparisons and physical crossing/support exclusions.
- `evidence/saturation-reference-*.json`: fixed-pressure coexistence roots of
  pL=P, pV=P, gL=gV from deliberately displaced diagnostic seeds. The earlier
  `saturation-seed-check-*` files preserve independent EOS checks at public seeds.
- `evidence/trace{30,44}.jsonl`: captured source execution, with exact API-input
  markers; PH decision followed by native inventory-recovery calls. Only events
  before the first `PH_dispatch` belong to the original PH decision.
- `evidence/probes-trace*.jsonl`: repeated preserved source-level signed probes
  and isolated PT traces. `no-superanc-trace*` is a separate diagnostic with
  superancillaries disabled, never a replacement backend/fixture.
- `evidence/instrumentation*.diff`: logging-only source additions; the 44-bit
  combined upstream diff also contains the **pre-existing B1 expression**. The
  exact source stages and source/binary manifests distinguish those changes.
- `evidence/summary.json`: derived reproduction, branch, cache and preservation
  ledger; no failed result is removed from its raw record.
- `evidence/*setup*`, `*failure*`, build logs, compiler commands/cache and
  environment/provenance records retain setup attempts and tool identities.

## Reproduce without overwriting historical evidence

Use a fresh isolated copy/check-out of this branch. The historical B1 JavaScript,
WASM and loader are reused unchanged, including official 7.2's scalar interface.
`prepare.py` documents how the matrix was selected; existing `inputs.json` is the
authoritative byte-pinned matrix and need not be regenerated.

Create external virtual environments with Python 3.12:

```bash
python3 -m venv /workspace/b3-runtime
/workspace/b3-runtime/bin/pip install CoolProp==8.0.0 numpy==2.3.5 cmake==3.31.6 ninja==1.11.1.4 playwright==1.62.0
python3 -m venv /workspace/b3-runtime72
/workspace/b3-runtime72/bin/pip install CoolProp==7.2.0 numpy==2.3.5
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b3-browsers
/workspace/b3-runtime/bin/python -m playwright install chromium webkit
```

The captured environment uses Chromium revision 1234 and WPE WebKit 2336. Supply
any required shared libraries in an external sysroot and use the recorded
`evidence/webkit-launcher.sh` with `EOS_WEBKIT_EXECUTABLE`; do not assume desktop
WebKit is physical Safari. Actual missing-library attempts and .deb hashes are
preserved. Supported executor network access is needed for downloads and local
browser server/socket execution in this environment.

```bash
export B3_EVIDENCE=/tmp/ammonia-b3-replay
mkdir -p "$B3_EVIDENCE"
task_b3=experiments/dx-fv/browser_eos_b3
/workspace/b3-runtime/bin/python "$task_b3/native.py" --label wheel8 --output "$B3_EVIDENCE/native-wheel8.json"
/workspace/b3-runtime72/bin/python "$task_b3/native.py" --label wheel72 --output "$B3_EVIDENCE/native-wheel72.json"
timeout 600 /workspace/b3-runtime/bin/python "$task_b3/run-browser.py"
timeout 180 /workspace/b3-runtime/bin/python "$task_b3/audit-browser.py"
timeout 180 /workspace/b3-runtime72/bin/python "$task_b3/audit-browser.py"
/workspace/b3-runtime/bin/python "$task_b3/saturation-reference.py"
/workspace/b3-runtime72/bin/python "$task_b3/saturation-reference.py"
```

Source native controls use upstream CoolProp exactly
`ae81610e7d23efc57f9d051c8e70a4d66e87537f`, matching the B1 source. Dependency
commits match the B1 manifest; Eigen/Valijson archives retain upstream SHA256
pins. Supply pinned `CPM_<Name>_SOURCE` overrides if a tag/download resolves
differently; never silently substitute a dependency. Configure/build:

```bash
git clone --depth 1 --branch v8.0.0 https://github.com/CoolProp/CoolProp.git /workspace/coolprop-b3
test "$(git -C /workspace/coolprop-b3 rev-parse HEAD)" = ae81610e7d23efc57f9d051c8e70a4d66e87537f
/workspace/b3-runtime/bin/cmake -S /workspace/coolprop-b3 -B /workspace/b3-build -G Ninja \
 -DCOOLPROP_SHARED_LIBRARY=ON -DCOOLPROP_EXTERNC_LIBRARY=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b3-runtime/bin/ninja \
 -DPython_EXECUTABLE=/workspace/b3-runtime/bin/python \
 -DPYTHON_EXECUTABLE=/workspace/b3-runtime/bin/python -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
timeout 900 /workspace/b3-runtime/bin/cmake --build /workspace/b3-build -j 2
timeout 1500 bash "$task_b3/build-native.sh"
```

`build-native.sh` records source30, logging30, the exact historical B1 source44,
then logging44. Only `git apply` of the preserved B1 patch recreates 44 bits;
`instrument.py` inserts diagnostics and changes no comparison or equation.
The source repository is an external build dependency; no commit/push is made
there. `B3_TRACE=1` enables logging in diagnostic libraries. The trace wrapper
uses the exported C API and records the original API argument bits before the
source's mass-to-molar conversion.

For a standalone trace with an already built diagnostic library:

```bash
B3_TRACE=1 /workspace/b3-runtime/bin/python "$task_b3/trace-probes.py" \
 --library /workspace/b3-native-artifacts/libCoolProp-diag30.so \
 --output "$B3_EVIDENCE/probes-repeat.json" 2> "$B3_EVIDENCE/probes-repeat.jsonl"
```

For the committed preservation checks, use the committed starting-file manifest
in the same repository layout. Replay `summarize.py` after supplying that
manifest in the new evidence directory and completing its named input files.
All scripts refuse to overwrite their scientific JSON outputs. Platform and
relocated source paths can change native binary hashes; numerical equivalence
must be checked independently. Exact compiler commands and source hashes record
the observed build, not a cross-platform bitwise-build guarantee.

Do not apply any proposed B4 correction during reproduction. Original numerical
budgets and failure/domain behavior remain the gates described in
[REPAIR_PROPOSALS.md](REPAIR_PROPOSALS.md). Review is the next action.
