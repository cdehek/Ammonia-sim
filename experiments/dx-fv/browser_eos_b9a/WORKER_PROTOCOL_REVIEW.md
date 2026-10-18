# Protocol, ownership and diagnostic retrieval

Protocol 1 retains unique session/worker/backend/request identity, strict command
sequence, clock, acceptedVersion, status, explicit success/refusal and safe error.
B/C add mode and diagnosticScope; A delegates original semantics untouched.
Worker owns original conserved state and solver. Presentation and evidence are
detached and cannot be applied as state. No authoritative ArrayBuffer transfer.

| Command | Supported boundary |
|---|---|
| initialize | Original package/engine/factory/create/record, one session |
| advance | Same original advance and complete diagnostic generation; compact response in B/C |
| snapshot | Same original model.record cadence as B9; compact B/C response |
| snapshotCompact | Projection of retained current original record; no invented model API |
| diagnosticsSummary(version) | Requested endpoint availability/counts/fault; explicit expiration |
| diagnosticsDetail(version) | Detached original record/attempts; full state only if current |
| diagnostics | Cumulative B history; C discloses four recent endpoint scopes |
| stop | Scheduling latch at original synchronous boundary; not physical trip |
| dispose | Clear ownership/cache/evidence then terminate |
| testEvidence | Only test-enabled sessions; in-owner reference parity/rollback proofs |

Detail requests require an explicit integer version. Envelope clock/version are
current owner metadata; result clock/version explicitly identify requested
historic evidence. Historic full scientific state is not retained and is returned
as null with stateScope; current state is cloned only on explicit detail retrieval.
Expired endpoint records return available:false, reason:unavailable/expired. They
do not silently substitute a newer version. A later refusal at the same accepted
version replaces that endpoint's status/evidence with current failure information.

B retains cumulative original attempts in worker ownership plus four endpoint
record/attempt scopes. C generates identical original diagnostics but retains four
recent endpoint scopes, discarding expired history explicitly. Observer remains
enabled, trace:true; no acceptance/check/FD/line-search/property call is skipped.
Generation is not optimized. Four endpoints are a count bound, not a byte bound.

Duplicate IDs use bit-exact original content comparison. Up to 256 detached
responses are cached, no eviction/reexecution: identical replay returns original
outcome; altered content refuses. Exhaustion consumes valid sequence and refuses
new work; dispose exempt. Client bounds eight pending requests; 30-s deadline
loses/terminates disposable session with unknown in-flight acceptance. No retry
with a new ID after an uncertain advance. Cache hits cannot mutate authority.

Display acceptance checks session, worker, backend, pending request/type/sequence,
then monotonic acceptedVersion AND sequence. New refusal immediately marks prior
readings stale and stores current fault. Older same-version snapshots cannot clear
it. The panel also ignores older display-sequence results. Successful command
receipt is distinct from numerical status; a returned record with stop is displayed
as numerical-stop or physical-domain-stop, not running. No live Error, pointer,
module handle or native exception ownership crosses the safe diagnostic envelope.

Source review: the original observer is optional, receives freshly constructed
work diagnostics and its return is unused. Callback exceptions propagate outside
probe classification. Diagnostic records contain copied residual/state scalars
and context arrays, not authoritative conserved objects. B/C only push evidence;
neither disables observer nor changes settings. Source remains literal. The
instrumented attribution loader wraps exported call boundaries before dependent
modules evaluate, delegates exactly once and passes exact full-work comparison.
