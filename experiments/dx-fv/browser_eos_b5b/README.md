# B5B — boundary classification and numerical recovery contract design

Start: `14b8b386148c687fcb549d5f17003fa9e63fbca8`.
Branch: `research/browser-eos-b5b-boundary-contract-design-20261016`.
The delivery commit is the commit containing this report, supplied in the final
delivery response and by `git rev-parse HEAD`; a commit cannot contain its own SHA.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [CONTRACT_PROPOSAL.md](CONTRACT_PROPOSAL.md),
[INTERFACES_AND_A2.md](INTERFACES_AND_A2.md), [MATRIX.md](MATRIX.md),
[OPTIONS.md](OPTIONS.md), and [MECHANICS_REPORT.md](MECHANICS_REPORT.md).
All files here are diagnostic research. No accepted/experimental backend,
adapter, loader, solver, artifact or historical evidence file is modified.

## Reproduction

Run from repository root with Python 3.12, mpmath and Playwright, Node and
Chromium. This delivery used Chromium 154.0.8037.57 and Playwright desktop WPE
WebKit 26.5, not physical Safari/iPadOS. Browser replay is bounded by an outer
150-second process timeout; per-engine launch/navigation timeouts are 30/45 s.

```
python experiments/dx-fv/browser_eos_b5b/audit.py --start
timeout 150 python experiments/dx-fv/browser_eos_b5b/replay.py
timeout 120 python experiments/dx-fv/browser_eos_b5b/analyze.py
python experiments/dx-fv/browser_eos_b5b/conversions.py
python experiments/dx-fv/browser_eos_b5b/classify.py
node experiments/dx-fv/browser_eos_b5b/propagation.cjs
python experiments/dx-fv/browser_eos_b5b/audit_evidence.py
```

Use a disposable output checkout or preserve copies before overwriting this
milestone's delivery evidence. `replay.py` uses `CHROMIUM_PATH` and `WEBKIT_PATH`
when set. Defaults are `/usr/bin/chromium` and
`/workspace/b5b-browsers/webkit-2336/pw_run.sh`. The current workspace has WebKit
installed under `/workspace/b5b-browsers`; host library warnings and setup are
retained in `evidence/webkit-setup.log`. The six required library packages were
downloaded from B5's `browser-libraries.json`, all SHA256-verified and extracted
under `/workspace/b5b-webkit-libs`; their shared libraries were copied into this
new WebKit installation's WPE sys/lib. No repository loader was edited.

The unchanged B5 evaluator expects
`/workspace/coolprop-b5/dev/fluids/Ammonia.json`. Download only that file from
pinned upstream CoolProp `ae81610e7d23efc57f9d051c8e70a4d66e87537f`, with SHA256
`4d451fadbe6eb1c2441169c599890cf7cd6edc818918f23959e2afb20a881e14`.
`analyze.py` verifies its digest before evaluation. Do not change the evaluator,
fluid constants or reference convention. No CoolProp clone/build is needed.
Reproduction requires installed browser libraries and localhost socket access.

The first network clone failed under sandbox proxy isolation; rerunning with
the tool's additional network permission succeeded. No authentication values
were printed. Browser setup used that same permission. The initial two browser passes were
made: the first confirmed values; the second supplied each engine's own saved
fixture keys instead of sharing Chromium key labels. Scientific bits agree.
The final bounded pass added two saved mathematical false-acceptance controls
after their discovery in B5's existing 73-pair ledger; it preserved those keys
and raw historical bits as well. The per-engine matrix has 24 PH diagnostics
plus these two fixed-inventory controls, separate from the seven originals.
No scientific acceptance failure or timeout was discarded.

## Machine-readable evidence

- `checkpoint.json`, `starting-file-hashes.json`, `refs-before.txt` and
  `start-audit.json`: exact checkpoint, all 1838 starting file hashes, all remote
  refs, independently verified artifact/accepted snapshot identities.
- `fixed-inputs.json`, `fixed-inventory.csv`: original fourteen browser identities,
  seven unique inventories, PH and DU bits, original conservative inventory and
  original output/error evidence. They are extracted, never regenerated.
- `chromium-replay.json`, `webkit-replay.json`: observed raw-before-guard paths,
  originating PH, full returned bits, independent DT calls, conversion, 24-case
  per-engine matrix, lower pressure and temperature guard isolation.
- `seven-case-analysis.json`: fresh 65/90-digit same-EOS roots, original PH vs
  mathematical EOS evaluation, exact rational rounding error of each binary64
  inventory operation, raw-state EOS evaluation and original residuals. Includes
  labeled inherited B5 detailed pressure attribution, not a new reference model.
- `matrix-mathematics.json`: fresh independent fixed-inventory and returned-state
  EOS checks including physical coexistence equations. No interval certificate.
- `exact-conversions.json`: exact rational Pa/bar values and conversion errors
  for the three adjacent boundary requests and seven raw recovered pressures.
- `information-loss-collisions.json`: non-injective PH→M/V/U examples.
- `false-acceptance-controls.json`: two saved exact-inventory outward-mathematical /
  inward-binary64 controls, independently checked at 65/90 digits and replayed
  through the actual unmodified adapter in both engines. No physical-exit claim.
- `prototype-results.json`: proposed classifications, observed outcomes, separate
  hypothetical contract samples; contains no returned thermodynamic states.
- `interface-source-evidence.json`, `propagation.json`: actual source ownership
  and interface-only error propagation observations, no A2 campaign.
- `scientific-audit.json`, `final-preservation.json`, `refs-after.txt`:
  focused checks and final preservation receipt. The separate post-push receipt
  described in delivery verifies final remote target and clean tree.

`audit.py` checks all historical file hashes and 143 archived native/browser
identities, including decompression hashes, and twelve A2 snapshots. It does
not rebuild external CoolProp/dependencies or requalify native libraries.
`audit_evidence.py` compares both browser engines to original B5 values and all
21 inherited sweep cases; errors remain errors. No complete A2 campaign is run.
Before final commit/push, record `git ls-remote origin` into `refs-after.txt`,
stage only this directory, and run `audit.py` to verify every starting ref and
only additive B5B changes. Repeat the remote comparison after push externally
to the committed evidence to avoid a self-referential final commit receipt.
