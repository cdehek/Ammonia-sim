# Static two-patch research — unqualified, construction rejected

Read [the full report](../GIBBS_TWO_PATCH_FEASIBILITY.md) and
[Mechanic's Report](MECHANICS_REPORT.md). These tools are not imported by any
accepted solver. They use 16 liquid knots and their six saturation rows only.

## Reproduction

Python 3.12.14; exact installed packages are pinned in `requirements.txt`.
Create a venv outside the repository and install those requirements. Set
`OPENBLAS_NUM_THREADS=1` for the recorded deterministic numerical configuration.

To check the **existing frozen candidate**, from the repository root:

```bash
python experiments/dx-fv/two_patch/certify.py
python experiments/dx-fv/two_patch/audit.py
python experiments/dx-fv/two_patch/supplement.py
```

These overwrite only this experiment's generated audit/certificate/supplement
files, never coefficients, samples or old research. Use a disposable checkout
if byte-identical delivered evidence must also be retained. An evidence-audit
pass explicitly retains scientific rejection.

To reproduce the fit without replacing frozen coefficients:

```bash
python experiments/dx-fv/two_patch/fit.py /tmp/ammonia-two-patch-refit
```

Compare the `coefficients`, `saturationCoefficients`,
`vaporEntropyCoefficients`, `pc`, `ps`, `tc`, `ts`, `rows`, `zmax` fields per patch
against the committed `evidence/candidate.json`. Those fields were bit-identical
in the recorded replay. Whole-file hashes differ because timings are recorded.
The fitter imports no CoolProp and does not read any EOS evidence.

For a complete independent fit/freeze/EOS replay, use a **disposable clone on
the delivered research branch**. Keep its original `evidence` directory as an
external baseline copy. Preserve `evidence/provenance.json` in place; move the
other generated files out of the clone's evidence directory, then run:

```bash
python experiments/dx-fv/two_patch/fit.py
python experiments/dx-fv/two_patch/certify.py
python experiments/dx-fv/two_patch/validate.py
python experiments/dx-fv/two_patch/supplement.py
python experiments/dx-fv/two_patch/audit.py
```

`validate.py` refuses to overwrite an existing `validation.json`. It freezes
candidate and code hashes **before importing EOS**. No previous EOS result is
used by `fit.py`. The low fit's `optimal_inaccurate` warning is expected and
retained; scientific feasibility is checked independently. `audit.py` requires
the isolated branch, exact WIP ancestry, and the protected remote refs from the
recorded repository. It checks all 215 old file hashes without modifying them.
Do not edit historical audit guards to make earlier research appear qualified.

## Scripts

- `fit.py`: source-only convex constrained fit; explicit physical Hessian.
- `model.py`: frozen polynomial evaluation, boundary trace and local recovery.
- `certify.py`: exact rational Bernstein bounds, physical cover, margins.
- `validate.py`: first frozen holdout EOS comparisons, probes, uncertainty, costs.
- `audit.py`: independent exact source intervals, high-precision recovery,
  rejection witnesses, coefficient/provenance checks and roundtrips.
- `supplement.py`: high-precision numerical differentiation, domain checks,
  static recovery timings; no EOS or fitting.

## Evidence map

| File | What it preserves |
| --- | --- |
| `provenance.json` | Identity, base, protected refs, 215 original file SHA-256s, archive availability |
| `candidate.json`, `candidate.sha256` | First fitted coefficients, source hash, optimizer statuses, constraints and runtimes |
| `freeze.json` | Pre-EOS candidate/code hashes, holdout design and unchanged gates |
| `certificate.json` | Exact-rational between-node bounds, failed coarse enclosure, successful covers and margins |
| `first-certificate.log` | First curved-domain certificate output, before final conservative arithmetic refinements |
| `knots.json` | Every knot adjustment, source-vs-EOS check and high-precision evaluation difference |
| `exact-interval-audit.json` | Independent rational verification against exact decimal source-rounding intervals |
| `holdouts.json` | All 264 PT comparisons, M/U/V recoveries and failures |
| `saturation.json` | 82 boundary comparisons, Gibbs/latent/Clapeyron identities and vapor errors |
| `continuity.json` | Two-sided pressure and offset interface evidence |
| `probes.json` | Original three-root inventory, matching EOS inventory and both saved high PH states |
| `saved-inventory-audit.json` | Independent high-precision recovery of original high-pressure inventories |
| `numerical-uncertainty.json` | Independent EOS input-pair checks and high-precision candidate evaluation/recovery |
| `failed-recovery-audit.json` | All 56 failures checked against monotone canonical-image endpoint ranges |
| `roundtrip-audit.json` | 30 same-candidate PH/canonical roundtrips; not a uniqueness proof |
| `rejection-witnesses.json` | Independent fixed-M/U/V pressure failures at 65 digits |
| `performance.json` | Five evaluation timing rounds, coefficient bytes and validation peak RSS |
| `supplement.json` | Independent derivatives, eight domain rejections, five recovery timing rounds |
| `validation.json`, `first-validation.log` | First holdout summary and scientific rejection |
| `fit-replay.json`, `fit-replay.log` | Bit-identical mathematical coefficients and retained low optimizer warning |
| `audit.json` | Evidence audit pass, explicitly unqualified scientific status |
| `delivery-verification.json` | Final scoped-file, syntax, protected-ref and preservation verification |

No datasets or earlier evidence were regenerated in place. This folder contains
only new experiment evidence. Numeric timestamps/costs describe this machine,
not a repeatability promise for timings or a browser benchmark.
