# Isolated conservative DX finite-volume prototype — roadmap stages 1–3

The authorized standalone tube/fin/air thermal Stage 1 is documented in [THERMAL_STAGE_1.md](THERMAL_STAGE_1.md), with separate thermal references, numerical tests and cost reports. It has no refrigerant coupling and changes no existing DX physics. The earlier handoff and authorization statements below describe their frozen stages; any next refrigerant-coupling stage still requires explicit approval.

For the current project transition and approval boundary, read [DEVELOPMENT_HANDOFF.md](DEVELOPMENT_HANDOFF.md) and the unimplemented [wall/air thermal design proposal](WALL_AIR_THERMAL_DESIGN_PROPOSAL.md). The completed spatial milestone is `c105584311ca4a539c8410bf02ae0519b2bc8448`; five sections is the provisional baseline and nine the comparison. Neither is proven converged. Current authorization is documentation only; historical stage restrictions below describe those frozen stages.

The subsequent approved **three-section numerical time-accuracy stage** is documented in [TIME_ACCURACY.md](TIME_ACCURACY.md), including conservative adaptive TR-BDF2, comparisons, event timing, browser cost and remaining limitations. The results below retain the original Stage 3 baseline.

The approved **three-versus-five-section comparison** is documented in [SPATIAL_RESOLUTION.md](SPATIAL_RESOLUTION.md). It independently qualifies time accuracy on both meshes, compares conserved inventory and phase timing, and records the five-section warm-start domain limitation. Three-section-only statements below describe the original Stage 3 baseline.

The approved **3/5/9-section comparison** is documented in [NINE_SECTION_COMPARISON.md](NINE_SECTION_COMPARISON.md), including separate temporal qualification, supported-interval convergence evidence, heat-source domain diagnostics and cost/memory measurements. No finer mesh or circuit integration is included.

Experimental branch: `experimental/dx-fv-stage-3`. This is a Node-testable component, not a replacement for Live plant, a new UI, or a complete refrigeration circuit. Production, PR #3, the existing connected model, equipment schemas, controls, training and generated standalone HTML are unchanged. See [RESTORE_POINTS.md](RESTORE_POINTS.md).

The architecture derives its arrays, faces, residuals and solver dimension from `sectionCount`. The default is three; the supported configuration range is bounded for input validation. **Only three sections are instantiated and validated in this stage.** Five-section or finer experiments require a subsequent approval. No spatial-accuracy claim is made yet.

## Run

From the repository root:

```sh
node experiments/dx-fv/test.cjs /tmp/dx-fv-results.json
```

This uses frozen direct-EOS references. To independently regenerate them with Python 3.12:

```sh
python -m venv /tmp/dx-fv-reference
/tmp/dx-fv-reference/bin/pip install CoolProp==7.2.0 numpy==2.5.3
/tmp/dx-fv-reference/bin/python experiments/dx-fv/generate_reference.py /tmp/dx-fv-reference.json
DX_FV_REFERENCE_PATH=/tmp/dx-fv-reference.json node experiments/dx-fv/test.cjs /tmp/dx-fv-live-results.json
```

The experimental workflow runs existing numerical regressions, the prototype, fresh direct-EOS reference regeneration/comparison, and the existing standalone build-consistency check. It uploads machine-readable verification results. Browser/UI files do not import this prototype.

## Shared contracts

All runtime values use SI-compatible units: mass kg, volume m³, pressure **bar absolute**, enthalpy/internal energy kJ/kg or kJ, heat/enthalpy flow kW, and time s. Pressure conversion in stored energy is explicit: `U = m*h − 100*p*V`.

- `conservation.cjs`: inventory conversion, a signed face mass/enthalpy flux, rate assembly and totals. A face is calculated once and shared by both adjacent sections with opposite signs. The external inlet/outlet ledger explains changes to total inventory in this open component; it does not falsely assert constant mass for an open exchanger. Each section has its own integrated face/heat ledger and conservation residual.
- `thermodynamics.cjs`: bounded `p/h` evaluation, inventory initialization and canonical `m/V/U` recovery through the unchanged engine. Liquid, mixture and vapor all use actual bulk enthalpy. No vapor selector, inventory clipping, extra vapor volume or running superheat prescription exists. Pressure/enthalpy are nonlinear solve coordinates; accepted physical state remains mass/internal energy/fixed volume. Canonical recovery must succeed before commitment.
- `hydraulics.cjs`: signed pressure-driven homogeneous-mixture transport, including reverse flow and explicitly declared check/shutoff behavior. For horizontal connections, `ΔP = a*m_dot + b*m_dot*abs(m_dot)`, where `a = 128*mu*L/(pi*D^4*rho)` and `b = (f*L/D + K)/(2*rho*A^2)`. The linear viscous term supplies a finite near-zero-flow response; the declared distributed/local inertial losses provide the quadratic term. Donor density and donor bulk enthalpy follow the flow direction. Pressure loss is not an energy sink: paired enthalpy transport accounts for flow work under the low-Mach approximation.
- `implicit.cjs`: backward Euler through damped Newton iterations, a finite-difference Jacobian and a pivoted dense linear solve. Failed trials halve the step; an exhausted numerical limit records a solver stop. If all line-search candidates leave the property domain, the property-domain cause is retained. It does not increase the EOS range.
- `evaporator.cjs`: configurable sections/volume fractions, one connection per face, prescribed `p/h` reservoirs, signed distributed heat inputs, accepted-only time/ledgers, detached returned records and atomic boundary edits. No compressor, PI, room, wall, equipment-profile or UI integration is present.

`create(config)`, `advance(state, seconds)`, `update(state, boundaryPatch)` and `record(state)` are isolated component interfaces. `trial(state, dt)` solves an uncommitted trial for diagnostics. Boundary edits do not advance time or alter inventory. A retained stop freezes subsequent advancement; this prototype reinitializes to start another experiment.

## Prototype geometry and assumptions

The test fixture uses three equal 0.001 m³ sections: 0.003 m³ total, 0.02 m equivalent flow diameter, and derived face-to-face lengths. It uses illustrative constant viscosity 1e-5 Pa·s, Darcy coefficient 0.02, inlet local-loss coefficient 1000 and outlet coefficient 2. The high inlet restriction is a declared screening/test coefficient, not inferred manufacturer geometry or a calibrated flashing valve. Actual coil/valve geometry and two-phase correlations require later requalification.

The upstream reservoir is 4 bar / 500 kJ/kg; the downstream reservoir is 3.5 bar / 1700 kJ/kg. Inlet enthalpy represents a supplied flashed-mixture boundary, not an implemented expansion valve. Reservoir pressure is a boundary, not prescribed section pressure. All three section pressures are solved from inventory and pressure-driven transport. The downstream reservoir enthalpy only becomes a donor value on reverse flow.

Heat is supplied as a declared rate per section. There is zero modeled wall/room energy storage and no heat-transfer correlation in this minimal isolation experiment. Future thermal components must pair their heat exchange with this ledger. No wall mass, ambient heat, separator or dry section is fabricated.

The mixture is homogeneous and in local thermodynamic equilibrium. There is no slip/void-fraction correlation, flow-regime selection, liquid-film model, entrainment, parallel-circuit maldistribution, gravity, choked-flow model, momentum storage or kinetic-energy inventory. The low-Mach quasi-steady resistance relation is a screening closure, not a universal two-phase piping law. Friction factor and viscosity are uncalibrated assumptions. Tests do not establish admissibility for severe pressure ratios or high mass flux.

## Observed results

Reference data and results are in [reference.json](reference.json) and [RESULTS.json](RESULTS.json). Numbers below describe the three-section fixture, **not Default plant performance**.

| Check | Observed result |
| --- | --- |
| 40 direct CoolProp liquid/mixture/vapor property states | Max p/h temperature difference 0.00626 K; density relative difference 0.0566%; canonical recovery pressure difference 0.0158 bar and temperature difference 0.00450 K |
| Three independently shot direct-EOS steady solutions | Max relative flow difference 0.000394%; section pressure difference <1e-6 bar; enthalpy difference 0.00474 kJ/kg; temperature difference 0.00177 K |
| Independently implemented direct-EOS backward-Euler startup, 1 s at 0.025 s steps | Max section pressure difference <1e-6 bar; enthalpy difference 0.00237 kJ/kg; temperature difference 0.000161 K |
| 18 kW distributed heat (6/6/6) | Progressive evaporation: first two sections remain mixtures, terminal becomes dry with about 41.54 K superheat |
| Reduce heat to 12 kW (4/4/4) | Terminal quality settles near 0.7595, with zero superheat and an explicit wet diagnostic |
| Restore heat to 18 kW | Dry terminal recovers; no prescribed superheat or inventory repair |
| Initially liquid-full sections | Actual liquid/mixture transport continues; no disappearance of the outlet path based on unavailable selected vapor |
| Sealed heat then cooling | Boiling/drying and condensation cross saturation with unchanged total mass and conserved energy |
| One-hour dry isolated operation | Mass residual magnitude ~6.7e-11 kg; energy residual ~1.15e-7 kJ; bounded inventory, no stop |
| One-hour wet isolated operation | Mass residual magnitude ~8.3e-10 kg; energy residual ~2.66e-7 kJ; wet terminal remains visible, no fabricated vapor |

The hour-long dry case took roughly 2–4 seconds on this execution host, with 7200 accepted 0.5 s steps. This is a single-host observation, not an iPad benchmark or production performance budget. The tests enforce all section and global residuals below 1e-8 kg and 1e-6 kJ. Hardware-dependent timing is recorded but not an acceptance assertion.

The nominal 41.54 K superheat is intentionally a consequence of the supplied fixture boundaries/heat, not a tuned DX design target. It demonstrates thermodynamic behavior and reference agreement. These values must not be copied into Default calibration.

The reference generator uses direct CoolProp 7.2.0, bypassing the embedded property table. It separately implements steady shooting and a Python/NumPy transient balance solve; it does not call this JavaScript prototype. CoolProp remains the same EOS source as the existing table. These comparisons validate interpolation, implementation and numerical consistency, **not independent measured equipment accuracy**.

## Numerical accuracy and failure distinctions

Backward Euler is stable in the tested stiff startup/phase cases, but is first-order and damping. For the same wet startup at 1 s, terminal enthalpy is approximately 1490.516, 1485.956, 1483.000 and 1481.362 kJ/kg at steps 0.2, 0.1, 0.05 and 0.025 s. Errors decrease under refinement. Direct-EOS agreement at the **same** timestep does not imply that 0.5 s steps resolve fast startup accurately. A higher-order comparison, automatic time-error control and phase-event timing validation remain outstanding.

At steady state, 0.5/0.25/0.125 s runs agree much more closely. An accepted solver residual is a balance-equation residual, not a local truncation-error estimate. Adaptive halving currently responds to nonlinear convergence/domain difficulties, not a calibrated time-accuracy estimator. Requested end times can introduce shorter final steps; arbitrary playback batching invariance is not claimed. Live scheduling/deadline contracts are deferred to approved integration work.

One intentionally concentrated startup heat distribution (2/4/12 kW with a low-mass initially dry terminal) reaches the existing 250 K-superheat property boundary around 0.546 s. This is recorded as a **domain** stop, with the last valid inventory retained. The same heat distribution has a valid steady state from an appropriate initial condition; startup thermal storage and boundary conditions matter.

A deliberately insufficient Newton iteration budget produces a distinct **solver** stop without consuming physical time or changing inventories/ledgers. The tests verify rejection rollback and frozen stops. Wet terminal fluid is a diagnostic in this isolated exchanger; without an attached compressor it is not labeled an equipment trip or forced to stop. Full compressor wet-suction event handling is deferred.

## Credibility relative to the existing model

The existing model cannot transfer selected vapor from a liquid-only core. A focused comparison verifies that limitation and demonstrates a positive, conservative liquid/mixture interface flux for the same source phase in the prototype. Reduced heat and increased feed pressure produce wet terminal states rather than preserving dry vapor selection. This is a credible improvement in the **transport mechanism**.

The fixture geometry, boundaries and thermal model differ from the current closed circuit. These results do not demonstrate that Default's 796/1080-second failure is fixed in the application, that its operating point is calibrated, or that the complete circuit will be stable. Existing UI/circuit code is deliberately unchanged.

## Verification scope and next decision

`test.cjs` exercises only three sections: property references, independent steady/transient references, shared signed fluxes, reverse/check/closed connections, cold startup, load and pressure disturbances, wet/dry recovery, feed isolation, liquid-full transport, sealed phase transitions, global/per-section ledgers, atomic rejection, numerical rollback/freezing, model-domain/solver distinction, timestep refinement and dry/wet one-hour operation.

All existing numerical tests remain enabled. The isolated workflow also regenerates references and checks that the existing standalone build remains consistent. Browser tests are unaffected because no application file or UI imports the experiment; this stage does not claim physical-device validation.

Recommended next work, pending explicit approval:

1. Review these three-section results and the homogeneous pressure-loss assumptions. Define a meaningful time-accuracy/error-control target and evaluate a higher-order conservative method and wet-phase event localization.
2. Supply/requalify thermal and geometric parameters; add declared wall heat storage and air-side coupling only within a separately approved stage.
3. Obtain approval for five-section/finer spatial comparisons before claiming mesh accuracy or choosing production section count.
4. Only after those decisions, approve coupling to receiver/valve/compressor and requalify Default, control gains, diagnostics, profiles, schematics and training.

No later integration stage or merge is authorized by these prototype results.
