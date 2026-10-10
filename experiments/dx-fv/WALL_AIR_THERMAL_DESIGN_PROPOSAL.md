# Design proposal: conservative tube/fin wall and air thermal model

**Proposal only — implementation requires explicit approval.** Scope is an isolated DX component on `experimental/dx-fv-stage-3`, starting from preserved spatial milestone `c105584311ca4a539c8410bf02ae0519b2bc8448`. Five sections is the provisional baseline; nine is a comparison, not continuum truth. No circuit, UI, profile, equipment calibration or production change is included.

## Purpose and selected architecture

Replace a prescribed refrigerant heat source in a new experimental mode with an explicit thermal network whose heat exchange responds to temperature and whose stored energy is conserved. Keep the historical prescribed-heat mode and its qualified tests as a separate restore/regression baseline. A different thermal model is a different physical problem; reduced excursions versus that baseline cannot alone prove improved spatial accuracy.

Recommend one tube node and one fin node per refrigerant section, with a **single finite, well-mixed sensible-air control volume** initially. Explicit separate metal states represent both tube and fin capacity/contact coupling. A combined tube/fin node is a possible later simplification only after demonstrating negligible internal temperature differences/time scales; it must not silently assume massless fins. A prescribed-temperature air reservoir can be a separate test boundary, with all heat crossing it recorded externally. Distributed air transport, moisture/frost, defrost and detailed fin temperature profiles are deferred.

A finite well-mixed air node is deliberately a minimal closure, not a coil airflow rating. Retain the same air volume/mass when refining refrigerant sections. It avoids accidentally changing air physics with section count. Future co-/counter-/crossflow air discretization requires its own geometry and convergence study.

## States, parameters and units

Refrigerant retains canonical section M/U/V and current equilibrium property recovery. Add tube energy E_t,i, fin energy E_f,i and air energy E_a. Thermal temperatures are recovered from those energies, not imposed on the refrigerant. Use kJ, kW, kg, s and K or consistently converted °C differences; conductance is kW/K, heat capacity kJ/K. Explicitly convert material data supplied in J/(kg·K) or W/K.

For a solid thermal node with fixed material mass:

`E(T) = m * integral[T_ref to T] cp(theta) dtheta`, and `C(T) = dE/dT > 0`.

For fixed-volume air use internal energy `E_a = m_a * integral cv_air(T) dT`; ventilation carries enthalpy `h_air = integral cp_air(T) dT`. Declare the ideal-gas sensible-air approximation and reference consistently; do not use cp for fixed-volume internal energy while also counting flow work through enthalpy. Air pressure dynamics and compressible airflow are outside this initial closure. Use a common documented reference convention and an invertible E(T). Initial prototype may use declared constant positive cp/capacity; variable cp needs independently checked integration/inversion and a material validity range. Wall temperature is not constrained by the refrigerant property-table temperature limit; each material has its own declared valid range.

Configurable experiment inputs must identify assumptions and provenance:

| Parameter group | Required declarations |
| --- | --- |
| Tube | Existing refrigerant geometry, outer diameter/thickness, material density/cp, wetted inner area, exposed bare external area |
| Fins | Count/pitch, thickness, net material volume excluding tube holes, exposed area, density/cp, tube-fin contact conductance |
| Heat transfer | Air-to-bare-tube and air-to-fin conductances; tube-to-refrigerant conductance; correlation domain if used; optional axial metal conduction |
| Air | Fixed volume/mass, cv and cp, initial temperature; external sensible load and optional ventilation mass/enthalpy boundaries |
| Initial conditions | Explicit tube, fin, air temperatures and refrigerant state/inventory profiles |
| Numerics | Separate thermal energy/temperature error scales, supported parameter bounds, tolerances and diagnostic budgets |

Tube mass follows `rho_material * π/4 * (D_outer²-D_inner²) * L`; fin mass follows actual net fin volume and density. These parameters are not inferred from desired superheat or tuned to suppress a domain stop. Preserve existing total refrigerant volume/length/restrictions. Do not alter Default profiles in this stage; use explicit experimental configurations. Missing equipment data must remain labeled illustrative, with no manufacturer fidelity claim.

For N sections, distribute capacity and transfer area by physical length/area fractions so their sums are invariant. Uniform local radial G and C scale with section length, not with interface count. If axial conduction is included, internal `G_ax = k*A/Δx`, with correct boundary/half-cell resistance, rather than G/N. Nonuniform initial profiles must be projected by **integrated energy** and inverted to temperature; averaging temperatures is not energy conserving when cp varies.

## Temperature-driven transfers and paired accounting

Define positive heat-transfer rates:

- `Q_at,i = G_at,i * (T_a - T_t,i)` — air to bare tube.
- `Q_af,i = G_af,i * (T_a - T_f,i)` — air to fin.
- `Q_ft,i = G_ft,i * (T_f,i - T_t,i)` — fin to tube.
- `Q_tr,i = G_tr,i * (T_t,i - T_r,i)` — tube to refrigerant.

All rates are signed and may reverse. A hotter refrigerant can heat the metal/air. Compute each link once per implicit stage and reuse exactly opposite energy contributions. Do not clamp Q to enforce cooling. Avoid double counting fin area or resistance: the fin-node conductance approximation must specify whether an effective fin correction is already included. A lumped dynamic fin plus a steady fin-efficiency formula is not automatically a consistent distributed-fin model; begin with an explicitly declared lumped network and independently qualify any later correction.

Balances without optional axial conduction:

```text
dM_r,i/dt = sum(signed refrigerant mass face fluxes)
dU_r,i/dt = sum(signed refrigerant enthalpy face fluxes) + Q_tr,i
dE_t,i/dt = Q_at,i + Q_ft,i - Q_tr,i
dE_f,i/dt = Q_af,i - Q_ft,i
dE_a/dt   = Q_load + air enthalpy inflow - air enthalpy outflow
             - sum_i(Q_at,i + Q_af,i)
```

Axial links, if later approved, also appear with opposite signs in adjacent metal nodes. The whole-system energy derivative is only refrigerant boundary enthalpy flow, air boundary enthalpy flow and declared external Q_load. Internal thermal links cancel. No friction-energy sink or extra evaporator heat is added to the enthalpy transport already accounting for flow work.

For a prescribed-temperature reservoir instead of finite air, omit E_a and treat its signed Q_at/Q_af as measured external boundary heat. Never hold finite-air temperature fixed while ignoring the energy required. A time-dependent setpoint is a reservoir boundary, not an instantaneous reset of a finite node's stored energy.

`Q_load` heats finite air; `Q_tr` is actual refrigeration heat. Do not also impose the old 12/18 kW directly into refrigerant. Mapping those old fixtures to a thermal experiment requires specifying air/wall initial temperatures, capacities and loads; there is no unique equivalent transient. In particular, the old warm fixture lacks an air temperature, so its 12 kW cannot define a unique physical warm-start thermal case.

Initially use positive declared conductances with no unvalidated phase switch. Later refrigerant heat-transfer correlations must account for phase/regime and their domains. Equilibrium bulk quality alone cannot locate a liquid film/dryout threshold. Smooth numerical regularization must preserve declared physical limits and be tested for sensitivity, rather than hiding discontinuities or fabricating vapor. Heat-transfer correlations and transport closure must be validated separately.

## Coupling and time integration

Retain adaptive TR-BDF2 as the initial candidate, but requalify it with thermal states. Solve refrigerant and metal/air energies **in the same implicit stages**. Use identical stage quadrature for every paired thermal transfer and both sides of each link. Avoid initial operator splitting: exact ledger cancellation alone would not make a split solution temporally accurate.

At every stage, recover refrigerant T from canonical M/U/V and wall/air T from E. Pressure remains a refrigerant EOS/transport result. Do not impose refrigerant temperature or PH from wall temperature; retain homogeneous-mixture donor transport and existing hydraulics to isolate the thermal change. Air mass is fixed for a closed node; optional balanced ventilation has explicit inlet/outlet energy accounting. Variable air mass or humidity is out of initial scope.

Extend the step-doubling norm to thermal energies and temperatures with declared absolute/relative scales; retain existing fluid M/U/PH controls and phase/event bracketing. A large metal energy must not mask fluid error, and a near-zero reference energy must not make relative tolerances meaningless. Reject nonrecoverable trial states and roll back **all** fluid/metal/air states, thermal/boundary ledgers, clocks and event evidence. Distinguish nonlinear convergence, accuracy exhaustion and supported-domain exit. External boundary changes remain atomic and do not reset stored energy or advance time.

Thermal time scales C/G may be much shorter than circuit time scales. L-stability does not guarantee time accuracy. Compare with backward Euler and an independently refined direct-EOS continuous-time reference, including stiff but finite capacities. C=0 is an algebraic limit, not a valid zero-capacity dynamic energy node; do not introduce singular states to force quasi-steady behavior.

## Startup, shutdown and disturbances

Initialize all material/air energies from explicit temperatures and fluid inventories. Preserve identical total initial energies across meshes. Document whether wall/fin/air begin equilibrated or out of equilibrium; do not manufacture a favorable initial wall temperature.

During startup, finite wall capacity moderates heat exchange, while signed transfer changes with source/fluid temperature. It may alter the warm pulse, but the model must still stop honestly if actual refrigerant states leave supported properties. During shutdown/feed isolation, wall and air continue exchanging heat with standing refrigerant; refrigerant mass stays conserved for sealed boundaries. Do not zero stored energy, force superheat or make all heat vanish merely because feed closes.

Represent load steps at the external air-load boundary. Air temperature, metal temperature and actual Q_tr then respond dynamically. Fan changes modify only explicitly modeled conductances/ventilation; off-state natural convection needs declared data, or an explicit isolated-air test boundary. Fan electrical heat and latent loads are not implicit sources. Separate boundary pressure/feed changes from air-load changes so causality and conservation are identifiable.

No attached compressor exists in this stage. Wet outlet remains visible. A future circuit must use actual outlet fluid and appropriate compressor admissibility; wall modeling must not guarantee dry suction by construction. No arbitrary evaporator liquid-level shutdown is proposed.

## Validation and proposed acceptance contract

Freeze c105584 baseline fixtures/references. New acceptance limits below are proposed for design approval, not achieved results. Declare each test's domains, scales and event definition before evaluating results.

| Verification | Proposed requirement |
| --- | --- |
| Paired links | Equal/opposite stage contributions from a single computed flux; closed-system total energy conserved with signed heat reversal |
| Refrigerant accounting | Retain per-section/global 1e-8 kg mass and 1e-6 kJ energy residual limits in existing fixtures |
| Combined energy | Initial target 1e-6 kJ absolute residual for bounded thermal fixtures; report absolute and energy-scale-relative residuals separately. If larger material energies challenge roundoff, justify a scale-aware budget independently before changing the criterion |
| Analytic network | Constant-C/G closed tube/fin/air networks agree with an independent matrix exponential; equilibrium temperatures follow total energy, not a forced setpoint |
| Thermodynamic recovery | Liquid/mixture/vapor states agree with direct CoolProp, with errors separated from interpolation; variable-cp energy inversion verified independently |
| Temporal refinement | On both meshes, nominal/tight/reference and independent max-step refinement resolve temperature, enthalpy, inventory and energy. Proposed nominal targets: temperature <0.01 K, h <0.05 kJ/kg against tight reference in supported fixtures; retain stricter historical thresholds where applicable |
| Events | Define terminal and common-port wet/dry events separately. Proposed well-conditioned crossing timing uncertainty <1 ms; demonstrate bracket/tolerance refinement. Flag grazing/ambiguous crossings rather than claiming universal timing accuracy |
| Long runs | At least one hour of supported wet and dry operation on both meshes, no drift/hidden energy source; equilibrium/reference budgets close |
| Rollback/stops | Forced solver/accuracy/domain failures preserve the last accepted complete state and original evidence; no clipping, extrapolation or invalid continuation |
| Spatial assessment | Report signed 5→9 changes in outlet intensives, total/distributed inventory, metal/air energy, heat distribution, pressure drop and phase timing. Small time errors required first; agreement alone does not prove convergence |
| Performance | Record Chromium/WebKit wall time, residual/Newton work, worst advance latency, Node isolated peak RSS/retained heap and serialized size. No main-thread or iPad acceptance claim without device/integration measurements |

Independent thermal tests should include a two-node analytic heat-exchange solution, a three-node matrix-exponential solution, heat reversal, adiabatic equilibrium, externally heated air with exact integral input, and balanced ventilation. Then build a separate Python conserved-M/U/thermal-energy Radau reference with direct EOS and independently coded thermal equations, refine that reference and compare event timing. Shared EOS/correlations still do not supply measured equipment validation.

## Required five/nine-section test matrix and repeated comparisons

Use identical total tube/fin masses and capacities, area/conductance distributions, air mass/volume, geometry, hydraulic coefficients, initial energy profiles and boundaries. Air node count stays fixed. Use the common physical coordinate/bin comparisons; never compare shifted terminal centers as a common measurement. Sample outlet p/h/T/superheat/quality at the same port, and retain unsupported recovery evidence.

1. **Thermal network qualification:** closed/loaded/ventilated constant-capacity networks, initial hot/cold metal, reversible heat flow, weak/strong finite conductance, variable-cp inversion if implemented. Independent analytic/reference cases precede fluid coupling.
2. **Coupled startup:** cold-wet and warm-dry fluid, independently varied air/tube/fin initial temperatures, feed opening and sealed startup. Record fluid and metal energy distribution and local source/advection budgets.
3. **Disturbances:** air heat-load increase/decrease, declared air reservoir temperature steps in that boundary mode, feed pressure/availability changes and conductance/fan changes. Distinguish wet/dry terminal crossings from sampled port wetness; localize port events if claiming their times.
4. **Shutdown/restart:** feed isolation/reopening and explicitly defined outlet boundaries, residual wall heat, sealed heat/cooling phase transitions. Preserve all inventories and time through rejected updates/trials.
5. **Extended operation:** wet/dry and graded-area/load cases, one hour minimum at nominal settings, with tight matched shorter intervals to qualify time accuracy. Domain exit is retained and unsupported continuation excluded.
6. **Warm-domain comparison:** rerun the untouched prescribed 0/6/12 kW baselines as regression evidence. Separately test temperature-driven warm starts with fully declared thermal initial states; compare supported intervals, budgets and time-refined domain clocks. Any continuation difference is a physical-model sensitivity result, not proof of convergence or a guaranteed cure.

Repeat the earlier BE-versus-TR-BDF2 accuracy/cost assessment on representative coupled thermal transients; all five/nine adaptive tolerance refinements and independent maximum-step refinements; direct-EOS steady shooting/transient Radau reference agreement with new thermal balances; startup/load/feed/phase timing; hour-long mass/energy ledgers; rollback/domain classification; inventory/pressure/outlet spatial comparisons; and fresh-process Node plus Chromium/WebKit benchmarks. Keep all legacy application and original 3/5/9 prescribed-heat suites enabled. Historical three-section results remain frozen; no new finer-than-nine study or automatic section-count escalation is included.

Old prescribed heat produced 12/18 kW steady cases. A new finite-air load may approach that duty at equilibrium but stores energy during transients; do not assert identical instantaneous refrigerant heat. Compare old versus new models only with explicit source/initial-energy differences documented. Temporal convergence on each new mesh must precede attribution of residual differences to space.

## Limits this proposal does not resolve

**Homogeneous mixture:** heat storage does not supply phase slip, film/entrainment, dryout, distribution among circuits or a carryover closure. Spatially smeared evaporation fronts may remain. A thermal correlation cannot silently introduce missing transport physics.

**Pressure losses:** constant f/μ, horizontal quasi-steady donor-density resistance and omitted momentum/gravity/choking remain screening assumptions. Changing temperatures changes density/flow but does not validate hydraulic predictions. Later closure/data comparisons need separate scope.

**Property domain:** temperature feedback may reduce or reverse heat in a hot cell, but boundaries may still drive unsupported p/h. Preserve table limits, classify true domain exits and exclude invalid intervals. A direct-EOS diagnostic outside the table does not authorize extending runtime properties. Wall/air temperatures need independently declared material models.

**Computational cost:** two fluid coordinates plus tube/fin energies per section and one air energy give roughly `4N+1` unknowns (21 at five, 37 at nine), versus 2N currently. Dense Jacobian/linear algebra and added thermal stiffness may materially increase cost; baseline nine/five ~2.1× browser startup cost cannot be extrapolated as the new ratio. Investigate block/sparse Jacobians only after a validated coupled prototype and benchmark, preserving conservation/error control. Worker scheduling or UI changes are outside this proposal's initial implementation scope.

**Calibration and circuit integration:** fin geometry, UA/correlations, contact resistance and capacity data are not available from current toy fixtures. No Default recalibration is authorized. A complete connected circuit will require separate compressor/valve control, sensor, dry-suction, profile, diagnostic, schematic and training migration/acceptance. Existing controllers and equipment behavior stay untouched here.

## Staged implementation proposal and approval gates

1. **Design/input approval (pending):** agree the two-node wall/one-node finite-air architecture, declared illustrative parameter set, reservoir test contract, error budgets and domain diagnostics. Preserve c105584 and this documentation commit as restore points. Obtain explicit authorization before code changes.
2. **Minimal isolated thermal network:** constant positive capacities/conductances, signed paired links, analytic references, initial energy/configuration contracts and rollback. No new transport or equipment calibration.
3. **Five-section coupled prototype:** add thermal energies to implicit TR-BDF2 stages, extend error control and ledgers, retain old prescribed-heat path. Qualify closed/network and startup/phase tests against independent references before nine-section claims.
4. **Temporal qualification and controlled five/nine comparison:** independently refine each mesh; repeat matched startup, disturbances, shutdown, domain diagnostics and extended runs. Report spatial differences without calling nine converged.
5. **Performance and review:** benchmark both browser engines and memory/work; identify any physical-device/background scheduling work needed later. Deliver results, limitations and a recommended next decision, then wait for approval.

No automatic transition to new transport closures, equipment calibration, finer meshes, Live Plant/UI integration, production changes or merging follows from any pass. Approve stage scope explicitly and retain a validated restore commit at each review boundary.
