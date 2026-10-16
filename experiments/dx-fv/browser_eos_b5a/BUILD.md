# Reproduction, identities and bounded execution

Run from the repository root. Never overwrite committed evidence. Create a new
output directory and use `B5_EVIDENCE` for inherited B5 scripts and
`B5A_EVIDENCE` for new scripts. External workspace paths below match this run.
Library names are experimental identities, not production selections.

## Source and control

Use the exact upstream source and four immutable patches in B5 BUILD.md.
Reconstruction must pass `browser_eos_b5/audit-start.py` against all 1,782
inherited source hashes, 137 artifacts and twelve accepted A2 snapshots.
All nine dependency digests must match `evidence/dependency-verification.json`.

Install isolated CoolProp 8.0.0, CMake 4.4.4, Ninja 1.13.2, NumPy and mpmath.
Set `PYTHONPATH=/workspace/b5-tools`, including when running installed CMake.
This run used mpmath 1.4.1; the exact stored 65-digit B5 references reproduced,
and independent 90-digit repeat checks passed. Coefficients remain exact
binary64 values lifted into arbitrary precision; these are mathematical EOS
references, not experimental accuracy claims.

Extract the archived B4C and B4B libraries into `/workspace/b5-libs/candidateB.so`
and `controlA.so`, respectively. Extract B5's diagnostic library into
`/workspace/b5-libs/diagnostic-final.so`. Verify compressed/decompressed SHA256
against the original native manifests before loading them. Configure and build:

```bash
PYTHONPATH=/workspace/b5-tools timeout 240 /workspace/b5-tools/bin/cmake \
 -S /workspace/coolprop-b5 -B /workspace/b5-native-build -G Ninja \
 -DCOOLPROP_SHARED_LIBRARY=ON -DCOOLPROP_EXTERNC_LIBRARY=ON \
 -DCMAKE_BUILD_TYPE=Release -DCMAKE_MAKE_PROGRAM=/workspace/b5-tools/bin/ninja \
 -DPython_EXECUTABLE=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
PYTHONPATH=/workspace/b5-tools timeout 900 /workspace/b5-tools/bin/cmake \
 --build /workspace/b5-native-build -j 2
cp /workspace/b5-native-build/libCoolProp.so.8.0.0 /workspace/b5-libs/rebuilt-control.so
```

Retain partial logs on timeout; do not turn a build attempt into a scientific
pass. Only resume an unchanged incremental build under a further explicit
bound, recording that attempt separately. Use the actual delivered run logs
and engineering report for whether such a resume was needed.

## Preserve and reproduce first

Use the inherited B5 replay with a fresh `B5_EVIDENCE` directory (120 seconds).
It extracts the original 250 records and bits, never reruns PH to replace them.
Run its trace-replay against the archived diagnostic with `B5_TRACE=1` and
against the rebuilt control (120 seconds each). Compare every fresh/reused result
and all seven original failures. Current original reproduction and traces are
in this milestone's evidence, not merely inherited counts.

Run B5 `references.py` (180 seconds), `high-precision.py` (240 seconds), and
`precision-audit.py` (240 seconds), supplying `original-failures.json` from B5
for the last script. The independent functions use fixed-rho/u homogeneous
roots and p/g/mixture-energy coexistence equations. They are never backend inputs.

## Gate A only

Read ALGORITHM_A.md and its committed pre-edit receipt before applying source:

```bash
python3 experiments/dx-fv/browser_eos_b5a/apply-gate-a.py /workspace/coolprop-b5
PYTHONPATH=/workspace/b5-tools timeout 300 /workspace/b5-tools/bin/cmake \
 --build /workspace/b5-native-build -j 2
cp /workspace/b5-native-build/libCoolProp.so.8.0.0 /workspace/b5-libs/A1.so
```

The application script requires the exact inherited source manifest and creates
`gate-a.patch` relative to B4C. Its pre-edit design commit is recorded in the
engineering report. No Gate B patch is implied by this application.

Seed a fresh B5A output directory with `fixed-inputs.json`, the independent
references, high-precision references and `original-failures.json`. Export
`B5A_EVIDENCE` to it; use the same path as `B5_EVIDENCE` when inherited scripts
need these inputs. New scientific writers refuse existing outputs.

```bash
timeout 120 python3 experiments/dx-fv/browser_eos_b5a/compare.py \
 --library /workspace/b5-libs/candidateB.so --label control
timeout 120 python3 experiments/dx-fv/browser_eos_b5a/compare.py \
 --library /workspace/b5-libs/A1.so --label A1
```

Each compares all 250 historical rows and all 73 unique pairs on both recovery
paths. It separately records originating-PH canonical differences, fixed-inventory
reference differences, fresh-EOS closure and actual strict pressure-side results.

For diagnostic A1, run B5A `instrument.py` (inherited B5 logging plus cached density getters) with `B5_EVIDENCE` set
to the fresh output directory; it stores original translation units and a
logging-only patch. Build with a 300-second bound, preserve as
`/workspace/b5-libs/A1-diagnostic.so`, and run B5 `trace-replay.py` on/off plus
uninstrumented A1 (120 seconds each) into the filenames used in delivered
`evidence/`. Restore the three saved original translation units afterward and
verify `source-stage-A1.json`. No generic solver termination is changed.
Run `gate-a-audit.py` (120 seconds) using `A1-trace-on.jsonl` and
`A1-comparison.json`. Review that gate independently before Gate B work.

## Focused regressions and remaining cases

Run the unchanged B4B `native-focused.py` against control and A1, normally and
with `--full-vle`, under 120-second bounds. The original B4A input file controls
all 86 base inputs and 344 signed probes. B4C `scientific-audit.py --native-only`
consumes default outputs named `native-controlA.json` and
`native-candidateB.json` in `B4C_EVIDENCE`. Its original assertions stay unchanged.
Run B4B lifecycle, B4C PH/PS/PU shared callers (both paths), and B4C cache audit
with their original library/output options, 120 seconds each.

New `shared-density.py` compares DH/DS/DP shared callers (120 seconds).
`regression-audit.py` compares every newly rerun regression with B4C;
`additional-eos-audit.py` applies fresh-EOS closure to the separate inventories.
`additional.py` retains all 21 saved B5 independent-PH inventories and solves
independent references for them (180 seconds). These are separate identities,
not additions to or replacements for the historical fixed-input ledger.

Stop downstream qualification if essential B5A scientific gates remain unresolved.
Do not use a raw returned endpoint or an exception change as physical acceptance.
Only if the gates pass may the limited accepted A2 browser fixtures proceed.
No complete B2/A2 campaign, browser support-policy edit, loader repair, production
selection or deployment is part of these commands.

After compilers and science finish, run `benchmark.py` serially (60 seconds),
using the two matched native libraries. It records five 150 ms rounds per
workload/path/build and counts errors separately. Native initialization/RSS are
not WASM linear-memory or physical iPad measurements. Native trace counts are
not browser internal iteration counts.
