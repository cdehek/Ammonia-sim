# B13-A0 scientific horizon diagnostics

**B13-A0 DIAGNOSTIC CHARACTERIZATION PASS**

Exact B12 parent `e6779247eec9a39350a39551eec1740f06097aeb`; new branch `research/b13-dx-fv-horizon-diagnostics-20261019`. All changes remain in this directory. No deployment, production merge, plant coupling, solver optimization, source change or tolerance relaxation.

All times above 0.001 s are UNQUALIFIED RESEARCH. No longer-duration scientific qualification is claimed.

| Fixture | Actual t (s) | Accepted substeps | Rejected trials | Residuals | Newton corrections / Jacobians | TR-BDF2 stages |
|---|---|---|---|---|---|---|
| cold | 0.01 | 32 | 1 | 5272 | 235 | 102 |
| warm | 0.01 | 86 | 8 | 19380 | 867 | 306 |

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md) for the decision, [SOLVER_PERFORMANCE_RESULTS.md](SOLVER_PERFORMANCE_RESULTS.md) for measured cost, [LONG_HORIZON_FEASIBILITY.md](LONG_HORIZON_FEASIBILITY.md) for conditional cost projections, and [NEXT_SOLVER_MILESTONE_PROPOSAL.md](NEXT_SOLVER_MILESTONE_PROPOSAL.md) for the next investigation. The owner-reported B12 commissioning retrospective is separate from instrumented evidence.

Reproduction from repository root (Python 3.12, Node 24.19.0; standard library only except optional figures):

```sh
python3 experiments/dx-fv/browser_eos_b13/audit.py
python3 experiments/dx-fv/browser_eos_b13/run.py --fixture cold --horizon 0.001 --name review-cold-baseline.jsonl.gz
node experiments/dx-fv/browser_eos_b13/verify-results.mjs
python3 experiments/dx-fv/browser_eos_b13/analyze.py
node --max-old-space-size=512 experiments/dx-fv/browser_eos_b13/contracts.mjs
python3 experiments/dx-fv/browser_eos_b13/plot.py
python3 experiments/dx-fv/browser_eos_b13/write-reports.py
```

Wrap contracts in `timeout 30` as in the recorded run. Use fresh receipt names; `run.py` refuses overwrite. Select each next horizon only after reviewing the earlier result under [HORIZON_PROBE_PROTOCOL.md](HORIZON_PROBE_PROTOCOL.md). The runner never chooses a longer horizon. Canonical three-replicate full probes use the sequence 0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01 s. `--variant observed` selects separate measurement code, `--variant control` selects original accepted A2 with unchanged settings.

`evidence/analysis.json` contains interval tables, phase events, convergence distributions, profiles, physical records and projections. Raw complete JSON lines are retained in compressed receipts. `scienceExact` preserves binary64 state/record bits. Each checkpoint's `attemptsHash` covers the original full cumulative diagnostic stream; the verifier restores the original undefined iteration-context field omitted by JSON and independently recomputes all canonical science/attempt hashes. To avoid committing repeated identical scientific payloads, `compact.py` verified their hashes and exact state encodings before replacing them with explicit references to canonical r1 checkpoints; independent timings, counters, CPU/memory samples and observed profiles remain in each run. `analyze.py` and `verify-results.mjs` resolve these references. Both canonical r1 receipts retain the full diagnostic streams. `receipt-deduplication.json` records the operation. No runtime/browser cache is tracked.

Node measurements are from a managed Linux VM, not a desktop Chrome/Edge benchmark or an owner-device test. Preserved B12 deployment is established by the owner's report and unchanged package/source bytes; B13 does not independently inspect the private deployment.

Stop for engineering review after the authorized research-branch push. Milestone status is in `milestone-status.json`.

Final local review gate:

```sh
python3 experiments/dx-fv/browser_eos_b13/validate.py
python3 experiments/dx-fv/browser_eos_b13/seal.py --verify
```

`evidence/remote-refs-after.txt` and `pr3-after.json` are post-implementation, pre-push snapshots. They prove no protected remote changes during research. After pushing only the new branch, read fresh snapshots into ignored `.runtime/remote-refs-published.txt` and `.runtime/pr3-published.json`, then run:

```sh
python3 experiments/dx-fv/browser_eos_b13/verify-protected.py --published --after .runtime/remote-refs-published.txt --pr-after .runtime/pr3-published.json
git status --porcelain
```

The final published-HEAD equality and clean-tree check are reported at handoff; they cannot be embedded in the same commit while naming that commit's own final SHA. No PR or deployed reference is mutated by these checks.
