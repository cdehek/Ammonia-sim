# B4A reproduction

Use a fresh isolated clone/replay directory. Never overwrite B1/B2/B3 binaries
or evidence. Scientific writers refuse existing output filenames. Select a new
`B4A_EVIDENCE` directory for replay, copy the starting preservation manifest into
it when reproducing the final audits, and retain this branch's original evidence.
`B3_EVIDENCE` is separately needed for the unchanged B3 coexistence reference
script. Paths below are the actual build paths; relocated paths can change hashes.

## Tools and pinned inputs

Observed: Debian 13 x86_64, GCC 14.2.0, Python 3.12.14, CMake 4.4.4,
Ninja Python package 1.13.2 (binary `1.13.2.git.kitware.jobserver-pipe-1`),
CoolProp wheel 8.0.0, NumPy 2.5.4, Playwright 1.62.0. Exact revisions, compiler
hash, SDK versions and package identities are in `evidence/provenance.json`.

```bash
python3 -m pip install --target /workspace/b4a-tools cmake==4.4.4 ninja==1.13.2 CoolProp==8.0.0 numpy==2.5.4
export PYTHONPATH=/workspace/b4a-tools
git clone --no-checkout https://github.com/CoolProp/CoolProp.git /workspace/coolprop-b4a
git -C /workspace/coolprop-b4a checkout --detach ae81610e7d23efc57f9d051c8e70a4d66e87537f
git clone https://github.com/emscripten-core/emsdk.git /workspace/emsdk-b4a
git -C /workspace/emsdk-b4a checkout --detach 389a68bc35dcff7ebae4614e1615099dafda00d1
timeout 240 /workspace/emsdk-b4a/emsdk install 4.0.12
/workspace/emsdk-b4a/emsdk activate 4.0.12
source /workspace/emsdk-b4a/emsdk_env.sh
```

Verify source HEAD, clean source and the upstream tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662` before patches. Emscripten is exactly
4.0.12 `6f625bd62ee64f4f8cd11476774741b961e4a2d5`; SDK release
`209b886304498eff50dd835850dc5715803401ed`; LLVM
`7f93487862d98bf1c168babba87daf6224d8a46f`; SDK Node 22.16.0.

## Control and repair builds

From the repository root, set the actual Python executable path in the command
below. The observed interpreter was
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`.

```bash
task_b4a=experiments/dx-fv/browser_eos_b4a
git -C /workspace/coolprop-b4a apply /workspace/Ammonia-sim/experiments/dx-fv/browser_eos_backend/flash-44.patch
timeout 240 /workspace/b4a-tools/bin/cmake -S /workspace/coolprop-b4a -B /workspace/b4a-native-build -G Ninja \
 -DCOOLPROP_SHARED_LIBRARY=ON -DCOOLPROP_EXTERNC_LIBRARY=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b4a-tools/bin/ninja \
 -DPython_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
timeout 900 /workspace/b4a-tools/bin/cmake --build /workspace/b4a-native-build -j 2
```

All nine dependency source trees must match `evidence/dependency-verification.json`,
which matches B3's digests. Git commits are pinned in that manifest; Eigen/Valijson
archives retain upstream URL/SHA256 pins in `evidence/upstream-dependencies.cmake`.
Supply `-DCPM_<Name>_SOURCE=<prefetched directory>` for those exact sources rather
than silently substituting a dependency on a download failure.

Configure WASM with the same Python/Ninja/export flags, substituting
`-B /workspace/b4a-wasm-build`, dropping the two native-library options, and adding:

```text
-DCOOLPROP_JAVASCRIPT_MODULE=ON
-DCMAKE_TOOLCHAIN_FILE=/workspace/emsdk-b4a/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake
-DCPM_Eigen_SOURCE=/workspace/b4a-native-build/_deps/eigen-src
-DCPM_msgpack-c_SOURCE=/workspace/b4a-native-build/_deps/msgpack-c-src
-DCPM_nlohmann_json_SOURCE=/workspace/b4a-native-build/_deps/nlohmann_json-src
-DCPM_valijson_SOURCE=/workspace/b4a-native-build/_deps/valijson-src
-DCPM_IF97_SOURCE=/workspace/b4a-native-build/_deps/if97-src
-DCPM_REFPROP_headers_SOURCE=/workspace/b4a-native-build/_deps/refprop_headers-src
-DCPM_boost_headers_SOURCE=/workspace/b4a-native-build/_deps/boost_headers-src
-DCPM_multicomplex_SOURCE=/workspace/b4a-native-build/_deps/multicomplex-src
-DCPM_fmt_SOURCE=/workspace/b4a-native-build/_deps/fmt-src
```

Build with `timeout 600 .../cmake --build /workspace/b4a-wasm-build -j 2`.
Preserve the completed native library as
`/workspace/b4a-native-artifacts/libCoolProp-control44.so` and JS/WASM separately
as `vendor/control44/` in the isolated replay copy. Confirm the exact original
failure before changing source. Only then:

```bash
python3 "$task_b4a/make-patch.py" /workspace/coolprop-b4a
timeout 240 /workspace/b4a-tools/bin/cmake --build /workspace/b4a-native-build -j 2
timeout 240 /workspace/b4a-tools/bin/cmake --build /workspace/b4a-wasm-build -j 2
```

Preserve outputs as `libCoolProp-liquid44.so` and `vendor/liquid44/`. `make-patch.py`
verifies the pinned upstream and exact B1 flash hash, changes the two caloric
liquid-dispatch conditions and emits/verifies `liquid-classification.patch`.
Source stage manifests record all tracked source hashes. Instrument only after
preserving both uninstrumented binaries:

```bash
python3 "$task_b4a/instrument.py" /workspace/coolprop-b4a
timeout 300 /workspace/b4a-tools/bin/cmake --build /workspace/b4a-native-build -j 2
# Preserve as libCoolProp-diagnostic44.so. B4A_TRACE=1 enables logging.
```

The exact compile commands and CMake caches are retained. Native release uses
`-O3 -DNDEBUG -std=gnu++17`, `-DCOOLPROP_LIB -m64 -DEXTERNC` plus upstream flags;
WASM uses upstream exception support, `COOLPROP_NO_INCBIN`,
`VALIJSON_USE_EXCEPTIONS=1`, `-lembind -s ASSERTIONS=1
-s DISABLE_EXCEPTION_CATCHING=0 -sALLOW_MEMORY_GROWTH=1 -s EXPORT_ES6=1
-s MODULARIZE=1`. There is no fast-math. All original fluid/EOS sources and
equilibrium equations are unchanged. Source and dependency licensing notices
are retained in `vendor/`; the exact original B1 flash source is already archived
in `../browser_eos_backend/source/` and the new liquid patch is supplied here.

## Scientific replay, in gated order

```bash
export B4A_EVIDENCE=/tmp/ammonia-b4a-replay
mkdir -p "$B4A_EVIDENCE"
# First run native-focused.py --primary-only against control and repair,
# with explicit new --output paths. Add --full-vle for the alternate path.
timeout 120 python3 "$task_b4a/native-focused.py" --library /workspace/b4a-native-artifacts/libCoolProp-control44.so --label control44 --output "$B4A_EVIDENCE/native-control44.json"
timeout 120 python3 "$task_b4a/native-focused.py" --library /workspace/b4a-native-artifacts/libCoolProp-liquid44.so --label liquid44 --output "$B4A_EVIDENCE/native-liquid44.json"
timeout 120 python3 "$task_b4a/native-focused.py" --library /workspace/b4a-native-artifacts/libCoolProp-liquid44.so --label liquid44-full-vle --full-vle --output "$B4A_EVIDENCE/native-liquid44-full-vle.json"
timeout 120 python3 "$task_b4a/extra-native.py" --library /workspace/b4a-native-artifacts/libCoolProp-control44.so --output "$B4A_EVIDENCE/extra-native-control44.json"
timeout 120 python3 "$task_b4a/extra-native.py" --library /workspace/b4a-native-artifacts/libCoolProp-liquid44.so --output "$B4A_EVIDENCE/extra-native-liquid44.json"
python3 "$task_b4a/fixed-inventory.py"
```

Repeat the native matrix with diagnostic library logging off/on, and on with
`--full-vle`, preserving stderr JSONL. `diagnostic-parity.json` documents equality
after excluding timing fields only. The reference-root and coexistence scripts
use the unmodified wheel's homogeneous DT EOS, never repaired PH or hardcoded
results. Run the unchanged B3 `saturation-reference.py` with
`B3_EVIDENCE="$B4A_EVIDENCE"` for its four displaced-seed roots.

Install Chromium 1234 / WebKit 2336 using Playwright 1.62.0. This Debian runtime
uses WPE WebKit with the exact isolated launcher in `evidence/webkit-launcher.sh`.
Six locally extracted Debian library packages and their SHA256 values are in
`provenance.json`; no host package installation is required. Point the launcher
to the replay browser bundle/sysroot and set:

```bash
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b4a-browsers
export EOS_WEBKIT_EXECUTABLE=/workspace/b4a-webkit.sh
timeout 120 python3 "$task_b4a/run-browser.py" --primary-only
# After both primary gates pass:
timeout 180 python3 "$task_b4a/run-browser.py"
timeout 120 python3 "$task_b4a/analyze.py"
# Only when eligibleForLimitedA2 is true:
timeout 120 python3 "$task_b4a/run-a2.py" --zero-only
timeout 240 python3 "$task_b4a/run-a2.py"
# After the bounded A2 checks:
timeout 120 python3 "$task_b4a/benchmark-native.py" --library /workspace/b4a-native-artifacts/libCoolProp-control44.so --output "$B4A_EVIDENCE/performance-native-control44.json"
timeout 120 python3 "$task_b4a/benchmark-native.py" --library /workspace/b4a-native-artifacts/libCoolProp-liquid44.so --output "$B4A_EVIDENCE/performance-native-liquid44.json"
timeout 180 python3 "$task_b4a/run-browser.py" --performance
```

`capture-stage.py`, `provenance.py` and `final-audit.py` generate source/build and
final ledgers when their documented input files exist. Final audits also require
the preserved original start manifest, independently verified accepted A2 source
hashes, control equivalence and diagnostic parity evidence. Original results
remain authoritative; replay differences must be reported, never normalized.

The hard process deadlines are intentional. Stop unnecessary downstream work
on an unexplained scientific gate failure. The full-VLE 35-bar inverse failures
are explicit in [GATE_SCOPE.md](GATE_SCOPE.md), with unchanged control evidence;
they are never converted into passes. No complete B2/A2 matrix, vapor correction,
physical iPad test, production update, merge or deployment is part of replay.
