# Connected live schematic · v0.5.0 stage 1

Open **Live plant → Initialize automatic DX example**. The schematic is above the inventory table. Start playback or Advance 10 seconds; select an equipment button (or tap its symbol) to inspect readings. The diagram scrolls independently on small screens, while inspection details remain readable without scrolling. Flow animation can be disabled and respects reduced-motion preferences.

## Data and timing

- Vessel pressure, temperature, phase, mass, liquid volume fraction and internal energy come from the storage model's retained accepted state. The diagram uses the active applied profile and resets when that equipment changes. Editing unapplied controls does not change the drawing.
- Fill height is a visualization of liquid volume fraction, not a geometric sight-glass prediction. The outlet exists only in circulating DX; isolated storage leaves it inactive and draws the evaporator-to-compressor path used by that mode.
- Feed, drain and vapor-link arrows use the same flow record as the inventory diagnostics: the last accepted substep average, with its exact interval, or current-state demand before a step/after Apply. Arrows follow the model's permitted transport direction. A closed valve command does not immediately make actual opening zero because actuator lag remains active.
- Compressor mass flow, electrical demand and discharge temperature are read-only current-state calculations from the same compressor routine used by integration. They are not interval-average measurements. Discharge temperature is distinct from condenser bulk temperature. Compressor-off demand is zero; latched stops or unsupported current-state calculations suppress demand instead of extrapolating.
- Animation runs only during active connected-model playback with positive supported flow and no stop. A paused diagram retains pressures, fills and static arrows. Animation speed is illustrative and does not encode fluid velocity. Stopped records may retain previous accepted port flows; the interval label identifies their time.
- Pressure units use the application's existing 1.01325 bar atmospheric reference; temperature differences use K or °F differences. Display conversions do not change model state.

This is a display layer, not additional physics or a plant piping drawing. Pipe, valve and compressor holdup remain excluded. The reference-cycle schematic and quasi-steady room model remain independent. See [ROADMAP.md](ROADMAP.md) for subsequent stages and calibration planned for v0.6.0.

## Verification

`tests/schematic.cjs` verifies observational purity, identical trajectories with/without display sampling, compressor energy-consistent discharge temperature and off/stop suppression. `tests/schematic-ui.cjs` checks model/display agreement, unit invariance, levels, keyboard/touch inspection, animation, shutdown pressures, blocked drain, valve lag, trips, equipment resets, isolated mode, reduced motion, tablet/mobile layout and standalone offline operation. CI runs this browser suite in Chromium and WebKit with an iPad device configuration.
