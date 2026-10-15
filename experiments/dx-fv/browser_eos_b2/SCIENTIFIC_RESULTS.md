# Independent scientific audit results

**Selected contracts pass; backend qualification remains BLOCKED.**
These values are derived from preserved raw outputs by audit-science.py, independently of the JavaScript balance implementation.

| Engine / fixture | Section / global mass kg | Refrigerant energy kJ | Tube/fin/air node energy kJ | Combined energy kJ |
|---|---|---:|---:|---:|
| chromium / cold | 9.10916e-12 / 1.72677e-11 | 5.43372e-09 | 1.33671e-13 | 5.43375e-09 |
| chromium / feed-step | 8.57225e-12 / 1.7355e-11 | 5.43515e-09 | 1.38556e-13 | 5.43508e-09 |
| chromium / heat-reversal | 7.804e-14 / 3.83832e-13 | 5.88305e-10 | 1.12088e-11 | 6.44001e-10 |
| chromium / load-step | 8.72236e-12 / 1.72387e-11 | 5.42798e-09 | 1.27898e-13 | 5.4279e-09 |
| chromium / warm | 6.05372e-12 / 9.19687e-12 | 2.84462e-09 | 5.93303e-13 | 2.84408e-09 |
| webkit / cold | 9.10916e-12 / 1.72677e-11 | 5.43372e-09 | 1.33671e-13 | 5.43375e-09 |
| webkit / feed-step | 8.57225e-12 / 1.7355e-11 | 5.43515e-09 | 1.38556e-13 | 5.43508e-09 |
| webkit / heat-reversal | 7.804e-14 / 3.83832e-13 | 5.88305e-10 | 1.12088e-11 | 6.44001e-10 |
| webkit / load-step | 8.72236e-12 / 1.72387e-11 | 5.42798e-09 | 1.27898e-13 | 5.4279e-09 |
| webkit / warm | 6.05372e-12 / 9.19687e-12 | 2.84462e-09 | 5.93303e-13 | 2.84408e-09 |

All ten operating audits pass the original 1e-8 kg / 1e-6 kJ budgets. Each includes all saved sample times in nominal, tight and reference runs. The unchanged accepted cap-refinement assertions also pass; their extra records are audited where the detached histories exist.

| Engine / fixture | Frozen direct-EOS ΔP Pa / Δh J/kg / ΔT K | Fresh same-table ΔP Pa / Δh J/kg / ΔT K (max across regimes) |
|---|---|---|
| chromium / cold | 0.0157818 / 0.116987 / 1.14892e-06 | 0.331073 / 1.85148 / 0.000134338 |
| chromium / feed-step | 0.0155475 / 0.117575 / 1.13389e-06 | 0.331073 / 1.87588 / 0.000134354 |
| chromium / heat-reversal | 0.115446 / 0.184726 / 7.73417e-05 | 4 / 5.27914 / 0.000766083 |
| chromium / load-step | 0.0155475 / 0.117575 / 1.13389e-06 | 0.331073 / 1.87588 / 0.000134354 |
| chromium / warm | 0.0109838 / 0.236757 / 3.07441e-05 | 0.25646 / 6.18208 / 0.00110788 |
| webkit / cold | 0.0157818 / 0.116987 / 1.14892e-06 | 0.331073 / 1.85148 / 0.000134338 |
| webkit / feed-step | 0.0155475 / 0.117575 / 1.13389e-06 | 0.331073 / 1.87588 / 0.000134354 |
| webkit / heat-reversal | 0.115446 / 0.184726 / 7.73417e-05 | 4 / 5.27914 / 0.000766083 |
| webkit / load-step | 0.0155475 / 0.117575 / 1.13389e-06 | 0.331073 / 1.87588 / 0.000134354 |
| webkit / warm | 0.0109838 / 0.236757 / 3.07441e-05 | 0.25646 / 6.18208 / 0.00110788 |

Frozen direct-EOS differences use the accepted refined-run comparison and its unchanged budgets. Fresh same-table differences compare separately executed accepted table-backed trajectories; they include backend and initial-inventory differences. They are not same-EOS temporal errors. No acceptance threshold was invented for that cross-backend table.

| Engine / fixture (nominal) | Terminal quality | Superheat K | Stop | Accepted half-steps / rejected trials | Recorded phase events |
|---|---:|---:|---|---|---:|
| chromium / cold | 0.192045061230951 | 0 | None | 642 / 5 | 0 |
| chromium / feed-step | 0.20458357586585932 | 0 | None | 572 / 13 | 0 |
| chromium / heat-reversal | None | 10.915132325777279 | None | 332 / 1 | 0 |
| chromium / load-step | 0.21346162373994113 | 0 | None | 436 / 5 | 0 |
| chromium / warm | 0.19791246007419142 | 0 | None | 906 / 49 | 5 |
| webkit / cold | 0.192045061230951 | 0 | None | 642 / 5 | 0 |
| webkit / feed-step | 0.20458357586585932 | 0 | None | 572 / 13 | 0 |
| webkit / heat-reversal | None | 10.915132325777279 | None | 332 / 1 | 0 |
| webkit / load-step | 0.21346162373994113 | 0 | None | 436 / 5 | 0 |
| webkit / warm | 0.19791246007419142 | 0 | None | 906 / 49 | 5 |

Detached history audit: 96 model histories, 64312 trials, 892 rejected trials, 892 exact rollback checks, 0 rollback failures. Accepted normalized temporal error maximum: 0.990842116231 (original limit 1).
All 80 independently auditable contract-history conservation records pass. Stop kinds, actual clocks, trial sizes and rejected/accepted work remain in the raw histories. The original cold operating executions lack detached trial histories; their original scientific assertions and saved conservation records pass, but a complete cold per-trial replay is NOT RUN. Cross-engine initial-inventory reuse occurs only after the entire returned record arrays compare exactly equal and is labelled in the audit.

Terminal wet outlets are reported as physical results. Native DT checks at every saved operating section retain residuals and actual phase separately in independent-scientific-audit.json. No property residual is repaired by the conservation audit. Other controller/Jacobian configurations, fresh regenerated direct-EOS trajectories and long operating endurance remain NOT RUN; see SUITE_RESULTS.md.

Independent native DT verification: 1500 saved section states, 0 evaluation errors. Maximum absolute P/h/u residuals: 0 / 1.16415321827e-10 / 1.33877620101e-09 Pa / J/kg / J/kg. This checks recorded recovered states against the matching EOS; it does not independently certify every PH inversion or experimental ammonia accuracy.

Independent native terminal audit: 30 states, 0 errors; maximum quality difference 0, maximum superheat difference 2.27373675443e-13 K. These are descriptive residuals, with no new acceptance budget.
