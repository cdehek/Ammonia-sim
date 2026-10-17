#!/bin/bash
# External build output only. Call with control or candidate after source audits.
set -euo pipefail
label=${1:?control or candidate}; task_root=/workspace/Ammonia-sim/experiments/dx-fv/browser_eos_b7
task_work=/workspace/b7-work
case "$label" in control|candidate) task_source=$task_work/upstream;; *) exit 2;; esac
export PYTHONPATH=/workspace/b7-tools
source "$task_work/emsdk/emsdk_env.sh"
# Reuse unchanged object files in one build tree. The independently verified
# three-file source transition is performed explicitly before candidate build.
task_build=$task_work/wasm-control
task_deps=$task_work/dependency-config/_deps
timeout 240 /workspace/b7-tools/bin/cmake -S "$task_source" -B "$task_build" -G Ninja \
 -DCOOLPROP_JAVASCRIPT_MODULE=ON -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_MAKE_PROGRAM=/workspace/b7-tools/bin/ninja \
 -DPython_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
 -DCMAKE_TOOLCHAIN_FILE="$task_work/emsdk/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake" \
 -DCPM_Eigen_SOURCE="$task_deps/eigen-src" \
 -DCPM_msgpack-c_SOURCE="$task_deps/msgpack-c-src" \
 -DCPM_nlohmann_json_SOURCE="$task_deps/nlohmann_json-src" \
 -DCPM_valijson_SOURCE="$task_deps/valijson-src" \
 -DCPM_IF97_SOURCE="$task_deps/if97-src" \
 -DCPM_REFPROP_headers_SOURCE="$task_deps/refprop_headers-src" \
 -DCPM_boost_headers_SOURCE="$task_deps/boost_headers-src" \
 -DCPM_multicomplex_SOURCE="$task_deps/multicomplex-src" \
 -DCPM_fmt_SOURCE="$task_deps/fmt-src" > "$task_work/configure-wasm-$label.log" 2>&1
cp -f "$task_build/CMakeCache.txt" "$task_root/evidence/$label-CMakeCache.txt"
cp -f "$task_build/compile_commands.json" "$task_root/evidence/$label-compile_commands.json"
timeout 900 /workspace/b7-tools/bin/cmake --build "$task_build" -j 2 > "$task_work/build-wasm-$label.log" 2>&1
mkdir -p "$task_root/vendor/$label"
cp -f "$task_build/coolprop.js" "$task_build/coolprop.wasm" "$task_root/vendor/$label/"
