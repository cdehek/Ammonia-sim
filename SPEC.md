# Ammonia Lab v0.2.0

## Audit of v0.1.0
The original HTML was unchanged when work resumed. Its Antoine correlation was valid over the stated domain but not a full equation of state. Its constant-k compressor estimate could not account for real ammonia enthalpy or entropy. It had no mass flow, capacity, power or load calculation. Original buttons executed in a full browser; preview environments may block JavaScript. Preserve an explicit startup notice when scripting is unavailable.

## Implementation contract
Standalone, offline HTML application with all property data embedded. Internal SI: pressure in bar absolute, temperature Celsius, enthalpy kJ/kg, entropy kJ/(kg K), density kg/m3, flow kg/s, duty kW. Display conversion must never alter the physical state.

Real-fluid property engine: interpolate an offline grid generated with pinned CoolProp 7.2.0 HEOS::Ammonia (Gao et al. 2020 EOS). No extrapolation. Validate interpolated results against direct CoolProp at unseen states and against NIST saturation data. Keep generator, tests and source provenance.

Single-stage DX and idealized flooded-separator cycles. Suction pressure is applied at the compressor. Evaporator pressure includes a user-entered suction-line loss. Condensing pressure is user specified or follows ambient plus a condensing approach. Liquid-line loss is isenthalpic and must not flash upstream of the valve. Evaporator and suction-line superheat are distinct; only evaporator superheat adds useful cooling. Flooded mode has saturated vapor leaving an ideal separator; pump head and recirculation flow are outside that idealization.

Compressor h2s = h(P2,s1), h2 = h1+(h2s-h1)/eta_is. Fluid work = m(h2-h1); electrical input = fluid work/eta_motor. Condenser duty = m(h2-h3). Expansion h4=h3. Useful cooling = m(hevap_out-h4). Suction-line heat = m(h1-hevap_out). Energy: Qcond = Qevap + Qline + Wfluid. Condenser heat excludes external motor losses.

Flow modes: prescribed refrigerant flow; solve required flow from specified load; estimate flow from swept volume and an explicit fixed volumetric efficiency. Fixed-efficiency mode is not a manufacturer performance map. Show required suction displacement in load mode. Evaluate condenser UA via an isothermal-condensation screening model and disclose that it omits desuperheating/subcooling zones. Condensing approach is an operating assumption, not a UA solution.

State diagrams, pressure-enthalpy chart, entropy/enthalpy state table, energy diagram, operating diagnostics and Carnot bounds. Scenario save/restore/compare and versioned JSON + CSV exports. Validation summaries with measured errors and sample counts.

Room-load transient: lumped thermal mass with fixed steady-state cycle capacity, thermostat deadband, ambient heat leakage and constant internal gain. Closed-form integration on each thermostat segment avoids timestep artifacts. Explicitly not refrigerant startup, inventory or pressure dynamics. Changes to the cycle invalidate previous transient results.

## Validation gates
Independent NIST saturation pressure comparisons; interpolation error tests across bounded pressure/temperature domain; direct-CoolProp cycle comparison with energy and phase constraints; input rejection; unit invariance; invalid-state output clearing; scenario persistence/import; keyboard/button operation; responsive layout; print and export smoke checks. Document maximum measured interpolation errors without interpreting them as total physical uncertainty.

## Follow-on models
Two-stage flash intercooling and full refrigerant-inventory dynamics require separately validated solvers and equipment data. Do not present placeholders as functioning modes. This release delivers a complete bounded steady-state application and room-load transient, with its scope visible in the app.
