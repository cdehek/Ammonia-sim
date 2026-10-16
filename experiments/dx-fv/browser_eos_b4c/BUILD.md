# B4C reproduction and resource limits

Keep the committed evidence immutable. Use a fresh checkout/output directory.
All Python evidence writers refuse existing scientific result names. Source
patch application requires exact B4B source. A replay on the delivery checkout
will identify its own HEAD in the preservation receipt; the original clean
starting checkpoint is recorded in the committed receipt.

## Archived native and browser replay

From the repository root, install isolated tools and extract libraries:

```bash
python -m pip install --target /workspace/b4c-tools cmake==4.4.4 ninja==1.13.2 CoolProp==8.0.0 numpy==2.5.4 playwright==1.62.0
export PYTHONPATH=/workspace/b4c-tools
export B4C_EVIDENCE=/tmp/ammonia-b4c-replay
mkdir -p "$B4C_EVIDENCE" /workspace/b4c-libs
task_b4c=experiments/dx-fv/browser_eos_b4c
xz -dc experiments/dx-fv/browser_eos_b4b/artifacts/libCoolProp-candidateB.so.xz > /workspace/b4c-libs/controlA.so
xz -dc "$task_b4c/artifacts/libCoolProp-controlA.so.xz" > /workspace/b4c-libs/rebuiltA.so
xz -dc "$task_b4c/artifacts/libCoolProp-candidateB.so.xz" > /workspace/b4c-libs/candidateB.so
xz -dc "$task_b4c/artifacts/libCoolProp-diagnostic-candidateB.so.xz" > /workspace/b4c-libs/diagnostic-candidateB.so
xz -dc experiments/dx-fv/browser_eos_b4b/artifacts/libCoolProp-diagnostic-candidateB.so.xz > /workspace/b4c-libs/diagnostic-controlA.so
python "$task_b4c/preserve.py"
```

Verify archive and decompressed hashes against `evidence/native-binaries.json`;
the archived scientific control/diagnostic-control identities are the unchanged
B4B candidate/diagnostic-candidate entries in B4B's native manifest.

```bash
for build in controlA candidateB; do
  timeout 120 python experiments/dx-fv/browser_eos_b4b/native-focused.py --library "/workspace/b4c-libs/$build.so" --label "$build" --output "$B4C_EVIDENCE/native-$build.json"
done
timeout 120 python "$task_b4c/scientific-audit.py" --native-only --output "$B4C_EVIDENCE/native-focused-gate.json"
```

Only continue if that gate passes. Run each build with `native-focused.py
--full-vle` to `native-<build>-full-vle.json`; run unchanged B4B `lifecycle.py`
to `lifecycle-<build>.json`; run B4C `shared-callers.py` normally and with
`--full-vle` to `shared-<build>.json` and `shared-<build>-full-vle.json`.
Every invocation takes `--library` and `--output`. Then:

```bash
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b4c-browsers
python -m playwright install chromium webkit
export EOS_WEBKIT_EXECUTABLE=/workspace/b4c-webkit.sh
timeout 180 python "$task_b4c/run-browser.py"
python "$task_b4c/scientific-audit.py" --output "$B4C_EVIDENCE/focused-gate.json"
timeout 180 python "$task_b4c/run-lifecycle-browser.py"
timeout 180 python "$task_b4c/run-shared-browser.py"
timeout 120 python "$task_b4c/fixed-inventories.py"
timeout 120 python "$task_b4c/run-browser-fixed35.py"
timeout 120 python "$task_b4c/upper-inventory.py"
timeout 120 python "$task_b4c/run-upper-inventory-browser.py"
python "$task_b4c/default-equilibrium-audit.py"
python "$task_b4c/boundary-audit.py"
python "$task_b4c/cache-audit.py" --library /workspace/b4c-libs/candidateB.so --output "$B4C_EVIDENCE/cache-candidateB.json"
```

Desktop WebKit uses the preserved `evidence/webkit-launcher.sh`, installed as
`/workspace/b4c-webkit.sh`. Download the six Debian packages named and hashed in
B4A `evidence/provenance.json:browserExtraDebs`, verify their SHA256, and extract
with `dpkg-deb -x` into `/workspace/b4c-sysroot`. Debian pool directories are
`libm/libmanette`, `h/hyphen`, `h/harfbuzz`, and `libg/libglvnd`. No host package
or loader modification is required. This is WPE WebKit on Linux, not iPadOS.

For logging parity, run `trace-matrix.py --library ... --output ...`, redirecting
stderr into distinct JSONL files. Use `B3_TRACE=1` for the inherited diagnostic
control; `B4C_TRACE=1` for the candidate. Run candidate diagnostic on/off and
uninstrumented, plus candidate `--full-vle`, under the filenames consumed by
`trace-audit.py`. Its PH snapshots must equal the full scientific matrix exactly.
Native logging has no extra EOS evaluation and no generic solver modification.

## Independent source rebuild

```bash
git clone --no-checkout https://github.com/CoolProp/CoolProp.git /workspace/coolprop-b4c
git -C /workspace/coolprop-b4c checkout --detach ae81610e7d23efc57f9d051c8e70a4d66e87537f
git -C /workspace/coolprop-b4c apply "$PWD/experiments/dx-fv/browser_eos_backend/flash-44.patch"
git -C /workspace/coolprop-b4c apply "$PWD/experiments/dx-fv/browser_eos_b4a/liquid-classification.patch"
git -C /workspace/coolprop-b4c apply "$PWD/experiments/dx-fv/browser_eos_b4b/pt-cache-consistency.patch"
python "$task_b4c/preimplementation.py"
timeout 240 /workspace/b4c-tools/bin/cmake -S /workspace/coolprop-b4c -B /workspace/b4c-native-build -G Ninja \
 -DCOOLPROP_SHARED_LIBRARY=ON -DCOOLPROP_EXTERNC_LIBRARY=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b4c-tools/bin/ninja \
 -DPython_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
timeout 900 /workspace/b4c-tools/bin/cmake --build /workspace/b4c-native-build -j 2
```

All 1,782 upstream tracked source hashes must match B4B candidate before B4C.
All nine dependencies must match `dependency-verification.json`. Exact versions,
URLs/pins, compiler and CMake commands are in the caches/compile-command records
and inherited `upstream-dependencies.cmake`; no dependency substitution is allowed.
Preserve `libCoolProp.so.8.0.0` as the rebuilt control before further builds.

Clone emsdk to `/workspace/emsdk-b4c`, checkout
`389a68bc35dcff7ebae4614e1615099dafda00d1`, install/activate **4.0.12**,
and source `emsdk_env.sh`. Configure the WASM directory with the same Release,
Ninja, Python and export flags, omit native shared/EXTERNC flags, and add:

```text
-DCOOLPROP_JAVASCRIPT_MODULE=ON
-DCMAKE_TOOLCHAIN_FILE=/workspace/emsdk-b4c/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake
-DCPM_Eigen_SOURCE=/workspace/b4c-native-build/_deps/eigen-src
-DCPM_msgpack-c_SOURCE=/workspace/b4c-native-build/_deps/msgpack-c-src
-DCPM_nlohmann_json_SOURCE=/workspace/b4c-native-build/_deps/nlohmann_json-src
-DCPM_valijson_SOURCE=/workspace/b4c-native-build/_deps/valijson-src
-DCPM_IF97_SOURCE=/workspace/b4c-native-build/_deps/if97-src
-DCPM_REFPROP_headers_SOURCE=/workspace/b4c-native-build/_deps/refprop_headers-src
-DCPM_boost_headers_SOURCE=/workspace/b4c-native-build/_deps/boost_headers-src
-DCPM_multicomplex_SOURCE=/workspace/b4c-native-build/_deps/multicomplex-src
-DCPM_fmt_SOURCE=/workspace/b4c-native-build/_deps/fmt-src
```

Build `/workspace/b4c-wasm-build` with `timeout 900 ... --build ... -j 2`.
Preserve control JS/WASM separately. Both rebuilt scientific control matrices
must match the archived B4B rows/probes exactly before accepting them as controls.

Record a fresh `preimplementation-decision.json` containing the SHA256 of
`ALGORITHM.md`, `preimplementation-thermodynamics.json`, successful control/source
verification and `functionalB4CPatchApplied:false`. Then apply:

```bash
python "$task_b4c/apply-repair.py" /workspace/coolprop-b4c
timeout 300 /workspace/b4c-tools/bin/cmake --build /workspace/b4c-native-build -j 2
```

Preserve the native candidate and pass its focused gate before the incremental
WASM build (`timeout 300`, `-j 2`). Put rebuilt browser outputs in a separate
replay loader copy; the shipped loader maps `controlA` to preserved B4B,
`rebuiltA` to the new control, and `candidateB` to the new candidate. Only asset
selection differs from B4B; exception handling is byte-for-byte inherited.

For a native diagnostic build run `instrument.py <source> <new-directory>`, build
with a 300 s deadline and retain the diagnostic library separately. Restore both
translation units saved in that directory and verify the complete candidate
source manifest. `src/Solvers.cpp` is never instrumented in B4C. Do not confuse a
diagnostic build-directory output with the preserved uninstrumented candidate.

Exact paths can affect hashes through `__FILE__`; generated incompressible JSON
ordering can also affect whole binaries. Scientific equivalence and full source
identities, not the version string alone, identify a rebuilt experimental backend.
MIT/Boost/MPL/LLVM/Emscripten/libc notices are preserved under `vendor/`.

## Gated A2 and timing

After focused and boundary gates pass, run `run-a2.py --zero-only` and
`run-a2.py` for candidate, then repeat with `--build controlA --tag=-controlA`.
Use 120/300 s deadlines. `a2-audit.py` applies the original accepted checks and
compares settings, work and events. These are the bounded saved fixtures only.

After all compilers and scientific workloads finish, run `benchmark-native.py`
serially for rebuilt control/candidate (`--library`, `--output`), then
`run-lifecycle-browser.py --performance --builds rebuiltA,candidateB` (180 s).
For matched A2 timing run `run-a2.py --cases cold --build rebuiltA
--tag=-perf-controlA` followed by `--cases cold --tag=-perf-candidateB`.
`performance-summary.py` uses these separate measurements. No unrelated ratios
are multiplied into simulator cost. No full A2 campaign or physical iPad claim.

Limits used: inspection/reproduction 10 min each; setup/build 60 min total;
individual full builds 900 s, incremental/diagnostic builds 300 s, at most two
compiler jobs per build; property/browser campaigns 120–180 s; bounded A2 300 s.
All deadlines completed. Preserve partial output and stop downstream experiments
if an essential physical or numerical gate fails. Stop for engineering review
after this milestone; do not deploy or start the 35-bar repair.
