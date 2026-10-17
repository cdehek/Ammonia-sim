# Research B8 — blocker disposition

**B8 TRIAGE PASS — ACTIONABLE DISPOSITION**

Accepted A2 requires PH, saturation and M/U/V recovery. Its current table engine has no CoolProp DP dependency. Four DU endpoints remain conditional full-VLE blockers; eleven DP identities remain scientifically invalid diagnostics outside the current model path. The seven-per-engine boundary refusals and two inward hazards remain separate qualification blockers.

Start: `429ce020128763454324529cc1c7640cf1f474e8`.
Branch: `research/browser-eos-b8-blocker-disposition-20261017`.
Delivery SHA: the commit containing this directory; obtain with:

```bash
git log -1 --format=%H -- experiments/dx-fv/browser_eos_b8/
```

Read the [Engineering Report](ENGINEERING_REPORT.md), [Mechanic’s Report](MECHANICS_REPORT.md), [call graph](PROPERTY_CALL_GRAPH.md), [reachability matrix](A2_PROPERTY_REACHABILITY_MATRIX.md) and [next milestone recommendation](NEXT_MILESTONE_RECOMMENDATION.md). A triage pass does not qualify an unresolved property or broader simulator. Recommended Option C is not started. Stop for engineering review and explicit approval before further work.

| Deliverable | Location |
|---|---|
| Engineering and industrial interpretation | ENGINEERING_REPORT.md; MECHANICS_REPORT.md |
| Four exact DU inputs and native/browser/default/full-VLE results | DU_ENDPOINT_DISPOSITION.md; evidence/du-endpoints.json |
| Eleven DP identities / full 44-observation provenance | DP_FAILURE_DISPOSITION.md; evidence/dp-identities-11.json; evidence/dp-observations-44.json |
| Actual accepted source/dependency edges | PROPERTY_CALL_GRAPH.md; evidence/a2-trace-summary.json; evidence/source-reference-index.json |
| Bounded observation with exact parity | trace-a2.cjs; evidence/a2-trace.json.gz; evidence/trace.log |
| Reachability / severity / confidence / consequence / smallest next milestone | A2_PROPERTY_REACHABILITY_MATRIX.md; ISSUE_PRIORITY_MATRIX.md; evidence/issue-priorities.json |
| Excel tracker import | evidence/issue-priorities.csv and issue-priorities.json (35 flat issue records) |
| C1 propagation / rollback / floor / synthetic versus natural | C1_FAILURE_PROPAGATION_REVIEW.md; evidence/c1-reused-a2-audit.json; evidence/du-adapter-replay.json |
| Original scientific contract | SCIENTIFIC_CONTRACT_AUDIT.md; source/artifact preservation and evidence/acceptance.json |
| Protected checkpoint / correction / PR / refs / all starting hashes | PROTECTED_CHECKPOINT_AUDIT.md; evidence/start-audit.json; starting-files-sha256.json; remote-*.tsv; pr3-*.json |
| Boundary hazards retained | evidence/boundary-attribution.json; webkit-ledger-69-hazard.json; webkit-ledger-76-hazard.json |
| Exact initialization construction provenance | initialization-provenance.mjs; evidence/initialization-provenance.json |
| Source result references | evidence/source-evidence-sha256.json; all original B7/B5A evidence remains protected |
| Reproducible extraction and disposition | extract-evidence.py; build-disposition.py; write-dp-report.py; verify-disposition.py |
| Failed attempts / execution scope | EXECUTION_NOTES.md; evidence/trace-attempt-1.log |
| Next milestone / alternatives / smallest success criteria | NEXT_MILESTONE_RECOMMENDATION.md |

All evidence filenames without a path in this table are under `evidence/`.

## Bounded reproduction

Use a disposable checkout of the delivered B8 branch. Python standard library and Node suffice; no CoolProp install/build, native execution, Playwright install or browser run is needed. The runtime trace uses exact preserved A2 snapshots and original table/engine, not root later research model files. Original browser/native results are reused with verified digests.

```bash
timeout 120s python experiments/dx-fv/browser_eos_b8/audit.py --final
timeout 30s python experiments/dx-fv/browser_eos_b8/extract-evidence.py
timeout 15s node experiments/dx-fv/browser_eos_b8/replay-du-adapter.mjs
timeout 15s node experiments/dx-fv/browser_eos_b8/initialization-provenance.mjs
timeout 45s node experiments/dx-fv/browser_eos_b8/trace-a2.cjs
timeout 30s python experiments/dx-fv/browser_eos_b8/build-disposition.py
timeout 15s python experiments/dx-fv/browser_eos_b8/write-dp-report.py
timeout 45s python experiments/dx-fv/browser_eos_b8/verify-disposition.py
```

These scripts write only B8 receipts and may overwrite regenerated B8 evidence; run in a disposable checkout. Trace counts/hashes can differ on another JS runtime without authorizing any accepted numerical change; exact observed/unobserved parity is checked within the run. The delivered Node 24 trace is observation evidence, not replacement historical Node 22 qualification. Archive compression is lossless. Gate 0 `audit.py --start` is only for exact starting HEAD, not reproduction after delivery.

`audit.py --final` checks local historical bytes, immutable artifacts, accepted snapshots and saved pre-push remote map. A fresh live remote snapshot must separately be compared with `remote-before.tsv`; the only allowed new ref is B8 and it must equal delivered HEAD. The final delivery response reports post-push clean/ref verification. No PR, merge or deployment is part of B8.

`evidence/delivery-manifest-sha256.json` seals all B8 files except itself. `seal.py` regenerates that manifest only after verification. Post-push receipts remain outside the commit.
