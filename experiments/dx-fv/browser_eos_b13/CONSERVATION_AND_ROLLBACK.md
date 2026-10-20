# Conservation, rollback and refusal

| Maximum absolute sampled residual | Cold | Warm |
|---|---|---|
| combinedEnergyResidualKJ | 6.32489e-12 | 1.49517e-10 |
| massResidualKg | 1.2637e-14 | 8.73063e-14 |
| maxNodeEnergyKJ | 8.97199e-15 | 5.19272e-14 |
| maxSectionEnergyKJ | 5.49888e-11 | 9.22285e-11 |
| maxSectionMassKg | 1.09927e-13 | 5.62084e-14 |
| refrigerantEnergyResidualKJ | 6.33386e-12 | 1.49375e-10 |
| thermalEnergyResidualKJ | 8.97893e-15 | 1.41887e-13 |

Units are kg for mass and kJ for energy. These maxima cover the seven completed output checkpoints through 0.01 s; they are not claims about every arbitrary intermediate time. The original audit checks global and section mass, fluid energy, thermal energy, combined energy and each thermal node. It independently reconstructs signed air/tube/fin exchange from ledgers. Preserved audit limits are 1e-8 kg and 1e-6 kJ; B13 changes no acceptance tolerance. The actual residuals are far smaller. Maximum nonlinear residual and normalized temporal error satisfy their original acceptance limits at output records.

Canonical normal fixtures end at 0.01 s with `stop:null`. Rejected coarse/fine trials never commit their candidate inventories or ledgers. Both accepted half-step commits are prepared against detached ledgers/events before installing the accepted trial. Earlier accepted adaptive trials within a multi-trial advance remain committed if a later trial stops. “Whole request rolled back” would be false in that situation.

Fresh contract witness: a sealed, zero-refrigerant-exchange fixture starts all thermal nodes at exactly 200 K with zero load. A scheduled -1 kW air load at 0.0001 s points out of the original supported domain. The request is 0.0002 s; actual committed progress is 0.0001 s. The original solver retries then returns a confirmed thermal-domain refusal at that accepted time. The evidence identifies node/stage/outward direction, retains the last physical state and stop, and preserves exact M/U/V, thermal energies and ledgers from before the refused motion. Repeating advance on the stopped state is unchanged. Invalid inlet p=0.29 bar update refuses before changing live state. Original-A2 and B9C witnesses agree bit exactly. See `evidence/domain-and-rollback.json`.

The separate one-second CPU-budget run is an external termination, not a solver/domain refusal. The supervisor retains its last complete output and sparse accepted-state progress observations, which may be later than that output. The incomplete pending trial is not labeled accepted. See `budget-termination-warm-010.jsonl.exit.json`; `timedOut:false` means the CPU signal arrived before the parent's wall-time kill, not that the solve completed. No accepted partial progress is discarded or described as a request-wide rollback.

No state clipping, artificial convergence, altered conservation, remapped property failure, illustrative-physics fallback or equipment alarm is introduced. No genuine normal-fixture numerical refusal occurred by 0.01 s, so such a refusal is not fabricated for this report. The separate original C1 regression receipt remains retained historical evidence; B13 does not claim a fresh general fault-injection campaign.
