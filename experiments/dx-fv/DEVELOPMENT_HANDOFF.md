# Ammonia Lab — experimental DX development handoff

Status: documentation transition after the completed spatial-validation milestone. **No thermal-model implementation is approved by this handoff.** Read the [thermal design proposal](WALL_AIR_THERMAL_DESIGN_PROPOSAL.md) before proposing the next isolated stage.

## Project objective and architecture

Ammonia Lab is a browser-based ammonia refrigeration simulator for learning, demonstration and eventual equipment-informed industrial simulation. The intended foundation must conserve refrigerant mass and energy, recover real-fluid states, expose wet suction and distinguish equipment trips from numerical/property failures. Future directions include DX, flooded, pumped-overfeed and custom systems; the experiment does not yet implement those complete systems.

The shipped application is a self-contained, generated `index.html`. Runtime physics uses canonical units; UI defaults are Fahrenheit and psig. `engine.js` and `properties.json` provide bounded real-fluid properties and the independent reference cycle. `dynamic-engine.js` provides the older quasi-steady refrigerant/dynamic-room model. `storage-engine.js`, `valve-engine.js` and inventory initialization implement the separate connected refrigerant circuit with receiver, evaporator core, outlet and condenser inventories. `capacity-controller.js` supplies managed manual/automatic compressor capacity control; the expansion valve has separate superheat PI control. Equipment profiles, live schematic, trends/history and training consume application records. `tools/build.py` embeds source/data into the standalone application and validation reports.

The existing connected DX model selects vapor from a lumped core into a separate outlet. That selection can conceal upstream liquid accumulation and lose its transfer path as the core fills. The experimental finite-volume component replaces that transport assumption only in isolated tests. **The existing Live Plant DX failure has not been fixed or replaced by this experiment.** Existing operational restore points are not proof of physical validity of that old model.

The experiment uses CommonJS modules under `experiments/dx-fv/`, with no application/UI imports. Arrays, geometry, connections and solver size derive from configurable `sectionCount`; qualified study fixtures permit only 3, 5 and 9. A 45-bin comparison grid is inventory accounting, not a 45-section simulation. Do not instantiate 17 or more sections without approval.

## Repository status and immutable milestones

Repository: `cdehek/Ammonia-sim`. Experimental branch: `experimental/dx-fv-stage-3`. The following refs were verified when preparing this handoff:

| Baseline | Commit | Status |
| --- | --- | --- |
| Production/main v0.5.0 | `0473d32f62db992fde0f581d116e1bd0c8e7d8ed` | Unchanged production branch |
| Reviewed v0.5.5 release candidate | `e86da1975dd177248a78d40c114bf76123c173ea` | Retained source baseline |
| PR #3 / preview trigger | `d4422425750a1d3c4e432cc103ac42ead40b7cc6` | Open, unmerged; empty trigger commit |
| Stage 3 three-section backward-Euler prototype | `f7b19adb67587d88195d53cee6081c8b014fb9ed` | Validated restore point |
| Adaptive TR-BDF2 temporal accuracy | `3e2cdbf1c8e1c9c42268a72bda5b0d05cf54f0f5` | Validated restore point |
| Completed three/five comparison | `7bf0c326414a7d8b7e51f553a273a0041fe1e827` | Validated restore point |
| Completed three/five/nine spatial validation | **`c105584311ca4a539c8410bf02ae0519b2bc8448`** | Latest validated scientific milestone; preserve unchanged |

The documentation commit is a descendant of `c105584`, not a rewrite of it. Its SHA is reported separately in the delivery message because a commit cannot contain its own SHA. [RESTORE_POINTS.md](RESTORE_POINTS.md) records historical stage boundaries. PR #3: https://github.com/cdehek/Ammonia-sim/pull/3 . Reviewed RC and preview trigger share tree `eda93677513ef420d11008e38255159fd3986578`.

GitHub Pages retains the approved application baseline. Cloudflare is configured with main as production and automatic non-production previews; do not confuse an experimental preview deployment with integration of the prototype. Re-read actual refs before resuming: this table is a snapshot, not a promise they will never move. No branch is merged by this handoff.

## Validated conservation and numerical foundation

- `conservation.cjs`: signed mass/enthalpy face fluxes, opposite contributions to neighbors, global and per-section accounting.
- `thermodynamics.cjs`: bounded PH evaluation and canonical recovery from mass, fixed volume and internal energy. Extensive state is M (kg), U (kJ), V (m³); `U = M*h - 100*p*V` for p in bar absolute and h in kJ/kg. Liquid/mixture/vapor transport uses bulk donor enthalpy, without ideal vapor selection.
- `hydraulics.cjs`: reversible horizontal pressure-driven homogeneous-mixture connections, declared boundary restrictions and half-cell boundary/full-cell internal lengths. For each face, `ΔP = a*ṁ + b*ṁ*abs(ṁ)`, with `a = 128*μ*L/(π*D^4*ρ)` and `b = (f*L/D+K)/(2*ρ*A²)`. The resistance formula uses SI pressure drop (Pa), converted to/from bar at the interface. Donor density follows flow direction. Pressure loss is not an extra thermal-energy sink.
- `implicit.cjs`: damped Newton, finite-difference Jacobian and dense pivoted solve. Backward Euler remains available as the historical default.
- `time-control.cjs` / `evaporator.cjs`: adaptive conservative TR-BDF2, gamma `2-sqrt(2)`, step doubling and error estimate divided by three. Accepted fine solutions are two half steps; no non-conservative extrapolated state is installed. Positive stage flux quadrature and canonical recovery preserve accounting. Phase crossings are bracketed.
- Public component contracts: `create`, `advance`, `update`, `record`, plus uncommitted diagnostic `trial`. Boundary edits do not consume time/change inventories. Rejection restores accepted states, clocks and ledgers; stops retain evidence and freeze advancement. `accuracy`, `solver` and `domain` failures are distinguished. A wet terminal is a diagnostic, not an equipment trip in an evaporator with no attached compressor.

Qualified cases cover properties, steady/transient references, reverse/shutoff/check flow, liquid-full transport, sealed phase changes, startup, load/feed changes, rollback and hour-long wet/dry operation. Ledger limits remain 1e-8 kg and 1e-6 kJ globally and per section. Nominal adaptive relative tolerance is 1e-6, max trial 0.5 s; tight/reference runs use 1e-7/1e-8 and 0.25/0.125 s caps with separately refined phase brackets. These are tested fixtures, not universal tolerances or calibrated equipment ratings.

## Spatial findings and approved baseline decision

All meshes preserve total volume 0.003 m³, diameter 0.020 m, derived length 9.5492966 m, viscosity 1e-5 Pa·s, Darcy f=0.02, inlet/outlet K=1000/2, reservoir conditions and total heat. Internal interfaces introduce no extra local loss. Uniform initial thermodynamic conditions give identical total initial M/U. Uniform and graded sources integrate to identical total prescribed heat on each mesh.

Representative 18 kW uniform steady results:

| Observable | 3 sections | 5 sections | 9 sections |
| --- | ---: | ---: | ---: |
| Total refrigerant mass (g) | 12.46751 | 14.37429 | 15.99838 |
| Liquid mass (g) | 4.33730 | 6.06999 | 7.57987 |
| Common-port enthalpy (kJ/kg) | 1703.07963 | 1702.82152 | 1702.65109 |
| Common-port temperature (°C) | 36.28586 | 36.17525 | 36.10222 |
| Common-port superheat (K) | 41.62432 | 41.51371 | 41.44068 |
| Whole-tube friction pressure drop (bar) | 0.02439615 | 0.02418753 | 0.02404963 |
| Cold-start terminal dry crossing (s) | 1.983952 | 1.798686 | 1.611079 |

Five-to-nine total-mass differences remain 8.54–11.30%; liquid-mass differences 15.48–24.87% across qualified wet/dry/graded steady fixtures. Consecutive total-inventory changes contract by factors 0.773–0.852; liquid changes by 0.782–0.871. This is sensitivity evidence, not asymptotic convergence. Cold/graded startup phase-time changes barely contract; the load-restoration crossing changes sign. Even the inlet-third inventory change grows while the whole-profile L1 difference decreases.

Same-mesh nine-section nominal/reference differences are much smaller: maximum 0.01438 kJ/kg enthalpy, 0.00605 K temperature and 76.7 microseconds terminal-phase timing. Spatial inventory/phase discrepancies cannot be attributed to these measured temporal errors. Terminal centers move with N; compare common-port traces/common physical inventory intervals, not cell-center pressures as if colocated. Reported event times are **terminal-cell saturation crossings**, not exactly localized common-port wet/dry events. The port trace recovers donor h at imposed outlet pressure; it is diagnostic, not another state or vapor selector.

**User-approved decision:** five sections is the provisional working baseline; nine is the higher-resolution comparison. Neither is proven converged. Three remains the historical baseline. No finer study is approved. See [NINE_SECTION_COMPARISON.md](NINE_SECTION_COMPARISON.md), [NINE_RESULTS.json](NINE_RESULTS.json), [SPATIAL_RESOLUTION.md](SPATIAL_RESOLUTION.md) and [TIME_ACCURACY.md](TIME_ACCURACY.md).

## Unresolved limits and warm-domain evidence

Warm startup at prescribed 12 kW reaches the existing 250 K-superheat boundary near 0.27258 s (five) and 0.25938 s (nine); three continues. Independent direct-EOS Radau integration reproduces these discrete-model excursions to approximately microseconds. Compare matched valid intervals only (e.g. through 0.2 s across all meshes); unsupported port recovery remains marked and invalid continuation excluded.

Zero prescribed heat supports all meshes for the tested 2 s; at 6 kW nine reaches the boundary near 0.525503 s. Initially Q/M is identical across meshes (~1468.3 kJ/(kg·s)); falling terminal inventory raises it to ~2870 near the stops. Total U can fall while specific u/T rises. Coarse upwind mixing transports the cold-feed influence earlier; finer resolution reveals the hot low-inventory pulse. Prescribed heat never diminishes or reverses when fluid exceeds an undeclared heat-source temperature. Missing wall storage and air-temperature feedback are structural omissions. Their individual contributions cannot be quantitatively separated by this unchanged-physics study.

Additional outstanding limits:

- Homogeneous equilibrium/no slip: no film, entrainment, dryout/front subcell model, parallel maldistribution or oil. Bulk wetness is not a proven carryover rate or dryout correlation.
- Pressure closure: illustrative constant viscosity/friction, horizontal low-Mach quasi-steady losses; no gravity, momentum storage, choking or validated two-phase multiplier. Conservation alone cannot qualify these closures.
- Properties: existing bounded table (~0.3–35 bar absolute, up to 250 K superheat and ~30 K subcooling), no extrapolation. Independent EOS agreement validates table/solver consistency, not measured equipment accuracy. Domain limits are neither solver failures nor equipment trips.
- Thermal source: externally imposed heat, no wall/air energy state. The proposed thermal model may change the warm excursion; it is not guaranteed to eliminate it or correct mixture/hydraulic assumptions.
- Performance: dense finite-difference Newton costs rise with state count. Hosted Chromium/WebKit nine/five startup median ratios were ~2.11/~2.07; a nine-section 0.1-s advance took up to 225/236 ms. Node peak RSS was ~105 versus ~88 MiB, including runtime/table/JIT, not just cells. Good throughput does not imply main-thread responsiveness. No physical iPad/full-circuit benchmark or worker integration is qualified.

## Validation references, commands and CI

Independent paths use direct CoolProp 7.2.0 / HEOS::Ammonia, NumPy 2.5.3 and SciPy 1.16.2: steady shooting, conserved-M/U Radau transients and independent Radau refinement. They do not call the JS solver/table, but share its EOS source and physical closures. They are numerical/thermodynamic references, not independent coil measurements. Root validation additionally compares Danfoss R717 saturation constants; NIST web tables were unavailable, so no NIST-table comparison is claimed. The property grid SHA256 is `b67ac977338f3b7b62d0bf3d590514083814e620fa922504d05e7510938ede6e`.

Source references: [CoolProp ammonia](https://coolprop.org/fluid_properties/fluids/Ammonia.html), [Danfoss constants](https://assets.danfoss.com/documents/latest/493262/AM187286420404en-000702.pdf), and root [README](../../README.md). Frozen experiment references are `reference.json`, `time-reference.json`, `spatial-reference.json` and `resolution-reference.json`; generators and reports explain sampling and tolerances. Raw trajectories/performance are workflow artifacts with finite retention; checked-in reports retain milestone summaries.

Run from a real repository checkout with Node 22+, Python 3.12 and Playwright 1.62.1:

```sh
npm ci
npx playwright install --with-deps chromium webkit
npm test
npm run test:browser
npm run test:webkit
python tools/build.py /tmp/ammonia-build
git diff --exit-code -- index.html validation.json integration-validation.json
node experiments/dx-fv/test.cjs /tmp/dx-fv-results.json
node experiments/dx-fv/time-test.cjs /tmp/dx-time-results.json
node experiments/dx-fv/spatial-test.cjs /tmp/dx-spatial-results.json
node experiments/dx-fv/resolution-test.cjs /tmp/dx-resolution.json
node experiments/dx-fv/warm-domain-test.cjs /tmp/dx-warm.json
node experiments/dx-fv/resolution-cost.cjs /tmp/dx-cost.json
node experiments/dx-fv/resolution-browser.cjs /tmp/dx-browser.json
```

Fresh references (use an isolated virtual environment):

```sh
python -m venv /tmp/dx-fv-reference
/tmp/dx-fv-reference/bin/pip install CoolProp==7.2.0 numpy==2.5.3 scipy==1.16.2
/tmp/dx-fv-reference/bin/python experiments/dx-fv/generate_reference.py /tmp/dx-reference-stage3.json
DX_FV_REFERENCE_PATH=/tmp/dx-reference-stage3.json node experiments/dx-fv/test.cjs /tmp/dx-fv-fresh.json
/tmp/dx-fv-reference/bin/python experiments/dx-fv/generate_time_reference.py /tmp/dx-reference-time.json
DX_FV_TIME_REFERENCE_PATH=/tmp/dx-reference-time.json node experiments/dx-fv/time-test.cjs /tmp/dx-time-fresh.json
/tmp/dx-fv-reference/bin/python experiments/dx-fv/generate_spatial_reference.py /tmp/dx-reference-spatial.json
DX_FV_SPATIAL_REFERENCE_PATH=/tmp/dx-reference-spatial.json node experiments/dx-fv/spatial-test.cjs /tmp/dx-spatial-fresh.json
/tmp/dx-fv-reference/bin/python experiments/dx-fv/generate_spatial_reference.py /tmp/dx-reference-resolution.json 3,5,9
node experiments/dx-fv/resolution-reference-check.cjs /tmp/dx-resolution.json /tmp/dx-warm.json /tmp/dx-reference-resolution.json /tmp/dx-reference-check.json
```

The resolution replay checks actual saved steady/heat-diagnostic states against fresh references and qualifies saved startup error bounds using fresh/frozen reference agreement; this is documented evidence replay, not a claim to rerun every expensive trajectory against a different file path.

`.github/workflows/verify.yml` runs application verification on main pushes/PRs/manual dispatch. `.github/workflows/dx-fv-experiment.yml` runs on experimental-branch pushes/manual dispatch, with four jobs: `prototype` (13 legacy numerical suites, historical prototype/time references and build consistency), `browser-performance` (legacy Chromium/WebKit and isolated benchmarks), `spatial-resolution` (historical 3/5 frozen/fresh), and `nine-section-resolution` (3/5/9 temporal/spatial/hour tests, cost, domain diagnostics and fresh reference replay). Failure artifacts retain diagnostics.

Validated c105584 run: https://github.com/cdehek/Ammonia-sim/actions/runs/38009179503 — all four jobs passed. Earlier restore CI links are in [RESTORE_POINTS.md](RESTORE_POINTS.md). This is milestone verification, not a claim that future thermal physics has passed tests.

## Safe resumption in a fresh Codex conversation

1. Read this file, the thermal proposal, restore points, numerical/spatial reports and any current `AGENTS.md`. Inspect repository identity, clean working tree, remote refs and user instructions. A downloaded file mirror is not necessarily a git checkout; do not operate on an unrelated workspace `.git`.
2. Fetch the repository without changing production. Inspect `experimental/dx-fv-stage-3`; confirm c105584 remains an ancestor and review any commits after this documentation transition. Use a separate checkout/worktree if needed. Never reset or force-push a live branch to a restore point.
3. For restore inspection, use a detached disposable checkout at the full SHA. Preserve the scientific milestone and old prescribed-heat fixtures/references unchanged. Record the new starting SHA before approved development.
4. Restate scope and approval status. The next decision is **approval of the minimal isolated wall/air thermal prototype and its declared parameter/air-boundary contracts**, after reviewing the proposal. Documentation approval does not authorize implementation. Ask for that decision before source changes.
5. Once explicitly authorized, follow the approved stages, five-section baseline/nine-section comparisons and independent temporal qualification. Preserve all prior regressions, paired ledgers, canonical recovery and atomic rollback. Report unsupported intervals honestly and benchmark computational cost.
6. Do not integrate into Live Plant, change main/PR #3, UI or equipment profiles, calibrate Default, invent protections, expand property limits, clamp inventory, force superheat, add vapor-selection transport, run finer meshes or merge without separate explicit approval. Later controller/profile/schematic/training migration needs its own integration plan and acceptance.

For a new conversation, provide this file plus the experimental branch name and documentation commit SHA, and specify whether the next design stage is approved. There is no unfinished thermal implementation to resume.
