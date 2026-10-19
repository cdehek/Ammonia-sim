# Research shadow protocol 1

Design scope: trusted pinned B9C table engine → dedicated worker → detached read-only evaporator panel. Actual workstation integration remains NO-GO. No public backend injection, arbitrary input edits, plant controls, continuous scheduling or fallback backend.

Request envelope: `{protocol:1, backendId, sessionId, requestId, sequence, type, args}`. backendId explicitly identifies `A2-table-B9C-b67afb3`; sessionId is fresh per worker. Request IDs and strict next sequence are required. Response repeats identity/type/sequence and includes success, current accepted clock/version, status, error, snapshot or null, timing and diagnostic availability. Sequence protects equal-version fault ordering as well as version ordering.

Worker creates its own loader, owned recursively frozen table engine and exact B9C model. Its loader, state, engines, cached PH objects, proposals and ledgers never leave the realm. Worker scientific numbers retain original binary64 values; structured clone detaches transport. Display must never submit M/U/V, p/T-derived inventory, rounded values or an old snapshot as state.

Minimal snapshot schema: protocol, backend/source identity (A2 and B9C commits), qualification string, sessionId, monotonic acceptedVersion, clockSeconds, freshness/status; five sections `{pressureBarAbsolute,temperatureC,massKg,internalEnergyKJ,volumeM3,enthalpyKJkg,phase,quality,wet,superheatK}`; thermal nodes `{id,temperatureK,energyKJ}`; inlet/outlet signed `{massKgS,energyKW}`; totals `{massKg,internalEnergyKJ}`; conservation residuals and cumulative boundary/thermal ledger summaries; numerical/domain stop or null; unavailable equipment fields explicitly null. Units are explicit metadata: bar absolute, °C, K, kg, m³, kJ, kJ/kg, kg/s, kW, seconds, dimensionless quality, Boolean wet. Original cells supply conserved M/U/V directly; original record supplies p/T/h, phase and rates. The projection may not reconstruct physical inventories.

States and transitions:

| State | Clock/readings behavior |
|---|---|
| initializing | No accepted readings; scientific assets/owned engine loading. |
| ready | Original create + record succeeded at t=0; initial version 0. |
| accepted-state | A supported advance returned an accepted record without stop; increment version if original accepted-step count changed. |
| pending | Last accepted readings remain visible; accepted clock does not animate. |
| numerical-refusal | Original solver/accuracy/property refusal; no new successful snapshot. Preserve last received readings as stale; expose actual current accepted clock/version and fault separately. |
| modeled-domain-stop | Only original independently confirmed domain evidence earns this label; no equipment trip. Last display retained stale. |
| stale | Last successful snapshot's own time/version retained; failure/pending/loss metadata is separate. |
| lost | Worker error/messageerror/timeout/termination; unknown in-flight state, terminate, no retry/resume. |
| disposed | Queued synchronous boundary disposal drops owner references/cache/evidence; acknowledge then terminate. |
| unqualified-backend | Wrong identity, missing scientific bundle or failed initialization; no success or illustrative substitution. |

Commands: initialize cold/warm; advance through exactly .0001/.0004/.0005 original requested intervals, bounded to .001 s; latest (projection of retained successful record, no property evaluation); diagnostics (original current record/attempts/accepted-state copy explicitly research evidence); stop (scheduling latch only); dispose. No resume command. Restart means new worker/session and original independent fixture, never continued state. Test-only named original numerical/thermal fixtures are restricted to test-enabled workers; never exposed as operator controls. Diagnostic generation remains original trace/observer cadence; timing and transport do not remove scientific checks.

FIFO queue includes initialization. Identical duplicate IDs replay a detached cached response without advancing science; altered duplicates refuse. Bounded cache (256, disposal exempt) refuses on exhaustion rather than re-executing an evicted request. Out-of-order sequence and wrong backend/session refuse. Protocol refusal does not manufacture a physical model fault. Client permits one outstanding physics command and exposes stop/dispose at a safe command boundary. Stop cannot preempt the synchronous solver; an advance already dispatched may accept before stop is acknowledged. Hard termination loses the session and retains stale last known data. Do not claim mid-stage cancellation.

Display installs only matching active session/backend/request/type/sequence responses, checks nondecreasing acceptedVersion and newer display sequence, and validates snapshot identity/clock/version. A newer refusal cannot be cleared by an older equal-version success. History stores only new successful versions, bounded to eight snapshots; initial state is a genuine t=0 observation. No successful point after a failed calculation, no fabricated trend. Diagnostic evidence is retained in worker until disposal, separately from the small history. A refused advance can follow earlier accepted substeps: current worker clock/version may be newer than the last displayed snapshot. This is disclosed explicitly, never silently rolled back or shown as a new successful reading.

Projection verification must compare every numeric/phase/wet field to the source record and cells using exact binary64 encoding before formatting, then verify every rendered numerical cell against its projected source. Fault paths compare worker state/record and original control and independently check physical rollback. Display rounding/conversion occurs only after verification and cannot affect solver settings or acceptance. Missing/unavailable quantities remain null and show “unavailable”, never zero.
