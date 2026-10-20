# B13-A0 bounded horizon protocol

Accepted qualification remains 0.001 s. Every result above that time is **UNQUALIFIED RESEARCH**, including successful runs. No UI, worker service contract, deployed asset, tolerance, numerical option or physical boundary changes are authorized here.

Start fresh cold and warm processes at 0. Follow accepted output increments 0.0001, 0.0004, 0.0005 s. Compare canonical B9C and separately instrumented science and adaptive-attempt hashes at all four checkpoints. Compare fresh accepted-A2 control in the same Node engine. Retained B11 Chromium receipts are checked separately: binary64 equality across browser/runtime versions is observed, not assumed.

Progression requires manual engineering inspection after each invocation: 0.001 → 0.002 → 0.005 → 0.01 s. Each invocation starts from zero and repeats prior output boundaries. Do not select the next horizon automatically. Stop a fixture's progression after a numerical/domain stop, failed conservation audit, phase ambiguity, material deterioration, severe expense (>5 seconds for one requested interval or >10× recent cost per accepted second), or exhausted process budget. A shorter diagnostic replay of the same horizon may characterize a refusal. A refusal does not authorize a longer run. No minutes/hours are executed.

`run.py` launches a separate Node process with a 30 s default wall/CPU budget (maximum 60 s), 512 MiB V8 heap limit, and 128 MiB output-file limit. These are research process limits, not modified solver budgets; the accepted maxAttempts/maxIterations/minStep remain unchanged. The parent kills the process group on wall timeout. Heap limit is not a total RSS cap. The raw output is compressed only after child termination. Completed checkpoint receipts are distinguished from `partial-progress`, which records previously committed M/U/V, thermal energy, ledger and time before the current trial commits. A killed trial is never called a numerical refusal.

Canonical runs import the pinned B9C bundle unchanged. They retain the accepted diagnostic observer, plus sparse progress writes; `observerMS` records that callback overhead. Observed runs use the existing pinned B9C diagnostic bundle and a two-anchor Jacobian timing scope in an in-memory copy. Export wrappers time residuals, Newton and linear solves before the model captures them. No extra scientific evaluation is made. Full state/record binary64 encodings and decision hashes must agree with canonical runs. Inclusive nested scopes must not be summed as disjoint categories.

Every checkpoint preserves full state, record, cumulative original observer events, work counters, requested and actual increment, wall/CPU time, memory, settings, conservation audit and refusal. Raw decimal diagnostic events are supported by exact attempt hashes; full checkpoint state/record also retain explicit binary64 encoding. Record/serialization/observer overhead is reported separately where observable. These Node process measurements are neither browser benchmarks nor owner-device measurements. Worker/UI overhead may use clearly dated retained evidence only; no fresh UI is introduced.

Reproduce one bounded run from repository root:

```sh
python3 experiments/dx-fv/browser_eos_b13/run.py --variant canonical --fixture cold --horizon 0.001 --name reproduction-cold-001.jsonl.gz
```

Use fresh receipt names. Inspect the result before independently choosing any next allowed horizon. Never run historical builders, since several overwrite historical evidence.
