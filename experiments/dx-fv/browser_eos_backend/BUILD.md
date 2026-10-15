# Reproduce the controlled backend

Do this in an isolated checkout/runtime. No production workflow is required.
The successful environment is Debian 13 x86_64, Python 3.12.14, CMake 3.31.6,
Ninja 1.11.1.4, Emscripten 4.0.12 (`6f625bd62ee64f4f8cd11476774741b961e4a2d5`),
LLVM clang 22.0.0git (`7f93487862d98bf1c168babba87daf6224d8a46f`).
The SDK release identity is `209b886304498eff50dd835850dc5715803401ed`.
SDK Node is 22.16.0. Host Node is not needed to run the Python browser harness.

## Pinned source and tools

The following are the actual successful paths. Embedded source filenames can
affect binary hashes: bitwise repeatability below is established at these source
and dependency paths, not across arbitrary platforms or relocated source trees.

```bash
git clone --branch v8.0.0 --depth 1 https://github.com/CoolProp/CoolProp.git /workspace/coolprop-b1
git -C /workspace/coolprop-b1 rev-parse HEAD
# MUST equal ae81610e7d23efc57f9d051c8e70a4d66e87537f; otherwise stop.
git clone --branch 4.0.15 --depth 1 https://github.com/emscripten-core/emsdk.git /workspace/emsdk-b1
git -C /workspace/emsdk-b1 rev-parse HEAD
# MUST equal 389a68bc35dcff7ebae4614e1615099dafda00d1; otherwise stop.
/workspace/emsdk-b1/emsdk install 4.0.12
/workspace/emsdk-b1/emsdk activate 4.0.12
python3 -m venv /workspace/b1-runtime/python
/workspace/b1-runtime/python/bin/pip install cmake==3.31.6 ninja==1.11.1.4 CoolProp==8.0.0 numpy==2.3.5
```

Use the commit identities, not a newly resolved moving tag. Archive dependencies
have upstream SHA256 pins. CMake's two named tags resolved to nlohmann/json
`55f93686c01528224f448c19128836e7df245f72` and fmt
`e424e3f2e607da02742f73db84873b8084fc714c`; verify those before compiling.
Other dependency commits and recursive submodule pins are recorded in
`evidence/build-provenance.json`. For a stricter future replay, prefetch each
recorded commit and supply `-DCPM_<Name>_SOURCE=<directory>` rather than resolving
tags again. Do not substitute dependency versions on a failed download.

## Unmodified 30-bit control, then one-expression patch

```bash
/workspace/b1-runtime/python/bin/cmake -S /workspace/coolprop-b1 -B /workspace/b1-runtime/build30 -G Ninja \
 -DCMAKE_TOOLCHAIN_FILE=/workspace/emsdk-b1/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake \
 -DCOOLPROP_JAVASCRIPT_MODULE=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b1-runtime/python/bin/ninja \
 -DPython_EXECUTABLE=/workspace/b1-runtime/python/bin/python \
 -DPYTHON_EXECUTABLE=/workspace/b1-runtime/python/bin/python \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
/workspace/b1-runtime/python/bin/cmake --build /workspace/b1-runtime/build30 --target coolprop -j 2
# Preserve coolprop.js / coolprop.wasm as build30 BEFORE patching.
python3 experiments/dx-fv/browser_eos_backend/make_patch.py /workspace/coolprop-b1
/workspace/b1-runtime/python/bin/cmake --build /workspace/b1-runtime/build30 --target coolprop -j 2
# Preserve these outputs separately as build44; do not replace official assets.
```

`make_patch.py` verifies the complete original flash source SHA256 and the unique
target expression. It writes the reviewed diff and alters only `30` to `44` in
the main bracketed `HSU_P_flash_singlephase_Brent` path. The shared routine serves
H/S/U at fixed P, so this is not an assertion of PH-only effect in every API.
The upstream explanatory comment is deliberately left byte-for-byte unchanged;
its 30-bit description no longer describes the experimental expression. The
supercritical narrow bracket and other flash settings remain at upstream values.
No fluid data, EOS equation, branch logic or solver setting is patched.

Compile flags: `-O3 -DNDEBUG -std=gnu++17`, exception catching enabled,
`COOLPROP_NO_INCBIN`, `VALIJSON_USE_EXCEPTIONS=1`. Link flags are upstream
`-lembind -s ASSERTIONS=1 -s DISABLE_EXCEPTION_CATCHING=0
-sALLOW_MEMORY_GROWTH=1 -s EXPORT_ES6=1 -s MODULARIZE=1`.
There is no fast-math flag. Exact per-file commands, cache and logs are retained.

## Full independent object-directory rebuild

Reconfigure with the same arguments and `-B /workspace/b1-runtime/rebuild44b`,
adding the following source overrides for all dependencies:

```text
CPM_Eigen_SOURCE            /workspace/b1-runtime/build30/_deps/eigen-src
CPM_msgpack-c_SOURCE        /workspace/b1-runtime/build30/_deps/msgpack-c-src
CPM_nlohmann_json_SOURCE    /workspace/b1-runtime/build30/_deps/nlohmann_json-src
CPM_valijson_SOURCE         /workspace/b1-runtime/build30/_deps/valijson-src
CPM_IF97_SOURCE             /workspace/b1-runtime/build30/_deps/if97-src
CPM_REFPROP_headers_SOURCE  /workspace/b1-runtime/build30/_deps/refprop_headers-src
CPM_boost_headers_SOURCE    /workspace/b1-runtime/build30/_deps/boost_headers-src
CPM_multicomplex_SOURCE     /workspace/b1-runtime/build30/_deps/multicomplex-src
CPM_fmt_SOURCE              /workspace/b1-runtime/build30/_deps/fmt-src
```

Pass each as `-DName=value`; compile target `coolprop -j 2`. All 68 translation
units/header-generation steps plus linking were rerun. The resulting JS and WASM
match the initial patched build byte-for-byte. Dependency files and generated
headers were reused, not independently downloaded or regenerated from scratch.
This is a repeated full compilation, not a second-platform reproducibility claim.

An initial replay attempt incorrectly used `FETCHCONTENT_SOURCE_DIR_*`, which
this CPM path did not honor; it attempted network downloads without executor
network access and was interrupted. No result from that attempt is used.

## Measurements

Python Playwright 1.62.1: install Chromium 1234 and WebKit 2336 outside Git.
This Linux runtime uses WPE WebKit with a local dependency launcher; missing
shared libraries were downloaded/extracted under `/workspace/b1-runtime/sysroot`,
without changing the host. `evidence/browser-runtime.json` records the details.
The harness needs loopback socket permission in this executor.

```bash
export PLAYWRIGHT_BROWSERS_PATH=/workspace/b1-runtime/browsers
export EOS_WEBKIT_EXECUTABLE=/workspace/b1-runtime/webkit-local.sh
python3 experiments/dx-fv/browser_eos_backend/run_browser.py
/workspace/b1-runtime/python/bin/python experiments/dx-fv/browser_eos_backend/analyze_precision.py
# Separate CoolProp 7.2.0 + NumPy 2.3.5 venv:
/workspace/b1-runtime/python72/bin/python experiments/dx-fv/browser_eos_backend/analyze_precision.py
python3 experiments/dx-fv/browser_eos_backend/run_supplement.py
python3 experiments/dx-fv/browser_eos_backend/run_synthetic.py
python3 experiments/dx-fv/browser_eos_backend/run_coupled.py
python3 experiments/dx-fv/browser_eos_backend/run_performance.py
/workspace/b1-runtime/python/bin/python experiments/dx-fv/browser_eos_backend/analyze_coupled.py
python3 experiments/dx-fv/browser_eos_backend/package_ipad.py /tmp/ammonia-b1-ipad-new ipad-replay-package.json
python3 experiments/dx-fv/browser_eos_backend/smoke_offline.py /tmp/ammonia-b1-ipad
python3 experiments/dx-fv/browser_eos_backend/audit.py
```

Use a **new output evidence directory or isolated research copy** for replay.
The property/synthetic runners retain completed files. Never delete or overwrite
the committed historical evidence. Coupled runs persist new partial records and
failures; existing files are retained, so inspect incomplete files explicitly.
