# B7 — B5A Gate A browser/WASM qualification

**FOCUSED BROWSER GATE A PASS**

Gate 1 PASS — BUILD AND ABI VERIFIED. Gate 2 PASS — FOCUSED BROWSER GATE A PASS.
The three independently resolved original liquid inventories recover in actual
Chromium and desktop WebKit through the compiled legacy DU repair. Four Gate B
endpoints remain unresolved. This is limited experimental qualification through
an isolated runtime configuration harness, not complete backend, A2 or production
qualification.

Supplemental unchanged DP endpoint diagnostics include invalid raw qualities;
`evidence/quality-disposition.json` strictly refuses them. DP physical
qualification is not passed. They are retained outside the three-liquid DU claim.

Branch: `research/browser-eos-b7-gatea-wasm-qualification-20261017`.
Start: `f6227de0760d81994c60497869f5c6013a9d403f`.
The full final delivery SHA is the commit containing this directory, provided in
the delivery response and recoverable without a self-referential file hash:

```bash
git log -1 --format=%H -- experiments/dx-fv/browser_eos_b7/
```

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md),
[FAILURE_MATRIX.md](FAILURE_MATRIX.md), [EXCEPTION_ABI.md](EXCEPTION_ABI.md),
[PERFORMANCE_AND_MEMORY.md](PERFORMANCE_AND_MEMORY.md), and
[the Mechanic's Report](MECHANICS_REPORT.md). Reproduction is in [BUILD.md](BUILD.md).
Machine-readable decisions are `evidence/gate1-audit.json` and
`evidence/acceptance.json`. Every archived result remains an observation with its
original scientific qualification status.

| Required deliverable | Location |
|---|---|
| 1. Branch and full final SHA | Above; delivery response; Git object containing this report |
| 2. Starting checkpoint and preservation | `evidence/checkpoint.json`, `starting-files-sha256.json`, `start-audit.json`, `final-preservation.json` |
| 3. Complete inherited source/patch manifest | `source-control.json`, `source-candidate.json`, `source-final-complete.json`, `start-audit.json`, `dependency-verification.json` |
| 4. Original Gate A patch hash | `source-*.json`; engineering report; original patch remains protected in B5A |
| 5. Matched rebuild instructions | BUILD.md, `build.sh`, `build-diagnostic.sh` |
| 6. Generated artifact identities | `evidence/artifacts-with-diagnostics.json`, `vendor/` |
| 7. Exception ABI review | EXCEPTION_ABI.md, `abi-generated-source.json`, `wasm-abi-inventory.json`, `abi-*-corrected.json` |
| 8. Full-VLE activation | DESIGN.md, `runtime-environment.mjs`, `activation-*.json`, `gate1-audit.json` |
| 9. Three resolved liquids | FAILURE_MATRIX.md, `seven-science-audit.json` |
| 10. Four unresolved endpoints | FAILURE_MATRIX.md, acceptance blocker list |
| 11. Complete seven-case matrix | FAILURE_MATRIX.md, `activation-*.json`, `seven-science-audit.json` |
| 12. 250 records / 73 pairs | `fixed-inputs.json`, `fixed-inventory.csv`, `canonical-provenance.json`, `ledger-*.json`, `native-fresh-replay.json`, `ledger-science-audit.json` |
| 13. Inherited property regressions | `regressions-*.json`, `inherited-focused-audit.json`, `shared-*.json`, `additional-audit.json` |
| 14. B6 loader/lifecycle | `loader.mjs`, `loader-vs-B6.diff`, `lifecycle-*-serialized.json`, `regression-audit.json`, worker evidence |
| 15. C1 and strict 35 bar | `c1-*-explicit-bar.json`, `support-attribution.json`, engineering report |
| 16. Focused A2 | `a2-*.json`, `a2-audit.json`; unchanged existing B6/C1 subset |
| 17. Native/Chromium/WebKit numbers | `seven-science-audit.json`, `ledger-science-audit.json`, `native-*-comparison.json`, `native-fresh-replay.json`, `shared-native-audit.json` |
| 18. Original budget audit | `seven-science-audit.json`, `ledger-science-audit.json`, `inherited-focused-audit.json`, `a2-audit.json`, engineering report |
| 19. Workers, memory, performance | PERFORMANCE_AND_MEMORY.md, `workers-*.json`, `worker-audit.json`, `performance-*.json`, `performance-summary.json` |
| 20. Source differences/provenance | Source manifests, `diagnostic-*.patch`, `loader-vs-B6.diff`, compile commands/caches, build/runtime identities |
| 21. Failed attempts and omissions | EXECUTION_NOTES.md, retained `evidence/logs/`, initial failed browser receipts |
| 22. Qualification blockers | `evidence/acceptance.json`, `evidence/final-review.json`, `quality-disposition.json`, engineering report |
| 23. Next scientific milestone | Engineering report; stop for engineering review |
| 24. Reproduction commands | BUILD.md and scripts in this directory |
| 25. 🔧 Mechanic's Report | MECHANICS_REPORT.md |

All evidence paths in the table are relative to `evidence/` unless a source or
report is named. `delivery-manifest-sha256.json` seals B7 files; it excludes itself.
The final post-push receipt is emitted outside the Git tree to avoid embedding
the hash of its own commit. The final clean/ref audit is also reported in the
delivery response. Only additive B7 research is committed and pushed. No merge,
deployment, UI/Live Plant change, Gate B repair or further campaign follows.
