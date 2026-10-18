# Compact operator snapshot v1

A detached view of an already accepted record, never a replacement physical
state. Worker exclusively owns original M/U/V, solver proposals, thermal energy,
ledgers, schedules and events. No display value is accepted as scientific input.

Envelope retains protocol, mode, worker/backend/session/request identity, strict
sequence, acceptedVersion and clock, success/refusal and diagnostic scope.
Snapshot fields and units are defined in snapshot-schema.json. Unrounded JS
Numbers are copied by structured clone. Pressure remains original bar absolute;
temperature converts original Celsius by +273.15 to kelvin. Mass is kg; total
internal energy is kJ, not specific enthalpy. Source cell M/U is copied directly.

Five sections expose pressure, temperature, mass, internal energy, phase, quality
and wet indicator. Original tube/fin/air nodes provide temperatures. Inlet is
only the original specified boundary PH; no extra property lookup is performed.
Terminal bulk and supported/refused outlet summaries are original record values.
Mass and combined energy residuals retain original meaning. Last accepted step
is the final original trace interval divided by two for adaptive TR-BDF2's committed
half steps; null before any commit. This is distinguished from requested advance.

Numerical status distinguishes ready, scheduling-stopped, physical-domain stop,
numerical stop, record-unavailable, failed and lost session. A refusal carries
the current clock/version/fault immediately, even if no new record can be made.
Last received snapshot is marked stale on any relevant refusal; an older equal-
version response cannot clear newer fault metadata. No missing record is invented.

Qualification: short five-section accepted table-backed research; effective
uncalibrated conductance; no complete model/backend/operator qualification. Wet
bulk indication is not a compressor suction safety guarantee. There are no
compressor, receiver, valve, plant alarm or safety-trip measurements.

## Diagnostic separation

snapshotCompact projects the retained current original record without property
work. diagnosticsSummary returns scope/counts and availability for an explicitly
requested accepted version. diagnosticsDetail returns a detached original record,
full authoritative state copy and original observed attempts for that retained
version. These are research commands, not model methods. Only four recent endpoint
evidence entries are retained in Mode B; the original cumulative attempts array
and B9-style generation remain intact during the session. Expired versions return
explicit unavailable, never another version. Failure evidence for the current
version replaces its prior successful evidence and remains visible in all replies.

The response cache remains capped at 256 with refusal on exhaustion and disposal
exempt. Identical duplicates replay the original detached response; altered
duplicates refuse. No LRU eviction permits double execution. Diagnostics can
expire independently of cached responses: a cached old response remains honestly
tagged with its original version and cannot install a stale display.
