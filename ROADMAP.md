# Ammonia Lab roadmap

## v0.5.0 · visualization and training

1. **Live schematic** (implemented): connect vessel fills, readings, flow direction, compressor state and feed valve position to the connected refrigerant model. Provide component inspection, accessible controls, pause/reduced-motion behavior and tablet layouts.
2. **Trends and event history** (implemented): synchronized pressure, temperature, superheat, opening, level and electrical-demand histories, with applied changes, playback actions and original stop/clearing evidence. Exact sample inspection and SI export use bounded simulation-time history.
3. **Training scenarios** (implemented): repeatable guided startup, load increase, hot ambient, feed restriction and superheat tuning exercises. Change supported model inputs, with measured objectives, reflection, hints, reset, debrief and frozen JSON evidence. Default recipes enforce supported controls and stop outcomes. Add missing physics before teaching scenarios that depend on it.
4. **Release verification and polish** (implemented): accepted-boundary completion prevents playback overshoot; selected and retained lessons are clearly labeled. Verify display/model consistency, scenario outcomes, frozen exports, two-hour retention, offline operation and desktop/iPad browser emulation. See [RELEASE_CHECKS.md](RELEASE_CHECKS.md).

## v0.5.5 · connected compressor capacity control

1. **Controller foundation** (implemented, current stage): independent single-compressor manual/automatic suction PI, speed limits, sensor/actuator/ramp response, run/rest/start timing, tracking anti-windup and external-stop priority. See [CAPACITY_CONTROL.md](CAPACITY_CONTROL.md).
2. **Connect to the model**: integrate at accepted control boundaries, retain conservative accounting and independent protection; validate startup/load response and feed-valve interaction.
3. **Controls and visualization**: user modes/setpoint/limits, target/actual pressure and requested/actual capacity trends, clear limiting reasons. Evaluate bank sequencing separately before implementing it.
4. **Verification and release polish**: integrated dynamics, trips/recovery, mode switching, refinement, appropriate training, browsers/offline and final release checks.

Connected plant speed remains manual in stage 1. The independent module is bundled but dormant; existing manual multi-compressor profiles and saved schemas remain unchanged.

## v0.6.0 · equipment calibration

Use manufacturer performance data or measured system operating data to calibrate compressor performance, effective valve flow areas and heat-transfer assumptions. Track data provenance, supported operating ranges, uncertainty and comparison against measurements. Numerical conservation alone does not establish measured plant accuracy.

Real equipment protection/interlocks and unsupported oil, entrainment, defrost or piping behavior require separate modeling and validation before inclusion in training.
