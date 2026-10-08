# Ammonia Lab roadmap

## v0.5.0 · visualization and training

1. **Live schematic** (current stage): connect vessel fills, readings, flow direction, compressor state and feed valve position to the connected refrigerant model. Provide component inspection, accessible controls, pause/reduced-motion behavior and tablet layouts.
2. **Trends and event history**: synchronized pressure, temperature, superheat, opening, level and room histories, with control changes and stop/recovery events.
3. **Training scenarios**: repeatable guided startup, load increase, hot ambient, feed restriction and superheat tuning exercises. Change supported model inputs, with objectives, hints, reset and debrief. Add missing physics before teaching scenarios that depend on it.
4. **Release verification and polish**: validate display/model consistency, scenario outcomes, offline operation and desktop/iPad browser behavior.

## v0.5.5 · connected compressor capacity control

Automatic suction-pressure control, compressor speed limits and response delays, and interactions with feed-valve control. Connected speed remains manual until this work is implemented. Evaluate sequencing against the supported compressor-bank model.

## v0.6.0 · equipment calibration

Use manufacturer performance data or measured system operating data to calibrate compressor performance, effective valve flow areas and heat-transfer assumptions. Track data provenance, supported operating ranges, uncertainty and comparison against measurements. Numerical conservation alone does not establish measured plant accuracy.

Real equipment protection/interlocks and unsupported oil, entrainment, defrost or piping behavior require separate modeling and validation before inclusion in training.
