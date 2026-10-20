# B15 — exact vapor PH pressure-bracket reuse

**B15-A1 EXACT-EQUIVALENCE OPTIMIZATION PASS**. Final candidate passes Node and same-browser scientific gates. Warm paired median improvement 13.41%; cold -2.51% (1/6 faster). All measurements and uncertainty are retained.

Branch `research/b15-vapor-ph-bracket-reuse-20261020`; B14 start `71608010fe49946dc542a4d85dff315c875274ad`; design commit `90806af` preceded implementation. Final SHA is branch HEAD supplied at delivery (a commit cannot embed its own hash). All work is B15-only. Qualification remains 0.001 s; all longer results are **UNQUALIFIED RESEARCH**; maximum solve 0.01 s.

Final review found v1's optional internal PT argument reachable through public PT. Its forged-holder counterexample, source and all timings are preserved under `prototype-v1/` / `evidence/prototype-v1-*`. Final PT forwards only the original three public arguments; fresh property, coupled, refusal, browser and performance checks bind the corrected build. No failing comparison was removed. Main property binary64 payload has the same SHA for both ordinary-input suites. Final reports exclude v1 timing from final-version estimates.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [PERFORMANCE_BENCHMARK.md](PERFORMANCE_BENCHMARK.md), and [NEXT_MILESTONE_RECOMMENDATION.md](NEXT_MILESTONE_RECOMMENDATION.md). No promotion/deployment is authorized.

## Reproduce from repository root

```sh
python3 experiments/dx-fv/browser_eos_b15/validate.py
python3 experiments/dx-fv/browser_eos_b15/seal.py --verify
sh experiments/dx-fv/browser_eos_b15/final-audit.sh
python3 experiments/dx-fv/browser_eos_b15/build.py
python3 experiments/dx-fv/browser_eos_b15/run.py control warm original review-control
python3 experiments/dx-fv/browser_eos_b15/run.py candidate warm original review-candidate
node --max-old-space-size=512 experiments/dx-fv/browser_eos_b15/verify.mjs review-control review-candidate
python3 experiments/dx-fv/browser_eos_b15/browser.py warm-original browser-review-warm
python3 experiments/dx-fv/browser_eos_b15/performance.py --out-file .runtime/review-timings.json
```

Use unused names; retained evidence is never silently replaced. `run.py` supports cold/warm × original/added/fine and control/candidate/observe-control/observe-candidate; pair each schedule to its own control. `supervise.py` bounds regression scripts. Node built-ins/Python standard library suffice; installed Playwright/Chromium only for browser, Matplotlib only for figures. No dependency was added. Historical generators were not run. `science-v2.py` / `finish-science-v2.py` document the final replay after preserving preliminary artifacts; these campaign scripts intentionally use fixed names and refuse overwrites.

`receipts.mjs` resolves verified lossless local references; full original scientific vectors are retained once. `receipt-compaction.json` records exact resolved JSON hashes; `verify-compaction.mjs` verifies them. The earlier v1 compaction manifest is retained separately. Runtime data/caches are ignored here. Original control is restored by selecting `control-bundle.mjs`; it is byte-identical to pinned B9C. No code outside B15 enables reuse. Remove B15 in a separate checkout to remove the experiment without accepted-source edits.
