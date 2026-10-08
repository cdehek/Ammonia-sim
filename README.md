# Ammonia Lab v0.4.5

Open `index.html` in Chrome, Edge, Firefox or Safari. The file is self-contained and works offline. HTML previews can disable JavaScript; the startup notice remains visible when controls cannot initialize.

Display units default to **psig and Fahrenheit** on startup and Reset. Room temperatures and thermostat deadband follow the selected temperature units. SI units remain explicitly labeled in numerical reference data and CSV exports.

## v0.4.5 · connected refrigerant simulation

Open **Live plant → Initialize automatic DX example** to load circulating DX, air boundaries, 70% manual compressor speed and automatic feed control at 9 °F difference (5 K). It uses the active profile and applied initial room conditions, and resets the circuit. With Default equipment this is a ready-to-run example. Use Start or Advance 10 seconds. Change ambient air, room heat gain, leakage, feed control, drain availability or speed and Apply to perturb the running circuit.

The connected model evolves receiver, evaporator core, outlet and condenser mass/internal energy. Pressures and phases follow the bounded real-fluid EOS. Feed/drain flow is pressure driven; the outlet provides actual superheat and dry compressor suction. Valve and sensor response lag are modeled. Mass and combined room/refrigerant energy remain conservative. Wet suction, property boundaries and numerical limits are explicit stops, separate from hardware trip thresholds. Isolated mode retains sealed heating/cooling and manual pump-down.

Profiles use schema 3 with optional inventory and connection specifications. Older profiles migrate without invented charge or valve geometry; configure a custom profile before using circulation. Default inputs remain illustrative. The original quasi-steady room model and reference cycle calculator remain available as separate models. See [STORAGE_MODEL.md](STORAGE_MODEL.md), [VALVE_CONTROL.md](VALVE_CONTROL.md) and [RELEASE_NOTES.md](RELEASE_NOTES.md).

Stage-4 integration checks cover 24 operating/fault/recovery cases, phase exhaustion, control changes, atomic invalid-input rejection, playback batching and timestep refinement. The deterministic [integration-validation.json](integration-validation.json) report is embedded in **Model & validation**. It verifies numerical behavior and accounting; it does not establish manufacturer-calibrated or measured plant accuracy.

## v0.4.1 fault handling

Live playback stops within the current numerical interval (one simulated second by default) when an equipment trip, solver limit or model-domain limit is detected, at every playback speed. Unused playback time is discarded. Equipment trips retain their triggering readings and configured limits in a separate fault summary and SI CSV columns; off-state pressure metrics remain unavailable. Solver/model stops are labeled separately and never assert an equipment trip. Correct inputs and reset the trip or clear the model stop before resuming; reset the plant when room temperature is outside the model domain. Historical fault records remain in CSV after clearing a stop.

## Equipment profiles

The Live plant now has a read-only **Default** and custom equipment profiles. Create from Default, duplicate, edit, save, select, delete inactive profiles, and import/export profile JSON. Custom specifications can use the existing example curves or fixed efficiency assumptions. Source notes and revisions distinguish user estimates and user-entered manufacturer values from validated performance data.

Profiles persist in the browser; JSON exports are the portable backup. **Use profile** applies equipment and resets an existing run while retaining operating settings. Saving an active profile alone does not alter running equipment. Refrigerant volumes and optional charge/fill initialization have an equilibrium starting-state preview; they initialize the connected circuit; they do not alter the original quasi-steady model. See [EQUIPMENT_PROFILES.md](EQUIPMENT_PROFILES.md) for supported systems, workflow, units, storage and schema.

## Quasi-steady room model

Select **Live plant** to run the coupled room/equipment model. Start, Pause/Resume, Reset and Advance 1 minute work at 1×, 60× or 300× playback. Apply live setpoints, heat load, ambient air, exchanger UAs, manual speed or automatic suction PI control and staging for up to three identical example compressors; disturbance buttons provide quick demonstration changes. Trends show pressures, room temperature, speed, capacity and power. Trips latch until reset, and minimum on/off times are enforced.

The supplied compressor curves are **example equipment**. Pressures are solved from compressor flow and approximate exchanger-zone balances. Refrigerant equilibrates each step: this is a dynamic room/control model, not refrigerant-inventory or pressure-startup physics. [DYNAMIC_MODEL.md](DYNAMIC_MODEL.md) gives equations, assumptions, control behavior and validation. Reference calculator inputs at left and existing saved scenarios remain independent of the live plant. Defaults remain Fahrenheit and psig.

### Build and verify

With Node.js 22+ and Python 3.12:

```sh
npm ci
npx playwright install --with-deps chromium
npm test
npm run build
npm run test:browser
npm run test:webkit
```

`npm test` uses checked-in reference data; Python CoolProp is needed only to regenerate that data/property grid. Browser tests launch a local server and use bundled Chromium (or `/usr/bin/chromium` when installed). The build embeds source and JSON data into `index.html`; no browser build dependencies or network APIs are needed at runtime. The GitHub verification workflow checks source/bundle consistency, physics, dynamic controls and browsers on pushes and PRs. GitHub Pages currently publishes the checked-in root `index.html` through its existing deployment configuration.

## What is implemented

- Bounded real-fluid properties generated with CoolProp 7.2.0 / HEOS::Ammonia, using the Gao et al. (2020) EOS. The browser interpolates this grid; it does not run the native CoolProp library or extrapolate beyond the grid.
- Single-stage direct expansion and an ideal flooded-separator boundary.
- Compressor suction and condensing pressures, ambient-based condensing assumption, evaporator superheat, suction-line heating, subcooling, pressure losses and compressor/motor efficiencies.
- Prescribed mass flow, load-based required flow, or swept volume with fixed volumetric efficiency.
- State-point enthalpy, entropy, density, phase and vapor mass fraction; cooling duty, compressor electrical input, COP, condenser duty, motor losses and energy-balance checks.
- Interactive equipment explanations, pressure–enthalpy chart, state table, diagnostics and UA screening.
- Local scenario saving, restoring, comparison, versioned JSON import/export, CSV results and print/PDF.
- A lumped room/product sensible-cooling model with ambient heat leakage, internal gain, thermostat deadband and UA-limited cooling. Ideal proportional refrigerant-flow/electrical-power modulation is assumed as coil capacity falls below nominal cycle capacity.

## Physics and scope

The core model solves h2s from discharge pressure and suction entropy. Actual discharge enthalpy follows the specified isentropic efficiency. Expansion is isenthalpic. Useful evaporator heat and suction-line heating are accounted for separately. Compressor motor losses are assumed external to the refrigerant.

Single-stage cycle enthalpy accounting:

- Qevap = m(h5 − h4)
- Wfluid = m(h2 − h1)
- Wmotor = Wfluid / eta_motor
- Qline = m(h1 − h5)
- Qcond = Qevap + Qline + Wfluid

The application rejects unsupported phases and property-domain requests. It warns when the chosen cold-space temperature cannot supply the specified evaporator outlet superheat or the user-set equipment screening assumptions fail. Invalid submitted inputs clear calculated results and disable exports/saving.

The room model integrates a piecewise-linear thermal ODE analytically through thermostat and coil-capacity transitions. It is not a refrigerant startup or inventory model. Its targets must remain above the evaporator outlet temperature. It excludes latent loads, defrost, fan/pump power and oil behavior.

Flooded mode omits recirculation flow, pump head and separator inventory. Compressor volumetric efficiency is a user assumption, not a manufacturer map. UA checks are isothermal screening estimates, not segmented heat-exchanger ratings. The separate connected DX model resolves lumped refrigerant inventory; metal/pipe storage, oil, entrainment, defrost and two-stage flash intercooling remain outside this release.

## Validation

The physics test uses 560 unseen single-phase property states, 160 saturation states and 159 eligible complete-cycle comparisons against direct CoolProp. One intentionally sampled out-of-domain cycle is rejected. Seventeen independent controller-fit pressure/temperature comparisons use Danfoss's published R717 constants, derived from REFPROP 10.

Measured maximum discrepancies:

| Quantity | Difference |
|---|---:|
| Saturation temperature | 0.000452 K |
| Specific enthalpy | 0.00112% |
| Density | 0.00462% |
| Cycle discharge temperature | 0.00703 K |
| Cycle cooling duty | 0.00111% |
| Cycle electrical input | 0.00466% |
| Cycle COP | 0.00404% |
| Energy residual | 1.28e-13 kW |
| Manufacturer controller-fit agreement | 0.140 K |

These quantify interpolation/solver agreement in the sampled cases, not total physical uncertainty. CoolProp cycle comparisons share the same underlying EOS. The independent manufacturer fit is a saturation check, not measured equipment validation. The NIST fluid table endpoint returned HTTP 403, so direct NIST fluid-table validation is not claimed.

## Sources

- [CoolProp ammonia EOS documentation](https://coolprop.org/fluid_properties/fluids/Ammonia.html)
- [Danfoss refrigerant controller constants, May 2025](https://assets.danfoss.com/documents/latest/493262/AM187286420404en-000702.pdf)
- [Danfoss industrial refrigeration application handbook](https://assets.danfoss.com/documents/latest/89440/AB137786416217en-000501.pdf)

## Reproduce

Python 3.12, CoolProp 7.2.0 and Node.js are used for generation/verification. The shipped HTML requires none of them.

1. Install CoolProp 7.2.0 for Python. The scripts also check `/workspace/scratch/python-deps` used in this workspace.
2. `python tools/generate_properties.py`
3. `python tools/reference_cases.py`
4. `node tests/physics.cjs`
5. `python tools/build.py`
6. Serve the HTML locally and run `node tests/browser.cjs` with Playwright and Chromium. Adjust the test URL and browser path for your machine.

The property grid SHA256 is `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.

The standalone file, source, property generator, deterministic reference cases and validation report are delivered together. No accounts, remote API calls or tracking are required by the app. Local scenario persistence depends on browser storage permissions; JSON exports remain available when storage is unavailable.
