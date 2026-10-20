# Performance methodology and limitations

Sequential processes, same machine/runtime, original fixture schedules, n=3 canonical and n=3 detailed diagnostic measurements per fixture. Alternate schedules each use one canonical/observed pair for numerical sensitivity, not throughput statistics. No concurrent heavy profiling solves run. A short offline analysis overlapped one sensitivity process; **all sensitivity timings are excluded from the three-sample performance summary**. Counts/science remain exactly verified.

| Fixture | Canonical advance wall median [range] ms | Observed advance wall median [range] ms | Median ratio |
|---|---|---|---|
| cold | 213.05 [205.87, 239.85] | 404.63 [395.96, 407.18] | 1.899 |
| warm | 1139.25 [1094.53, 1158.26] | 1692.30 [1651.58, 1851.98] | 1.485 |

Wall time sums six advance calls, including original record/observer work within advance, excludes later checkpoint hashing/serialization, initialization, module import and supervisor compression. Process receipts separately include serialization and gzip in supervisor wall time; do not compare that to solver time. CPU includes user+system CPU across process threads; it may exceed wall time on this two-CPU-quota host. Raw per-run wall/CPU, construction and resource data are retained. CPU and wall are not interchangeable.

Inclusive scopes overlap: Jacobian contains derivative residual/property work; residual contains evaluate; evaluate contains hydraulic/thermal and boundary properties; public PH contains inverse/branch. Counts of lexical branch work also include MVU recovery outside PH. Original diagnostics and B14 counter/map/clone/hash work can execute inside timers. Matrix hashing is explicitly inside the Jacobian timing envelope. Hook overhead is nonuniform across scopes, so dividing each observed scope by canonical time would be invalid. No additive pie chart or percentages summing to 100% are presented.

Public property timers include PH input tracking and result accounting, not only unwrapped engine code. Per-column timings include all instrumented residual work. Branch and PH counts give stronger algorithmic evidence than extrapolating these timer shares. No exclusive CPU percentage for pressure binary search, interpolation, allocation or GC is measured. PH observer-index bins include calls between attempts and are contextual, not causal intervals.

Short samples have JIT warmup, process startup, scheduler and GC noise. n=3 median/range is descriptive; it is not a statistical confidence interval or a desktop benchmark. Warm first-sample MVU timing is an outlier (137.7 versus about 68–69 ms) and is retained rather than discarded. Instrumentation wall overhead is large; no optimization speedup or real-time factor for desktop production is claimed.

Host: Linux x86_64 Xeon Platinum 8573C; 3 visible logical CPUs, quota 2; cgroup memory 8 GiB. Each solve has 40 s wall / CPU budget, process group and explicit kill, 512 MiB V8 old-space, 64 MiB output-file limit, no core dumps and capped attempts/columns/commits/input-map observations. Heap cap is not RSS cap: code, external buffers and runtime overhead remain outside V8 old space. The host cgroup provides the overall memory bound. All normal cases complete well within budgets; no bound was silently increased. Maximum normal per-run supervisor wall time was under 8 s.

The deliberate 1 s timeout is separately labeled external-budget evidence, never a scientific refusal. Failed unique-anchor construction has no scientific sample. The campaign does not repeat B13's full historical validation or run a physical horizon >.01 s. No browser installation, device run, public Worker call or deployment occurred.

Future desktop Chrome/Edge profiling on ordinary Windows/macOS remains necessary. B12 remains the known-good reference. Owner-observed iPad .5–1 s initialization/disposal feedback is useful responsiveness evidence but cannot benchmark solver throughput.
