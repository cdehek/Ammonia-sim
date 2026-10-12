# Stage 2B phase-event timing investigation

**Diagnostic-only investigation completed. No correction implemented.**
The leading cause is saturation-temperature interpolation error in the existing
property source. Its small positive temperature bias changes the accumulated
coupled heat transfer and phase-transition time. The original accepted five-section
solver reproduces the discrepancy exactly; it is a pre-existing accuracy limitation
newly exposed by this extended boundary scenario, not a Stage 2B five-section
regression or evidence against nine-section construction.

Branch `experimental/dx-fv-stage-3`, HEAD
`be9eb35a4ddf5098e685182f8104685127c6a6ee`. The previous eight-file uncommitted
Stage 2B candidate and all failure evidence remain intact. No commit/push, default
change, frozen-reference replacement, acceptance relaxation or production change.
Stage 2B remains unqualified pending the user's decision and later complete checks.

## Event identity and exact errors

Both implementations locate the **terminal refrigerant control volume's bulk dew
crossing**, `g=h-hg(p_bulk)=0`, from negative to positive (wet to vapor/heating).
The volume stays fixed. This is neither finite-air/tube temperature nor outlet-port
superheat at the imposed outlet pressure. JS uses actual saturation margins, not
quality flags or a superheat clamp; the independent EOS uses the same criterion
on its last M/U pair. Root quality is approximately one. At precisely the boundary,
CoolProp can label a rounded result saturated or single-phase; that label does not
enter either event criterion.

| Mesh | Zero-based cell / physical x/L interval | JS event s | Converged EOS event s | Error ms | Requirement |
| --- | --- | ---: | ---: | ---: | --- |
| 5 | 4 / [0.800000, 1] | 146.383507171434 | 146.382180249400 | 1.326922 | <1 ms; fails |
| 9 | 8 / [0.888889, 1] | 146.911304327853 | 146.909931921277 | 1.372407 | <1 ms; fails |

At the EOS crossing, five/nine bulk pressures are 3.500008233/3.500006012 bar;
h is 1601.489422/1601.489403 kJ/kg; temperature is
267.811495/267.811479 K; density is 2.848907/2.848906 kg/m³. Terminal M/U
are 0.001709344 kg / 2.527496379 kJ and 0.000949635 kg / 1.404163799 kJ.
The physical intervals differ between meshes. The EOS five/nine clock difference
is **0.527751672 s**, a discretization/location difference distinct from each
mesh's approximately 1.3 ms numerical disagreement with its own EOS reference.
Neither mesh is declared spatially converged or physically exact.

The first event follows the prescribed 120 s removal of feed pressure drive and
air load (inlet becomes 3.5 bar/h=500, air load 0; outlet stays 3.5 bar/h=1700).
Stored tube/fin/air energy continues to feed the fluid as inventory discharges.
Later 180/240 s changes cannot affect this event and were not replayed. Original
full 360 s evidence remains preserved; targeted prefixes are diagnostic evidence,
not shortened qualification or performance workloads.

## Reference convergence and localization

The saved independent cold endpoint at 120 s is the extended case's exact
pre-boundary checkpoint. Both existing coarse extended checkpoints match their
cold counterparts byte for byte. Direct-EOS local continuations use the same
independently assembled equations, augmented signed ledgers, HEOS, Radau, original
absolute tolerances, rtol 1e-10 and maxstep 0.025 s, from 120 to 147.5 s.
No accepted reference is regenerated or overwritten. Reconstructing checkpoint
M/U from saved rho/u and thermal energy from temperatures introduces only roundoff;
the five local clock reproduces its saved full fine-reference clock within 1.5 ns.

| Check | Five | Nine |
| --- | ---: | ---: |
| Existing coarse versus local fine EOS first-event difference | 25.694 ns | 11.091 ns |
| Table Radau maxstep 0.025 versus 0.0125 s, same rtol | 0.033 ns | 0.073 ns |
| Native JS half-step event bracket width | 10.415 µs | 24.933 µs |
| Native margin-linear clock versus conserved-linear dew root | -0.179 µs | -0.759 µs |
| Native clock versus 1 ms event-local independent replay | -0.113 µs | -0.239 µs |

EOS refinement is well below its unchanged <1 µs event-convergence requirement.
JS detects crossings in accepted fine half-step endpoints and interpolates linearly
in `h-hg`. SciPy detects sign changes on its internal steps and applies Brent root
finding to the same scalar evaluated on cubic Radau dense output in conserved
coordinates. Its event residuals are below 6e-12 kJ/kg. The conserved-linear test
uses the algebraically equivalent dew surface `U-M*hg(p_dew)+100*p_dew*V=0`,
where the existing saturated-vapor density curve determines p_dew from M/V.
This is only an interpolation comparator; the accepted event definition is untouched.
The 1 ms replay begins from the recorded last accepted state and includes final-step
integration/recovery effects as well as localization. Neither measure explains
1.3 ms. No dense output is evaluated outside its integration interval.

Two local direct-EOS calculations exercised the independent generator's already
existing D/U-to-D/T flash fallback once near the dew boundary. Detached recordings
show zero density error and u error below 2e-12 kJ/kg, satisfying the original
1e-7 kJ/kg recovery requirement. Replays with recording enabled reproduce event
times, physical vectors and work counts exactly. No residual for a failed flash
was fabricated. Retained SciPy overflow warnings concern passive zero-Jacobian
ledger columns; successful solves and independent balances are audited separately.

## Conditioning and property attribution

Wet-side dense-output slopes at 0.1–1 ms distances are approximately
**51.64 and 50.54 kJ/(kg s)**. Dry-side margins also cross sharply; the short
pressure/phase adjustment changes the slope without making it shallow. Both
crossings are well-conditioned for this comparison. The earlier recorded secant
was insufficient alone; the one-sided measurements now confirm the conclusion.
The event surface itself differs slightly with property source: evaluating the
same EOS M/U through the protected engine gives only about 0.70/0.71 µs of
margin-equivalent timing displacement. The large error builds up in evolution.

An independent table-property comparator uses the unchanged `properties.json`
constitutive interpolation and exact diagnostic inversion, with independently
assembled Radau equations. It is not a new accepted property engine or direct-EOS
reference. At the event-window samples it agrees with original PH/MUV APIs to
7.59e-8 kJ/kg in h, 2.92e-8 K in T and 1.41e-10 relative density, with zero
pressure difference. It separates table constitutive error from JS integration
and inversion precision. Original 32/38-iteration inversion routines remain unchanged.

The controlled temperature-component comparator starts from the same saved JS
M/U and thermal energies at 120 s. It retains direct-EOS pressure, density,
enthalpy and event surface, and adds only the measured table saturation-temperature
offset to heat-transfer evaluation. Paired fluid/tube energy and corresponding
ledgers receive equal/opposite contributions. This is a causal diagnostic ablation,
not a thermodynamically complete alternate reference or a qualified trajectory.
Its approximately 98% reproduction of the post-120-second property shift is strong
numerical evidence for temperature interpolation as the dominant contributor.

Signed timing attribution (exact sum; milliseconds):

| Contribution | Five | Nine |
| --- | ---: | ---: |
| Inherited differences through 120 s | -0.659951 | -0.677657 |
| Post-120 s table versus direct-EOS evolution | +2.026885 | +2.090759 |
| JS evolution versus independent same-table evolution | -0.039899 | -0.040457 |
| Event-local replay residual | -0.000113 | -0.000239 |
| Observed total error | +1.326922 | +1.372407 |

The temperature component contributes **1.982992/2.044812 ms**, **97.834%/97.802%** of post-120 s property divergence. Remaining post-120 s constitutive effects are **43.894/45.948 µs**. Inherited initial-inventory, property and integration effects before 120 s are measured together; their internal split is not claimed established.

The original linear interpolation in log pressure over [3.438994525,
3.507872201] bar overestimates saturation temperature by **0.00010836/0.00010839 K**
near the crossings. A warmer predicted fluid reduces tube-to-fluid heat input
under the unchanged conductance law. The finite tube/fin/air stores integrate
this tiny bias over the pressure-removal transient. Instantaneous temperature
error can be far inside its 0.01 K budget while event timing exceeds 1 ms.

Nominal/tight/resolved JS clocks approach the independent table clocks with
approximately 0.82/0.18/0.04 ms errors, consistent with temporal refinement.
The limiting table-versus-direct-EOS clock discrepancies are approximately
1.367/1.413 ms: more temporal refinement would expose, rather than remove, the
property-source discrepancy. The roughly 40 µs remainder includes temporal,
nonlinear and inversion effects; it is not asserted pure truncation error.
Pointwise inversion differences are much smaller than saturation interpolation.

## Legacy reproduction, safeguards and proposed remedy

Immutable `be9eb35a4ddf5098e685182f8104685127c6a6ee` coupled-model/implicit
sources reproduce all saved five-section initial/output records from 0 through
150 s **exactly**, including the failing event and solver work. Old/current local
five-source replays also match exactly. Five/nine checkpoint replays reproduce
the recorded clocks bit for bit; observer disabled/enabled states, records,
work and normal property-call counts hash identically. Capture uses detached
existing values; diagnostic property comparisons occur afterward in a separate
engine. No normal integration calculations are substituted.

Independent accounting passes original per-section/global mass <1e-8 kg,
fluid/node/combined energy <1e-6 kJ in every local comparator. The preservation
audit verifies **187 existing tracked/candidate files byte for byte**, including
all uncommitted Stage 2B files, accepted references, property data, workflows and
application code. No original assertion, numerical/physical setting or acceptance
budget is modified. Strict phase accuracy still **fails**; diagnostic audit success
means the evidence is consistent, not that Stage 2B qualifies.

**Smallest proposed correction experiment:** an explicitly selected, isolated
research saturation-temperature reconstruction with higher-order interpolation
of the existing frozen samples in log pressure. For example, a three-point
quadratic evaluated only at these two pressure points reduces T error from
approximately 108 µK to 0.425 µK. This point comparator has not been integrated
as a correction and is not global validation of quadratic interpolation.
Apply any proposed temperature reconstruction consistently to PH and canonical
recovery, including existing superheat/subcooling temperature offsets; retain
p/h/rho/u, M/U/V, physical equations, conductances, hydraulic closure, inversions,
all tolerances, event definition and optional A1/A2 selection. Keep original
interpolation as default and preserve `engine.js`/`properties.json` unchanged.

After separate approval, first test the full initial-to-first-event prefixes on
both meshes against the same converged EOS clocks, with domain/continuity and
monotonicity checks for the proposed reconstruction. If successful, resume every
held Stage 2B scientific/regression/browser check and full-duration operating
comparisons. Frozen references and the <1 ms event budget remain unchanged.
Do not compensate timestamps, recalibrate conductance, change event identity,
force a tighter timestep as a supposed property fix, or promote a new default.
A1/A2 efficiency options do not correct this constitutive temperature bias.

Remaining uncertainties are the small non-temperature constitutive contribution,
the inherited-state split before 120 s, and a candidate's global interpolation/
full-trajectory behavior. A focused correction experiment is justified by the
measured leading cause; further numerical optimization or a multi-hour diagnostic
matrix is unnecessary for this diagnosis. Implementation requires user approval.

## Reproduction and evidence

New files only: `phase-event-investigation.cjs`,
`phase_event_reference_diagnostics.py`, `phase_event_table_comparator.py`,
`audit_phase_event_investigation.py`, this report. All are under
`experiments/dx-fv/`. Node 22.23.3, Python 3.12.14, CoolProp 7.2.0,
NumPy 2.5.3, SciPy 1.16.2. Evidence lives in
`/tmp/ammonia-phase-event-evidence/`; original failure evidence remains
`/tmp/ammonia-stage2b-evidence/`. Archive retention across workspace replacement
is not guaranteed. No full qualification matrix was run.

Use the pinned Node/Python runtimes and the preserved Stage 2B evidence:

```sh
SAVED=/tmp/ammonia-stage2b-evidence
OUT=/tmp/ammonia-phase-event-evidence
node experiments/dx-fv/phase-event-investigation.cjs legacy-prefix "$OUT/legacy-prefix.json" 5
for pair in '5 five' '9 nine'; do
  set -- $pair
  node experiments/dx-fv/phase-event-investigation.cjs local "$OUT/local-$2-js.json" "$1" js
  python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/eos-$2-fine.json" "$1" eos 1e-10 .025
  python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/eos-$2-js-seed.json" "$1" js 1e-10 .025
  python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/table-$2-js-seed.json" "$1" js 1e-10 .025 table
  python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/temperature-$2-js-seed.json" "$1" js 1e-10 .025 sat-temperature
  python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/table-$2-refined.json" "$1" js 1e-10 .0125 table
  python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/localization-$2.json" "$1" checkpoint 1e-10 .025 table "$OUT/local-$2-js.json"
  node experiments/dx-fv/phase-event-investigation.cjs properties "$OUT/properties-$2.json" "$1" js "$OUT/eos-$2-fine.json"
  node experiments/dx-fv/phase-event-investigation.cjs table-check "$OUT/table-check-$2.json" "$1" js "$OUT/table-$2-js-seed.json"
  node experiments/dx-fv/phase-event-investigation.cjs localization-check "$OUT/localization-check-$2.json" "$1" js "$OUT/local-$2-js.json"
done
python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/eos-nine-recorded.json" 9 eos 1e-10 .025
python experiments/dx-fv/phase_event_reference_diagnostics.py "$SAVED" "$OUT/eos-five-js-seed-recorded.json" 5 js 1e-10 .025
python experiments/dx-fv/audit_phase_event_investigation.py "$OUT" "$OUT/audit.json" "$SAVED"
```

`preserved-files.json` is the pre-investigation worktree hash manifest retained
with the evidence. Reproduction requires that candidate snapshot and original
saved checkpoints; outputs are always separate diagnostic files, never frozen
reference replacements. Full numerical results, replay/equivalence assertions,
reference work counts, recovered flash records, warnings and conservation are in
`audit.json` and the individual JSON/log files. Wall-clock comparisons and solver
performance claims are outside this investigation. Stop for review before correction.
