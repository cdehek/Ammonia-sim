# Stage 2A-R — targeted source-review correction and diagnostics

Preserved candidate: `aa9514b0338b6021d9afc4b9f47f88ebdde765da`. This remains an unchanged ancestor. The corrective restore SHA and exact hosted CI run are reported in delivery; a commit cannot contain its own SHA. Stage 2A remains pending user milestone acceptance. No Stage 2B work is authorized here.

## Scope and exact-boundary classification

Only the isolated coupled model, optional diagnostic recording, new tests/probes and experimental documentation/evidence change. Historical property/transport/hydraulic/implicit modules, standalone Stage 1, all frozen references and application/workflow files remain unchanged. No tolerance, perturbation formula, line-search rule, iteration budget, integration method, heat-transfer closure, protected boundary/profile or production behavior is changed.

The source review found that `domainEvidence()` discarded even conclusive exact-boundary evidence when the exhausted step exceeded 1e-6 s. The fix rechecks the identified node's **accepted-state** temperature and signed derivative before that predictor threshold. Only an exact support limit with a truly outward derivative qualifies. General failed property/nonlinear probes still require corroboration; probe labels alone cannot establish an exit.

The original retry sequence remains unchanged. This is a classification correction, not an early-stop/retry optimization. No candidate temperature is clipped and no predictor/property extension becomes an accepted state.

Node 22 before/after tests use both 200/400 K boundaries and `minStep=1e-9, 1e-5, 0.5 s`. With outward air loading, the candidate labels the larger-floor exits `solver`; corrected code labels all three `domain`. Inward and zero rates remain supported and match candidate states/ledgers. Upper tube-boundary heating through signed 0.60 kW/K refrigerant exchange is also checked; that extreme supported initial state is a domain stress fixture, not an adopted operating case.

`COUPLED_R_DOMAIN_RESULTS.json` retains **27 boundary cases and 10 solver/probe checks**, including real Newton-budget exhaustion, unsupported probes, deliberately misleading boundary-proof metadata, and failures after nonempty accepted clock/ledger/boundary history. Accepted cells, thermal energies, clocks, ledgers, events, scheduled boundary records/index and accepted counts remain unchanged by rejected attempts. Stopped advancement and edits remain frozen. Diagnostic rejection/work counters are permitted to accumulate and are not physical inventories.

## Nonlinear diagnostics and behavior preservation

An optional third argument to `createCoupledModel(engine, options, observeAttempt)` receives detached per-trial diagnostic data. It records residual vectors, physical residual scales, dominant components, PH/phase states, actual derivative perturbations/branch/probe outcomes, line-search factors/results and iteration exhaustion. It is absent by default. Observers are diagnostic consumers; callback errors propagate outside the nonlinear solver. They must not edit model state or numerical settings.

`coupled-diagnostics.cjs` loads the exact candidate sources from git without a checkout and compares candidate, corrected and observed runs under Node 22.23.3. Cold/warm starts use the approved temperatures and 1 kW air load, through 120 s. Sealed reversal uses the approved fixture through 60 s at all three existing qualification regimes. **All physical inventories, clocks, ledgers, events, accepted/rejected timestep traces and residual-evaluation counts hash identically across those three implementations.** Observation does not tune numerical decisions.

| Reversal regime | Max trial s | Accepted trials | Rejected trials | Newton exhaustion | Temporal rejection |
| --- | ---: | ---: | ---: | ---: | ---: |
| Nominal rtol 1e-6 | 0.5 | 962 | 922 | 921 | 1 |
| Tight rtol 1e-7 | 0.25 | 963 | 907 | 906 | 1 |
| Reference rtol 1e-8 | 0.125 | 976 | 727 | 725 | 2 |

These regimes change both tolerance and step cap, following existing qualification settings; they are not an isolated tolerance-only experiment. Cold/warm nominal runs have 321/444 accepted trials and 5/33 rejections, **zero failed Newton solves**; their rejections are temporal/event driven.

Every one of the **2,552 failed Newton solves** is in superheated vapor, and every failure reaches the unchanged 30-iteration budget. There is no derivative branch rejection or failed derivative probe in these runs. All failures are dominated by tube-energy rows; failing row indices differ in this symmetric fixture and do not identify physical hot spots.

Nominal failed thermal closures range from **1.00017e-12 to 4.81654e-12 K**. Refrigerant residual norms range from **2.18647e-13 to 3.20052e-12**, already below the 1e-11 nonlinear criterion. Nominal line searches record 42,073 accepted reductions and 298,993 non-reducing candidates, with no final line-search exhaustion. Strict residual decreases nevertheless stall close to the closure budget until the iteration cap. Failures extend from approximately 0.369 to 59.819 s, rather than being confined to a phase crossing. Failed proposed steps range 0.04566–0.31350 s.

Converged solves do satisfy the unchanged **1e-12 K thermal closure**. However, that budget is not consistently attained at attempted larger steps; adaptive retries recover accepted solutions. No evidence establishes that it is mathematically impossible, and no relaxation or correction factor is introduced.

The preserved PH inverse uses 38 temperature bisections. Its 250 K vapor search has resolution width **9.094947e-10 K**. A separate exact piecewise-linear inversion of the same table enthalpy measures error up to **4.548397e-10 K**, with small enthalpy perturbations yielding unchanged returned temperature. This separates inversion quantization from EOS/table interpolation error. The observed gap relative to 1e-12 K closure is a plausible cost contributor, not proof of sole causation.

Canonical M/U/V recovery is separate: density-offset inversion uses 32 bisections (maximum vapor width 5.820766e-8 K), with a 1e-7 kJ/kg specific-energy stopping tolerance and pressure search. Sampled PH-to-canonical recovery temperature discrepancies stay below **2.864908e-8 K** and satisfy unchanged stage consistency limits. The diagnosed failures occur inside Newton before that acceptance recovery; its coarser inversion must not be confused with the PH residual-path resolution.

Representative sequential shared-worker reversal wall times in seconds (candidate/corrected/observed, including record processing) are nominal **59.02/65.14/71.56**, tight **47.58/56.31/63.78**, reference **42.10/41.80/49.25**. These are not controlled hardware benchmarks and do not supersede the earlier 31.2 s measurement. Observed timing includes archive serialization/IO; numerical work/state counts are exactly equal, and no speed improvement is claimed.

`COUPLED_R_DIAGNOSTICS.json` contains each failed solve's final physical/scaled residuals, dominant component and operating state. `COUPLED_R_FAILED_NEWTON.jsonl.gz` retains complete iteration/derivative/line-search histories as concatenated gzip JSONL members. An independent standard-library Python audit verifies all 2,552 histories, **1,669,542 derivative probes** and **902,052 line-search probes** in failed histories, including perturbation arithmetic, residual norms, reduction decisions and iteration exhaustion. Archive SHA-256: `c1ca2203fcf6026d2da70d5331c1bb5ac49ffe74a29997ce2cf8bdbcfe3a30fc`.

Proposed remedies **require separate approval**: investigate exact linear thermal-block derivatives or algebraic elimination while retaining joint implicit stages; evaluate piecewise table derivatives/precision compatibility; and test failure-aware step growth to avoid repeatedly proposing intervals above a demonstrated nonlinear convergence ceiling. Preserve historical properties, nonlinear/conservation/reference budgets and rollback. No such remedy is implemented here.

## Direct EOS versus runtime interpolation support

The independent reference's nominal envelope (0.3–35 bar, up to 250 K superheat/30 K subcooling) is not the complete runtime availability boundary. The preserved table generator omits below-200-K liquid rows; interpolation requires both pressure-bracket rows, and the engine applies its existing missing-row margin. Direct-EOS physical support, table PH availability, table-inventory recoverability and direct-EOS-inventory recoverability are distinct.

CoolProp 7.2.0 confirms the reported **0.32 bar / 200.05 K** physical state, with h=19.69252839 kJ/kg, rho=728.6204391 kg/m³ and saturation temperature=219.14335554 K. Nominal reference margins remain positive. Actual table pressure brackets are **0.3183890254–0.3247658591 bar**, with maximum liquid subcooling **18.9999999 K**. Both runtime PH and direct-EOS M/U/V recovery reject this example as outside their bounded table. This does not invalidate the five qualified operating reference trajectories.

`coupled-runtime-support.cjs` is a diagnostic batch probe of the unchanged runtime. It separately reports PH support, table-inventory recovery and stage-consistency differences, and EOS-inventory recovery. `investigate_coupled_domain.py` supplies direct-EOS points and separately inspects the actual missing-row mask; it does not replace the independent RHS or modify frozen references. `COUPLED_R_REFERENCE_DOMAIN.json` records the example and five additional points.

Proposed future qualification: retain direct-EOS integration/refinement; run a separate runtime-availability check on samples and safeguarded dense-output/boundary brackets. Sparse samples alone cannot certify an entire interval. A matching continuous boundary checker should independently reproduce pressure brackets and the declared table-generation missing-liquid mask, then cross-check against the authoritative runtime probe. Numerical inversion failure must remain distinct from proven physical exit. Extending tables or replacing existing frozen comparisons requires separate approval; neither occurs here.

## Qualification and reproduction

`COUPLED_R_QUALIFICATION.json` records final coupled frozen/fresh, independent accounting, domain/control/diagnostic/property and Chromium/WebKit results, dependency versions, preservation hashes and established hosted coverage. Existing acceptance limits and test/reference files are unchanged. New coupled checks remain **absent from hosted workflow invocation**; workflow changes are outside this authorization. The unchanged hosted workflow is run on the delivery SHA for all established application/DX/Stage 1/spatial checks and archives its normal artifacts.

Use Node 22.23.3, Python 3.12, CoolProp 7.2.0, NumPy 2.5.3, SciPy 1.16.2 and existing Playwright 1.62.1:

Before/after probes require the preserved candidate's git object to be available. A shallow clone may need that object fetched explicitly; the default depth-one hosted checkout is not sufficient for these historical comparisons. No workflow change is made here.

```sh
node experiments/dx-fv/coupled-domain-test.cjs /tmp/coupled-r-domain.json
node experiments/dx-fv/coupled-diagnostics.cjs /tmp/coupled-r-diagnostics.json /tmp/coupled-r-failed.jsonl.gz
python experiments/dx-fv/audit_coupled_diagnostics.py /tmp/coupled-r-diagnostics.json /tmp/coupled-r-failed.jsonl.gz /tmp/coupled-r-diagnostic-audit.json
node experiments/dx-fv/coupled-property-diagnostics.cjs /tmp/coupled-r-diagnostics.json /tmp/coupled-r-property.json
python experiments/dx-fv/investigate_coupled_domain.py /path/to/node22 /tmp/coupled-r-reference-domain.json
node experiments/dx-fv/coupled-test.cjs /tmp/coupled-r-results.json
python experiments/dx-fv/generate_coupled_reference.py /tmp/coupled-r-fresh-reference.json
python experiments/dx-fv/generate_coupled_domain_reference.py /tmp/coupled-r-fresh-domain-reference.json
DX_COUPLED_REFERENCE_PATH=/tmp/coupled-r-fresh-reference.json node experiments/dx-fv/coupled-test.cjs /tmp/coupled-r-fresh-results.json
python experiments/dx-fv/audit_coupled_results.py /tmp/coupled-r-results.json /tmp/coupled-r-accounting.json
node experiments/dx-fv/coupled-controls.cjs /tmp/coupled-r-controls.json
node experiments/dx-fv/coupled-browser.cjs /tmp/coupled-r-browser.json
```

Local browser libraries are installed only under `/tmp`; WebKit's temporary bundle receives links to missing system libraries because its wrapper replaces `LD_LIBRARY_PATH`. `PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=1` skips only the system-cache preflight for those relocated libraries. Both real engines and all scientific assertions execute. Hosted browsers use the unchanged normal dependency installation. Sandbox child-process/browser-launch setup failures were environmental; no numerical assertions were suppressed.

Remaining limitations: uncalibrated geometry/conductances and fixed-mass finite air; provisional five-section mesh; costly superheated reversal; incomplete low-pressure reference-domain correspondence; and no new hydraulic-reversal/grazing-event/extended-operation qualification. No nine-section coupling, correlation, circuit/control/UI/production change, integration decision or Stage 2B implementation is included. Delivery stops for user review.
