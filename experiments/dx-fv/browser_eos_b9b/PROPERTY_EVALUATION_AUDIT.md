# Accepted table-property and cache audit

The engine is root `engine.js` / `properties.json`, Git-verified against A2.
It never invokes B7, CoolProp, WASM or raw CoolProp DP. B9A's saved
`scientific-audit.json` and original baseline receipts agree with the reproduced
public counts below in both engines. These cover the full bounded workload,
including initialization and seven records; they are not one Newton iteration.

| Operation | Cold | Warm |
|---|---|---|
| Section PH requests | 14570 | 38550 |
| Existing stage-cache hits | 12398 | 32871 |
| Existing stage-cache misses / real section PH | 2172 | 5679 |
| All real public engine PH | 8476 | 22072 |
| Public SAT | 9261 | 23752 |
| All lexical SAT including public | 27548 | 69776 |
| Nested SAT beyond public | 18287 | 46024 |
| Independent MVU / DU | 445 | 940 |
| Single-phase PH inverse | 2976 | 14234 |
| Mixture PH inverse | 5500 | 7838 |
| Branch interpolation calls | 119040 | 601320 |

`thermo.ph` checks finite p/h and .3–35 bar support, then calls `engine.ph` and
public `engine.sat`. It adds wet/superheat indications to a new object.
`engine.ph` delegates to lexical `inverse(p,h,'h')`. That routine evaluates
saturation and tests the original phase interval. A mixture uses statePX and
direct mixture formulas; a single-phase state uses a bounded 38-iteration
temperature-offset bisection. Each single-phase PH requires 40 branch calls:
edge check, 38 bisections, final statePT interpolation. No derivative is requested
from an EOS; the outer nonlinear solver supplies signed FD derivatives.

`sat` brackets log pressure and interpolates table saturation fields, including
log-density interpolation. `branch` brackets offset and pressure, makes two
within-pressure rows and a final interpolated row via mixRow. That means repeated
log/exp arithmetic, small temporary arrays, bracket pairs and result objects;
“table-backed” does not mean a PH calculation is a single direct array lookup.
Support checks retain the exact original epsilon, axes and missing-liquid-row
behavior. This audit changes none of them.

`inverse` computes sat(p), then statePX or statePT computes it again at the SAME
p. Those lexical calls do not go through the public proxy. Public SAT timing
therefore excludes them, while PH timing includes them. Internal counters prove
the duplication; they do not independently time its private CPU cost.

`stateMVU` validates stored mass/volume/energy, computes rho=M/V and u=U/M,
and calls lexical stateDU. stateDU evaluates atDensity at the supplied pressure
guess, normally with up to ten bounded pressure iterations and a scan/48-step
bracket fallback. Here atDensity count equals DU count: every recovery finishes
on its first pressure evaluation. AtDensity uses direct mixture relations or
a 32-iteration density/temperature inverse. Thus the cold branch count is
2,976×40=119,040; warm is 14,234×40+940×34=601,320. Recovery is independent
scientific validation, not a substitute for a failed PH result.

SAT reconciliation is exact: cold 9,261 public + 2×8,476 PH lexical + 3×445 MVU
lexical = 27,548. Warm 23,752 + 2×22,072 + 2×940 = 69,776. Cold's extra MVU
SAT is the mixture liquid-volume-fraction calculation. Public thermo.recover
also requests SAT and constructs wet/superheat fields.

## Existing PH Map

One Map is created inside each solveStage, before Newton. Its key is precisely
`${x[2*i]}:${x[2*i+1]}`, using JavaScript Number string conversion without
rounding. Section index is deliberately absent: identical PH coordinates in
different cells share a property state in that stage. Positive pressure and
nonzero fixture enthalpies avoid the +0/−0 string identity exception here; this
is not a proof for all arbitrary inputs.

Each of five section requests checks has/set/get. A successful miss stores the
genuine thermo.ph result. A thrown evaluation is not installed. Entries survive
Newton iterations and rejected line-search candidates within that stage; there
is no eviction. The Map is discarded after stage return/failure, and never
shared with the next TR-BDF2 stage, another trial, record or model session.
No numerical state or input coordinate is changed by the cache.

The measured hit rates are 85.09% cold and 85.27% warm. Thermal probes alone
produce 7,150 / 18,975 section cache hits: all five PH coordinates remain fixed.
Pressure/enthalpy probes reuse other unchanged cells; original guesses and
repeated exact coordinates can also hit. This reuse already exists in B9/B9A:
the public 8,476 / 22,072 PH counts are AFTER the stage cache.

Across the whole workload, logical PH state requests including bypassed section
hits are 20,874 / 54,943; genuine engine PH calls are 8,476 / 22,072. The section
request vector is separately 14,570 / 38,550, of which only 2,172 / 5,679 miss.
Do not compare one of those denominators with a different scope.

The two imposed boundary PH states bypass this Map and are reevaluated by every
rate evaluation. Residuals alone request them 5,828 / 15,420 times. Extra rate
evaluations at trial start and during recording add more. This exact fixed-input
repetition is a potential future opportunity, subject to deterministic-table,
validation, mutability and failure-semantic proof. No new cache is installed.

`propertyByContext` and per-stage/trial deltas retain the complete split among
initialization, section residual misses, boundary rates, coordinates, canonical
recovery, commit/event checking and recording. Property-sequence hashes prove
that the observational copy preserves every original public call's order,
arguments, return bits and thrown diagnostic meaning. Cache counters and nested
calls are read-only additions. Counts alone establish no CPU percentage.
