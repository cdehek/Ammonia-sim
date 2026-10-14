# Coworker demonstration — approximately 2–3 minutes

Before presenting, pass the physical iPad checklist, open the exact candidate in full Safari through the tested access method and confirm Default equipment. Keep the host/network available if using the local LAN route. The application version remains the existing v0.5.0; Demo Candidate v0.1 is packaging identity.

Time the recipe warmup on the actual iPad during rehearsal. If initialization/warmup is slow, load Hot condenser air before the coworker arrives and begin with its accepted baseline readings, then show the disturbance, trip and recovery. The presentation target does not promise a particular device's calculation speed.

| Time | Existing controls and operator explanation |
|---|---|
| 0:00–0:25 | Tap **Initialize auto DX**, then **+10 s**. “This is a circulating ammonia DX example with a resolved outlet, manual compressor capacity and automatic liquid feed.” Point to suction/discharge pressure, room temperature, actual superheat, receiver liquid volume and valve actual/command. At 10 s expect roughly 50.94/157.13 psig, 58.90 °F, 10.47 °F superheat difference, and 18.16% opening; transient values are not claimed steady state. |
| 0:25–0:45 | Tap compressor/feed equipment. Start briefly at 10×, then Pause. Open Operator Assist: “It reads accepted model evidence; paused playback does not mean the compressor setting was disabled.” Close Assist. |
| 0:45–1:10 | Guided exercises → **Hot condenser air** → Load. Read the reflection and submit the physically correct answer. Apply the existing disturbance (ambient 25→40 °C / 77→104 °F). This recipe includes a real 30 s model warmup and resets the prior connected run. |
| 1:10–1:40 | Use the exercise's **+10 s** four times, until the stop at approximately **65.125 s total**. Point out rising condenser pressure and the actual **high discharge temperature** trip. “This model hits the temperature protection before its pressure protection.” Do not alter thresholds or manufacture faults. |
| 1:40–2:10 | Open Operator Assist and show recorded **338.29 °F ≥ 338.00 °F**, captured discharge pressure **241.04 psig**, suction **34.11 psig**, speed **70%**. Close Assist and select the original stop in Trends & history. These are retained triggering values, not new readings after clearing. |
| 2:10–2:40 | Restore controls → Clear stop → +10 s. Show completed objectives and retained stop/clear history; export the exercise JSON or history CSV to Files if time permits. “Clearing the model latch is not approval to restart a real plant.” |
| 2:40–3:00 | “This is an illustrative lumped training simulator, not calibrated plant equipment. Numerical checks support conservation and property calculations, not real-plant accuracy. Oil, entrainment, defrost and multistage behavior are outside this model.” Export evidence, Pause, Initialize auto DX, close Assist and return to top for the next coworker. |

Hot condenser air is the most compelling existing exercise because it links an actual modeled trip, recorded evidence and Operator Assist. For a quicker alternative, Restricted liquid feed with correct reflection completes at 40 s after its 30 s warmup; its 2% command shows actuator lag and reduced feed. Missing reflection leaves it active and allows the modeled temperature trip at 56.7375 s. Do not describe that stopped attempt as successful completion.

Do not use this simulator for actual refrigeration safety decisions. Attempts/history are not restored after reload; save exports before reset, reinitialization or closing. Profile changes invalidate the connected run and exercises require Default. The independent/reference workspaces remain available with `?workspace=all`.
