# Coupled model equivalence

PASS: exact original B9C control versus B15 candidate on cold/warm and original/added/fine schedules, bounded at 0.01 s. Each schedule has its own original control; no equality across different schedules is imposed.

| Fixture / schedule | Checkpoints incl. zero | Full residuals | Actual matrices/corrections | Accepted half-states |
|---|---:|---:|---:|---:|
| cold / original | 7 | 5272 | 235 | 32 |
| cold / added | 9 | 6038 | 269 | 38 |
| cold / fine | 13 | 7366 | 328 | 48 |
| warm / original | 7 | 19380 | 867 | 86 |
| warm / added | 9 | 19182 | 858 | 88 |
| warm / fine | 13 | 19530 | 873 | 98 |


Full states/records include all five refrigerant inventories/U/fixed volumes, solution coordinates, recovered properties, eleven thermal energies and temperatures, signed hydraulic/donor energy fluxes, heat rates, ledgers, clocks/events/stops and accepted progress. Original trace objects and attempt hashes compare exactly. Detailed hooks also compare every accepted half-step, temporal coarse/fine estimator result, adaptive rejection and controller proposal.

Receipts `equivalence-<left>--<right>.json` identify each unique pair (canonical/candidate, canonical/observed and observed-control/observed-candidate). Cryptographic hashes are computed from explicit binary64 scientific encodings. Full original attempts retain signed derivative residuals; actual matrices/corrections and residual-object hashes are captured before solver consumption. Direct retained B13/B14 original and B14 alternate warm checkpoints match. `scientific-summary.json` and `b13-direct-checkpoints.json` summarize.

The two same-engine observer paths match the uninstrumented scientific paths. Lossless content references were introduced only after exact comparison; `receipt-compaction.json` and `verify-compaction.mjs` verify original parsed JSON hashes, with reference sources retained here. No timeout receipt is substituted for completed science. Above 0.001 s remains UNQUALIFIED RESEARCH.

After the public-interface correction, all six final candidate canonical/observed schedules were freshly replayed. Original control source bytes and earlier complete control receipts are unchanged; verification checks final candidate build hashes and compares to those exact same-runtime controls. All browser pairs were freshly rerun in both variants. Final timing pairs use new clean processes for both variants.
