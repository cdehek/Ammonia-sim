#!/bin/bash
set -euo pipefail
label=${1:?control or candidate}
task_root=/workspace/Ammonia-sim/experiments/dx-fv/browser_eos_b7
task_work=/workspace/b7-work
export PYTHONPATH=/workspace/b7-tools
source "$task_work/emsdk/emsdk_env.sh"
python3 -B "$task_root/instrument.py" "$label"
timeout 300 /workspace/b7-tools/bin/cmake --build "$task_work/wasm-control" -j 2 > "$task_work/build-wasm-$label-diagnostic.log" 2>&1
mkdir -p "$task_root/vendor/$label-diagnostic"
cp -f "$task_work/wasm-control/coolprop.js" "$task_work/wasm-control/coolprop.wasm" "$task_root/vendor/$label-diagnostic/"
python3 -B "$task_root/instrument.py" "$label" --restore
