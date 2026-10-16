# Execution scope and retained incidents

- Fresh managed workspace; full clone obtained through the configured proxy with
  tool additional network permission. Initial default-sandbox ls-remote could
  not connect to the proxy. No credential values were inspected or printed.
- Checked out the exact B5B branch/commit, observed empty porcelain status, then
  created only the requested C1 branch. `95f7881` commits the pre-edit review and
  starting audit, before functional implementation.
- Playwright WebKit 2336 was installed in `/workspace/c1-browsers`. Its initial
  host-library warning is retained in `evidence/webkit-setup.log`. The same six
  SHA256-verified Debian archives listed in B5's `browser-libraries.json` were
  extracted into `/workspace/c1-webkit-libs` and copied into this disposable WPE
  sys/lib. No repository loader or browser artifact was changed.
- Initial Chromium/WebKit sets passed (`*-initial-pass.json`). Extended harness
  runs initially failed `detached commit injection` (`*-detached-harness-failure.json`):
  a fourth crossings call could occur in an accuracy-rejected trial rather than
  second commit preparation. The test now uses the accepted static sealed/zero
  exchange fixture for that injection, preserving every numerical setting.
  `*-extended-pass.json` and final `*-replay.json` both pass their respective sets.
- Initial native per-call-process bridge encountered an outcome assertion without
  sufficiently detailed capture; a repeat reached the 120-second outer deadline.
  No native thermodynamic conclusion is drawn from those incomplete attempts.
  A persistent local FIFO bridge replaced per-request process initialization.
  Default-sandbox child process setup produced `spawnSync mkfifo EPERM`; the
  same supported additional permission used for browser processes succeeded.
  This was not an automatic-approval rejection or a policy denial.
- A native A2 attempt with one-byte FIFO reads also reached the 120-second outer
  deadline. Buffered pipe reads completed the actual 24-scenario native A2 set
  under the same 120-second bound, without modifying any scientific configuration.
  Its JSON evidence is `native-A2.json`. Native bridge time is IPC-inclusive and
  cannot be interpreted as pure C++ performance. The numerical backend is the
  same archived B4C library throughout. `native-wrapper.log` and
  `native-properties.log` retain completed receipts. All 250 original native
  outcomes independently match the saved B5 ledger before wrapper tests.
- Three actual native full-VLE QT exceptions are replayed separately through
  the candidate wrapper. The test-only configuration restores superancillaries
  afterward. This is not a browser endpoint implementation or qualification.
- Final guard supplement tests actual loader nonfinite refusal before entering
  C++; it does not exercise or repair inherited rejected-PT exception cleanup.
- Browser process deadlines: 220 s for the focused two-engine integration run,
  90 s for guard supplement; launch 30 s, worker 30 s. Native replay 90 s;
  native full wrapper/A2 120 s; properties-only supplement 45 s. No complete
  long-duration trajectory or options/refinement sweep is run.

All emitted data are new C1 evidence. Historical reports, inputs and artifacts
remain byte-preserved. Setup incidents and harness corrections do not count as
scientific passes; final scientific assertions apply only to completed evidence.
