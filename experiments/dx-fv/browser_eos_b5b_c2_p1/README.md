# B5B-C2-P1 — validated phase and saturation feasibility

**PARTIAL PHASE CERTIFICATION**

Validated local coexistence roots, saturation-side inequalities across entire
homogeneous root-temperature intervals, and signed mixture qualities are
demonstrated. A generated homogeneous wrong-phase root is excluded by a
validated higher-entropy competitor at the same exact conserved inventory.
Complete stable-equilibrium selection for the primary inventories remains
conditional on an unproved convex-envelope/topology obligation.

This is standalone research, not a runtime implementation, accepted property
state, original scientific qualification, browser qualification or plant trip.

Start: `7c75d9538d57080a01dffbf7e06128a27e2b9ccd`, clean before creating
`research/browser-eos-b5b-c2-p1-phase-certification-20261016`.
The delivery SHA is the commit containing these files, reported by Git and the
delivery response. It cannot be embedded in its own commit.

Read [PROOF_OBLIGATIONS.md](PROOF_OBLIGATIONS.md),
[FORMULATION.md](FORMULATION.md),
[PHASE_CERTIFICATION_MATRIX.md](PHASE_CERTIFICATION_MATRIX.md),
[BRANCH_AND_TOPOLOGY.md](BRANCH_AND_TOPOLOGY.md),
[ENGINEERING_REPORT.md](ENGINEERING_REPORT.md) and
[MECHANICS_REPORT.md](MECHANICS_REPORT.md).
[RUNTIME_AND_ASSUMPTIONS.md](RUNTIME_AND_ASSUMPTIONS.md),
[SCIENTIFIC_CONTRACT_AUDIT.md](SCIENTIFIC_CONTRACT_AUDIT.md) and
[EXECUTION_NOTES.md](EXECUTION_NOTES.md) cover limits and preserved failures.

## Reproduce without overwriting evidence

From the repository root, use Python 3.12 and a virtual environment outside the
repository. No CoolProp source checkout, compilation or installed CoolProp is
needed. Install only `python-flint==0.8.0` and `mpmath==1.3.0` from
`requirements.txt`. The measured FLINT version is 3.3.1.

```
python -m venv /tmp/ammonia-p1-replay
/tmp/ammonia-p1-replay/bin/pip install -r experiments/dx-fv/browser_eos_b5b_c2_p1/requirements.txt
export PYTHONDONTWRITEBYTECODE=1
export P1_EVIDENCE="$PWD/experiments/dx-fv/browser_eos_b5b_c2_p1/evidence/reproduction-new"
/tmp/ammonia-p1-replay/bin/python experiments/dx-fv/browser_eos_b5b_c2_p1/run.py
/tmp/ammonia-p1-replay/bin/python experiments/dx-fv/browser_eos_b5b_c2_p1/verify.py
```

Choose a fresh output directory; `run.py` refuses to replace an attempts log.
Reproduction adds files only below P1, so it intentionally makes the worktree
untracked there. Do final clean-tree verification before reproducing or in a
separate checkout. `summarize.py` generated the delivered review matrix and
contract comparisons; it is not needed to validate fresh numerical evidence.
All attempts have 20-second deadlines; no precision above 256 bits is used for
validated arithmetic. mpmath uses 65/90 digits for diagnostics, 105 for audits.

## Evidence map

- `starting-files-sha256.json`, `checkpoint.json`, `remote-refs-before.tsv`,
  `inherited-identities.json`: Phase 0 preservation and arithmetic availability.
- `c2-reproduction.json`: all nine original exact inputs and 192/256-bit local
  proofs, with the corrected exact-M/U/V versus rounded-DU distinction.
- `inputs.json`, `results.json`, `attempts.jsonl`: 17 cases, exact hexadecimal
  input identities, diagnostic proposals, full residual/Jacobian/Krawczyk
  enclosures and individual failures. Rational endpoints are authoritative.
- `verification.json`: independent derivatives, corner checks, higher-precision
  revalidation of old boxes, negative controls and entropy comparison.
- `phase-matrix.json`: separate inventory/root/pressure/coexistence/side/quality/
  competing-phase/scientific/browser fields. Zero complete physical certificates.
- `scientific-contract-audit.json`, `performance-summary.json`, `runtime.json`:
  unchanged numerical limits, bounded timings and artifact assumptions.
- `initial-run/`: preserved earlier execution and failed nesting expectation.
- `preservation.json`, `delivery-manifest-sha256.json`: final prepush byte audit.

## Exact preservation and post-push verification

Fetch no new CoolProp source and modify no protected ref. From a clean delivery
checkout, record current remote refs read-only and run:

```
git rev-parse HEAD
git status --porcelain=v1
git ls-remote origin > /tmp/ammonia-p1-remote-after.tsv
PYTHONDONTWRITEBYTECODE=1 python experiments/dx-fv/browser_eos_b5b_c2_p1/preserve.py --remote-refs /tmp/ammonia-p1-remote-after.tsv --require-clean
git diff --name-status 7c75d9538d57080a01dffbf7e06128a27e2b9ccd HEAD
```

This audit uses only the Python standard library. It checks 1,996 starting files,
143 artifacts, five patches, 12 accepted A2 snapshots, exact engine identity,
all 31 protected remote entries including PR #3, and only additive P1 changes.
The only permitted new remote ref must equal HEAD. `--receipt` was used before
commit to save receipts; omit it after push to leave the tree clean. Check that
the delivery commit has the exact starting checkpoint as its parent and that
every changed path is an addition below this P1 directory. No merge/deployment.

Stop for explicit engineering review. Recommend parking broader certification
until a narrow independently reviewed topology dependency exists, and prioritize
the separate rejected-PT loader repair under its own authorization. No next
milestone is started by this delivery.
