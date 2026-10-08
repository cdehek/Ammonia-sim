# Guided exercises · v0.5.0

## Start and repeat

Activate Default equipment, open Live plant and select a guided exercise. Load/reset replaces the connected run with a fixed setup; it does not edit or delete custom profiles. It does not derive room conditions from the separate quasi-steady inputs. Other model tabs remain independent. Custom active equipment disables loading because the recipes have only been verified against Default.

The fixed room starts at 15 °C, with 30 MJ/K thermal capacity, 0.1 kW/K leakage, 2 kW heat gain and 25 °C ambient. Circulating DX uses air boundaries, enabled compression at 70% manual speed, automatic feed with a 5 K superheat target, PI gains 0.04/0.004, available drain and zero test vessel heaters. Default profile geometry, charge and protection limits apply. Display defaults are Fahrenheit/psig; evidence retains SI.

Warmup advances the actual model before the attempt starts. It is not a fabricated steady state. Lesson time and history retain that advance.

| Exercise | Warmup | Disturbance and measured objectives |
|---|---:|---|
| DX startup | 0 s | Positive feed and compressor demand after 10 s; at least 60 s elapsed and actual/sensed superheat within ±1 K of 5 K for 20 consecutive sampled seconds. |
| Room load increase | 30 s | Gain changes to 20 kW without an instantaneous room-temperature jump; observe 30 s of temperature response without a stop. |
| Hot condenser air | 30 s | Ambient changes to 40 °C; condenser pressure rises at least 0.5 bar above baseline; capture the computed high-discharge-temperature trip. Restore ambient to 25 °C, disable compression and command feed closed, clear the stop and continue off for 10 s. |
| Restricted liquid feed | 30 s | Command 2% manual opening; observe opening initially above command due to actuator lag, then after 10 s opening below 4% and feed below half baseline without a stop. |
| Superheat target response | 120 s | Set 7 K automatic target; after at least 30 s, actual/sensed superheat remain within ±0.5 K for 20 consecutive sampled seconds. |

Each exercise additionally requires a correct reflection. Incorrect submissions are recorded and do not grant that objective. Measured objectives can be inspected as they are satisfied; hints explain where to look. Changing an input outside the supported recipe interrupts the attempt. End retains the partial evidence; load/reset begins a fresh attempt and clears the reflection selection. The selector is locked while an attempt is active. Afterward, the selected lesson preview is labeled separately from the retained attempt; objectives, hints, reflection and debrief beneath the attempt heading still refer to that attempt. Reset retained attempt restarts it, while Load exercise starts the selected lesson.

## Physics and grading

Disturbances call the existing atomic model-update interface. Playback and ten-second advancement delegate the connected-run controls. The grader observes accepted data and never changes a pressure, temperature, flow, energy or controller state. Accepted flow observations include their averaging interval; compressor demand remains current-state telemetry.

Objectives use accepted history observations and simulated timestamps, independent of browser refreshes. Sustained bands require uninterrupted sampled evidence. Before-change snapshots do not count as post-change observations. Missing observations due to bounded retention interrupt grading. The hot-air ten-second continuation may end between periodic samples; its exact accepted endpoint is explicitly marked with a null sample ID and source label rather than inventing a history observation. A stop snapshot retains its original trigger readings and limits after clearing.

Default hot air reaches a discharge-temperature trip rather than the pressure trip one might expect. Restoring off-state inputs and clearing demonstrates model continuation, not qualification for a plant restart. A prolonged 2% restriction can also cause a temperature trip; the feed lesson deliberately grades its short response. The target-response lesson needs its established 120-second warmup: changing targets during early inventory redistribution can yield a different outcome. It demonstrates target response, not validated PI gain tuning.

## Evidence lifecycle

Completion, unexpected stop, manual end or interruption pauses playback. During a training advance, the grader observes committed outer endpoints before the next interval is integrated. The first accepted completion boundary halts the request and discards unused pending time, regardless of playback speed. Missing reflections still leave the lesson active, so supported physical stops can occur. This hook never observes rejected predictors or alters the integration equations. Finished debrief/export evidence is frozen before subsequent free exploration. Selecting another lesson retains the last report until Load/reset explicitly replaces it. External reinitialization or equipment application interrupts an active lesson before resetting the connected run.

Export JSON contains the applied profile and initial room, baseline, objective timestamps/readings, reflection attempts, disturbance actions, original expected fault, accepted history observations/events and final controls/boundaries. It preserves SI values at full precision. Existing history retention limits still apply and appear in the report. Attempts are not restored after reload; download a report before leaving. Profile storage/import and existing CSV schemas are unchanged.

## Verification and scope

Numerical tests run all five recipes against the connected model and check sustained objectives, wrong reflections, unexpected stops, incompatible controls, conservation, batching and identical physical trajectories with/without grading. Browser tests cover all exercise flows, export freezing, warmup/reset, active-profile guards, units, playback, older-browser compatibility, keyboard, tablet/mobile layouts and offline operation. Chromium and WebKit CI complement numerical evidence; iPad emulation does not establish physical-device testing.

These are lessons about this supported lumped Default model. No manufacturer/measured calibration, real operating procedure, oil or entrainment behavior, defrost, multistage systems or connected automatic suction capacity control is introduced. Unsupported physics must be implemented and validated before dependent lessons are added. Final acceptance coverage is recorded in [RELEASE_CHECKS.md](RELEASE_CHECKS.md); v0.6.0 remains equipment calibration.
