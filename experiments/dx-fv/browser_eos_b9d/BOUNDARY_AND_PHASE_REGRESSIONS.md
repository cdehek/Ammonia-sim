# Bounded supported regressions

**PASS** in Chromium and desktop WebKit; same-engine control/candidate exact.

| Scenario | Both browsers |
|---|---|
| flow-reversal | EXACT |
| scheduled-boundary | EXACT |
| manual-boundary | EXACT |
| saturated-0 | EXACT |
| saturated-1 | EXACT |
| saturated-0.4 | EXACT |
| superheated-outlet | EXACT |
| thermal-200 | EXACT |
| thermal-400 | EXACT |
| numerical-stop | EXACT |
| inlet-phase-0 | EXACT |
| outlet-phase-0 | EXACT |
| inlet-phase-1 | EXACT |
| outlet-phase-1 | EXACT |
| inlet-phase-0.25 | EXACT |
| outlet-phase-0.25 | EXACT |
| inlet-phase-0.75 | EXACT |
| outlet-phase-0.75 | EXACT |
| superheated-inlet | EXACT |
| manual-inlet-only | EXACT |
| manual-outlet-only | EXACT |
| scheduled-two-boundaries | EXACT |
| strict-valid-boundary-0.3 | EXACT |
| strict-valid-boundary-35 | EXACT |

Original cold/warm nonzero-exchange fixtures retain .0001/.0004/.0005 requested intervals to .001 s and naturally reject one/three accuracy trials. Other cases remain bounded to .0002 s; scheduled patches occur at .0001 and .0002 s. Additional saturated liquid/vapor and x=.25/.75 inlet/outlet cases derive h from the original saturation interface; they are valid prescribed boundaries, not fabricated phase coordinates. Superheated inlet uses original statePT at Tsat+20 K. Original B9C also covers genuine x=.4 mixture and superheated outlet. All fourteen additional trajectories return without stop in both browsers, including strict valid .3/35-bar inlet boundaries.

Original reversal verifies negative inlet/outlet flows and actual reversed outlet donor h=1700 kJ/kg in energy transport. Manual inlet-only/outlet-only and sequential scheduled changes use model.update/original schedule, preserving boundary event times and state ownership. New stages see the changed boundary; no stage cache survives.

Strict PH tests retain .3±1e-12 / 35±1e-12 bar, endpoints, nonfinite/zero pressure, supported hf/hg and subcool/superheat edges and original refusals. Unsupported enthalpies and missing liquid rows refuse through the original applicable interfaces. Missing-row statePT is not falsely represented as a PH failure: original PH branchLimit avoids those rows. Valid update interfaces reject unsupported inputs before spec/state installation. These negative tests establish original refusal semantics, not new supported physical phases.

Genuine outward thermal 200/400 K fixtures retain original confirmed domain proof and exact no-commit physical/identity rollback. Numerical-stop fixtures deliberately use existing maxIterations=1/maxAttempts=20 only for fault tests, never cold/warm timing/qualification. They may retain earlier accepted substeps; per-rejection rollback is distinct from reverting an entire requested interval. Restart and repeated record generation compare exactly. Scope is local phase/boundary regression, not inventory-wide phase/topology or full A2 qualification.
