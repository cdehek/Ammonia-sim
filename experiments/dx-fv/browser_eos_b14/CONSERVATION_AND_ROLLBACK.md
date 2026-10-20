# Conservation and rollback

PASS: every canonical output record and every retained accepted half-state in both primary fixtures and both alternate schedules passes the original mass <1e-8 kg / energy <1e-6 kJ budgets. Independent thermal closure reconstructs each node from signed air/tube/fin link ledgers and imposed air load. Donor energy transport is independently checked against flow sign and original donor enthalpy. No new tolerance is introduced.

| Maximum absolute closure | Cold | Warm |
|---|---|---|
| massKg | 1.2637e-14 | 9.13402e-14 |
| fluidKJ | 6.33386e-12 | 1.56013e-10 |
| thermalKJ | 9.78731e-15 | 1.62759e-13 |
| combinedKJ | 6.32489e-12 | 1.56176e-10 |
| sectionMassKg | 1.09927e-13 | 6.05484e-14 |
| sectionEnergyKJ | 5.49888e-11 | 9.93275e-11 |
| nodeKJ | 9.7769e-15 | 5.75893e-14 |
| independentNodeKJ | 9.78384e-15 | 5.75928e-14 |

These maxima cover all accepted half states, not just requested outputs. Warm combined maximum 1.56176e-10 kJ can therefore exceed the protected B13 requested-output summary (~1.50e-10) without contradiction. Cold combined max remains ~6.32489e-12 kJ. Section mass and energy budgets, global refrigerant U, eleven-node storage, air-side 1 kW imposed load and combined coil energy all pass. Constant section volumes and global inventory are retained from the exact original states.

Ledger equations independently used: section mass change = left-face mass − right-face mass; section U change = left donor-enthalpy transport − right transport + tube heat. Thermal storage change = imposed air load − tube-to-refrigerant transfer globally, with link signs checked independently for each node. Combined energy eliminates internal tube exchange. Negative face flow uses the right donor; no unsigned-flow reinterpretation occurs. Changes in section 0 h/T at the event occur while its M and U both increase, without creating or losing inventory.

## Atomic accepted progress and domain refusal

`domain-and-rollback.json.gz` replays original B13's separately labeled sealed, zero-exchange 200 K fixture. It accepts 0.0001 s, applies the original scheduled −1 kW air load, and confirms an outward derivative at the exact thermal support boundary. The resulting **genuine domain refusal** retains earlier accepted time and inventories. Original A2, original B9C and the observed source match bit exactly for state, record, full attempt diagnostics, stop/evidence and partial accepted progress. Repeated advance after stop is unchanged; invalid inlet update p=.29 bar rolls back exactly. The witness requests .0002 s but actual committed horizon is .0001 s.

The original advance prepares both half pieces against detached ledgers/events before atomically installing them. B14 copies these prepared pieces but counts them as accepted only for completed trials whose original acceptance trace and final state are verified. No rejected candidate becomes an accepted diagnostic state. All original normal-fixture rejection decisions are temporal accuracy, not this domain witness.

## External termination

A deliberately labeled 1 s wall-budget canonical warm witness is killed as an entire process group. Exit −9 / `timedOut:true` is external supervision, not a solver stop or physical fault. Its last requested checkpoint is .0001 s; its last independently observed accepted snapshot is .0004911886098445242 s. Every retained partial snapshot is bit-exact against the corresponding canonical full run (`external-budget-validation.json`). No state after that snapshot is claimed; the pending trial is not accepted by the receipt. No retry was made. This independently preserves B13's distinction between budget exhaustion and numerical/domain refusal.

No numerical rejection becomes a plant alarm. Terminal bulk wet describes a model state, not compressor liquid carryover safety. This fixture is one evaporator with artificial fixed reservoirs, uncalibrated conductances and no compressor safety measurement.
