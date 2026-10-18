# Execution notes and retained unsuccessful evidence

The workspace began without a checkout. The first sandboxed clone could not
reach its proxy; explicitly network-enabled execution succeeded. The checkout
was clean at exact B9A, then the isolated B9B branch was created. No remote or
protected file was changed by setup. Gate 0 verified 2,675 historical files and
14 A2 sources against original Git objects, plus all C1/B6/B7/B9 files at their
protected commits. Pre-instrumentation design commit: 5fae85a.

Browser dependencies were installed only in /workspace/b9-runtime using the
unchanged pinned B9 setup; its warnings/log are retained. No host/operator
workstation dependency was installed. Actual measured browsers are the original
Playwright Chromium 151 and WPE WebKit 26.5, not system Chromium 154.

Original B9 service and direct frozen-worker baselines passed before diagnostic
runs. External Chromium sampling followed; the first driver expression defined
and inadvertently invoked a function without arguments. That harness failure is
retained as passive-chromium-harness-failed.json.gz and its log. It supplied no
qualified CPU profile. The corrected pass then accidentally enabled sampling on
its bracketing controls too; those successful-science receipts/profiles are
retained under superseded-sampled-controls-* and excluded from final overhead
and CPU summaries. The final bounded passive pass enables Profiler only on the
designated sampled worker and records controls separately. No scientific outcome
or property count changed in those successful superseded runs.

The diagnostic copy inserts observations only, with a full exact diff and an
independent deletion audit restoring every original byte. Node smoke checks
preceded the three browser measurement rounds. Final successful-fixture validation
checks exact scientific fields separately from profiler metadata and compares
every original public property request/result sequence. Additional bounded
failure cases use original C1 sources and original-vs-observational A2 copies.

Final review found that the first main-matrix original control unnecessarily
constructed unused context strings and a no-op timing closure on public property
calls. Those context/closure operations are now bypassed in the original and
pass-through controls. Earlier controls/matrix/CPU receipts are retained under
superseded-control-context-* and excluded from final statistics. The predefined
baseline/passive/matched matrix and Node reference were rerun after this harness
correction; this was not a search for favorable timing. All scientific data in
the earlier matrix remained unchanged. Final scientific validation/failure
checks follow the corrected matrix, sequentially. Worker dispatch later gained
only the additional isolated-copy failure command; measured profile.mjs/scientific
copy implementation was not changed during or after the matrix. A post-run
same-browser Time.factor replay reconstructs every adaptive proposal without
executing any further model or property work.

Offline analysis corrected two parser issues: sorting a null clock-resolution
probe with numeric values, and excluding its own CPU summary from the raw-profile
glob on reruns. These changed no raw evidence or experiment. Final analysis
asserts exact parity, original budgets, complete count reconciliation and
observational insertion identity. Large raw gzip receipts preserve full original
arrays rather than substituting compact/gauge snapshots.

All research files are additive under B9B. Historical file/ref/PR preservation,
final branch ancestry and clean working tree are sealed separately. No mutation
of a production ref, deployment or review message to another person is made.
