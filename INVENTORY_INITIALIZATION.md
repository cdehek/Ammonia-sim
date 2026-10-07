# Inventory initialization contract · v0.4.5 stage 1

This stage defines explicit initial refrigerant mass and internal energy for three isolated equilibrium volumes. It does not advance them in time or change the existing Live plant model. Its purpose is to prevent ambiguous initial conditions when storage physics is added.

## State definition

Each refrigerant volume V contains saturated liquid and vapor at a specified pressure p. Liquid volume fraction f determines phase masses:

- Liquid mass = V f ρf
- Vapor mass = V (1 − f) ρg
- Total mass = liquid mass + vapor mass
- Vapor mass quality = vapor mass / total mass
- Specific phase internal energy u = h − 100 p / ρ, with h in kJ/kg and p in bar absolute
- Stored internal energy U = liquid mass × uf + vapor mass × ug, in kJ

Receiver and condenser use initial discharge pressure; evaporator uses initial suction pressure. Temperatures and phase densities/enthalpies come from the existing bounded CoolProp-generated saturation grid. Liquid **volume** fill and vapor **mass** quality are distinct. Energy uses the property grid's reference convention; absolute energy is not a heat input.

The reference starting state is saturated, without initial superheat or subcooling. It is not necessarily the algebraic live equipment equilibrium, and the rooms and refrigerant need not start at equal temperature. Initial suction/discharge pressures are separate from operating control targets. Piping, compressor/valve holdup and metal thermal energy are excluded from this three-volume charge definition.

## Independent inputs

**Levels mode:** specify all three volumes, two initial pressures and all three liquid volume fractions. Total modeled charge is derived.

**Charge mode:** specify all three volumes, two initial pressures, total modeled charge and evaporator/condenser fills. The receiver fill is derived. Its allowed charge interval is the fixed mass in the evaporator/condenser plus receiver vapor-only mass through receiver liquid-only mass. Reject values outside this interval. Only negligible floating-point endpoint tolerance is accepted.

The unused dependent specification is null in JSON. A null initialization means not configured; partial volume metadata is still allowed for legacy/live-only profiles. Successful schema validation is separate from successful physical initialization. The initializer returns `ready`, `status`, summary totals, per-vessel state data and assumptions. Stage 2 must require `ready` and must not interpret absent settings as zero inventory.

## Stage-2 handoff

Use `AmmoniaInventory.createInitializer(engine, profiles).preview(profile)` as the bounded starting-state contract. Before running storage dynamics, extend the property solver to recover pressure/temperature/phase from stored mass, internal energy and volume; handle saturated, subcooled and superheated states. Reconcile any additional modeled holdup with the charge definition instead of silently adding refrigerant. Metal heat capacities and any additional geometric allocations require explicit definitions when added.

Maintain mass and energy conservation through transfer and phase changes. Validate initialization and evolution against independent direct-property reference states, sealed-volume behavior, timestep refinement and startup/shutdown cases. Current initialization tests check existing statePX mass/volume/energy consistency, charge/fill round trips and three starting inventories against direct CoolProp saturated density/internal-energy references. Per-vessel tolerances are 0.01% for mass and 0.02% for internal energy. These share the same EOS and do not validate a future transient model or measured plant behavior. Regenerate references with `python tools/initialization_reference.py`; CoolProp is needed only for regeneration.

Stage 3 adds valve flow and actuator/superheat control. Stage 4 validates the integrated system. Stage 1 alone claims no evolving storage or valve simulation. Stage 2 now uses this contract in the separate storage laboratory; see STORAGE_MODEL.md. The current three-volume charge definition is unchanged.
