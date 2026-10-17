# Source-level message ownership

| Source / function | Owner and boundary |
|---|---|
| build.py | Read-only historical source verification; literal package generation; no state |
| accepted-bundle.mjs / loader | Closed original module resolution in the receiving realm; no DOM |
| service.mjs / service | Per-session state/model, property counters, original attempts, scheduling latch, strict sequence and bounded duplicate-response cache |
| service.mjs / execute(initialize) | Import/construct original engine and model, original fixture, canonical create and record; failure installs no model |
| service.mjs / execute(advance) | Original synchronous advance; returned record, detached state/attempts; no change to requested time for latency |
| service.mjs / snapshot | Original record plus structured-cloned accepted state; no property substitution |
| service.mjs / stop/dispose | Adapter scheduling boundary; no fabricated physical stop; disposal clears model/state/attempt/cache references |
| worker.mjs | Dedicated FIFO request entry; physics stays in this realm; response posting/timing; no DOM |
| client.mjs / request,send | Unique IDs, session/worker/backend identity, sequence, max eight pending requests, 30-s deadline; identical pending duplicate coalesces |
| client.mjs / receive | Match envelope/pending request; install only nondecreasing version for active session; detached display |
| client.mjs / lose,dispose | Reject pending work, terminate worker, drop main control closure; last display is known received state only |
| index.html | Minimal research UI, actual state summaries, input acknowledgement, rendering, pagehide termination; no production imports/controls |
| values.mjs / diagnostic | New plain safe diagnostic objects; excludes native pointer/handle/module/stack/cause fields; no Error object transfer |
| values.mjs / exact | Artifact-only bit tags; never reconstruct scientific inputs from formatted text |
| c1-tests.mjs | Exact unchanged C1 wrapper/copies and existing B6 subset; explicitly synthetic refusal injection and worker-local exact rollback |
| b7-subset.mjs | Separate optional original property backend; native exceptions cleaned by reviewed loader; safe counts and stack delta only leave realm |
| probe-worker.mjs | Disposable test-only owner; runs C1/B7 subset or transport/error tests. Not an invented accepted-model API |

Scientific authority is NEVER in a response cache or display. Those are detached
copies. Accepted object identity exists only inside the owning model realm. No
solver buffer is transferred/detached. The transport test transfers a copied buffer
and verifies all bytes, including a NaN payload; numeric NaN payload preservation
is not presumed across Number operations.

A worker's synchronous solve cannot process a new event until it returns. The
promise queue additionally serializes async initialization and command dispatch.
Stopping means finishing the already requested advance then refusing future
advances. Emergency termination does not undo/recover original solver trials.

Test-only probe commands c1, b7, echo, jsError and crash have explicit protocol v1
request/session/sequence/type/worker/backend IDs and success/refusal envelopes.
Their clock/version are null because they own complete disposable scenario suites,
not an exposed simulation session. c1/B7 results carry actual accepted state/error
metadata internally. Their backend IDs are C1-table-synthetic, B7-gateA-subset and
B9-transport-test respectively. No extra actuator/physical-state API is introduced.

The 256-response cache stops accepting new work when full. Valid-envelope refusal
consumes its sequence, so dispose still works; dispose clears cached state copies.
Lifecycle evidence covers exhaustion/disposal and the eight-pending backpressure
limit. Normal benchmark sessions are far below this cap; that correction does not
change their scientific or timing path.
