# Timing ownership and overlap ledger

| Boundary | Contains / excludes | Valid interpretation |
|---|---|---|
| Original advance | Trials, stages, original checks/diagnostics, commits, mandatory final record | Authoritative computation elapsed control |
| Trial | Coordinates, canonical checks, initial rates and two stages | Inclusive; overlaps stages |
| Stage | Newton plus post-solve recovery/checks | Inclusive; overlaps Newton/recovery |
| Newton | Initial/FD/line-search residuals, matrix solve/assembly, correction, diagnostics | Inclusive; overlaps residual/linear |
| Residual | Stage cache, PH misses, rates, inventories, blend, normalization | Inclusive; overlaps rates/PH/blend |
| Rates | Boundary PH, temperature checks, flow/heat/thermal assembly | Inclusive; overlaps PH |
| Thermo PH | Engine PH, public saturation, guard and derived indications | Inclusive; overlaps both properties |
| Engine PH | Lexical inverse, saturation, branch interpolation | Public timer includes internal calls |
| Engine MVU | DU/atDensity inverse and any lexical SAT | Independent canonical operation; internal SAT overlaps |
| Public SAT | Exported invocations only | Does not include lexical internal SAT |
| Linear timer | Original dense solve and read-only matrix diagnostics | Containing diagnostic interval, not pure elimination |
| Wrapper exclusive remainder | Parent minus immediate measured child intervals | Instrumented remainder, not intrinsic CPU |
| Detached state/attempt copy | After original advance, before evidence hash/transport | Separate actual boundary, not part of physical advance |
| Snapshot record | Extra original endpoint record | Recovery/flux/validation, not just copying |
| Worker RTT | Imports, model work, evidence copies/hashes, dispatch/transport | Research delivery, not solver-only or compilation-only |
| Sample leaf/source | Mutually exclusive included stack samples | Sparse source attribution; excludes unrooted GC/outside-advance work |

No nested interval sums or percentage breakdown across overlapping boundaries
are valid. Timing calls and bookkeeping themselves consume time. Coarse clocks
can yield zero intervals and imprecise remainders. The raw exclusive map is kept
for audit but not advertised as a calibrated intrinsic cost model. No microbench
subtraction or massaged 100% partition is used.

Private thermal/fluid subexpressions, branch-check/normalization arithmetic,
diagnostic generation/allocation and GC are not each independently attributable.
Raw CPU source lines are observation positions, subject to JIT/inlining; they
are not proof of per-expression exclusive cost. No WebKit sampled CPU breakdown
or independently measured condition number is available. No long-run memory,
retention, sustained throughput or physical-device result is established.
