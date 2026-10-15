# Complete accepted A2 gate ledger

**Assessment: BLOCKED.** The full A2 backend qualification is incomplete and a valid-domain numerical defect is demonstrated.
All PASS entries below are newly executed B2 tests. B1 historical results are not counted.
Each row is an unchanged accepted assertion group, not an assertion count. The original suite is split only to retain independent later results after a failure; failed blocks stay failed.

FD thermal Jacobian / failure-aware growth, original five-section physics:

| Accepted assertion group | Chromium | WebKit |
|---|---|---|
| Five-section allocation, defaults and scope | [PASS](evidence/chromium-suite-fd-aware-block-0.json) | [PASS](evidence/webkit-suite-fd-aware-block-0.json) |
| Cold startup: three regimes, temporal/direct EOS and cap refinement | [PASS](evidence/chromium-suite-fd-aware-operating-cold.json) | [PASS](evidence/webkit-suite-fd-aware-operating-cold.json) |
| Warm startup: three regimes, events and cap refinement | [PASS](evidence/chromium-suite-fd-aware-operating-warm.json) | [PASS](evidence/webkit-suite-fd-aware-operating-warm.json) |
| Load disturbance: three regimes, exact schedule and cap refinement | [PASS](evidence/chromium-suite-fd-aware-operating-load-step.json) | [PASS](evidence/webkit-suite-fd-aware-operating-load-step.json) |
| Feed disturbance: three regimes, exact schedule and cap refinement | [PASS](evidence/chromium-suite-fd-aware-operating-feed-step.json) | [PASS](evidence/webkit-suite-fd-aware-operating-feed-step.json) |
| Sealed heat reversal: three regimes, signed heat and cap refinement | [PASS](evidence/chromium-suite-fd-aware-operating-heat-reversal.json) | [PASS](evidence/webkit-suite-fd-aware-operating-heat-reversal.json) |
| Zero-exchange thermal300s and refrigerant equivalence | [PASS](evidence/chromium-suite-fd-aware-block-2.json) | [PASS](evidence/webkit-suite-fd-aware-block-2.json) |
| Sealed isothermal equilibrium | [PASS](evidence/chromium-suite-fd-aware-block-3.json) | [PASS](evidence/webkit-suite-fd-aware-block-3.json) |
| Fixed-step TR-BDF2 and backward-Euler order | [PASS](evidence/chromium-suite-fd-aware-block-4.json) | [PASS](evidence/webkit-suite-fd-aware-block-4.json) |
| Exact thermal energy-reference/state/timestep invariance | [PASS](evidence/chromium-suite-fd-aware-block-5.json) | [PASS](evidence/webkit-suite-fd-aware-block-5.json) |
| Pure trial, atomic mixed patch and exact scheduled boundaries | [PASS](evidence/chromium-suite-fd-aware-block-6.json) | [PASS](evidence/webkit-suite-fd-aware-block-6.json) |
| Second-half injected recovery failure and exact rollback | [PASS](evidence/chromium-suite-fd-aware-block-7.json) | [PASS](evidence/webkit-suite-fd-aware-block-7.json) |
| Forced solver/accuracy/domain stops, frozen stopped state | [PASS](evidence/chromium-suite-fd-aware-block-8.json) | [PASS](evidence/webkit-suite-fd-aware-block-8.json) |
| Forced failures after prior accepted state/ledger | [PASS](evidence/chromium-suite-fd-aware-block-9.json) | [PASS](evidence/webkit-suite-fd-aware-block-9.json) |
| Confirmed refrigerant-domain stop with exact rollback | [PASS](evidence/chromium-suite-fd-aware-block-10.json) | [PASS](evidence/webkit-suite-fd-aware-block-10.json) |
| Thermal-domain-clock refinement against independent reference | [PASS](evidence/chromium-suite-fd-aware-block-11.json) | [PASS](evidence/webkit-suite-fd-aware-block-11.json) |
| Unsupported refrigerant trial leaves state untouched | [PASS](evidence/chromium-suite-fd-aware-block-12.json) | [PASS](evidence/webkit-suite-fd-aware-block-12.json) |
| Original mesh, closure, domain and scope guards | [PASS](evidence/chromium-suite-fd-aware-block-13.json) | [PASS](evidence/webkit-suite-fd-aware-block-13.json) |

The operating groups each contain the original nominal/tight/reference regimes, same-EOS temporal and frozen direct-EOS assertions, and the additional accepted maxStep=.025 refinement. The source assertion marker block14 is excluded from scientific totals. **A passing selected group is not full four-configuration A2 qualification.**

| Domain suite runtime | Configuration | Status | Completed cases |
|---|---|---|---:|
| node | fd-aware | [PASS](evidence/a2-domain-pt-fd-aware.json) | 36 |
| node | exact-aware | [PASS](evidence/a2-domain-pt-exact-aware.json) | 36 |
| chromium | fd-aware | [PASS](evidence/chromium-domain-pt-fd-aware.json) | 36 |
| chromium | exact-aware | [PASS](evidence/chromium-domain-pt-exact-aware.json) | 36 |
| webkit | fd-aware | [PASS](evidence/webkit-domain-pt-fd-aware.json) | 36 |
| webkit | exact-aware | [PASS](evidence/webkit-domain-pt-exact-aware.json) | 36 |

The domain results use the explicitly separate, unambiguous PT mapping in adapter-pt.mjs. Original B1 PH/DU and all accepted equations/assertions are unchanged. The original33-pass/3-blocked interface runs are preserved separately. Phase-imposed/ambiguous PT has no claimed general mapping.

| Remaining/distinct accepted path | Status | Exact boundary |
|---|---|---|
| Original B1 adapter domain suite, FD/failure-aware | BLOCKED | 33 completed cases, then3 statePT interface cases blocked; raw failure retained. |
| Original B1 adapter domain suite, exact/failure-aware | BLOCKED | 33 completed cases, then3 statePT interface cases blocked; raw failure retained. |
| A2 rules, resets, history and phase controls | PASS | Unchanged accepted rules mode; FD-aware and exact-aware selections. |
| Original coupled-controls, Node22 FD-aware | PASS | All5 nominal fixture trace/error/event checks plus valid-first atomic patch rollback. |
| Original coupled-test full other3 configurations in both engines | NOT RUN | Baseline FD/original, exact/original and exact/failure-aware full operating/order/control matrices remain open. Domain/rules results above do not replace them. |
| Original coupled-controls other3 configurations | NOT RUN | No full controls-mode result for baseline/exact/exact-aware. |
| Original coupled-browser command/all4 selections | NOT RUN | The unmodified coupled-test assertions execute directly in browsers above; the separate original smoke-command matrix was not executed and is not counted. |
| Original coupled-domain-test legacy predecessor/bitwise path | NOT RUN | A2 approved domain assertion body is executed above; the distinct predecessor comparison remains unexecuted. |
| Fresh independent trajectory generator and fresh-reference suite/all4 selections | NOT RUN | Frozen direct-EOS comparisons run in completed cases; fresh NumPy2.5.3/SciPy1.16.2/CoolProp7.2 trajectory regeneration and suite reruns remain open. |
| A2 baseline ancestor byte-identical replay mode | NOT RUN | No ancestor four-path EOS-backed trajectory replay. |
| A2 compare full5fixtures x3regimes x4configurations | NOT RUN | The selected FD-aware complete core attempt is separate; no full four-path matrix claimed. |
| A2 observed mode and complete phase-diagnosis deterministic replays | NOT RUN | Detached histories and rules are scoped results; these distinct full original commands remain open. |
| A2 original four-path5-block Node performance qualification | NOT RUN | B2 matched30/44 browser/property and short coupled cost are reported separately. |
| Exploratory adaptive backward-Euler methods diagnostic | NOT RUN (outside accepted gate) | Retained historical limitation is not relabeled passed; established fixed-step BE order runs above. |
| B1 static16-case synthetic closures per browser/build | NOT RUN in B2 | B1 results/artifacts preserved; the new8-case canonical screen is a different experiment. |
| New moderate/long operating endurance, repeated transitions, hour-scale runs | NOT RUN | Gated off by the demonstrated valid-liquid canonical/coupled failure. |
| Physical Safari/iPad scientific and performance qualification | NOT RUN | No actual device available; Linux desktop WebKit is separate evidence. |
| Production property migration, Live Plant, hosting/deployment | NOT RUN / not authorized | No merge, application integration, hosting or Cloudflare changes. |
| Redundant Node-WASM complete coupled-test attempt | INCOMPLETE | Stopped cold block to prioritize browser campaign; no completed operating result counted. |
| Fresh same-table auxiliary full verification | INCOMPLETE / not a backend qualification claim | Fresh operating reference groups are retained individually; auxiliary table-only repeat scope is separate from B2 EOS qualification. |

Additional precision/canonical/model regression, separate from the accepted operating fixtures:

| Engine | Backend | Canonical compatible cases | Failed/error cases | Result |
|---|---|---:|---:|---|
| chromium | build30 | 1/8 | 7/8 | [FAIL](evidence/chromium-boundary-build30.json) |
| chromium | build44 | 1/8 | 7/8 | [FAIL](evidence/chromium-boundary-build44.json) |
| webkit | build30 | 1/8 | 7/8 | [FAIL](evidence/webkit-boundary-build30.json) |
| webkit | build44 | 1/8 | 7/8 | [FAIL](evidence/webkit-boundary-build44.json) |

Six physically valid liquid-side cases also reject a0.001s sealed, zero-exchange pure trial in the unchanged coupled source. State rollback is exact. One endpoint completes; the35bar case errors during initial recovery. Detailed primary diagnostics show Newton norm already below1e-11, followed by the original PH/DU stage compatibility rejection. The model therefore cannot be qualified throughout its supported input domain.

The native-root phase-aware derivative analysis identifies invalid Q-band outputs on physically single-phase inputs; no smooth homogeneous derivative is demanded across a true phase transition. Full exact inputs, outputs, phases, residuals and signed probes are in the raw236-state matrices and matching native audits.

The complete612-request original property/precision matrix was rerun for all4backends and both engines. Coarse native-value/success-error-pattern checks pass; those comparisons can share native flash defects. Independent DT and canonical tests remain decisive.

Conservation, direct-EOS/table differences, terminal quality/superheat and rollback history coverage are reported in independent-scientific-audit.json. Missing early initial/trial archives are explicit; no history is invented. Original forced solver/domain/accuracy stops are expected assertions, while the additional valid-domain model failure above is a real blocker.
