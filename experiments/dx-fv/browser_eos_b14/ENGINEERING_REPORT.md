# B14-A0 engineering report

**B14-A0 PHASE/JACOBIAN DIAGNOSTIC PASS**

Scientific equivalence PASS. Baseline `eddb2e7add904238162ead68ef9e2c1b8874f04d`; isolated branch `research/b14-phase-jacobian-diagnostics-20261019`. Gate 0/design was committed first as `12dae83`. The final delivery SHA is the tip containing this report, reported in the delivery response and available with `git rev-parse HEAD`; self-embedding a final commit hash is not possible. All work is confined to `experiments/dx-fv/browser_eos_b14/`.

## Main diagnosis

The warm section-0 transition is **superheated vapor → liquid + vapor (cooling)**. Its accepted bracket is [0.0053591276016748427, 0.0053820385212110817] s; 0.0053754278169825922 s is the unchanged interpolated event. The opposite direction assumed in the request is not supported by the pinned evidence. Quality is null outside the valid mixture domain and is never extended into vapor as a fraction.

Original warm startup rejections are led by U4. The five late rejections are led in order by U1, U0, U1, U0, U1, with max errors 34.2474, 54.4708, 3.81319, 3.52410 and 1.37651. M/P also contribute strongly. Cold is led by U0. All 31 original temporal terms reconstruct bit exactly; the aggregation is a maximum, not a 21-coordinate RMS. Warm thermal terms peak below .075 and never lead rejection.

High-confidence cause category: refrigerant temporal-prediction error during rapid inventory/pressure dynamics. Measured saturation-side slope changes and a subsequent face-1 flow reversal support a combined local constitutive/hydraulic mechanism with **moderate confidence in causal attribution**, not a quantified partition. The final rejected trial starts in mixture and spans the flow reversal. Extra outputs change rejection count while conserving state, confirming segmentation/controller sensitivity. No Newton refusal or failed normal property probe occurs. Neither 'phase label alone' nor 'bad scaling alone' is an established explanation.

## Reproduced science and workload

| Metric | Cold | Warm |
|---|---|---|
| Actual research horizon s | 0.01 | 0.01 |
| Accepted physical half-steps | 32 | 86 |
| Accuracy-rejected trials | 1 | 8 |
| TR-BDF2 stages | 102 | 306 |
| Jacobian builds | 235 | 867 |
| Residual evaluations | 5272 | 19380 |
| Derivative residuals | 4935 | 18207 |
| Public PH calls during advance | 5028 | 17416 |
| Max combined closure over all accepted halves kJ | 6.32489e-12 | 1.56176e-10 |

All original schedule states, conserved inventories, thermal energies, records, attempts, controller decisions, events/ledgers/stops and actual Jacobian hashes match canonical exactly. All seven checkpoints match saved B13; original A2 control matches the four qualified baseline checkpoints. Accepted scientific qualification remains **0.001 s**. No physical horizon >.01 s is explored.

## Column, residual and PH findings

Thermal columns make zero PH calls and all expected stage-cache hits; they still perform 9,537 warm residual evaluations. P/H derivative columns cause 8,606 warm PH calls and 321,600 vapor branch interpolations. Median aggregate column envelopes are 587.73 ms P/H versus 218.27 ms thermal (three heavily instrumented processes). Expected shared initial PH pairs explain the small per-column call-count asymmetry. No fallback/sign/shrink asymmetry appears.

Warm public PH has 15,739 vapor calls with 38 bisections and 40 branch interpolations each (629,560 branch operations); total warm branch count 703,306 also includes MVU recovery. Many pressure-location operations are identical within each call, while bisection offsets vary. Existing section cache hit rate is 85.10%; stage boundary cache misses exactly twice per stage. Thermal-column PH work has already been eliminated by accepted caching, so it is not the opportunity it might appear to be from coordinate count alone.

Residual inclusive median is ~1,031 ms warm, evaluate ~140 ms, PH ~618 ms, linear solve ~18.8 ms, with nested scopes and substantial measurement overhead. These are not additive CPU shares. At least 116,280 selected source-array constructions and 19,380 topology Map constructions occur in warm residual assembly; actual heap bytes/GC/exclusive allocation time are **unknown**. No claim that allocation is the bottleneck is made.

The proposed next experiment is exactly one: **single-inversion exact pressure-bracket reuse in vapor PH**, retaining 38 bisections and all thermodynamics/acceptance/failure semantics. Measured repeated work and a narrow owner make it a defensible first proof experiment. No optimization or speedup is implemented or claimed. Ranked alternatives and rejection gates are in `NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md`.

## Schedule, conservation and failure evidence

Added/fine output schedules produce 88/98 accepted physical halves and 7/5 rejections. At .01 s their max differences from original are .09275/.23924 of declared original tolerance scales, with all accepted-state conservation budgets satisfied. These are distinct numerical trajectories, not bit-identical schedules or convergence proof.

Global/section mass/U, signed hydraulics, donor-enthalpy transport, tube/fin/air storage, independent thermal-node closure, air load and combined energy pass original tolerances. Separate original A2/B9C/observed domain witness preserves committed .0001 s and exact rollback/refusal evidence. Deliberate external wall-budget termination retains the last independently proven accepted .0004911886098445242 s; it is neither a numerical refusal nor plant alarm.

## Performance and resources

Canonical advance wall median/range: cold 213.05 [205.87,239.85] ms; warm 1139.25 [1094.53,1158.26] ms. Detailed observer median: cold 404.63 ms (+89.9%), warm 1692.30 ms (+48.5%), n=3. Jacobian timing includes actual-matrix hashing; per-column/property scopes include accounting. Counts/exact traces are stronger evidence than original-cost attribution from these scopes. CPU, process wall, serialization and worker transport are distinct; no browser transport is measured.

Linux Node 24.19.0, 3 visible CPUs / quota 2, 8 GiB cgroup memory. Normal process budgets: 40 s wall/CPU, 512 MiB V8 old space, 64 MiB output, capped observation history, process-group kill and no core dump. All normal runs complete in under 8 s supervisor wall. No budget extension, unsupported normal case or conservation violation occurs. The unique-anchor construction failure is retained as a pre-solve harness error and excluded from scientific samples.

## Remaining uncertainty and protection

Causal shares of phase/hydraulic/interpolation/estimator effects, true converged error, exclusive pressure-bracket/array/GC CPU cost and future desktop browser performance remain unresolved. None blocks reporting these diagnostics, and none authorizes changing the model. Fixed artificial reservoirs and uncalibrated transfer remain; wet terminal state is not compressor safety evidence.

All 3613 historical files, A2 closure, B9C/B9D, B12 source/package, B13 evidence and original workstation are unchanged. All 39 protected remote head/tag identities and PR #3 identity pass before/after audit. Only this B14 branch is authorized for push; no merge, production/main change, Cloudflare deployment or public Worker testing occurs. Publication is verified separately against the final branch SHA. **Stop for engineering review.**
