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
