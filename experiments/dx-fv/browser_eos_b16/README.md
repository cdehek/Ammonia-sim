# B16 — desktop browser Worker performance and integration readiness

**B16-A0 DESKTOP/WORKER READINESS PASS**. Integration decision: **CONDITIONAL GO** for a later separately authorized isolated research review. No integration, deployment, default change or accepted-engine promotion.

Start B15 `eb3856cfdc0b6a602d8e8ae347e6b4a955b7bf35`; branch `research/b16-desktop-worker-performance-20261020`; design `20406db` committed before implementation. Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md), [COLD_PERFORMANCE_ROOT_CAUSE.md](COLD_PERFORMANCE_ROOT_CAUSE.md) and [INTEGRATION_READINESS_DECISION.md](INTEGRATION_READINESS_DECISION.md). Every file is B16-owned. Scientific bundles are frozen B15 copies; all accepted/historical files remain unchanged.

Actual Linux Chromium Workers pass exact science/failures. Warm benefit persists; cold tradeoff depends on runtime/warmup and remains unresolved causally. No actual owner Windows/macOS/Edge/WebKit qualification. Accepted horizon .001 s; all longer results UNQUALIFIED RESEARCH, maximum solve .01 s. No refrigeration run is extended in time by repeated reset sessions.

## Owner handoff

Extract [b16-owner-benchmark.zip](b16-owner-benchmark.zip), run `python3 serve.py` (Windows often `py serve.py`), open localhost:8765. Read [OWNER_DESKTOP_BENCHMARK.md](OWNER_DESKTOP_BENCHMARK.md). Python standard library plus an existing browser; no scientific environment/npm install, public deployment or Cloudflare access. Genuine owner-device status is NOT TESTED. Packaged actual UI/download validation was Linux cloud only.

## Reproduce from repository root

```sh
python3 experiments/dx-fv/browser_eos_b16/audit.py review
python3 experiments/dx-fv/browser_eos_b16/validate.py
python3 experiments/dx-fv/browser_eos_b16/run-browser.py science --name review-science
python3 experiments/dx-fv/browser_eos_b16/run-browser.py performance --name review-worker
python3 experiments/dx-fv/browser_eos_b16/run-browser.py micro --name review-micro
python3 experiments/dx-fv/browser_eos_b16/run-browser.py retention --name review-retention
python3 experiments/dx-fv/browser_eos_b16/run-node.py primary --name review-node
python3 experiments/dx-fv/browser_eos_b16/run-node.py counters --name review-counters
python3 experiments/dx-fv/browser_eos_b16/run-node.py jitless --name review-jitless
node --max-old-space-size=512 experiments/dx-fv/browser_eos_b16/context-counts.mjs
```

Use fresh names: retained receipts are never overwritten by campaign runners. `trace` campaign has fixed trace artifact names; reproduce it in a fresh isolated checkout/directory rather than overwriting delivered trace evidence. Installed Playwright/Chromium are required only for automation. Primary performance runners fail closed unless the retained pinned Chromium science receipt passed. Run heavy suites sequentially. Scripts bound processes/CPU/heap/history and tear down Workers/browser; external loss is not scientific refusal. Analyze retained delivered samples with `analyze.py`; rerender reports with `write-reports.py`; plot actual pairs with `plot.py`. Review-named samples remain separate and are not silently substituted into delivered statistics.

`assets/` contains original/candidate plus separate counted/observer sources. `evidence/` retains exact science hashes, compressed full refusal records, failed initial harness assumptions, every valid timing sample, V8 traces, context/cache counts, short memory observations and protected-source/ref/PR audits. `lossless-compaction.json` verifies raw science JSON bytes after decompression. `.runtime/` is ignored temporary runtime/download/socket storage, never a dependency tree or committed trace cache. Machine-readable milestone status is at the directory root. Final branch SHA and remote/clean completion check are supplied at delivery.
