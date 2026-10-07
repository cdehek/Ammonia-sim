# Connected DX circuit · v0.4.5 stage 3

Stage 3 adds a circulating circuit to the storage laboratory. It remains a development model awaiting stage-4 integrated validation and release. Use Live plant → Connected refrigerant circuit. Select circulating DX, room/ambient boundaries, enable the compressor at 70%, select automatic feed control, and initialize. Default target is 9 °F temperature difference (5 K). All operating controls require Apply, Start or Advance; initialization always reads the current controls. Changing circuit geometry requires reinitialization.

## Inventory and outlet

Circulating mode resolves receiver, boiling core, evaporator outlet and condenser as fixed volumes. The outlet is a fraction of the profile's existing evaporator volume, not additional holdup. Initialization assigns the specified superheated outlet state at initial suction pressure, then subtracts its mass, volume and internal energy from the original evaporator. Total initial charge and energy are unchanged. This represents initial thermal stratification; the recovered core pressure can differ slightly from the uniform preview. Insufficient initial vapor space is rejected. The initial outlet-superheat setting is a declared initial condition, not a running heat source.

The boiling core supplies vapor through ideal phase selection and a one-way pressure-driven vapor connection. The outlet itself uses its actual recovered bulk state. Compressor suction is taken from this outlet; a wet outlet latches a model-domain stop rather than synthesizing dry superheat or asserting a physical safety-device trip. This does not model droplet entrainment, a separator, pipe holdup, liquid carryover protection or moving phase boundaries. Closed-circuit mode preserves stage-2 isolated/pump-down behavior.

Outlet heat transfer uses its specified fraction of evaporator UA. Remaining UA belongs to the core. In air mode both signed heat exchanges are drawn from the room. Outlet superheat is Tout − Tsat(Pout), zero for equilibrium mixtures, with a first-order sensor lag initialized to the actual outlet superheat. Compressor speed remains manual for this stage.

## Hydraulic laws

Each effective area is Cd × A in m², including discharge coefficient. It is not nominal valve bore or an inferred manufacturer Cv/Kv rating. Feed liquid comes from the receiver; the condenser drain takes available liquid into the receiver. Missing liquid produces zero flow with a diagnostic. Reverse pressure closes the one-way connection.

Liquid flow is ṁ = effectiveArea × opening^exponent × sqrt(2 ρ ΔPeffective). Available ΔP is upstream minus downstream pressure plus ρgH for the gravity drain. An IEC-style recovery/flashing cap uses ΔPlimit = FL²(Pup − FF Pvapor), FF = 0.96 − 0.28 sqrt(Pvapor/Pcritical), and ammonia critical pressure 113.33 bar absolute. Vapor pressure is recovered from liquid temperature within the existing bounded property grid. ΔPeffective is the smaller of available pressure and this cap. The rule is a generic screening approximation for flashing flow, not a validated ammonia two-phase valve rating. Exact shutdown flow is zero at zero actual opening; a shutdown command still follows actuator lag.

Feed transfer is isenthalpic. Pressure reduction and stored-state recovery determine flash quality; no charge is added. Gravity drain adds gH to specific inlet enthalpy. The released potential energy is explicitly integrated as mechanical work and separately reported as drain gravity energy. There is no elevation/potential-energy inventory: this is an external head boundary, just as external test heat is a boundary.

Core-to-outlet vapor flow uses an equilibrium real-fluid nozzle: G = ρ(P,sup) sqrt(2 [hup − h(P,sup)]), with SI energy conversion. At large pressure reductions a fixed pressure-ratio scan locates the approximate peak mass flux and caps the flow below that critical pressure. This is a homogeneous-equilibrium nozzle approximation with a coarse choking search, not a frictional pipe or calibrated flow curve. No flow law extrapolates outside the property grid.

## Control and numerics

Manual, shutoff and automatic feed commands share a first-order actuator with the profile time constant. Automatic control uses error = sensed superheat − target, command = clamp(kp × error + integral, 0, 1). Positive error opens the feed. Conditional integration prevents accumulation further into command saturation. Switching from manual/shutoff to automatic aligns its integral to the current actual opening. Gains remain SI per kelvin even when the target/sensor display uses °F differences. A target is a command, never a prescribed pressure or temperature state.

Actuator opening, sensor and integral are integrated with the same adaptive Euler/Heun trials as inventory and room energy. Rejected trials commit none of them. Error estimates include controller states. Hardware trips retain actual accepted-state readings; wet suction, property boundaries and solver limits remain separate model stops. Paired mass/enthalpy ports, compressor work, drain head and heat all use the same accepted quadrature. CSV includes the exact schema-3 profile, room snapshot, controls, controller states, flow diagnostics, outlet states and conservation ledgers in SI.

Profiles v1/v2 migrate to v3 without inventing connection specifications or changing existing inventory/revision. Their connected circuit remains unavailable until explicitly configured. Closed storage and original quasi-steady calculations remain available. Duplicate Default for illustrative specifications or enter measured geometry and source notes. Profiles do not contain operating gains, commands or targets.

## Verification and limits

`tests/valves.cjs` checks liquid flashing caps, opening curves, reverse flow, gravity head, isenthalpic flashing, vapor choking, anti-windup, actuator response, missing phases, migration, initial partition conservation, wet startup rollback, batching invariance and timestep refinement. A 600-second Default automatic run reaches approximately 5.016 K actual superheat with mass residual below 1e-8 kg and combined energy residual below 1e-6 kJ. A 20-second refinement from 0.1 to 0.05-second outer intervals and half tolerance changes outlet pressure by approximately 0.00000735 bar. These are numerical and accounting checks, not measured plant or valve validation.

`tests/valves-ui.cjs` verifies connected controls, actual versus sensed superheat, Fahrenheit differences, editable geometry, missing specifications, reset requirements, exports and mobile layout. Existing property, dynamic, profile, initialization and storage suites remain enabled. Stage 4 must broaden integrated operating/fault scenarios and complete release validation. Metal/pipe storage, frictional pressure loss, oil, defrost, latent loads, dynamic compressor sequencing and manufacturer-calibrated valve behavior remain outside this stage.
