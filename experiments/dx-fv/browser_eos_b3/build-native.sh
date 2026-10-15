#!/bin/bash
# Run after the documented pinned source/dependency configure and baseline build.
set -euo pipefail
task_repo=/workspace/Ammonia-sim
task_source=/workspace/coolprop-b3
task_build=/workspace/b3-build
task_python=/workspace/b3-runtime/bin/python
task_b3="$task_repo/experiments/dx-fv/browser_eos_b3"
task_evidence="${B3_EVIDENCE:-$task_b3/evidence}"
task_artifacts=/workspace/b3-native-artifacts
mkdir -p "$task_artifacts"
for task_bits in 30 44; do
 if [ "$task_bits" = 44 ]; then
  git -C "$task_source" restore src/Backends/Helmholtz/FlashRoutines.cpp src/Backends/Helmholtz/HelmholtzEOSMixtureBackend.cpp src/Solvers.cpp
  git -C "$task_source" apply "$task_repo/experiments/dx-fv/browser_eos_backend/flash-44.patch"
  timeout 600 /workspace/b3-runtime/bin/cmake --build "$task_build" -j 2 > "$task_evidence/build44.log" 2>&1
 fi
 cp -f "$task_build/libCoolProp.so" "$task_artifacts/libCoolProp$task_bits.so"
 if [ ! -f "$task_evidence/native-source$task_bits.json" ]; then
  timeout 120 "$task_python" "$task_b3/native.py" --library "$task_artifacts/libCoolProp$task_bits.so" --label "source$task_bits" --output "$task_evidence/native-source$task_bits.json" 2> "$task_evidence/source$task_bits-inputs.jsonl"
 fi
 "$task_python" "$task_b3/instrument.py" "$task_source"
 timeout 600 /workspace/b3-runtime/bin/cmake --build "$task_build" -j 2 > "$task_evidence/build-diag$task_bits.log" 2>&1
 cp -f "$task_build/libCoolProp.so" "$task_artifacts/libCoolProp-diag$task_bits.so"
 timeout 120 env B3_TRACE=1 "$task_python" "$task_b3/native.py" --library "$task_artifacts/libCoolProp-diag$task_bits.so" --label "diag$task_bits" --output "$task_evidence/native-diag$task_bits.json" 2> "$task_evidence/trace$task_bits.jsonl"
 timeout 120 env B3_TRACE=1 "$task_python" "$task_b3/trace-probes.py" --library "$task_artifacts/libCoolProp-diag$task_bits.so" --output "$task_evidence/probes-diag$task_bits.json" 2> "$task_evidence/probes-trace$task_bits.jsonl"
 timeout 120 env B3_TRACE=1 "$task_python" "$task_b3/trace-probes.py" --library "$task_artifacts/libCoolProp-diag$task_bits.so" --disable-superanc --output "$task_evidence/probes-no-superanc$task_bits.json" 2> "$task_evidence/no-superanc-trace$task_bits.jsonl"
done
