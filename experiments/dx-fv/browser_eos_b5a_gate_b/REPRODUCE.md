# Focused reproduction

Use an isolated checkout of the delivery commit. Do not overwrite committed
evidence. No CoolProp/WASM compilation or A2/B2 campaign is needed.

Runtime used: Linux x86_64/glibc 2.41, Python 3.12.14; exact mpmath/NumPy versions
are in mathematical-references/binary64-results JSON. CoolProp is unmodified
8.0.0, with wheel Git identity and binary hashes in `supplement.json`. The native
Gate A archives and their identities remain in B5A's original artifact manifest.
No fast-math setting is introduced. Timing samples are host-specific.

1. Reconstruct pinned upstream source only for verification and EOS coefficients,
   following B5 BUILD.md: clone CoolProp v8.0.0, require commit
   `ae81610e7d23efc57f9d051c8e70a4d66e87537f` at `/workspace/coolprop-b5`, apply
   the four inherited B1/B4 patches and then the existing B5A `gate-a.patch`.
   Do not make any new source edits. Do not run apply-gate-a.py (it is a historical
   patch-generation workflow); apply the already committed patch directly.
2. Install `CoolProp==8.0.0`, NumPy and mpmath into isolated tools. This run used
   `/workspace/b5-tools` for the wheel and NumPy, and the supplied Python mpmath.
3. Set a fresh absolute evidence path and run the audit before loading archives:

```bash
export PYTHONPATH=/workspace/b5-tools
export GATE_B_EVIDENCE=/tmp/ammonia-gate-b-repeat
mkdir -p "$GATE_B_EVIDENCE"
timeout 90 python experiments/dx-fv/browser_eos_b5a_gate_b/audit_start.py
```

The audit extracts verified libraries to `/workspace/gate-b-libs/`. It verifies
1,782 Gate A source hashes, all five patches, 143 artifact identities, 12 accepted
A2 Git snapshots, and extracts the exact seven saved inventory bits. Full
dependency trees are unnecessary for this archive replay and are not reverified.

4. Replay just the seven original cases using the inherited harness:

```bash
export B5_EVIDENCE="$GATE_B_EVIDENCE"
timeout 90 python experiments/dx-fv/browser_eos_b5/trace-replay.py \
 --library /workspace/gate-b-libs/A1.so \
 --output "$GATE_B_EVIDENCE/native-results.json" \
 > "$GATE_B_EVIDENCE/native.log" 2> "$GATE_B_EVIDENCE/native-markers.jsonl"
B5_TRACE=1 timeout 90 python experiments/dx-fv/browser_eos_b5/trace-replay.py \
 --library /workspace/gate-b-libs/A1-diagnostic.so \
 --output "$GATE_B_EVIDENCE/native-trace-results.json" \
 > "$GATE_B_EVIDENCE/native-trace.log" 2> "$GATE_B_EVIDENCE/native-trace.jsonl"
```

5. Run the standalone research sequentially, retaining logs and any partial
   output on timeout. From repository root:

```bash
timeout 240 python experiments/dx-fv/browser_eos_b5a_gate_b/math_reference.py
timeout 120 python experiments/dx-fv/browser_eos_b5a_gate_b/binary64.py
timeout 180 python experiments/dx-fv/browser_eos_b5a_gate_b/native_analysis.py
timeout 90 python experiments/dx-fv/browser_eos_b5a_gate_b/bracketing.py
timeout 30 python experiments/dx-fv/browser_eos_b5a_gate_b/supplement.py
```

`math_reference.py` writes exact cases and 65/90-digit references before displaced
seed tests; each solve has a 14-iteration bound. Binary64 has a 20-iteration bound
and keeps all stagnant/invalid algebraic results. Homogeneous candidates use a
12-iteration bound. Native reused state is compared with fresh state on every
case. These bounded diagnostic policies do not change accepted solver settings.

The delivered initial grid was corrected to avoid state-coordinate normalization
round trips. Fresh reproductions generate the corrected grid directly; the
initial grid is a retained historical attempt, not a required second experiment.
`supplement.py` provides the scripted separate-process binary64 repeat; the
additional delivered `binary64-repeat.json` is an earlier equivalent replay.

6. Run the scientific evidence audit against the fresh output path. It verifies
   the generated neighboring-state report matches the committed NEIGHBORS.md
   without rewriting it. A difference fails the audit and requires investigation.

```bash
timeout 45 python experiments/dx-fv/browser_eos_b5a_gate_b/scientific_audit.py
```

An audit PASS checks research integrity; it explicitly reports
`backendQualified:false`. Remote/preservation auditing belongs to the delivery
workflow and requires network access; do not push or move protected branches
during reproduction. Full A2/B2, browser candidate builds, B5B policy, loader
cleanup, plant integration and deployment are outside this reproduction.
