# B5B-C2 reproduction and evidence index

Assessment: **CONDITIONALLY FEASIBLE**. Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md),
[FORMULATION.md](FORMULATION.md), [STRATEGIES.md](STRATEGIES.md),
[RUNTIME_AND_INTERFACE.md](RUNTIME_AND_INTERFACE.md), [MATRIX.md](MATRIX.md)
and [MECHANICS_REPORT.md](MECHANICS_REPORT.md).

Start: `7809d08be67eab7cb9b537b1c1199b456b2da122`.
Only delivery branch:
`research/browser-eos-b5b-c2-inventory-certification-feasibility-20261016`.
The delivery commit SHA is `git rev-parse HEAD` and the delivery response.
No C3, merge, deployment or runtime integration is authorized or performed.

## Bounded reproduction

Use a disposable checkout and a **fresh** output directory. Scripts refuse to
overwrite research evidence. No full A2 campaign or CoolProp build is needed.
Python 3.12, mpmath 1.3.0, python-flint 0.8.0 (FLINT 3.3.1), Playwright 1.62.0,
Chromium 154 and desktop WPE WebKit 26.5 were used. Native libraries are the
preserved archives, decompressed and digest-checked by the imported C1 Native
class into `/workspace/c2-native`. The actual native library identities are in
`evidence/native.json`. There is no CoolProp wheel dependency.

Install diagnostic arithmetic outside the repository:

```sh
python -m pip install --target /workspace/c2-deps python-flint==0.8.0
PLAYWRIGHT_BROWSERS_PATH=/workspace/c2-browsers python -m playwright install webkit
```

The host required the exact six Debian archives listed in the historical
`../browser_eos_b5/evidence/browser-libraries.json`. Fetch through the configured
proxy, verify each SHA256, extract with `dpkg-deb -x` into a disposable directory,
and copy `usr/lib/x86_64-linux-gnu/*.so*` into WebKit's
`minibrowser-wpe/sys/lib`. C2's `browser-setup.json` records those same digests.
Do not modify loaders or repository assets. Browser launch is bounded at 30 s;
the outer timeout bounds synchronous browser evaluation. Loopback/child-process
network access may need the execution tool's additional network permission.

The inherited B5 evaluator reads
`/workspace/coolprop-b5/dev/fluids/Ammonia.json`. Its bytes must match C2's
preserved `evidence/Ammonia.json` and SHA256
`4d451fadbe6eb1c2441169c599890cf7cd6edc818918f23959e2afb20a881e14`.
If that external setup path does not exist, create its parent directories and
symlink it to the preserved C2 JSON. Do not overwrite a pre-existing source tree.
No evaluator equation is changed to accommodate the path.

From repository root, with a new empty output directory:

```sh
export PYTHONPATH=/workspace/c2-deps
export C2_EVIDENCE=/tmp/c2-reproduction
mkdir "$C2_EVIDENCE"
timeout 150 python experiments/dx-fv/browser_eos_b5b_c2/replay.py
C2_ORIGINS_ONLY=1 timeout 90 python experiments/dx-fv/browser_eos_b5b_c2/replay.py
timeout 60 python experiments/dx-fv/browser_eos_b5b_c2/native.py
timeout 300 python experiments/dx-fv/browser_eos_b5b_c2/reference.py
timeout 90 python experiments/dx-fv/browser_eos_b5b_c2/supplement.py
timeout 90 python experiments/dx-fv/browser_eos_b5b_c2/local_enclosure.py
timeout 45 python experiments/dx-fv/browser_eos_b5b_c2/verify_numerics.py
timeout 45 python experiments/dx-fv/browser_eos_b5b_c2/analyze.py
timeout 30 python experiments/dx-fv/browser_eos_b5b_c2/scientific_audit.py
```

Use `C2_ENGINES`, `CHROMIUM_PATH` and `WEBKIT_PATH` to select installed engines;
the full delivered evidence uses both. Reference/analyzer currently uses the
Chromium raw coordinates and separately preserves both engines' observations.
Native results are not substituted for browser results. Each original inventory
comes from authoritative hexadecimal bits, never rounded decimal displays.

To call the local diagnostic at a supplied exact inventory, create a JSON file
with only hexadecimal `M`, `V`, `U_kJ` fields. For example, extract those fields
from any delivered `matrix.json` row programmatically. Supply a proposed decimal
or rational temperature center:

```sh
PYTHONPATH=/workspace/c2-deps python experiments/dx-fv/browser_eos_b5b_c2/local_enclosure.py \
  --inventory /tmp/inventory-bits.json --seed 345.56367343079841661977999199115
```

The seed is not trusted. Opposing enclosed endpoint signs must independently
validate a root. This CLI returns local interval evidence with complete status
UNRESOLVED, or NUMERICAL_FAILURE. It never supplies an accepted property state.
The default trial radius is `1e-30 K`; `--radius` changes a proposed bracket,
not support or scientific tolerances. A poor bracket can fail or straddle the
pressure boundary. Ordinary high-precision references remain explicitly
HIGH_PRECISION_DIAGNOSTIC.

## Evidence index

| Evidence | Role |
|---|---|
| `historical-file-hashes.json`, `baseline.json`, `refs-before.txt` | Exact checkpoint, all historical bytes/artifacts/A2 snapshots and protected refs |
| `source-verification.json`, `upstream-*`, `Ammonia.json` | Independent 1,782-file inherited-patch reconstruction receipt and pinned mathematical/source data |
| `chromium-replay.json`, `webkit-replay.json` | Actual nine primary, 24 PH diagnostic and four endpoint browser operations, every raw getter bit and adapter outcome |
| `*-origins.json` | Actual PH origin replay and exact conserved construction for both inward hazards |
| `native.json` | Actual archived B4C comparisons and unresolved Gate A endpoint control outcomes |
| `references.json` | 65/90-digit exact-M/U/V and rounded-DU roots, 90-digit internal molar roots, homogeneous/coexistence alternatives, stability and conditioning |
| `equilibrium-supplement.json` | Independent endpoint derivatives and applicable physical-equation replay of retained B5-sweep-19 initial diagnostic failure |
| `inventory-arithmetic.json` | Every original arithmetic stage, rational errors, stored rationals, original PH and internal molar bits |
| `local-enclosures.json` | 192/256-bit validated local homogeneous root/pressure/cv bounds; complete status unresolved |
| `numerical-verification.json` | Independent implementation comparisons and bad-seed/invalid-input/straddling/metastable adversaries |
| `matrix.json` | Complete joined per-case exact bits, actual outcomes, three mathematical targets, local enclosures and original qualification scope |
| `performance.json`, run logs | Actual diagnostic costs, exclusions and retained attempts |
| `scientific-audit.json` | All 37 original standalone numerical budgets, pressure repetition and explicit unqualified phase/backend scope |
| `initial-analysis/` | Earlier evidence join before supplement residual was added; retained rather than overwritten |
| `decisions.json`, `runtime-environment.json` | Gate decisions, classification, versions and arithmetic artifact identities |
| `source-manifest.json`, `final-preservation.json`, `refs-after.txt` | New-file integrity and final historical/protected-ref audit |

The baseline receipt uses inherited source verification for its original scope;
the later source-verification receipt independently reconstructs all five patches.
No source dependency build is claimed. For audit reproduction, stage only C2
additions, capture fresh remote heads and PR #3 refs into C2 `refs-after.txt`,
then run `audit.py`. That audit intentionally writes C2 receipts; run it in a
disposable checkout to preserve delivery evidence. Final post-push verification
is performed externally to avoid a commit hash referring to itself.

All scientific limits, support bounds, signed differences, conservation,
phase/Newton/TR-BDF2 requirements, strict refusal and rollback remain unchanged.
Desktop WebKit is not physical iPad evidence. Full certification/qualification
and unrelated blockers remain open.
