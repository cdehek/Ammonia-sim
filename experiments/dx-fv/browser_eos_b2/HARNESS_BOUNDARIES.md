# Accepted mathematical problem and harness boundaries

The accepted model equations and assertion bodies can be supplied to the EOS
adapter without changing the mathematical problem. The catalog integrity audit
verifies all 77 supplied source/data strings against accepted Git objects and all
19 assertion entries (18 scientific groups plus a marker) against exact source
text. No omitted configuration is inferred to pass.

| Interface or command | B2 disposition | Minimum isolated harness work |
|---|---|---|
| Original PH/DU, saturation, M/U/V recovery | Executed unchanged; boundary regression FAIL | Diagnose the backend; do not alter the accepted equations or guard |
| `statePT(p_bar,T_C)` in three accepted hot-boundary cases | Original interface BLOCKED; separate B2 PT mapping completes all 36 cases per selected configuration/runtime | Keep `adapter-pt.mjs` explicitly separate; existing unambiguous PT flash and original support guards suffice |
| Phase-imposed or ambiguous PT | Unsupported by the minimum mapping; no accepted hot fixture requests this | Specify an equivalent interface before claiming that capability; do not substitute a nearby PH state |
| Node filesystem, Git ancestor extraction, `Module._compile`, child-process helpers | Browser has no equivalent direct API; selected assertion bodies run through extraction/module injection | Extract pinned source/data and ancestor factories outside the browser, then inject the same backend into both comparison paths; preserve exact assertions |
| Separate original smoke, ancestor, observed and full phase-diagnosis commands | NOT RUN, not a demonstrated physics incompatibility | Extend the isolated loader/factory wiring and archive each original command result separately |
| Other three complete Jacobian/controller suites | NOT RUN | Reuse equivalent option injection and unchanged source; no missing mathematical primitive has been demonstrated |
| Fresh independent direct-EOS trajectory generation | NOT RUN | Run the accepted native generator with its original pinned environment, then the full comparison matrix; keep reference generation independent of WASM |
| Original Node performance command | NOT RUN | Browser timing APIs require separate measurement plumbing and overhead disclosure; B2 short matched timing is a distinct result |

Original predecessor/ancestor equality assertions compare algorithms supplied with
the same property backend. They must not be reinterpreted as a demand for bitwise
equality between table and direct-EOS trajectories. B2 reports those cross-backend
differences separately, without changing any original acceptance threshold.

The PT interface was the concrete accepted-test adapter gap demonstrated here.
Its isolated mapping clears the tested interface gate; it does not repair the
PH phase-classification defect or complete the unexecuted scientific matrix.
