# Residual assembly and allocation

The original Newton workload decomposes exactly into:

| Fixture | Initial stage residuals | Derivative residuals | Line-search residuals | Total |
|---|---|---|---|---|
| cold | 102 | 4935 | 235 | 5272 |
| warm | 306 | 18207 | 867 | 19380 |

All line searches succeed at factor 1; none of this normal workload is wasted on failed nonlinear probes. Accuracy rejection still spends complete coarse/two-half stage work. The original stage closure builds states from exact PH keys, inventories from EOS density/enthalpy, thermal energies, endpoint rates, weighted integrated rates, then 21 scaled conservative residuals.

## Inclusive observed scopes

| Scope | Cold ms median [range] | Warm ms median [range] |
|---|---|---|
| residual | 209.67 [208.54, 210.70] | 1031.23 [1010.86, 1057.34] |
| evaluate | 51.66 [46.36, 52.43] | 139.86 [129.16, 140.07] |
| property.ph | 51.83 [50.75, 53.64] | 618.15 [615.06, 650.08] |
| property.stateMVU | 4.32 [4.05, 4.35] | 68.84 [68.28, 137.73] |
| linear | 12.37 [11.43, 13.00] | 18.81 [18.24, 18.94] |

`evaluate` includes hydraulic and thermal-rate assembly and any boundary property calls; it is not an isolated array-allocation timer. Residual includes evaluate, section property/cache work, inventory assembly, blend, original diagnostics and B14 timers/counters. Property scopes nest inside residual/Jacobian; stateMVU recovery also occurs outside residuals. These rows cannot be summed or subtracted into exclusive CPU buckets.

## Demonstrably repeated construction

Source inspection establishes at least six selected array-producing sites per residual: states map, cells map, energies map, fluid flatMap, thermal map, final concat. That is at least **31,632 cold / 116,280 warm source-level array constructions** before counting nested map/flatMap pair arrays, blend term arrays, rate arrays, returned objects or the Jacobian. Every residual also calls evaluate and constructs a fresh thermal-node index Map from the same topology, plus temporary key arrays. At least 5,272 / 19,380 such Map constructions occur in residuals. Section string keys are constructed five times per residual even on hits. Counts describe JS operations; JIT escape analysis can change actual heap allocations.

On thermal probes PH is unchanged, so original fluid inventory objects and hydraulic faces are recomputed from unchanged inputs. All 9,537 warm thermal probes have zero PH misses, yet still traverse the six hydraulic connections and fifteen thermal links. This proves repeated constitutive assembly under identical fluid inputs. It does not authorize skipping it or prove its exclusive runtime.

`trial` calls evaluate twice on identical initial states/energies, once for the outward thermal-domain check and once for the initial TR-BDF2 rate. The table engine also repeatedly brackets the same pressure inside one PH inversion. These are independent observed/source-supported opportunities, with different proof and ownership concerns. Existing stage/boundary caches are preserved exactly; none of these computations was reused by B14.

## Allocation/GC attribution limit

No allocation profiler or causal GC attribution was run. Process max RSS, heap snapshots at completion and CPU totals are resource bounds, not bytes per residual. Original trace recording and B14 copied vectors, exact encodings, hash arrays and PH repeat maps add their own allocation and can trigger GC. JIT worker CPU also contributes. **The amount of wall time consumed by original temporary arrays/objects, and whether original allocation/GC is a material bottleneck, remain unmeasured.** No percentage or speculative precision is assigned. Counts and exact equivalence justify a candidate investigation, not a claimed optimization speedup.
