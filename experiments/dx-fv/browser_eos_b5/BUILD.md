# Reproduction and bounded execution

Do not overwrite committed evidence. Use a new `B5_EVIDENCE` directory; all B5
Python writers honor it. The scripts read original B4C/B4B fixtures in place.
They never regenerate saved inputs. Run from the repository root. Paths below
match the delivered harness; change path constants only in a separate replay
checkout if your workspace differs.

## Archived binary replay

Install isolated tools (use your configured network/proxy normally):

```bash
python -m pip install --target /workspace/b5-tools CoolProp==8.0.0 cmake==4.4.4 ninja==1.13.2
python -m pip install --target /workspace/b5-tools72 CoolProp==7.2.0
# scipy/numpy, mpmath 1.3.0 and Playwright 1.62.0 were also available.
export PYTHONPATH=/workspace/b5-tools
export B5_EVIDENCE=/tmp/ammonia-b5-replay
mkdir -p "$B5_EVIDENCE" /workspace/b5-libs
b5_task=experiments/dx-fv/browser_eos_b5
xz -dc experiments/dx-fv/browser_eos_b4c/artifacts/libCoolProp-candidateB.so.xz > /workspace/b5-libs/candidateB.so
xz -dc experiments/dx-fv/browser_eos_b4b/artifacts/libCoolProp-candidateB.so.xz > /workspace/b5-libs/controlA.so
xz -dc "$b5_task/artifacts/rebuilt-uninstrumented.so.xz" > /workspace/b5-libs/rebuilt-uninstrumented.so
xz -dc "$b5_task/artifacts/diagnostic.so.xz" > /workspace/b5-libs/diagnostic-final.so
```

Verify SHA256 against B4C/B4B native manifests and B5 `native-binaries.json`
**before** loading libraries. Native source/build instructions below are needed
for independent reference coefficient access and the full source audit, but
archived fixed DU replay itself does not require a build.

```bash
timeout 120 python "$b5_task/replay-native.py"
PYTHONPATH=/workspace/b5-tools72 timeout 120 python "$b5_task/replay72.py"
timeout 120 python "$b5_task/ph-replay.py"
PYTHONPATH=/workspace/b5-tools72 timeout 120 python "$b5_task/ph-replay.py" --historical72
timeout 180 python "$b5_task/references.py"
timeout 240 python "$b5_task/high-precision.py"
python "$b5_task/failure-ledger.py"
timeout 120 python "$b5_task/attribution.py"
timeout 240 python "$b5_task/precision-audit.py"
timeout 120 python "$b5_task/diagnostics.py"
```

The original fixed inputs are produced by extracting saved JSON numbers/bits,
not by rerunning PH. Newly formed inventories in PH/reference/sweep experiments
have explicit separate labels and are never used to replace the fixed ledger.
The 65/90-digit evaluator requires `/workspace/coolprop-b5/dev/fluids/Ammonia.json`
from the exact pinned source; SHA256 is recorded in high-precision evidence.

## Browsers

Install Playwright WebKit into `/workspace/b5-browsers`. The delivered run used
system `/usr/bin/chromium` 154.0.8037.57, WPE WebKit 26.5 and Playwright 1.62.0.
Browser version differences must be recorded, not assumed bit-identical.

```bash
PLAYWRIGHT_BROWSERS_PATH=/workspace/b5-browsers python -m playwright install webkit
```

Use the unchanged B4C WPE launcher with only runtime filesystem paths changed:
replace `b4c-browsers` with `b5-browsers` and `b4c-sysroot` with `b5-sysroot`,
write `/workspace/b5-webkit.sh`, and make it executable. This is an external
browser launch script, not the EOS loader.

The same six Debian packages/hashes are listed in `evidence/browser-libraries.json`
and B4A `evidence/provenance.json:browserExtraDebs`. Download their exact URLs,
verify SHA256 and `dpkg-deb -x` into `/workspace/b5-sysroot`. No host package or
EOS loader modification is needed. WPE avoids the GTK host dependencies listed
in the preserved setup warning. Keep that warning as a setup attempt.

```bash
PLAYWRIGHT_BROWSERS_PATH=/workspace/b5-browsers timeout 180 python "$b5_task/replay-browser.py"
PLAYWRIGHT_BROWSERS_PATH=/workspace/b5-browsers timeout 180 python "$b5_task/run-browser-diagnostics.py"
timeout 120 python "$b5_task/eos-audit.py"
```

These scripts start a loopback HTTP server, read local preserved assets and
shut the server down after the run. They do not deploy a site. The exact inherited
B4C loader and accepted research adapter are imported directly. Browser full-VLE
configuration is not exposed; the output states that limitation. The diagnostic
guard wrapper logs calls/results without altering arguments or error handling.

## Native source reconstruction and logging-only rebuild

```bash
git clone --depth 1 --branch v8.0.0 https://github.com/CoolProp/CoolProp.git /workspace/coolprop-b5
git -C /workspace/coolprop-b5 rev-parse HEAD
# MUST be ae81610e7d23efc57f9d051c8e70a4d66e87537f

git -C /workspace/coolprop-b5 apply "$PWD/experiments/dx-fv/browser_eos_backend/flash-44.patch"
git -C /workspace/coolprop-b5 apply "$PWD/experiments/dx-fv/browser_eos_b4a/liquid-classification.patch"
git -C /workspace/coolprop-b5 apply "$PWD/experiments/dx-fv/browser_eos_b4b/pt-cache-consistency.patch"
git -C /workspace/coolprop-b5 apply "$PWD/experiments/dx-fv/browser_eos_b4c/upper-quality-classification.patch"
python "$b5_task/audit-start.py"

timeout 240 /workspace/b5-tools/bin/cmake -S /workspace/coolprop-b5 -B /workspace/b5-native-build -G Ninja \
 -DCOOLPROP_SHARED_LIBRARY=ON -DCOOLPROP_EXTERNC_LIBRARY=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b5-tools/bin/ninja \
 -DPython_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
timeout 900 /workspace/b5-tools/bin/cmake --build /workspace/b5-native-build -j 2
cp /workspace/b5-native-build/libCoolProp.so.8.0.0 /workspace/b5-libs/rebuilt-uninstrumented.so
```

All nine dependency trees must match B5 provenance/B4C dependency digests.
The CMake cache and full compile commands are preserved. Host GCC is
14.2.0-19; Release O3/NDEBUG/C++17, no fast-math. Different build paths/generated
resource ordering can change whole-binary SHA; scientific equivalence is checked
separately. No new WASM build is needed or made in B5.

Before instrumentation, the rebuilt uninstrumented library must replay the
archived B4C scientific results exactly:

```bash
timeout 120 python "$b5_task/trace-replay.py" --library /workspace/b5-libs/rebuilt-uninstrumented.so \
 --output "$B5_EVIDENCE/rebuilt-uninstrumented.json" \
 > "$B5_EVIDENCE/rebuilt-uninstrumented.log" 2> "$B5_EVIDENCE/rebuilt-uninstrumented-markers.jsonl"
python "$b5_task/instrument.py" /workspace/coolprop-b5
timeout 300 /workspace/b5-tools/bin/cmake --build /workspace/b5-native-build -j 2
cp /workspace/b5-native-build/libCoolProp.so.8.0.0 /workspace/b5-libs/diagnostic-final.so
B5_TRACE=1 timeout 120 python "$b5_task/trace-replay.py" --library /workspace/b5-libs/diagnostic-final.so \
 --output "$B5_EVIDENCE/trace-on-results.json" \
 > "$B5_EVIDENCE/trace-on.log" 2> "$B5_EVIDENCE/trace-on.jsonl"
timeout 120 python "$b5_task/trace-replay.py" --library /workspace/b5-libs/diagnostic-final.so \
 --output "$B5_EVIDENCE/trace-off-results.json" \
 > "$B5_EVIDENCE/trace-off.log" 2> "$B5_EVIDENCE/trace-off-markers.jsonl"
timeout 120 python "$b5_task/trace-audit.py"
```

The instrumentation script saves exact originals and a unified logging-only
patch under the output directory. Restore FlashRoutines.cpp and VLERoutines.cpp
to `src/Backends/Helmholtz/`, and Solvers.cpp to `src/`, from those originals.
Rerun `audit-start.py` to verify the full inherited B4C source manifest. Do not
confuse the build directory's diagnostic library with an uninstrumented backend.
The first phase-only instrumentation trace/binary is preserved as an earlier
stage; the final patch additionally logs Brent termination, with identical results.

```bash
python "$b5_task/scientific-audit.py"
python "$b5_task/diagnosis.py"
```

For the full preservation/provenance audit, copy the committed
`starting-file-hashes.json` into the new evidence directory and run
`provenance.py` after source restoration. The original manifest refers to the
B4C checkpoint, not a claim that a later replay checkout has its original clean
starting status. `final-audit.py` compares that baseline and recorded remote refs.

All scientific replays carry process limits of 120–240 seconds, browser runs
180 seconds, native configure 240 seconds, initial build 900 seconds and
logging-only incremental builds 300 seconds, at most two compiler jobs.
Setup/source/build budget was bounded to 30 minutes; all required experiments
completed within their individual deadlines. No coupled/A2 campaign, speculative
functional fix, generic EOS sweep or physical iPad run was performed. Preserve
partial output if a future replay times out or cannot launch; do not invent a
replacement failure.
