"""Render exact per-identity table; scientific fields come from saved evidence."""
import json
from pathlib import Path
B=Path(__file__).resolve().parent;d=json.loads((B/'evidence/dp-identities-11.json').read_text())
s='''# Supplemental DP disposition

**DP physical qualification remains FAIL / NOT QUALIFIED.** Every invalid raw equilibrium quality is refused. The saved 44 observations reduce to **11 exact path/input identities**, each observed in Chromium/WebKit × control/candidate. Fresh/reused observations corroborate each result; they are not extra bugs. There are eight inherited native full-VLE identities and three default browser rounding identities. This split is verified against actual rows, not inferred from a label.

The grouping key is `(fullVLE, density bits, pressure bits)`. Fixture identity is retained and checked within each group. Different paths at identical numeric inputs remain distinct execution identities. All pressures are Pa, density kg/m³. Raw outcomes are complete states, not exceptions.

| Issue | Historical fixture | Path | rho binary64 | p binary64 | Native raw Q | Chromium raw Q | Desktop WebKit raw Q |
|---|---|---|---|---|---:|---:|---:|
'''
for r in d['rows']:
 n=r['observations'][0]['nativeRaw']['values']['Q'];qs={e:next(x['rawReturn']['values']['Q'] for x in r['observations'] if x['engine']==e) for e in ['chromium','webkit']}
 s+=f'| {r["issueId"]} | `{r["fixtureId"]}` | {"full VLE" if r["fullVLE"] else "default"} | `{r["inputBits"][0]}` | `{r["inputBits"][1]}` | {n!r} | {qs["chromium"]!r} | {qs["webkit"]!r} |\n'
s+='''
## Per-identity interpretation

For **every row** above:

- Actual numerical phase enum is **6** (`iphase_twophase`) in native and both browsers. The browser raw Q is outside [0,1]. All property calls return; the later strict scientific quality audit refuses each browser state. Do not confuse caller return with scientific acceptance.
- Control/candidate raw states are exact within each browser; fresh/reused states are exact. Native fresh/reused states and preserved historical shared-density A1 rows match. No Gate A regression or repair of DP is inferred.
- Exact-input independent physical phase qualification is **NOT ESTABLISHED**. An hf/hg fixture and numerical coexistence label are same-EOS provenance, not proof that the exact binary64 rho,p describes a physical equilibrium mixture. A negative or greater-than-one equilibrium fraction remains inadmissible, however small.
- No accepted adapter exposes a DP method. The original adapter and C1 wrapper expose PH, SAT and stateMVU only; stateMVU requests DU. The full accepted dependency closure and bounded unchanged runtime trace establish no CoolProp DP request by A2.
- Current A2 cannot consume these raw DP results through its implemented property interface. Its table engine does evaluate an internal density-at-pressure function while inverting DU; that independent table code has no CoolProp/loader call and does not inherit these raw DP outputs.
- The B7 raw loader exposes DP experimentally and checks finite output, so it can return these invalid states to explicit diagnostic callers. It has no global quality admissibility gate. The historical convert function maps an out-of-range Q to x=null; applying that convention to a future DP result would not establish a homogeneous physical phase. No such DP conversion path is implemented today.
- Current severity is **P3 diagnostic-only**, with high confidence in interface exclusion and observed invalidity. Scientific status remains **REFUSED**. For a future DP consumer these are configuration/feature blockers, requiring an independent admissibility and reference gate before use.

Eight full-VLE rows reproduce native Q outside [0,1] exactly, including original shared-density control/A1 evidence. Three default rows have native Q exactly 0 or 1 and browser Q outside the interval. An endpoint-valued native Q does not by itself prove independent physical phase/reference qualification either. Chromium and desktop WebKit agree on the raw qualities listed here; this is not physical-device Safari qualification.

## Numerical and physical consequences

There is no current A2 initialization, Jacobian, line-search, thermal/hydraulic, conservation, event or wet-suction consequence from these **DP observations**, because no implemented caller requests them. This does not prove all PH/DU implementations flawless; shared endpoint PH phase-label differences are a separate retained P2 item.

A future direct consumer could extrapolate an equilibrium mixture with negative component mass, or relabel it homogeneous via x=null. That could corrupt density/enthalpy/temperature interpretation and wet-suction reporting, then alter heat transfer and signed donor fluxes. These are conditional interface risks, not observed baseline simulator contamination. Even if p/h/T differences meet canonical numerical budgets, invalid equilibrium Q cannot be accepted.

No repair is proposed without a prioritized DP dependency. Smallest reopening condition: identify a real supported caller and its operating inputs; then define a bounded DP physical-admissibility/reference milestone. Do not spend a full EOS repair campaign on the current raw diagnostics alone.

## Full provenance and reproduction

[dp-observations-44.json](evidence/dp-observations-44.json) retains the full original B7 quality disposition without dropping any observation. [dp-identities-11.json](evidence/dp-identities-11.json) contains all requested bits, original historical shared-density rows and indices, four observations per identity, native/raw browser state vectors and bits, phase/quality/reference/caller distinctions, adapter eligibility, A2 reachability, consequence and disposition. [source-evidence-sha256.json](evidence/source-evidence-sha256.json) binds all original result files.

`timeout 30s python experiments/dx-fv/browser_eos_b8/extract-evidence.py` verifies 44→11, exact binary64 inputs, control/candidate identity, fresh/reused parity, original native correspondence, eight full-VLE invalid-native versus three default native endpoints, and strict physical refusal. It performs no EOS work. The scientific B7 `quality-disposition.py` and original matrix are unchanged.
'''
(B/'DP_FAILURE_DISPOSITION.md').write_text(s)
