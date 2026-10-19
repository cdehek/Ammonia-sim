# Table purity and aliasing audit

PASS within the owned fixed-table contract in BOUNDARY_PH_EQUIVALENCE_DESIGN.md.
The table is caller-mutable in the general API; this fact requires explicit
ownership enforcement in the isolated entry. It is not assumed away.

| Dependency / owner | Source observation | Consequence |
|---|---|---|
| engine.js::ph/inverse | lexical call graph and local 38-iteration inverse | deterministic same-engine arithmetic |
| sat/pBracket/bracket | captured logs/table, no writes or lookup history | no stateful saturation/phase selection |
| branch/mixRow | reads table primitives; allocates fresh arrays | no returned table alias |
| statePT/statePX | fresh flat primitive fields | first result has no mutable nested objects |
| thermo.ph | validates, calls PH then SAT, spreads new flat object | original first successful validation retained |
| evaluate | thermal checks, inlet then section spread then outlet | lazy original precedence required |
| hydraulics::connectionFlow/coefficients | reads p/rho, no mutation or identity test | unchanged donor selection |
| conservation::flux | reads donor.h, emits fresh primitive rates | no identity-sensitive consumption |
| trial/domainEvidence/record | separate evaluate call sites | excluded from stage reuse |
| patchSpec/applyBoundary/advance | synchronous stage calls, patch outside stage | no cross-stage stale entry |

The source proof excludes altered Math intrinsics, table mutation, engine method
replacement and injected/stateful backends. Runtime evidence must verify shape,
determinism, source identities, projected property order and exact science.
