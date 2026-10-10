# Stage 1 restore points — frozen before prototype development

Repository: `cdehek/Ammonia-sim`. Experimental branch: `experimental/dx-fv-stage-3`.

| Restore point | Full commit | Meaning |
| --- | --- | --- |
| Production / main v0.5.0 | `0473d32f62db992fde0f581d116e1bd0c8e7d8ed` | Existing approved production application |
| Reviewed v0.5.5 release-candidate source | `e86da1975dd177248a78d40c114bf76123c173ea` | Existing review corrections and passing legacy verification |
| Current PR #3 / Cloudflare preview | `d4422425750a1d3c4e432cc103ac42ead40b7cc6` | Empty deployment-trigger commit; same source tree as reviewed candidate |

Reviewed/preview tree: `eda93677513ef420d11008e38255159fd3986578`.

These are operational restore baselines, with the connected DX phase-selection limitation identified in the investigation. “Known-good” does not mean the old evaporator physics is validated. Main, PR #3 and production files must not be changed by this experiment. The experimental branch starts at the preview commit and retains those existing ancestors. The immutable SHA values make each baseline independently retrievable without changing a live branch.

To inspect a baseline in a separate checkout: `git switch --detach <full-commit>`. Do not force-reset main or PR #3. Prototype files are under `experiments/dx-fv/`; deleting that directory in a disposable checkout removes the experiment without replacing application files.

Stages 4 and later, five-section validation, production integration, profile/UI migration and merging require separate explicit approval. This stage exercises three sections only.

## Validated Stage 3 prototype restore point

Commit `f7b19adb67587d88195d53cee6081c8b014fb9ed` freezes the validated three-section prototype and its original backward-Euler tests/references. Hosted verification: https://github.com/cdehek/Ammonia-sim/actions/runs/37996731094 . The numerical time-accuracy stage is a fast-forward descendant on the same experimental branch; this commit remains retrievable. No production or release-candidate ref is moved.

The currently authorized follow-up is isolated three-section temporal accuracy only. Spatial refinement, equipment calibration, circuit/UI integration and merges still require explicit approval.

## Validated temporal-accuracy restore point

Commit `3e2cdbf1c8e1c9c42268a72bda5b0d05cf54f0f5` preserves conservative adaptive TR-BDF2, its three-section temporal comparisons and all verified baseline files. Hosted verification: https://github.com/cdehek/Ammonia-sim/actions/runs/38000900498 . The approved spatial-comparison work is a fast-forward descendant on the same experimental branch.

The current authorization permits isolated **three-versus-five-section** comparisons only. No finer integrated mesh, equipment calibration, Live Plant/UI integration, production/PR #3 changes or merges are authorized. Earlier three-section-only notes describe the frozen prior stages.

## Validated three/five-section restore point

Commit `7bf0c326414a7d8b7e51f553a273a0041fe1e827` preserves the qualified three-versus-five comparison and all earlier baselines. Hosted verification: https://github.com/cdehek/Ammonia-sim/actions/runs/38003601163 . The approved nine-section stage is its fast-forward descendant on the same experimental branch.

Current authorization covers isolated **3/5/9-section** spatial comparison and unchanged-physics diagnostics only. No 17-or-finer integrated mesh, wall/equipment physics, calibration, Live Plant/UI/production/PR #3 changes or merges are authorized. Earlier three/five-only restrictions describe their frozen stages.

## Completed three/five/nine spatial-validation milestone

Commit **`c105584311ca4a539c8410bf02ae0519b2bc8448`** preserves the completed controlled spatial study, independent temporal/EOS qualification, warm-domain evidence and browser/cost verification. Its parent is `7bf0c326414a7d8b7e51f553a273a0041fe1e827`. Hosted verification: https://github.com/cdehek/Ammonia-sim/actions/runs/38009179503 — all four experimental jobs passed.

The user reviewed and accepted **five sections as provisional working baseline and nine as higher-resolution comparison; neither is proven spatially converged**. This milestone is retained unchanged as an ancestor of the documentation transition. No main or PR #3 ref is moved.

The current authorization is **documentation only**: [DEVELOPMENT_HANDOFF.md](DEVELOPMENT_HANDOFF.md) and [WALL_AIR_THERMAL_DESIGN_PROPOSAL.md](WALL_AIR_THERMAL_DESIGN_PROPOSAL.md). Thermal implementation, finer meshes, equipment calibration, circuit/UI/profile integration and merges require explicit approval. Earlier authorization statements in this file describe their historical stages and are superseded by this current boundary.
