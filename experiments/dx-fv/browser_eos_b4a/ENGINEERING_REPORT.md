# B4A — controlled liquid phase-classification repair

**Final assessment: FOCUSED REPAIR PASS.** The original liquid classification
defect is corrected, original budgets pass in the focused supported cases, and
no relevant new regression is observed. **Full backend qualification remains
pending.** Preserved inverse/support failures are not passing results.

Branch: `research/browser-eos-b4a-liquid-phase-repair-20261015`.
The full delivery SHA is supplied in the final handoff; it identifies the commit
containing this report. Start: exactly
`4e1295be9493d8bce4ca35ee0cf61accb7465226`, clean tracked checkout of B3.
Execution took place October 15–16 UTC, 2026. No merge or deployment.

## Checkpoints, preservation and evidence review

B3's engineering report, repair proposals and mechanic's report, B2's exact
liquid counterexample and B1's build/precision/solver contract were reviewed
before source modification. B3 captured native decisions are the primary causal
evidence; the complete B2 campaign was not rerun. Fresh source44 controls match
all 57 historical B3 native PH, DT and PH-derived-inventory results exactly.
Fresh WASM controls match all 57 base and 228 probe records in both browsers.

All **939 starting tracked files** retain SHA256, including official 8.0,
source30, historical source44, official 7.2, B1/B2/B3 evidence and native archives.
All twelve accepted A2 source snapshots match Git objects at the exact accepted
checkpoint. All nine dependency trees match B3's content digests. Original
native archive/compressed and browser artifact hashes were verified before work.

| Preserved checkpoint | Full SHA |
|---|---|
| Accepted five-section A2 | `be9eb35a4ddf5098e685182f8104685127c6a6ee` |
| B1 precision backend | `ef1562ae1680fccf3323391e9ec83788c5ae1e69` |
| B2 blocked qualification | `6a220dd6c94bff08e00e0107cfec71854166ede2` |
| B3 confirmed root cause | `4e1295be9493d8bce4ca35ee0cf61accb7465226` |
| Operator Workstation UI | `262b6092b2ed694073ad9ffd41265f44dd0b6ca0` |

Production main, PR #3, accepted research, UI, release candidates and hosting are
untouched. Only additive B4A research files are committed.

## Algorithm and source review

[ALGORITHM.md](ALGORITHM.md) was recorded before editing CoolProp. At subcritical
P, a negative caloric quality selects the existing bounded homogeneous liquid
inversion instead of the equilibrium lever equation. This is based on the
independently stable liquid root and caloric position below saturation, not an
arbitrary imposed phase. The original requested P and H/S/U are passed through;
the existing solver determines T/rho and propagates failure. No property is
clamped, substituted or polished for the model.

The patch changes only two conditions in
`HelmholtzEOSMixtureBackend::p_phase_determination_pure_or_pseudopure`:

```cpp
if (Q < -1e-9 || (Q < 0 && (other == iHmolar || other == iSmolar || other == iUmolar))) {
    // existing liquid dispatch, unchanged
}
```

Both the superancillary and full-VLE paths are addressed. The former retains
its cache clearing and Tsat bound; the latter retains saturation_called and its
computed liquid endpoint. `HSU_P_flash` then calls the original bounded flash.
Its stable liquid temperature domain, melting/minimum limits, phase checks,
range checks and failure behavior remain. B1's 44-bit outer stopping expression
is preserved byte-for-byte. EOS, fluid data, reference convention, equilibrium
equations, support limits, density flash, DU, Newton and TR-BDF2 are unchanged.

This is not a blind all-caller zero-threshold replacement. Before editing,
both endpoints and their plus/minus-one-ULP h neighbors were independently
examined at all four pressures: all 24 homogeneous diagnostic roots converged
within B3's 1e-5 Pa / 1e-8 J/kg limits. Returned PQ h round-trips to molar h
without difference in the tested native runtime. Very close inputs can be
unresolved at the independent reference resolution; the new rule resolves a
negative difference using the bounded inversion instead of treating uncertainty
as physical vapor volume. A numerically unsuccessful inversion is exposed.
The 24 exact/ULP endpoint cases are also retained in the post-build matrix.

Q=0 and 0<Q<1 preserve the original equilibrium calculation; Q=1 preserves the
vapor endpoint. Stable superheated vapor retains its original dispatcher.
Unsupported/invalid inputs retain their exceptions and support guards. The
upper 1<Q<=1+1e-9 band remains explicitly invalid and unresolved here; it is not
counted as preserved legitimate coexistence. No vapor or PT/cache repair is made.

Shared callers were traced through mass-to-molar conversion: PH, PS and PU all
use HSU_P_flash. Native focused PS/PU tests cover 24 states (liquid, mixture,
vapor at four pressures); all eight liquid inversions select liquid and their
raw canonical limits pass. Mixture/vapor PS/PU rows are identical to control.
PT passes iT and DP passes iDmolar to the classifier; neither gains the new
caloric condition. DU uses HSU_D_flash and is unmodified. The generic full-VLE
code also serves pseudo-pure fluids; their behavior is not qualified by this
ammonia-only experiment.

Rejected strategies: clipping quality or assigning saturation density would
change the requested inventory; enlarging tolerance permits more invalid
extrapolation; rejecting valid liquids denies the supported state; a custom
Newton/reference-root substitution duplicates existing machinery; a simultaneous
upper-Q or cache patch couples separate defects. See ALGORITHM.md for details.

## Exact source and build provenance

Upstream CoolProp 8.0.0 commit
`ae81610e7d23efc57f9d051c8e70a4d66e87537f`, tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662`.

| Source identity | SHA256 |
|---|---|
| B1 44-bit FlashRoutines.cpp | `9e6d3be44cc61c3ca5b539fa10f4587cfeef3e286dec2d267fe90933df67c0e3` |
| Original classifier | `526a59c5797cdf3b0620e195e9149141de559711fe09a998035d3ab0d81ab65d` |
| Repaired classifier | `6c6a2997936f9c006a2b5341632bdabc8626feb60655471359aad44bd93daf55` |
| Liquid patch | `67eb377174cda509980b5c17b3283abcda9fb9e7f0f265c23a29b58cbd724572` |

Control-to-repair changes exactly one source file; the only prior change is the
qualified B1 flash expression. Diagnostic builds add logging in the classifier
and flash files only; their separate diffs and hashes are retained. Native
logging on/off and uninstrumented results are identical across all 86 rows in
the corresponding path, excluding wall-clock fields only. Captured primary
quality remains negative, dispatch becomes homogeneous liquid, and each native
path records six homogeneous residual evaluations (control bypassed the flash).

Build tools: GCC 14.2.0; CMake 4.4.4; Ninja 1.13.2; Python 3.12.14;
Emscripten 4.0.12 at `6f625bd62ee64f4f8cd11476774741b961e4a2d5`; LLVM
`7f93487862d98bf1c168babba87daf6224d8a46f`; SDK release
`209b886304498eff50dd835850dc5715803401ed`, SDK Node 22.16.0.
All dependency revisions/content digests match B3. Native release flags include
`-O3 -DNDEBUG -std=gnu++17 -DCOOLPROP_LIB -m64 -DEXTERNC`; upstream WASM flags
retain exceptions, memory growth and ES6 modularization. No fast-math. Exact
commands/caches, source stages, licensing notices and reproduction are in
[BUILD.md](BUILD.md) and `evidence/provenance.json`.

| Binary | Uncompressed SHA256 |
|---|---|
| libCoolProp-control44.so | `e5812fbadaa45e7ae766081c87ca8e13f6fff96bf925a1105a53eb82641b3728` |
| libCoolProp-liquid44.so | `7a31ae229a6f62bc3f53b570759f631b29c393f743826a6de08ce9d1b87e36de` |
| libCoolProp-diagnostic44.so | `4ca12059489d7c57d214ec8e1d039a3daeceae50f0892aaa7a8574098e22ba4d` |
| vendor/control44/coolprop.wasm | `eff473068c5f9950a37cdffef013a931b291c606bf7768d21b0c4fe8c1d82126` |
| vendor/liquid44/coolprop.wasm | `25dceb87d7845e52c53a2599b959fc7d1e7739f09660ca3c92b2e3b298ab0306` |

Both JS wrappers have SHA256 `ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`. Archive hashes are in `native-binaries.json`; all notices are retained. B4A controls are new builds and do not replace historical artifacts. Source-path/tool differences change hashes; numerical equivalence is checked independently.

## Primary counterexample: before and after

Exact P=30298.937123458254 Pa, bits `40dd96bbf9d4ab61`.
Exact h=98904.56398938334 J/kg, bits `40f825890619bb4c`.
No requested-input rounding occurs. Chromium and WebKit return identical rows.

| Measurement | Unchanged WASM source44 | Repaired WASM source44 |
|---|---:|---:|
| Phase enum | 6 | 0 |
| Quality | -6.99036205016646e-10 | -1 |
| Temperature K | 218.26293725550536 | 218.26293702735882 |
| Density kg/m³ | 707.4995406964335 | 707.4983265879039 |
| Fresh-DT pressure residual Pa | 2870.50263307 | -8.10905476101e-08 |
| Fresh-DT enthalpy residual J/kg | 2.58914243804 | -5.96628524363e-10 |
| Canonical ΔP Pa | 4245.08707887 | -0.000430944030086 |
| Canonical Δh J/kg | 6.00012695993 | -5.91491698287e-07 |
| Canonical ΔT K | 0.000495447217304 | -4.66116034659e-11 |

Independent wheel8 homogeneous EOS Newton roots converge with no backend PH
substitution. The physical root is about 2.28146e-7 K below saturation.
At the repaired returned DT coordinates, cp=4383.138987600951 J/(kg K),
cv=2963.1955667967936 J/(kg K), kappa=5.979609868285529e-10 Pa^-1, all positive;
fresh DT identifies liquid. The independent saturation solve enforces pL=P,
pV=P and gL=gV from displaced seeds; all four pressures converge.

Native repaired default gives T=218.2629370273589 K,
rho=707.4983265879034 kg/m³, fresh-DT ΔP=-3.4055483411066234e-7 Pa,
Δh=-2.6193447411060333e-10 J/kg; canonical ΔP=-0.0004309440810175147 Pa.
Native full-VLE gives T=218.26293702735882 K,
rho=707.4983265879039 kg/m³, fresh-DT ΔP=-8.109054761007428e-8 Pa,
Δh=-5.966285243630409e-10 J/kg; canonical ΔP=7.057096809148788e-7 Pa.
All primary p/h/T canonical comparisons pass .1 Pa/.1 J/kg/1e-4 K in both paths.
Native/browser final-bit differences remain visible, not coerced to agreement.

Original standalone limits (<10 Pa, <50 J/kg, <.01 K), independent root limits
(1e-5 Pa, 1e-8 J/kg), nonlinear scale 1e-11 and canonical limits are unchanged.
The repaired state agrees with the independently converged root within those
standalone budgets. All 42 homogeneous base reference roots converge; maximum
root residuals are 8.3633e-7 Pa and 1.3388e-9 J/kg, below their original limits.
This uses an independent inversion/evaluation of the same EOS, not independent
experimental ammonia data or a different thermodynamic formulation.

## Exact signed derivatives

All four original signed probe inputs/bit patterns are retained. Finite
differences use the original nominal step; actual binary64 increments are
reported separately. Analytic derivatives come from the independent root.

| Probe | Actual increment | Physical branch | FD density derivative | Independent homogeneous derivative | Ratio | Normalized mass / energy contamination |
|---|---:|---|---:|---:|---:|---:|
| P+ | 0.00999999999839929 | liquid | 6.64488197799074e-07 | 6.64499173052975e-07 | 0.999983483419774 | 1.55128e-16 / 2.31271e-16 |
| P- | -0.00999999999839929 | coexistence crossing | excluded | excluded | excluded | homogeneous smoothness not required |
| H+ | 0.000989045642199926 | liquid | -0.00026778474786508 | -0.000267784127133341 | 1.00000231803037 | 8.6775e-16 / 1.10491e-15 |
| H- | -0.000989045642199926 | liquid | -0.000267784517973085 | -0.000267784127133341 | 1.0000014595329 | 5.46374e-16 / 4.27668e-16 |

The P nominal probe is ±.01 Pa and h probe is ±.0009890456398938335 J/kg.
The reverse-P state is a genuine mixture with Q=1.5531609308105042e-8;
it is not a failed smooth derivative. Across both browsers, 108 supported
same-liquid probe comparisons pass: maximum normalized mass contamination
2.01949e-13 and energy contamination 2.02347e-13, below the existing 1e-11.
No arbitrary derivative percentage tolerance is used. Probes above 35 bar are
explicitly unsupported; steep valid coexistence derivatives are not failures.

## Focused saturation matrix and endpoints

The exact 57 B3 inputs include preserved .001/.01 J/kg approaches, endpoints and
diagnostic ±.99e-9/±1.01e-9 quality-band offsets at hf and hg. Diagnostic inputs
remain labeled and never replace solver probes. B4A adds the saved B1 fixture,
twelve established stable/mixture states and sixteen one-ULP endpoint neighbors:
86 bases and 344 signed probes per artifact/path. Native control/repair runs
exercise superancillary and disabled-superancillary/full-VLE paths. Both browser
engines exercise distinct new control/repaired WASM artifacts.

Independent phase classification gives 21 liquid, 21 vapor, 20 coexistence and
24 endpoint-unresolved bases. All 86 PH calls succeed in each tested path.
Every resolved physical liquid selects homogeneous liquid after repair, with
no liquid-side lever extrapolation. All 41 resolved vapor/coexistence base PH
outputs are identical to control; legitimate mixtures are preserved.
`endpoint-continuity.json` additionally compares all sixteen ULP neighbors per
engine with their preserved endpoints: normalized density/mass changes are
within the original 1e-11 scale. `original-budget-ledger.json` records each
primary standalone, reference-root and canonical component comparison explicitly.
Endpoint/ULP behavior and every exception/recovery result are retained, without
silently moving inputs. Homogeneous derivative assertions are excluded at
endpoint uncertainty and physical crossings. No new endpoint PH exception or
resolved-liquid derivative failure is observed in this finite sample.

Representative browser results, below hf (all original values retained):

| Pressure bar absolute | Offset | Repaired phase | Fresh-DT ΔP Pa | Fresh-DT Δh J/kg | Canonical ΔP Pa |
|---|---|---|---:|---:|---:|
| 0.302989371234583 | .001 J/kg | liquid | -8.10905476e-08 | -5.96628524e-10 | -0.00043094403 |
| 3.5 | .001 J/kg | liquid | 2.29512807e-07 | -4.43134923e-07 | 0.000344155764 |
| 7.99999998175486 | .001 J/kg | liquid | 1.63912773e-07 | -6.17001206e-09 | 4.08024061e-06 |
| 35 | .001 J/kg | liquid | 5.02448529e-07 | 1.16415322e-09 | 1.48545951e-07 |
| 0.302989371234583 | .99e-9 latent (diagnostic) | liquid | 3.65082087e-07 | 2.18278728e-10 | -0.00061031873 |
| 3.5 | .99e-9 latent (diagnostic) | liquid | -1.86089892e-07 | -4.42028977e-07 | 0.000311788579 |
| 7.99999998175486 | .99e-9 latent (diagnostic) | liquid | -2.96393409e-07 | -6.98491931e-10 | -2.46800482e-08 |
| 35 | .99e-9 latent (diagnostic) | liquid | 2.84984708e-07 | -1.88592821e-08 | 7.04871491e-06 |

All raw default-path liquid canonical limits pass. At exactly 35 bar the
unchanged browser adapter rejects nine C recovery cases, the same identities as
control, because numerical recovery exits its strict support guard. They remain
adapter failures even when raw differences meet canonical budgets.

With superancillaries disabled, three 35-bar physical liquid C inventories throw
in DU: hf-.001 J/kg and diagnostic hf-1.01e-9 / hf-.99e-9 latent. Physical A
also throws. At all 31 identical fixed 35-bar A/C inventories, control and repair
produce identical recovery output/errors. These are preserved inverse failures,
not canonical passes and not suppressed regressions. Native 7.2's three
historical 35-bar DU exceptions remain in unchanged B3 evidence; no new 7.2
source campaign is claimed. [GATE_SCOPE.md](GATE_SCOPE.md) explains the supported
liquid gate and why these retained limitations do not qualify those inverses.

The upper band still returns Q>1 in nine sampled browser inputs, including two
ULP endpoint diagnostics. These are invalid extrapolations, not genuine mixtures;
the source change does not repair or certify them. This and the separate vapor
cache defect prevent an entire-backend qualification claim.

## Independent A/B/C inventory ledger

The original arithmetic is retained exactly:
`V=.003/5; M=rho*V; U_kJ=M*(h/1000)-100*(P/1e5)*V; rhoDU=M/V; uDU=U_kJ/M*1000`.
V is actually 0.0006000000000000001 m³, bits `3f43a92a30553262`.
There is no clipping, algebraic replacement, redefinition or normalization.

| Quantity | A independent physical root | B fixed historical erroneous PH | C repaired PH |
|---|---:|---:|---:|
| M kg | 0.4244989959527423 | 0.42449972441786016 | 0.4244989959527424 |
| U kJ | 41.96670874636291 | 41.96678079488777 | 41.96670874636292 |
| V m³ | 0.0006000000000000001 | 0.0006000000000000001 | 0.0006000000000000001 |
| Recovered P Pa | 30298.936692513904 | 34544.02420232762 | 30298.936692514224 |
| Recovered h J/kg | 98904.56398879048 | 98910.56411634327 | 98904.56398879185 |
| Recovered T K | 218.26293702731203 | 218.26343270272267 | 218.2629370273122 |
| ΔP Pa | -0.000430944350228 | 4245.08707887 | -0.000430944030086 |
| Δh J/kg | -5.92859578319e-07 | 6.00012695993 | -5.91491698287e-07 |
| ΔT K | -4.67821337224e-11 | 0.000495447217304 | -4.66116034659e-11 |
| Original canonical limits | PASS/PASS/PASS | FAIL/FAIL/FAIL | PASS/PASS/PASS |

C agrees with A at ordinary binary64 resolution but remains a separate measured
inventory. B is unchanged and still recovers the higher pressure appropriate
to its different mass/energy; the correction does not make B recover the
preferred original pressure. C's DU inventory residual is about -1.270e-10
kg/m³ and +1.497e-8 J/kg. Its fresh-DT pressure differs from the DU getter by
about 1.859e-6 Pa, retained explicitly and well below the original canonical
budget. DU labels A/C Q=0 at a slightly shifted numerical endpoint, while
independent DT resolves the recorded coordinates as liquid; no exact DU phase
classification claim follows. Every inventory's DT/EOS and original budget
comparisons are present in raw evidence. The original compatibility failure is
resolved for C; no conservative ledger or accepted solver was changed.

## B1 precision and other regressions

The saved B1 input P=30298.937123458254 Pa, h=94523.34612321304 J/kg retains
bit-identical base/probe records in native and both browsers. Browser ratios:
rho_P forward 0.999959589002674, reverse 1.00004549618386;
rho_h forward 1.00000072850827, reverse .999998480945913.
Original signed perturbations and normalized scales pass. The 44-bit benefit is
retained; no 30-bit or official artifact is overwritten.

The ten additional native domain/invalid cases give identical control/repair
records: eight exceptions and two supported pressure-boundary successes.
PS/PU liquid states improve consistently; mixture and stable vapor inverse
states are unchanged. There is no observed new failure in an unrelated sampled
property region. This finite regression sample does not establish global fluid,
critical/triple, mixture or pseudo-pure accuracy.

The separate saved vapor regression P=799999.9981754856 Pa,
h=1624022.744737779 J/kg is **UNRESOLVED / FAIL, unchanged**. Its complete native
and browser base/probe records are bit-identical to control. Native fresh-DT h
residual remains -0.00011919043026864529 J/kg; isolated PT cached-minus-fresh-DT
h remains +0.00011973525397479534 J/kg, pressure -0.001824048813432455 Pa.
This can pass coarse value/canonical checks while failing the original local
nonlinear energy-consistency screen (about 8e-11 versus 1e-11). It is not
silently called passing, improved by B4A, or conflated with the liquid defect.

Chromium 151.0.7922.34 and WPE WebKit 26.5 return identical complete control and
repaired focused rows. Independent native DT reevaluation matches browser DT
p/h/u exactly across this finite sample and its probes. Native returned PH final
digits differ slightly in places and are reported separately. Native diagnostic
parity is proven; no browser-internal execution trace or instrumented WASM build
is claimed. The native trace plus matched browser behavior establishes this
experiment's attribution.

## Limited accepted A2 compatibility

The original five-section dependency closure is verified at
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. It is injected through the unchanged
isolated B1 adapter. The original B2 zero-exchange initialization and .001 s pure
trial now succeed in both engines; the input trial state remains exactly
preserved. The original conservative PH/M/U/V check passes without a solver edit.

The selected accepted accuracyOptions(1e-6), finite-difference thermal Jacobian
and failure-aware timestep growth are unchanged. Newton limit 30, fluid norm
1e-11, thermal closure 1e-12 K, original probes, line searches, mass/energy
conservation, TR-BDF2, domain guard, rollback and temporal acceptance rules remain.
The original A2 scientific `check` function is extracted verbatim from its Git
object and applied to each recorded sample, including independent thermal-node
ledger reconstruction.

Both engines complete cold/warm/heat-reversal at .01/.05/.2 s and feed-step at
.01/.2/1/5/15/15.01 s, retaining the original fixtures and saved feed event.
Maximum aggregate mass residual is 1.3471e-12 kg and section mass 1.1937e-12 kg
(limit <1e-8); maximum section energy 6.1365e-10 kJ and combined energy
4.3108e-10 kJ (limit <1e-6). All unchanged recorded scientific assertions pass.

This is a bounded compatibility pass, **not full A2 backend qualification**.
No full tolerance/refinement/frozen-reference, option, domain-stop/rollback or
long-run qualification matrix is claimed. The implementations remain unchanged;
the full matrix is a future gate, not inferred from the short trials.

## Runtime and memory

Three short matched timing rounds use the exact saved primary, original
57-boundary workload and B1 fixture. Native timing measures C API PH update only
(ctypes/error-buffer overhead included, getters excluded); browser timing uses
the existing complete low-level adapter call. Results are descriptive, not a
new speed budget or controlled statistical performance guarantee.

| Runtime | Primary control → repair µs/call | Ratio | Boundary control → repair µs/call | Ratio |
|---|---:|---:|---:|---:|
| native | 5.435 → 55 | 10.12× | 30.18 → 30.07 | 0.9963× |
| chromium | 5.623 → 68.12 | 12.12× | 24.76 → 35.72 | 1.443× |
| webkit | 6.235 → 61.12 | 9.804× | 29.53 → 35.44 | 1.2× |

The primary penalty pays for six actual homogeneous residual evaluations instead
of an invalid lever shortcut. No physical checks or budgets were optimized away.
B1 timing ratios fluctuate .75–1.11 in these short observations despite identical
property results/code path; no incidental speed improvement is established.

WASM initialization total control→repair: Chromium 1948.7→2055 ms,
WebKit 2065→1994 ms. Both use streaming compilation and grow linear memory from
22,544,384 to 56,360,960 bytes at first factory; observed workload memory remains
56,360,960 bytes for both builds. Native max RSS is 127172/127104 KiB for
control/repair processes, including Python/wheel overhead. Chromium JS heap is
about 56.8/44.7 MB at the recorded snapshots; WebKit exposes no corresponding
heap metric. No timing-workload property exception or init failure occurs.
No physical Safari/iPad result is claimed.

## Failures, limitations and review disposition

The raw evidence retains the failed historical liquid inventories, upper-Q
extrapolations, vapor cache failure, default 35-bar support rejections, three
disabled-superancillary 35-bar DU exceptions and historical native7.2 failures.
No source repair is claimed for these separate inverse/cache/support issues.

Setup attempts are retained: network access capability was needed for clone;
initial native configure omitted EXTERNC and its build was interrupted before
measurements, then fully rebuilt correctly; WebKit needed isolated local
libraries; the first dependency-verifier schema lookup failed before comparison;
the patch generator initially hit a Python formatting exception before any source
write. Its following control-only stage snapshot was retained under an explicit
generator-failure name; the actual repaired stage was captured separately.
All used builds, numerical outputs, equality checks and final assertions complete.

The result is limited to the finite ammonia support sample, same-EOS independent
inversions, native Linux and desktop Chromium/WPE WebKit. There is no different
EOS/experimental-data validation, broad critical/triple/mixture/pseudo-pure
qualification, full B2/A2 rerun, physical iPad qualification, long run or production
integration. Generic shared-source consequences require broader review before
any upstream or production use.

[B4B_PREREQUISITES.md](B4B_PREREQUISITES.md) defines separate vapor/cache and
upper-Q decisions, inverse/support resolution, complete scientific qualification,
browser/device/runtime and deployment prerequisites. [BUILD.md](BUILD.md) supplies
bounded reproduction commands; [README.md](README.md) maps machine-readable
evidence. Every original checkpoint, accepted scientific assertion and historical
comparison artifact is preserved.

**Stop for engineering review and explicit approval.** No production engine/UI
change, Live Plant integration, merge, deployment or B4B vapor correction occurs.
