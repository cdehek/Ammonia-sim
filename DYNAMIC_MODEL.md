# Live plant model v0.4.0

The live plant is a room thermal transient coupled to a quasi-steady, single-stage direct-expansion equipment model. It is not a refrigerant-inventory or pressure-startup transient. The original operating-point calculator and version-1 scenario format remain independent and unchanged.

## Equipment equations

At each running speed, solve two unknown saturation temperatures (evaporating and condensing) so the required evaporator and condenser conductances equal their supplied UAs. A damped finite-difference Newton solve checks both relative residuals below 1e-6. No feasible/converged solution produces an explicit model lockout, rather than silently substituting specified pressures or extrapolating properties.

Compressor flow is swept volume / 3600 × speed × volumetric efficiency × suction density. The **example** curves are:

- volumetric efficiency = clamp(0.88 − 0.035 × (pressure ratio − 2), 0.35, 0.90)
- isentropic efficiency = clamp(0.78 − 0.004 × (ratio − 4)² − 0.035 × (1 − speed)², 0.45, 0.80)
- motor efficiency = clamp(0.93 − 0.07 × (1 − speed)², 0.80, 0.94)

These curves are illustrative assumptions, not manufacturer data or an operating envelope. Equipment profiles can instead supply fixed volumetric, isentropic and motor efficiency assumptions. These values are used directly; no manufacturer map interpolation or fitting is implied. See EQUIPMENT_PROFILES.md. Speed denotes effective swept-volume fraction over 20–100%; one to three identical example compressors can share the suction/discharge pressures. There is no manufacturer unloading map.

Evaporator required UA is the sum of boiling duty / room-to-saturation temperature difference and superheat duty / log-mean temperature difference. Condenser required UA sums desuperheating, condensation, and subcooling zones in the same way. Room and condenser air are treated as constant-temperature reservoirs within each zone: finite air flow, distributed refrigerant pressure loss, wet-bulb conditions, frost, and detailed exchanger geometry are omitted. Sensible-zone LMTD is an approximation with variable refrigerant heat capacity.

Evaporator superheat is min(3 K, 25% of room-to-evaporation approach); condenser subcooling is min(3 K, 25% of condensation-to-ambient approach). Suction-line heating is 2 K. These are explicitly prescribed closure assumptions, not expansion-valve control or liquid-level predictions. Dynamic piping losses are zero. Compressor external motor losses and suction-line heat retain the reference solver's accounting.

The reference solver's supported suction range (0.35–8 bara), condensing range (3–30 bara), phase constraints, and property domain still apply. Exceeding them stops equipment calculations. Off-state refrigerant pressures are unavailable, rather than fabricated or retained.

## Room, controls, and time

Room equation: C dT/dt = UA_leak (T_ambient − T) + internal gain − equipment cooling. C is MJ/K × 1000, giving kJ/K. Each short interval uses the analytical room solution with frozen equipment duty, then recomputes equipment performance. Compressor electricity integrates actual calculated electrical input; it does not scale a fixed cycle COP.

The thermostat uses setpoint ± half the deadband, minimum-on/off timers, and an independent availability override. Automatic speed command is clamp(0.5 + Kp × (actual suction bara − target bara) + integral, 0.2, 1). The integral uses conditional anti-windup. Actual speed follows a first-order actuator response. Pressure is an algebraic equipment result, not an imposed control target. Manual mode specifies commanded speed but retains thermostat/timers/trips. Availability loss and trips override minimum run time.

Automatic staging enables another compressor after sustained speed saturation and a positive suction-pressure error. It removes a stage after sustained low speed and a negative pressure error. The staging delay and each compressor's minimum on/off times are enforced. All active example compressors share the same speed fraction and common pressures; new stages enter the quasi-steady bank without a modeled mechanical/refrigerant startup. Manual mode requests all selected compressors at the manual speed, subject to restart timers. Compressor count changes require Reset.

High/low pressure and discharge-temperature limits are configurable demonstration thresholds, not safety ratings. Trips latch until operator reset; resetting does not bypass the minimum-off timer. Numerical non-convergence is clearly included in the lockout message and must not be interpreted as a measured physical fault.

Default numerical interval is one simulated second, independent of playback rate. Fractional elapsed time accumulates; background browser playback pauses. Refinement to half-second intervals is tested. This release models speed-actuator lag and room storage, but **does not** model refrigerant vessel mass/energy storage, compressor mechanical startup, expansion-valve dynamics, latent loads, defrost, or fan/pump electricity.

Room initial temperature, thermal mass and compressor count require Reset after time advances. Ambient, heat gain, exchanger UAs, setpoints, control mode, availability, tuning and limits can change during a run. Latest 7,200 output samples are retained. Plotted setpoints use historical values. Live CSV includes explicitly labeled SI values and disturbance-related inputs. Existing reference scenarios remain compatible; they are not live-session saves.

## Validation

`tests/dynamic.cjs` checks 18 coupled equilibria across room/ambient temperatures and speeds, cycle and room energy conservation, both UA residuals, lower capacity from reduced evaporator UA, increased head pressure from reduced condenser UA/warmer air, model-domain rejection, manual speed, automatic identical-compressor staging, individual stage timers, trips/reset, anti-short-cycle timers, availability loss, disturbances, playback batching invariance, and timestep refinement. Browser tests cover live controls, conversions, CSV, mobile layout, reference-mode isolation and error reporting.

The measured default eight-hour case has two compressor starts. One-second versus half-second intervals differed by approximately 0.00028 K in final room temperature and 0.00035% in compressor electricity. Room energy residual was approximately 0.000002 kJ. These are numerical checks of the stated model, not measured plant or equipment validation. The original CoolProp property/cycle comparisons remain separate.

Manufacturer maps, exchanger ratings, control settings and plant trends are required before representing a particular installation. Refrigerant inventory/startup dynamics, heterogeneous compressor banks, recirculation pumps/levels, evaporative condensers and two-stage systems are later models, not functioning options in this release.
