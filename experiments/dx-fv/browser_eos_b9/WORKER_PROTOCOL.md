# B9 protocol v1

Request: `{protocol:1,workerId,backendId,requestId,sessionId,sequence,type,args}`.
Response repeats those fields (without args), and adds `{success,clock,
acceptedVersion,status,result,error,timing}`. Clock/version are null before any
model exists. Backend is `accepted-A2-table`; workerId is caller-selected unique
realm identity, checked by the owner. Session cannot be reused after disposal.

| Command | Implementation and meaning |
|---|---|
| initialize | Build verified package/engine/factory, create original cold/warm fixture, original record; once per session |
| advance | Original advance duration; returns original record and detached accepted state; refuses adapter stop/dispose |
| snapshot | Original record and detached state; record failure remains an error |
| diagnostics | Detached counters, traces and accepted clock/version; no new thermodynamic evaluation |
| stop | Set service scheduling latch at command boundary; never writes physical model stop |
| dispose | Drop owner references; acknowledge last known accepted clock/version; terminate client afterward |

FIFO promise queue includes initialization. Strict next sequence advances for
valid envelopes even if a command refuses; malformed/out-of-order requests do
not advance sequence. Request IDs cache up to 256 complete responses. An identical
duplicate replays; altered duplicate refuses. Cache exhaustion refuses new work
(dispose exempt). Client limits pending commands to eight. A request timeout marks
the whole session lost and terminates worker: uncertain advance is never retried
with a new ID. Client can resend the identical ID while session remains live.

Errors are plain immutable diagnostic data: name, message, faultKind, evidence,
propertyCause/domainCause, nonlinearResidual, recordFailure and safe native
name/representation if present. Recursive extraction excludes native addresses,
handles, stack and mutable references. Unsupported thrown values have explicit
type/text; they never become successful state. Snapshot failure may retain a
numerical/domain stop but returns no successful property snapshot.

Native cleanup remains solely in the reviewed loader. This protocol cannot own
or clean a native pointer. No raw `excPtr`/state pointer is serializable.

The service exposes only accepted state after an original advance returns. On an
unexpected error after original commits, clock/version truthfully identify current
accepted state; no partial snapshot is supplied. A synchronous solve has no safe
mid-call cancellation. Stop/dispose commands wait; hard termination loses session.

Main display installs only responses from active session/worker/backend, matching
pending request/type/sequence, with nondecreasing acceptedVersion. Late stopped,
disposed/replaced-session callbacks are ignored. A crash leaves last received
accepted snapshot labeled session lost; unknown in-flight state is not recovered.

Structured clone preserves numeric values and graph identity within its cloned
graph, not references into solver. Scientific state uses original JS Numbers;
IEEE binary64 comparisons tag every number with exact big-endian bits. NaN
payloads are compared with typed-array byte transport (JS numeric NaN payload
canonicalization is not a scientific contract). Signed zero/Infinity/NaN and
transfer-detachment receive explicit deterministic tests. No JSON scientific
transport; JSON evidence contains bit tags. Transfer uses copied test buffers only.
