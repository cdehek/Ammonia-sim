# Scientific baseline and provenance

The clean starting checkout was detached at exact B12 `e6779247eec9a39350a39551eec1740f06097aeb` and matched `origin/research/b12-private-https-ipad-preview-20261019` before creating the new isolated branch. No repository AGENTS.md files were found. `evidence/local-refs-before.txt`, `remote-refs-before.txt`, and `pr3-before.json` preserve pre-implementation identities. No remote mutation is authorized except pushing the new B13 branch.

| Protected reference | Commit |
|---|---|
| A2 | be9eb35a4ddf5098e685182f8104685127c6a6ee |
| B10 | a49c5c4ade306fe02117139cf81c30a59727a7b1 |
| B11 | 909de1579051bfadca0e282adf93eaedc0e24b9c |
| B12 | e6779247eec9a39350a39551eec1740f06097aeb |
| B9C | b67afb3215075b2ec82bef376d39e03953dc0da2 |
| B9D | 20ddac46423a7a742af19ac415ef8796cf3a429f |

`audit.py` reads every tracked B12 blob through Git and compares its bytes with the working tree. `evidence/historical-files.json` retains blob IDs, SHA-256 and byte counts; `source-preservation.json` records the fourteen-file accepted A2 closure, including original thermodynamic tables. Snapshot sources match protected A2 blobs exactly. Root research files that historically differed from A2 are not silently used: the pinned bundle contains the accepted closure.

B9C `candidate-bundle.mjs`, `diagnostic-candidate-bundle.mjs`, original-A2 `control-bundle.mjs` and isolated model match their protected Git blobs. B11's deployed science copy is byte-identical to the B9C candidate. B11 portable ZIP/assets and original workstation source derivations are checked by the read-only B12 verifier, with output redirected into B13. Retained Chromium/WebKit receipts and training exports are revalidated, not regenerated or overwritten.

Fresh Node comparisons establish bit-exact original-A2 ↔ B9C ↔ diagnostic B9C equality at the four accepted checkpoints. Three canonical 0.01 s runs and the observed replay have exact checkpoint and cumulative attempt hashes. Settings match B9D's `trace:true,timestepGrowth:'failure-aware'`; no tolerance, minStep, iteration or attempt budget changes. `thermalJacobian` remains its original default finite differences, not the optional exact mode.

Retained browser comparison: all eight Node-versus-Chromium state/record comparisons differ at the binary64 level. A cold initial density witness is Chromium `4033d96d03316dda` versus Node `4033d96d03316dd9`; initial total mass differs accordingly. Different engine versions/math implementations are a plausible explanation, not an isolated proven cause. This pre-existing runtime difference is already present with original A2 and does not arise from B13 instrumentation. Same-engine equality remains mandatory and passes. No fresh browser parity or personal-device benchmark is claimed.

PR #3 baseline: open/unmerged; base `main` at `0473d32f62db992fde0f581d116e1bd0c8e7d8ed`; head `v0.5.5-stage-1` at `d4422425750a1d3c4e432cc103ac42ead40b7cc6`. The before/after audit compares these plus state/draft/repository identities. The owner reports B12 as deployed; private hosted assets were not inspected or modified.
