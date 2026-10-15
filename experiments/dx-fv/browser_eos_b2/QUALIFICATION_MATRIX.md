# B1 → B2 qualification boundary (audit before B2 experiments)

B1 checkpoint: ef1562ae1680fccf3323391e9ec83788c5ae1e69.
Accepted A2: be9eb35a4ddf5098e685182f8104685127c6a6ee.
Only B2 additions are permitted. checkpoint.json pins all 609 starting files.
All 12 B1 accepted dependencies match the accepted Git objects byte for byte.
B1 BUILD.md, SOLVER_CONTRACT.md, ENGINEERING_REPORT.md, raw precision,
supplement, coupled, audit and build-provenance evidence were inspected.

| Contract | B1 completed | B2 planned boundary |
|---|---|---|
| Exact liquid PH defect, both engines/four builds | Pass 44-bit; controls fail slope/closure | Preserve; exact-input broad phase matrix rerun |
| Static M/U/V | 16/16 per engine candidate | Historical only unless explicitly rerun |
| Near-saturation vapor caloric residual | Remaining ~−0.00011919 J/kg | Primary exact fixture, DT residuals, native cross-check, source-path diagnosis |
| Phase-aware derivatives | Stable liquid/vapor only | Both sides, endpoint and coexistence exclusions, crossing flags, original probes |
| Five operating fixtures × three regimes × two engines | 30/30 pass | Full accepted assertion suite through injection |
| Same-EOS temporal comparisons | 20/20 pass | Also accepted maxStep refinement and fixed-step order |
| Independent conservation / frozen direct EOS | Pass limited operating matrix | Reconstruct every completed B2 record; distinguish table versus direct EOS |
| Zero-exchange, sealed, reference-offset invariance | Not run | Unchanged coupled-test assertion blocks |
| Pure trial, atomic update, scheduled transitions | Not run | Unchanged coupled-test and controls |
| Forced solver/accuracy/domain, second-half rollback | Not run | Unchanged coupled-test assertion blocks |
| Exact-boundary and false-proof classification | Not run | Complete accepted domain paths where adapter permits |
| Four Jacobian/controller configurations | Only FD/failure-aware operating runs | Attempt unchanged accepted selections; explicit per-block results |
| A2 rules, phase replay, original-controller ancestor comparisons | Not run | Inventory separately; require Node filesystem/Git/compiled injection harness |
| statePT hot-refrigerant boundary fixture | Missing adapter interface | BLOCKED: synchronous statePT(p_bar,T_C); no substitute PH fixture |
| Long duration / repeated transitions | Not run | Gated on complete short-suite success; no hour run if any gate open |
| Matched 30/44 coupled cost | Not run | Matched short workload after scientific runs; report harness overhead |
| Browser memory/offline/worker | Limited B1 pass, 53.75 MiB linear memory | New measurements where executed; total device memory remains unknown |
| Physical Safari/iPad | Not run | NOT RUN: actual device unavailable; no hosting authorized |

The B1 adapter uses unchanged canonical M=rho V, U=Mh−PV and direct DU recovery,
with accepted table PH only as a support guard. No interpolation or correction is
returned. Requested PH coordinates remain stage coordinates; actual DT residuals
are separately measured. No accepted source, threshold, finite difference,
fixture, reference or source-level EOS expression is altered in B2.

The complete accepted suite is the source of assertions. Independent execution
of an assertion block preserves failures and permits collecting later contracts;
it does not convert a failed full suite into a pass. Final results are recorded
in SUITE_RESULTS.md and evidence; this table records the pre-execution boundary.

Final B2 disposition: all 18 selected FD/failure-aware core groups pass in each
browser; all 36 domain cases pass per engine/configuration with the explicitly
isolated PT mapping. Original 33-pass/3-blocked interface runs remain preserved.
The eight-case canonical regression passes only one endpoint per build/engine,
and the same-phase liquid derivative/coupled counterexample fails. The full
four-configuration/reference suite, long operating endurance and physical device
qualification remain NOT RUN. Final assessment is **BLOCKED**.

Matched 30/44 property and short coupled cost measurements complete in both
engines, with observed WASM linear memory 53.75 MiB. Offline-context replay
completes 4/4 backends in Chromium and fails navigation for 0/4 in WebKit;
origin-disabled cache replay completes 4/4 in both. These separate results do not
qualify physical Safari or total device memory. See PERFORMANCE_RESULTS.md.
