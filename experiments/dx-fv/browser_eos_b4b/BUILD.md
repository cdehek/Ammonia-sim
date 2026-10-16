# B4B reproduction and build provenance

Use a fresh replay workspace or new output directories. Do not redirect output
over committed evidence. Scientific JSON writers refuse existing result names.
The existing workspace already contains completed results; no rerun is required
to inspect them. Source and artifact identities are in `evidence/provenance.json`.

## Replay archived native artifacts

Install the exact reference/tool packages in an isolated target as in B4A:

```bash
python -m pip install --target /workspace/b4b-tools cmake==4.4.4 ninja==1.13.2 CoolProp==8.0.0 numpy==2.5.4 playwright==1.62.0
export PYTHONPATH=/workspace/b4b-tools
export B4B_EVIDENCE=/tmp/ammonia-b4b-replay
mkdir -p "$B4B_EVIDENCE" /tmp/ammonia-b4b-libs
task_b4b=experiments/dx-fv/browser_eos_b4b
xz -dc experiments/dx-fv/browser_eos_b4a/artifacts/libCoolProp-liquid44.so.xz > /tmp/ammonia-b4b-libs/controlA.so
xz -dc "$task_b4b/artifacts/libCoolProp-candidateB.so.xz" > /tmp/ammonia-b4b-libs/candidateB.so
xz -dc "$task_b4b/artifacts/libCoolProp-diagnostic-controlA.so.xz" > /tmp/ammonia-b4b-libs/diagnostic-controlA.so
xz -dc "$task_b4b/artifacts/libCoolProp-diagnostic-candidateB.so.xz" > /tmp/ammonia-b4b-libs/diagnostic-candidateB.so
```

First verify the decompressed/archive SHA256 against `native-binaries.json`.
`controlA` references the preserved B4A archive without replacing it.

```bash
for build in controlA candidateB; do
  timeout 120 python "$task_b4b/native-focused.py" --library "/tmp/ammonia-b4b-libs/$build.so" --label "$build-primary" --primary-only --output "$B4B_EVIDENCE/native-$build-primary.json"
done
```

Check requested p/h/T, independent getter p/h/u, canonical recovery and local
energy/probe scales before continuing. The primary mode includes saved vapor,
B4A liquid and B1 precision, with their original signed perturbations.

```bash
for build in controlA candidateB; do
  timeout 120 python "$task_b4b/native-focused.py" --library "/tmp/ammonia-b4b-libs/$build.so" --label "$build" --output "$B4B_EVIDENCE/native-$build.json"
  timeout 120 python "$task_b4b/native-focused.py" --library "/tmp/ammonia-b4b-libs/$build.so" --label "$build-full-vle" --full-vle --output "$B4B_EVIDENCE/native-$build-full-vle.json"
  timeout 120 python "$task_b4b/lifecycle.py" --library "/tmp/ammonia-b4b-libs/$build.so" --output "$B4B_EVIDENCE/lifecycle-$build.json"
  B3_TRACE=1 timeout 120 python "$task_b4b/trace-cases.py" --library "/tmp/ammonia-b4b-libs/diagnostic-$build.so" --output "$B4B_EVIDENCE/trace-$build-results.json" 2> "$B4B_EVIDENCE/trace-$build.jsonl"
  timeout 120 python "$task_b4b/trace-cases.py" --library "/tmp/ammonia-b4b-libs/$build.so" --output "$B4B_EVIDENCE/trace-$build-uninstrumented-results.json"
done
cp "$B4B_EVIDENCE/lifecycle-controlA.json" "$B4B_EVIDENCE/lifecycle-controlA-replay.json"
```

Repeat the candidate full matrix using its diagnostic library with `B3_TRACE`
unset/set, naming outputs `native-diagnostic-candidateB-off.json` and `-on.json`.
Only `elapsedSeconds` is excluded when comparing these full rows with the
uninstrumented result. Fixed-inventory comparison and provenance scripts use
the documented `/workspace/b4b-native-artifacts/libCoolProp-<label>.so` paths;
in a new workspace, extract the corresponding archives there or adjust paths
in a separate replay copy. Preserve the original scripts/evidence.

## Browser, compatibility and cost replay

Use Playwright 1.62.0 Chromium 1234 and WebKit 2336:

```bash
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b4b-browsers
python -m playwright install chromium webkit
export EOS_WEBKIT_EXECUTABLE=/workspace/b4b-webkit.sh
timeout 180 python "$task_b4b/run-browser.py"
timeout 180 python "$task_b4b/run-lifecycle-browser.py"
python "$task_b4b/analyze.py"
# Only when focused-gate.json eligibleForLimitedA2 is true:
timeout 120 python "$task_b4b/run-a2.py" --zero-only --tag=-asserted
timeout 300 python "$task_b4b/run-a2.py"
timeout 120 python "$task_b4b/fixed-inventory.py"
timeout 120 python "$task_b4b/run-browser-fixed35.py"
```

Debian uses the isolated WPE launcher in `evidence/webkit-launcher.sh` with six
exact Debian packages. Package filenames/SHA256 are inherited from B4A's
`evidence/provenance.json` `browserExtraDebs`; these were redownloaded and verified.
Extract with `dpkg-deb -x` under `/workspace/b4b-sysroot`; no host package or
configuration change is required. An initial default GTK WebKit launch failure
remains in the evidence. WPE WebKit is desktop Linux, not a physical iPad.

After scientific workloads finish, measure cost without concurrent compilers or
A2 workloads. Run `benchmark-native.py --library ... --output ...` for each build
as `performance-native-controlA.json` / `performance-native-candidateB.json`, then:

```bash
timeout 180 python "$task_b4b/run-lifecycle-browser.py" --performance
python "$task_b4b/performance-summary.py"
python "$task_b4b/audit.py"
```

`audit.py` evaluates independent EOS, derivatives, original normalized probes,
instrumentation equivalence, phase-aware lifecycle, original A2 trace/norm checks
and conservation. Missing evidence fails explicitly. Do not overwrite prior
audit outputs; choose a fresh replay evidence directory.

## Independent source rebuild

Use fresh directories with the exact original paths if binary path identity is
required. Other paths can change binary hashes through embedded `__FILE__`.

```bash
git clone --no-checkout https://github.com/CoolProp/CoolProp.git /workspace/coolprop-b4b
git -C /workspace/coolprop-b4b checkout --detach ae81610e7d23efc57f9d051c8e70a4d66e87537f
git -C /workspace/coolprop-b4b apply "$PWD/experiments/dx-fv/browser_eos_backend/flash-44.patch"
git -C /workspace/coolprop-b4b apply "$PWD/experiments/dx-fv/browser_eos_b4a/liquid-classification.patch"
timeout 240 /workspace/b4b-tools/bin/cmake -S /workspace/coolprop-b4b -B /workspace/b4b-native-build -G Ninja \
 -DCOOLPROP_SHARED_LIBRARY=ON -DCOOLPROP_EXTERNC_LIBRARY=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b4b-tools/bin/ninja \
 -DPython_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
timeout 900 /workspace/b4b-tools/bin/cmake --build /workspace/b4b-native-build -j 2
```

Verify all source hashes against `source-stage-controlA.json` and all nine
dependencies against `dependency-verification.json` before applying B4B. Preserve
the completed control library separately. Dependencies and upstream archive URL
hashes are in `upstream-dependencies.cmake`; no dependency substitutions occurred.

Install emsdk at `389a68bc35dcff7ebae4614e1615099dafda00d1`, install/activate
4.0.12, and source its environment. Configure `/workspace/b4b-wasm-build` with
the same Release/Ninja/Python/export flags, dropping the native shared/EXTERNC
flags and adding:

```text
-DCOOLPROP_JAVASCRIPT_MODULE=ON
-DCMAKE_TOOLCHAIN_FILE=/workspace/emsdk-b4b/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake
-DCPM_Eigen_SOURCE=/workspace/b4b-native-build/_deps/eigen-src
-DCPM_msgpack-c_SOURCE=/workspace/b4b-native-build/_deps/msgpack-c-src
-DCPM_nlohmann_json_SOURCE=/workspace/b4b-native-build/_deps/nlohmann_json-src
-DCPM_valijson_SOURCE=/workspace/b4b-native-build/_deps/valijson-src
-DCPM_IF97_SOURCE=/workspace/b4b-native-build/_deps/if97-src
-DCPM_REFPROP_headers_SOURCE=/workspace/b4b-native-build/_deps/refprop_headers-src
-DCPM_boost_headers_SOURCE=/workspace/b4b-native-build/_deps/boost_headers-src
-DCPM_multicomplex_SOURCE=/workspace/b4b-native-build/_deps/multicomplex-src
-DCPM_fmt_SOURCE=/workspace/b4b-native-build/_deps/fmt-src
```

Build with a 900 s deadline and `-j 2`; preserve control JS/WASM in a new directory.
Control equivalence is established by results, not just hashes: source-directory
paths and upstream incompressible JSON enumeration can change whole-binary hashes.
Generated fluid content remains equal; no source fluid data changes.

After control reproduction and algorithm review, copy the preserved control source
manifest into the fresh evidence directory and apply the exact reviewed patch:

```bash
cp "$task_b4b/evidence/source-stage-controlA.json" "$B4B_EVIDENCE/source-stage-controlA.json"
python "$task_b4b/apply-repair.py" /workspace/coolprop-b4b
timeout 300 /workspace/b4b-tools/bin/cmake --build /workspace/b4b-native-build -j 2
timeout 300 /workspace/b4b-tools/bin/cmake --build /workspace/b4b-wasm-build -j 2
```

Preserve candidate outputs separately. `apply-repair.py` requires exact B4A
sources, retains the existing patch if identical, and writes the candidate source
stage into the selected evidence directory. Do not copy rebuilds over archived
research artifacts. The repository's browser loader selects archived artifacts;
use an isolated replay copy/loader mapping to test newly rebuilt binaries.

For diagnostics, `instrument.py <source> <new diagnostic evidence directory>`
adapts B3 logging and saves exact original translation units for restoration.
Build native with a 300 s deadline; preserve the diagnostic library. Restore those
three saved source files afterward and verify the candidate source hashes. No
instrumented WASM build is claimed. Exact actual compile commands and CMake
caches accompany this milestone. MIT/Boost/MPL/LLVM/Emscripten/libc notices are
retained under `vendor/`; pinned upstream source plus all three functional patches
and exact diagnostic diffs provide the corresponding experimental source.

Budgets: verification/reproduction 30 minutes, build setup 60 minutes, focused
validation 60 minutes; two compiler jobs per build, 120–180 s property/browser
deadlines, 300 s limited A2 deadline. Build/test command deadlines were met; the later documentation resume did not
restart the experimental campaign.
No full B2/A2 campaign, production integration, hosting or deployment is part of
reproduction. Preserve failed outputs and stop downstream work if a primary gate
fails.
