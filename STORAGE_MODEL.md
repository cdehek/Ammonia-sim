# Refrigerant storage model · v0.4.5 stages 2–3

Stage 3 adds an optional fourth outlet volume and connected valve control; see [VALVE_CONTROL.md](VALVE_CONTROL.md). The following describes the retained isolated mode. The stage-2 laboratory evolves three uniform fixed-volume refrigerant inventories. It is a development checkpoint, with feed and condenser-to-receiver drain connections closed. It supports sealed heating/cooling, air/room coupling and manual compressor pump-down from evaporator to condenser. Stage 3 must supply valve/drain flow laws and outlet superheat control before claiming a circulating refrigeration-plant simulation.

## State and property recovery

Each volume stores refrigerant mass m, internal energy U and fixed volume V. Recover density ρ = m/V and specific energy u = U/m, then solve the bounded real-fluid grid for pressure, temperature and phase. Two-phase states use equilibrium mass quality and specific-volume mixing. Subcooled-liquid and superheated-vapor states use their corresponding property branches. The solver uses bounded warm-start Newton iterations followed by pressure bracketing, without extrapolation. Explicit domain stops retain the last accepted valid inventory.

The shared cycle solver now also supports inverse subcooled-liquid enthalpy/entropy states. Existing steady-cycle results and Default quasi-steady behavior remain covered by their regression suites. The property grid is unchanged: 0.3–35 bar absolute, 0–250 K superheat, up to 30 K subcooling, and the existing minimum liquid-temperature boundary. Cold liquid rows use only cells that exist in both adjacent pressure rows.

## Conservation

For every fixed refrigerant volume:

- dm/dt = sum of entering mass flows − sum of leaving mass flows
- dU/dt = heat into the volume + sum(ṁin hin) − sum(ṁout hout)

There is no moving-wall boundary work. Flow energy is **enthalpy**, while stored energy is **internal energy**. Each internal connection removes and adds the same mass. Unchanged inlet/outlet enthalpy is an isenthalpic transfer boundary; a changed enthalpy contributes explicit work at rate ṁ(hin − hout). Stage 3 is responsible for the hydraulic flow law; the port API does not invent a valve coefficient or infer flow from a setpoint.

Manual pump-down takes dry vapor from evaporator to condenser. For a two-phase evaporator the vapor outlet is saturated, with ideal phase selection; for a superheated evaporator it uses the bulk vapor state. A liquid-only suction volume stops the model instead of compressing liquid. This ideal outlet assumption is not a modeled separator or proof of carryover protection. No terminal superheat zone is resolved yet. The compressor uses profile displacement, compressor count and efficiency assumptions at actual recovered pressures. Discharge enthalpy follows the isentropic-efficiency relation. Refrigerant receives compressor fluid work; electrical input includes motor inefficiency, with motor losses external to the modeled room/refrigerant system.

## Thermal boundaries and controls

Sealed mode has prescribed signed heat rates: positive into the refrigerant, negative out. With all heat rates zero and compressor off, mass, energy and state stay constant. The room does not evolve in sealed mode.

Air mode exchanges Qevap = UAevap(Troom − Tevap) and Qcond = UAcond(Tambient − Tcond), without rectifying their signs. Each exchanger uses its uniform bulk equilibrium temperature rather than segmented zones. Receiver is adiabatic except for its explicit test heat. Evaporator test heat is also drawn from the room in air mode; receiver/condenser test heat is external.

Room energy changes at ambient leakage + internal gain − total evaporator heat. Combined conservation checks compare the change in refrigerant internal energy plus room energy with externally supplied heat and compressor fluid work. Evaporator exchange cancels internally. Profile volumes include no piping, compressor/valve holdup or metal energy. Zero metal storage is an explicit stage-2 approximation; adding it later must define its heat capacity and energy balance.

Operating controls are applied separately from the quasi-steady Live plant. Pump-down is manual at the specified identical-bank speed; this stage does not apply thermostat/PI staging or minimum-on/off timing to that experiment. Profile pressure/discharge-temperature trips apply when compression is enabled. Solver/domain limits use separate categories. Trips retain actual accepted-state readings and discard unconsumed playback time. Changing the active profile invalidates the storage run; saving a profile revision alone does not alter its snapshot. Only one Live/storage playback timer runs at a time. Off-state pressures remain available because the inventory still exists.

## Integration and validation

Adaptive Euler/Heun error estimation subdivides fixed 0.1-second outer intervals. Paired mass and enthalpy fluxes and thermal exchanges use the same accepted quadrature. Rejected trials change no physical state or integrated totals. Mass is never repaired by clipping or adding charge. Property-domain failures retry smaller steps, then latch a stop at the last accepted state. Hardware limits are checked on committed states; default detection resolution is at most one outer interval. Pending playback time is discarded at a fault. Smaller numerical steps are supported for refinement.

`tests/storage.cjs` covers sealed invariance, heating/cooling, boiling/condensation, single-phase recovery, pump-down/shutdown, isenthalpic port conservation, unavailable phases, missing initialization, property limits, fault batching and rollback, total mass/energy conservation and timestep refinement. It checks 90 seeded direct CoolProp density/internal-energy reference states: 30 liquid, 30 vapor and 30 mixtures. Regenerate with `python tools/storage_reference.py` using CoolProp 7.2.0.

Direct-reference acceptance limits are 0.05 bar pressure for compressed liquid, 0.002 bar for vapor/mixtures and 0.02 K temperature. Compressed-liquid pressure is more sensitive to interpolation because liquid compressibility is small. These tolerances describe the checked sample; they are not universal error bounds or measured plant validation. References share the same EOS as the embedded grid.

Observed seeded maximum differences: liquid pressure 0.026157 bar, vapor pressure 0.000151 bar, mixture pressure 0.000111 bar, temperature 0.002609 K. In the 20-second coupled pump-down/air case, mass residual was below 1e-12 kg and combined energy residual below 1e-8 kJ. Refining the maximum step from 0.1 to 0.05 seconds changed evaporator pressure by about 0.00000112 bar. These conservation checks verify accounting; they do not validate the heat-transfer or compressor assumptions against a real plant.

The browser regression covers initialization, units, heat response, pressure retention, exports, recovery, timer isolation, unavailable initialization and mobile layout. CSV contains the exact profile and room-condition snapshots, applied controls, per-vessel states, conservation totals and fault evidence in SI.
