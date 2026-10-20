# PH inversion cost

Original B13 workload reproduces exactly after subtracting initialization measured separately: cold **5,028 PH / 8,400 branch interpolations**; warm **17,416 PH / 703,306 branch interpolations**. All supported normal PH probes succeed. B14 did not change table inversion, stopping rules, classification, cache ownership or support.

## Necessary original algorithmic work

Warm 15,739 public PH calls return superheated vapor; 1,677 return liquid + vapor. Every vapor PH inversion executes a bound-check branch, exactly 38 bisection branch evaluations, then one final statePT branch: **40 branch interpolations per call**, 629,560 total and 598,082 bisection iterations. Remaining 73,746 warm branch calls arise from canonical stored M/U/V recovery rather than public PH. Cold has 210 vapor PH calls (predominantly its fixed outlet), producing all 8,400 branches; 4,818 mixture PH calls need none. These counts come from original functions plus contextual counters; no iteration termination was approximated.

`branch` independently brackets superheat/subcool offset and pressure, and interpolates h/s/log-density from original rows. In a vapor PH inversion all 40 branch calls have the **same exact p**, while trial offset varies. Each repeats `Math.log(p)` and pressure-axis binary search and allocates bracket results. This establishes repeated invariant pressure-location work, not repeated identical thermodynamic states. The 38 variable-offset evaluations remain necessary to the authorized algorithm. The count does not establish how much of PH CPU is pressure search versus interpolation/log/exp.

Warm derivative columns contain 8,606 PH calls: 8,040 vapor calls →321,600 branch operations and 566 mixture calls →0. Pressure/enthalpy perturbations change exact inputs and cannot be treated as approximate cache hits. Thermal columns make no PH calls. Per-column counts and per-phase/context totals are in `columns-warm.json`, `analysis.json:fixtures.warm.ph`; observer-index PH bins are provided only as interval context and include record/commit calls between attempt observers, not exclusive trial scopes.

## Current cache effectiveness

Warm section requests 96,900: 82,461 hits / 14,439 misses (85.10%). Cold 26,360: 22,373 / 3,987 (84.87%). Original stage-owned shared exact-pair map explains both thermal hits and uniform-section reuse. Warm stage boundary requests are 38,760, with 612 misses (two per 306 stages) and 38,148 hits. Including nonstage trial/record calls gives 39,384 requests / 1,236 misses. Cold equivalent totals are 10,760 requests / 420 misses / 10,340 hits. Trial/record calls intentionally retain the original uncached path. These figures demonstrate expected B9C cache benefit without adding cross-stage reuse.

An observational exact binary64 input map over the entire run finds 12,501 distinct warm PH pairs in 17,431 initialization-inclusive calls: 4,930 calls repeat a prior pair; cold 3,427 distinct / 5,043 calls, 1,616 repeats. This map returns no properties and changes no cache. Warm fixed inlet and outlet each appear 620 times including initialization; each is seen across 307 observer stage indices. Many identical accepted coordinates recur during error estimation, phase checking and commit/record generation. Cross-stage/input repetition is not automatically safely reusable: spec identity, property ownership, support failures and returned-object aliasing still require proof.

## Conditioning and near-saturation cost

Mixture PH is inexpensive direct interpolation; vapor PH has the full fixed 38-iteration cost even arbitrarily close to saturation. Across the accepted section-0 boundary, density and temperature slopes change as documented in `constitutive-probes.json`, but iteration count does not increase. Public PH costs decrease for section 0 once it becomes mixture. Thus expensive warm PH is primarily **many vapor-side fixed-loop calls**, not an observed inversion convergence failure or extra iteration surge exactly at the event.

Bisection interval width is 250/2^38 ≈9.09e-10 K. It remains unaltered; the original classification tolerance band and p/h coupling are also retained. Local zero-offset table continuity passes; complete global conditioning and interpolation-knot influence are not characterized. No new thermodynamic engine, approximate cache, quantization, extrapolation or CoolProp path is introduced.

Observed PH timing median is about 618 ms warm (615–650) and 51.8 ms cold (50.7–53.6), n=3 diagnostic processes, including instrumentation and initialization. Protected B13's lighter public PH timing (~475.6 ms warm) is not overwritten or equated to these measurements. Short timing and observer costs limit precise CPU attribution.

## Opportunity assessment

The clearest bounded opportunity is **reuse of the pressure interpolation bracket only within one vapor PH inversion**. It targets 40 repeated pressure-location operations per vapor call while preserving the 38 bisections, offset lookups, branch interpolation arithmetic and final property calculation. Savings are bounded above by affected PH time; their actual fraction is unmeasured. The next proposal requires exact science/failure equality before any speed comparison. No such optimization has been implemented here.
