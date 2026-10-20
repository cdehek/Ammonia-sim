# Instrumentation equivalence

**PASS for all completed scientific pairs.** Same Node runtime, fixture, options and requested schedule reproduce original state/record and original attempt hashes exactly. Canonical original schedule also reproduces every saved B13 hash at 0, .0001, .0005, .001, .002, .005, .01 s for both fixtures. Original A2 control and B9C match exactly at the four accepted baseline checkpoints.

`verify.mjs` independently recomputes exact encodings, compares complete states/records (including M/U/V, eleven energies, ledgers, trace, rejections, growth controller, phase events, time and stop), and compares full original attempts including every derivative residual. JSON drops explicitly undefined iteration contexts, so those original undefined keys are restored before recomputing attempt hashes. No numerical tolerance is used for these comparisons.

Actual observed Jacobians are hashed before `solveLinear`. Independently, the verifier reconstructs each canonical matrix from original base-iteration residual and each selected derivative residual divided by its original signed step. All 235 cold and 867 warm matrices match. Alternate schedules' own matrices also match their paired canonical runs. Matrix verification therefore covers numerical results beyond merely matching final output.

The estimator capture hook copies original coarse/fine results and initial conserved coordinates after the unchanged error is calculated. Offline reconstruction retains original expression ordering and equals each aggregate bit exactly. Controller hooks copy installed proposals; all rejected proposals reconstruct and match the following trial exactly. Original events are neither augmented nor reordered. Additional counters/vectors live outside scientific objects.

## Transformations and boundaries

B14 starts from pinned `diagnostic-candidate-bundle.mjs`, which itself differs from canonical only by the separately documented B9C observations. Existing hooks count lexical sat/branch/inverse/MVU, public properties, section hits and boundary calls, and time evaluate/trial/stage/record. B14 adds unique-anchor hooks for each column, actual matrix hash, detached temporal vectors, prepared accepted half pieces and installed controllers. Module-export wrappers time Newton/residual and linear solve while returning unchanged objects. No optional exact thermal Jacobian mode is enabled.

`instrumentation-transformations.json` retains base and transformed SHA-256 plus every replacement; `observation-only.patch` shows the full diff from canonical. An identity replacement for `errorEstimate` is only a fail-closed anchor verification, not a scientific edit. All expression operands and returned values are unchanged. Hook errors are not silently accepted: measured normal runs hit no observation limits or errors.

A development attempt `observed-cold-r1` failed closed on a nonunique source anchor **before initialization or any solve**. Its empty trace and exit receipt are retained. The anchor was narrowed to the commit/applyBoundary context, then `observed-cold-r1-fixed` passed all gates. This is a harness-construction error, not a scientific refusal or an equivalent measurement. The cold first sample predates addition of an aggregate PH observer-index counter; that counter adds no source/science changes and timing ranges include this minor observer variation. All profiles share the same transformed scientific registry hash.

The original uninstrumented run still uses its original optional attempt observer and trace settings, matching B13; 'uninstrumented' means no B14 transformation/timers. This common original observation overhead is part of both runs. True no-observer production throughput is not measured.

## Initialization, timing and compaction

Separate no-advance initialization measurements identify 15 initial PH calls in each fixture. These explain initialization-inclusive totals of 5,043 / 17,431 versus advance totals 5,028 / 17,416. The raw hook label `initialization` means **unscoped property context**, also covering error/commit operations outside trial/record; it must not all be subtracted as construction cost. Only the separately measured initialization counts are subtracted. Other timing scopes retain initialization where applicable and are labeled accordingly.

Instrumentation increases advance wall time median by about 90% cold / 49% warm. Counts and exact traces remain valid; measured subscopes include instrumentation. Timing inequality is expected and disclosed, numerical inequality is rejected.

Receipts are compacted only after equivalence. Canonical content is referenced by name/time/hash; repeat full estimator/commit vectors are omitted after matching science and actual matrix hashes. First-sample vectors and all canonical schedule traces remain. `receipts.mjs` resolves references and final verification reruns comparisons. `receipt-compaction.json` records pre/post byte counts and hashes. No historical B13 evidence is rewritten.
