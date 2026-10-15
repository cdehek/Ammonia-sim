# B3 — CoolProp phase-decision forensics

**Final classification: ROOT CAUSE CONFIRMED.** Captured execution traces from
both historical precision variants demonstrate the liquid triggering branch;
independent stable liquid roots and paired inventory recoveries establish its
physical consequence. The separate vapor cache mechanism is also directly
observed in the pinned 8.0 source. No corrective patch is implemented.

| Scientific question | Evidence-backed finding |
|---|---|
| Incorrect liquid phase selection | Directly captured: subcooled h passes the negative-Q tolerance and selects phase 6. |
| Negative-quality extrapolation | Directly captured lever-density calculation; independent DT proves its thermodynamic inconsistency. |
| PH flash convergence | The homogeneous PH flash is bypassed for the saved liquid failure. Historical single-phase precision limitations are separate. |
| PH-to-DU inventory recovery | The physical liquid inventory passes; the inconsistent PH-derived inventory recovers a different, EOS-consistent state. Separate native7.2 high-pressure DU exceptions persist. |
| PT/cache consistency | Directly captured 8.0 final density/cache coordinate mismatch on isolated vapor PT; separate from phase selection. |

Delivery branch: `research/browser-eos-b3-phase-forensics-20261015`. The full
delivery SHA is the commit containing this report and is supplied in the handoff.
Its parent is exactly B2 `6a220dd6c94bff08e00e0107cfec71854166ede2`.

## Preservation and provenance

The initial checkout was clean at that exact B2 commit. All **854** starting
tracked files retain their SHA256, including every B1/B2 result and binary.
All **12** accepted dependency snapshots match Git objects at A2
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. B1 remains
`ef1562ae1680fccf3323391e9ec83788c5ae1e69`; UI remains
`262b6092b2ed694073ad9ffd41265f44dd0b6ca0`. Before/after remote refs and the
starting-file manifest are preserved. Only B3 additions are committed.

B2 engineering/scientific reports, liquid counterexample, qualification matrix,
source/cache attribution and preserved measurements were reviewed, together
with B1's original comparison, build provenance and accepted numerical contract.
The complete B2 campaign was not rerun. B1's pre-existing main H/S/U-at-P
bracket stopping expression is reproduced at 30 and 44 bits; its original flash
SHA256 is `debf60f85d1d0955f08596e64d3a4958d7f369657cb3161a6b7625fa508cf3df`,
and historical 44-bit SHA256 is
`9e6d3be44cc61c3ca5b539fa10f4587cfeef3e286dec2d267fe90933df67c0e3`.
That difference does not control the demonstrated two-phase path.

Native source is upstream CoolProp 8.0.0 commit
`ae81610e7d23efc57f9d051c8e70a4d66e87537f`, tree
`ca49b8c34df0dae93dcc7fe07e2815a10d967662`. Native unmodified30, historical44
and their separate diagnostic binaries are preserved as compressed research
artifacts. Full uncompressed/archive hashes are in
[native-binaries.json](evidence/native-binaries.json). Python wheels 8.0.0 and
7.2.0 supply matching-version checks; their actual revisions and binary hashes
are recorded in provenance. Browser official8, source30, source44 and official72
reuse the unchanged B1/B2 JS/WASM. Their exact hashes are pinned by the starting
manifest and source/binary provenance.

The native build uses GCC 14.2.0 on Debian 13 x86_64, CMake 3.31.6, Ninja
1.11.1.4, Release `-O3 -DNDEBUG -std=gnu++17`, with upstream native library flags
and no fast-math. Exact compiler commands, CMake cache, dependency revisions,
archive pins and source stage hashes are preserved. Only the three instrumented
C++ translation units differ in the external diagnostic source; no coefficient
or fluid-data file changes. Licensing/source links remain in the existing
B1 third-party notices; B3 artifacts are research libraries, not selected product
backends. Native and WASM compiler/binding differences are explicitly retained.

## Exact reproduction and physical reference

The original requested binary64 values are:

| Quantity | Decimal | Big-endian binary64 bits |
|---|---:|---|
| P, Pa | 30298.937123458254 | `40dd96bbf9d4ab61` |
| h, J/kg | 98904.56398938334 | `40f825890619bb4c` |

All four browser artifacts reproduce the same PH output in both Chromium and
WebKit: T=218.26293725550536 K, rho=707.4995406964335 kg/m³,
Q=−6.99036205016646e−10, phase 6 (two-phase). Fresh DT produces
P=33169.439756531385 Pa and h=98907.15313182138 J/kg, giving
**+2870.5026330731307 Pa** and **+2.5891424380388344 J/kg**.

| Implementation | Returned T K | Returned rho kg/m³ | Q | Fresh DT ΔP Pa / Δh J/kg |
|---|---:|---:|---:|---|
| Chromium/WebKit official 8.0 | 218.26293725550536 | 707.4995406964335 | −6.99036205016646e−10 | 2870.5026330731 / 2.58914243804 |
| Chromium/WebKit source30 | same | same | same | same |
| Chromium/WebKit historical44 | same | same | same | same |
| Chromium/WebKit official 7.2 scalar API | same | same | same | same |
| Native 8.0 wheel and source30 | 218.26293725550534 | 707.499540697082 | −6.990365783288272e−10 | 2870.5041658243 / 2.58914382009 |
| Native historical44 | same as native30 | same | same | same |
| Native 7.2 wheel | same as native30 | same | same | same |
| Native diagnostic30/44 | bit-identical to corresponding uninstrumented native build | | | |

Native/browser differences in final digits are reported rather than forced to
agree. They do not change the selected branch or physical conclusion. All three
additional browser repeats of the saved liquid and vapor fixtures are bit-identical
within each artifact/engine. For each native precision, all **57 full result rows**
are bit-identical with and without instrumentation. Eleven pairs of repeated
decision/probe/PT execution traces per precision compare exactly equal.

An independent homogeneous EOS Newton solve at the exact requested P/h gives
T=218.26293702735882 K and rho=707.4983265879036 kg/m³, approximately
2.28147e−7 K below saturation. It converges within the retained diagnostic limits
1e−5 Pa and 1e−8 J/kg; exact residuals and iterations are in the native JSON.
cp≈4383.13899 J/(kg K), cv≈2963.19557 J/(kg K) and
isothermal compressibility≈5.97961e−10 Pa⁻¹ are positive.

Saturation is independently checked by solving pL=P, pV=P and gL=gV from
deliberately displaced diagnostic seeds at all four pressures, in both native
versions. All eight coexistence solves converge in three recorded evaluations,
within 1e−5 Pa and 1e−8 J/kg Gibbs difference. This verifies the saturation
boundary using EOS equations. The liquid reference's stable root and temperature
relative to that boundary establish physical phase; the backend enum does not.
These independent calculations use the same EOS, not independent experimental
ammonia data or a second EOS formulation.

## Captured liquid phase decision

The primary trace enters the **superancillary** branch of
`HelmholtzEOSMixtureBackend::p_phase_determination_pure_or_pseudopure`.
The following values are copied from the captured native30 execution; native44
has the same decision sequence and values:

```text
API inputs: P=30298.937123458254, h=98904.56398938334 (original bits above)
requested hmolar = 1684.3961551124728 J/mol
Tsat             = 218.26293725550534 K
hf_molar         = 1684.396172142993 J/mol
hg_molar         = 26047.241751070433 J/mol
h-hf_molar       = -1.7030520211847033e-05 J/mol
h-hg_molar       = -24362.84559595796 J/mol
raw Q            = -6.990365783288272e-10
Q < -1e-9        = false
Q > 1+1e-9       = false
selected phase   = 6, two-phase
rho_molar        = 41543.038069130125 mol/m³
v_molar          = 2.4071421987384256e-05 m³/mol
HSU_P_flash dispatch: homogeneous = false
```

The trace captures endpoint EOS evaluations, quality, both comparisons, selected
phase, lever density/volume and subsequent dispatch. API input markers precede
the source's mass-to-molar conversion; the trace reports actual internal molar
values rather than claiming their conversion reproduces every input bit.
Public PH/DU outputs and independent DT residuals are captured in the paired
native JSON, joined by exact fixture identity. Events following the first
`PH_dispatch` in each native matrix block include the inventory recovery calls;
they are not mislabeled part of the original PH phase decision.

The selected formula is
`rho = 1 / (Q/rhoV + (1-Q)/rhoL)`. A negative Q extrapolates volume below the
saturated-liquid volume and produces an artificially dense state. The physical
coexistence bubble-side density/h derivative is approximately −1.214375,
whereas the independently converged liquid derivative is −0.000267784127.
The factor of about 4,535 is legitimate **on the coexistence side**. Extending
that relation into subcooled liquid is the demonstrated error.

This establishes two linked mechanisms: incorrect phase selection permits
negative-quality extrapolation, which produces the inconsistent liquid density.
The homogeneous PH flash is **not dispatched** for this failure, so its 30/44-bit
convergence setting cannot cause or cure this particular result. Other
single-phase flash convergence limitations remain separate.

As an explicitly separate diagnostic, disabling superancillaries in the same
native builds takes the full-VLE path. Captured Q=−6.991925014940802e−10 again
passes both quality comparisons, and the PH dispatcher again reports phase 6,
homogeneous=false. This is direct tracing of that alternative 8.0 path, not a
claim that it was the default execution or that 7.2 internals were instrumented.

## Paired canonical inventories

Use the original arithmetic, not algebraically substituted normalization:
`V=.003/5`, `M=rho*V`, `U_kJ=M*(h/1000)-100*(P/1e5)*V`;
DU receives `rho=M/V`, `u=(U_kJ/M)*1000`.
The actual binary64 V is 0.0006000000000000001 m³
(`3f43a92a30553262`). Both input and output bits are retained.
The actual M/V operation rounds A's DU-input density two ULPs above the DT-root
density; that ordinary representable increment is retained without correction.

| Quantity | A: independent physical liquid | B: unchanged browser PH density |
|---|---:|---:|
| M kg | 0.4244989959527423 | 0.42449972441786016 |
| U kJ | 41.96670874636291 | 41.96678079488777 |
| DU input rho kg/m³ | 707.4983265879038 | 707.4995406964335 |
| DU input u J/kg | 98861.7385352659 | 98861.73860875676 |
| DU P Pa | 30298.936692513904 | 34544.02420232762 |
| DU T K | 218.26293702731203 | 218.26343270272267 |
| DU h J/kg | 98904.56398879048 | 98910.56411634327 |
| Canonical ΔP Pa | −0.00043094435023 | +4245.087078869368 |
| Canonical Δh J/kg | −5.92860e−7 | +6.00012695993064 |
| Canonical ΔT K | −4.67821e−11 | +0.000495447217304 |
| Original .1 Pa / .1 J/kg / 1e−4 K limits | PASS / PASS / PASS | FAIL / FAIL / FAIL |

The physical liquid reference is diagnostic only; it never enters a coupled
model or substitutes a returned PH state. The paired adapter calls are standalone
inventory measurements. No normalization, clipping or hidden adjustment occurs.

Inventory A's native DU output labels the state Q=0, phase 6 at a slightly shifted
saturation endpoint. Fresh DT labels its recorded physical coordinates liquid.
Its fresh-DT pressure differs from the DU getter by about 1.24e−6 Pa; its
rho/u inventory residuals are approximately −1.27e−10 kg/m³ and +1.45e−8 J/kg.
Thus this is **within the accepted canonical budgets**, not a claim of exact DU
phase classification or unlimited numerical accuracy.

Inventory B's recovered state has fresh-DT pressure/h identical to its getters
in this sample, and u differs from the supplied inventory by about −1.50e−8
J/kg. At the *original PH* DT coordinates, however, declared u exceeds actual
EOS u by **1.4681077338 J/kg**. DU consequently finds a warmer state at that
density. The associated cell energy mismatch is about 0.0006232113 kJ. This is
a physical consistency diagnostic, not a claim that a conservative ledger was
modified. A and B are different inventories: their M differs by 7.28465e−7 kg
and U by 7.20485e−5 kJ; these differences must not be silently removed.

Native source30/44 and native8 give the same conclusion, with B ΔP≈4245.08936
Pa from their slightly different density. Native7.2 also recovers the primary
physical inventory within canonical budgets, but throws on **three** valid
35-bar liquid-reference inventories in this focused matrix. Those errors remain
in the raw results. This prevents any global statement that DU itself is always
reliable; it does not make DU the cause of the preserved low-pressure failure.

## Pressure boundary experiment

The matrix contains 57 base states: the original vapor fixture; 24 exact saved
B2 endpoints/outward .001/.01 J/kg offsets; and 32 labeled diagnostic offsets
at ±0.99e−9 and ±1.01e−9 times latent enthalpy, on both sides of hf and hg.
All retain the established four signed derivative probes unchanged.

Representative **browser44** liquid-side results:

| P bar absolute | Offset below hf | Returned branch | Fresh DT ΔP Pa | PH-derived DU ΔP Pa |
|---|---|---|---:|---:|
| .30298937123458254 | .001 J/kg | two-phase, negative Q | 2870.502633 | 4245.087079 |
| 3.5 | .001 J/kg | two-phase, negative Q | 170.288518 | 273.578630 |
| 7.999999981754856 | .001 J/kg | two-phase, negative Q | 56.773823 | 95.409031 |
| 35 | .001 J/kg | homogeneous liquid | 5.02e−7 | 1.49e−7 |
| 35 | .99e−9 × latent enthalpy (diagnostic) | two-phase, negative Q | 4.170042 | 8.067548 |

At 35 bar latent enthalpy is about 924,242.762 J/kg, so .001 J/kg already lies
beyond the −1e−9 band and dispatches liquid. The .99/1.01 diagnostic sweep
demonstrates the threshold at **each** pressure: below hf by .99e−9 latent
enthalpy selects extrapolated two-phase; by 1.01e−9 selects homogeneous liquid.
The latter states' raw canonical differences pass in browser44. This explicitly
includes successful states rather than treating every near-boundary result as
a failure. Positive offsets above hf and negative offsets below hg are physical
equilibrium; offsets above hg are physical vapor, some erroneously assigned
Q>1 inside the corresponding tolerance band. That upper quality-band issue is
distinguished from the saved .001 K-superheated vapor cache case below.

In the browser44 sample, physically equilibrium base/probe states have maximum
fresh-DT residuals about 9.78e−9 Pa and 4.66e−10 J/kg. Homogeneous roots are
verified for 33 stable base inputs per native version. Eight endpoint inputs
within 1e−8 J/kg reference resolution are explicitly left endpoint-unresolved;
no two-sided homogeneous smoothness assertion is imposed there.

The original saved liquid derivative probes remain:

| Probe | Nominal signed step | Actual binary64 increment | Physical result | FD / independent homogeneous derivative |
|---|---:|---:|---|---:|
| +P | .01 Pa | .00999999999839929 Pa | stays liquid | −182709.3146266 |
| −P | −.01 Pa | −.00999999999839929 Pa | crosses to equilibrium | excluded |
| +h | .0009890456398938335 J/kg | .000989045642199926 J/kg | stays liquid | 4534.91023848 |
| −h | −.0009890456398938335 J/kg | −.000989045642199926 J/kg | stays liquid | −4583.12389369 |

The three same-physical-phase failures contaminate the original normalized mass
scale by approximately 1.70–1.72e−6, versus the existing nonlinear scale 1e−11.
The phase-crossing probe has no homogeneous derivative requirement. The audit
classifies physical branches from saturation/reference roots, independently of
backend phase codes, and labels pressure probes beyond 35 bar **unsupported**.

At exactly 35 bar, some raw DU results exceed the upper pressure guard by only
1e−7–1e−6 Pa and are rejected by the unchanged adapter, even when raw canonical
differences pass. The negative-quality diagnostic also recovers beyond the
validated support envelope. Originating physical inputs are supported;
numerical recovery exits do not prove a physical domain exit. These guard
errors and native7.2 recovery exceptions are retained, never counted as passes.

## Separate vapor cache mechanism

Exact saved vapor input is P=799999.9981754856 Pa
(`412869ffff10db75`), h=1624022.744737779 J/kg
(`4138c7d6bea72295`). It is physically homogeneous vapor, about .001 K above
saturation, outside the quality-tolerance band responsible for the liquid bug.

Captured source30 isolated public PT execution at the PH-returned temperature
has this final density sequence, in mol/m³:

```text
Householder4 iteration 2:
  evaluated rho = 367.96004400516597
  relative pressure residual = -2.2800613130288793e-09
  ftol = 1e-8
  increment = +9.463514042295842e-07
  returned rho = 367.9600449515174
PT_flash assigns that returned rho
last derivative cache delta = 0.02686624153075102
calc_hmolar explicit delta  = 0.026866241599847938
cached dar/dtau             = -0.22795609240194037
cached dar/ddelta           = -3.776221025283233
```

The final residual is already smaller than ftol **before** the increment. The
solver increments x anyway, then exits the loop using the old fval and returns
the incremented x without evaluating it. `SolverTPResid::call` cached properties
at the earlier density. `PT_flash` assigns the later density. `calc_hmolar`
updates the explicit reduced-density coordinate but reuses the derivative
values from the recorded earlier cache fill. The trace confirms identical
cached derivative values at these two different coordinates. This termination
is the loop's residual test, not the relative-step termination.

Fresh DT at the returned native30 density and temperature reproduces the target
pressure, whereas PT's cached pressure differs by −.001824049046 Pa and cached
h exceeds fresh-DT h by **.000119735486805439 J/kg**. Its PH getter differs from
requested h by only +2.73576e−7 J/kg, while independently evaluated h misses by
about −.000119462 J/kg. Source44 captures the same mechanism, with PH fresh-DT
h residual about −.000119190 J/kg. An independent gas root at exact P/h gives
T≈291.0143614933414 K and rho≈6.266550903429371 kg/m³.

The isolated PT call has no enthalpy input and still exhibits the mismatch.
The vapor's homogeneous dispatcher, final density/cache coordinates, numerical
derivatives and independent DT values directly separate this mechanism from
negative-quality lever extrapolation. The 44-bit outer bracket change does not
refresh the inner PT cache. Native7.2 public PT reproduces the cache symptom;
its PH getter behavior differs, and no native7.2 internal source trace is claimed.

For scale, the native30 vapor h defect corresponds to about 4.49168e−10 kJ in
one original cell. Dividing by its actual accepted `max(1,abs(U_kJ))` scale
(U≈5.62621 kJ) gives about **7.98350e−11**, versus 1e−11. The historical B2
4.49e−10 number used the unit-energy screen; both are retained without changing
the accepted normalization. This local risk comparison is not a new property
tolerance or a claim that a B3 operating trajectory failed.

## Verification, limits and disposition

Chromium 151.0.7922.34 and WPE WebKit 26.5 each complete 57 base states and 228
signed probes for all four artifacts: **2,280 base/probe snapshots**, no PH matrix
exception. For every artifact, complete browser result rows compare equal
between engines. Official8 and source30 browser rows also compare equal.
Independent matching-version native DT reevaluation covers all 2,280 snapshots;
the recorded p/h/u differences from each browser's own independent DT evaluation
are zero in this finite sample. The 8.0 and 7.2 physical reference roots all
converge; original PH-derived failures, DU exceptions and support errors persist
in the result files. No failed assertion or measurement was suppressed.
All 25 reused historical fixtures' base/probe records also match the original
B2 outputs exactly for each of the eight artifact/engine combinations.

Instrumentation30/44 each compare equal to their uninstrumented control over
all 57 native rows, including paired inventories. Every preserved repeated
default source probe/PT trace compares exactly equal. Source inspection supports
interpretation, but the classification is grounded in the captured comparisons,
branch assignments, density calculation and independent roots.

Setup attempts remain in `setup-attempts.json` and raw failure/build logs. The
sequential campaign shell ended with an EOF harness error **after** all named
compilations and scientific outputs completed, because its script was edited
during execution. That campaign exit is not labeled a successful shell run.
Each individual output, trace, baseline comparison and final script syntax was
checked; no absent run is counted. The corrected final script supports a fresh
isolated replay. An earlier anchor assertion changed no source or measurement;
the initial misnamed diff was moved byte-for-byte and its identity corrected.

The liquid pressure residual fails the original standalone <10 Pa budget;
its h residual alone passes the coarse <50 J/kg value budget. All three canonical
budgets fail for the bad primary inventory. Stable physical inventory A passes
those same budgets. Passing a coarse value, derivative subset or conservation
ledger cannot certify an inconsistent state. Original mass <1e−8 kg, energy
<1e−6 kJ, nonlinear <=1e−11, thermal <=1e−12 K and all accepted temporal/frozen
reference budgets remain unchanged; no new dynamics campaign is claimed.

Unresolved limits are explicit: finite ammonia-only pressure/boundary sampling;
no critical-region, mixture or global phase-accuracy qualification; no separate
experimental EOS reference; no internal WASM or 7.2 source trace; native7.2's
35-bar DU exceptions remain causally unresolved; small DU endpoint/guard
behavior remains; no corrective candidate has been implemented or qualified;
no complete B2 rerun, long run or physical Safari/iPad validation. Native source
traces and matching browser symptoms support the browser attribution, but are
not presented as captured browser-internal execution.

[REPAIR_PROPOSALS.md](REPAIR_PROPOSALS.md) gives separate source-path candidates,
risks and proposed B4 acceptance gates. [README.md](README.md) supplies bounded
reproduction commands and evidence locations. The original checkpoints, model,
solver, inventories, perturbations, tolerances, EOS data, UI and Live Plant are
preserved. **Stop for engineering review and explicit approval.** No merge,
deployment, publication, production backend replacement or B4 correction occurs.
