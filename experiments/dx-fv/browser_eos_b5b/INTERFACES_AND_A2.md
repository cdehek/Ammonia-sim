# Observed interfaces, lost information and accepted A2 consequences

All paths below are unchanged. `evidence/interface-source-evidence.json` retains
line-numbered source excerpts and hashes. The twelve accepted dependency copies
match Git objects at `be9eb35a4ddf5098e685182f8104685127c6a6ee`; root `engine.js`
also matches that checkpoint. The accepted domain test is extracted read-only
as `evidence/accepted-A2-domain-test.cjs.txt`. No A2 simulation is executed.

## Actual historical path

```
original requested PH (Pa,J/kg), supported
  -> B4C PH: actual EOS getters (not identical to requested P/h in last bits)
  -> accepted ordered binary64 conservative M,U,V construction
  -> stateMVU(M,V,U,35): rho=M/V; u=(U/M)*1000
  -> B4C raw DU returns p,T,rho,h,u,s,Q
  -> convert(s,s.p/1e5,s.h/1000)
  -> table engine ph(p_bar,h_kJkg): passes original seven
  -> sat(p_bar): p>35, throws domain before SAT EOS evaluation
  -> no accepted state, no returned density/energy residual fields
```

Both engines observe `EOS_call(DU)`, `EOS_return`, `table_PH_call`,
`table_PH_pass`, followed by stack location `adapter.mjs:8`. Count `sat=1`
counts entry into the rejecting function, **not** a completed saturation flash.
No SAT request appears. The trace wrapper only records calls/returns; the
authoritative adapter and B4C loader are imported without edits.

| Interface | Receives and retains locally | Discards / cannot establish |
|---|---|---|
| `eos.evaluate(DU)` in B4C loader | exact rho/u numbers; actual getter p/T/h/s/rho/u/Q, finite-output check | No original PH, M/U/V, cell/time, physical direction, residual certificate or uncertainty bound. Exceptions are decoded into a new Error; native exception type/status details do not survive. |
| `stateMVU(M,V,U,guess)` adapter lines 23–31 | M,V,U and reconstructed rho/u; raw state before conversion; guess argument received but unused | No originating PH or inventory history. On strict failure, raw state and residual opportunities are lost to caller. Guess=35 proves nothing. Successful return includes inventory and residual fields but no independent certificate. |
| `convert(s,p,h)` lines 13–20 | raw s and comparison coordinates; DU supplies raw p/h; PH supplies requested p/h | Cannot distinguish explicit PH support from recovered DU support except through its caller. Table rejection is not wrapped with scope or consistent fault kind. Raw p is absent in accepted PH's displayed p semantics. |
| `sat(p_bar)` lines 7–11 | only one number, counts | Does not know whether P is requested, recovered, guessed or part of a physical direction. Strict p<.3/p>35/nonfinite rejection precedes EOS. No accepted origin can be inferred. |
| `ph(p_bar,h_kJkg)` lines 22 | explicit requested values, table guard before PH EOS, raw state locally | Returns requested p/h semantics with EOS density/u/T; it does not return actual PH getter p/h or a verified origin certificate. Requested support is not a proof about a later rounded inventory. |
| table `engine.js` `ph` / `bracket` | PH support, log-pressure bracketing and bounded caloric branches | Inherited eps=1e-8 is a bracketing rule, not strict adapter policy. It passes the seven tiny recovered overshoots. It does not prove EOS root consistency or physical trajectory exit. |
| accepted `thermodynamics.ph` | strict explicit P/h guard, engine result, saturation, derives equilibrium wet/superheat | Inside catch, unlabeled errors default to `domain`; a raw numerical PH exception can therefore be overclassified. Explicit `solver` survives. |
| accepted `thermodynamics.recover` | cell M,V,U,pressureGuess to engine MVU; derives wet/superheat only after success | No originating PH relation; does not default unlabeled errors to domain. Raw/unlabeled errors propagate; coupled catch later treats missing kind as solver. |

An observed subtlety: the new +100 Pa unsupported recoveries fail earlier at
the table PH guard with `Error: State outside the validated property domain.`
and **no faultKind**. The seven microscopic overshoots pass that table guard
and get `domain` from strict sat. Thus distance beyond the boundary does not
even determine a uniform current failure label. `evidence/propagation.json`
demonstrates, by six interface-only calls with synthetic errors, that unlabeled
PH errors become domain, while unlabeled MVU errors stay unlabeled and reach
the coupled fallback as solver. This is no physical experiment or coupled run.

## Non-injective construction proves missing provenance cannot be inferred

The liquid requests at Pmax, its adjacent inward Pa value, and its adjacent
outward Pa value have distinct P bits but identical M/V/U/rho/u bits in both
browsers. The mixture triple does too. These are the saved B5 PH diagnostics,
not regenerated originals. See `information-loss-collisions.json` for all bits.
The outward request is independently unsupported as an explicit PH input.
Identical DU inputs plus identical guess=35 necessarily present identical
information to a deterministic `stateMVU` implementation. It cannot recover the
original requested-input class. Nor can M/V/U alone establish whether any of
these inventories was supplied by a plant trajectory, direct DU input, or PH
construction. Information about chronology, intent and physical direction is
absent, not merely hidden in a last bit.

Independent EOS analysis can diagnose wrong-side numerical error or mathematical
unsupported inventory. It still cannot reconstruct lost PH lineage or establish
a physical operating excursion at nanopa. Previous-pressure-guess acceptance or
fixture-name lookup would be unjustified provenance invention.

## Accepted five-section failure flow

`coupled-model.cjs` wraps fluid errors with refrigerant source, section and stage
(`fluidCall`, lines 73–76). That adds location, not physical proof. It constructs
each stage inventory in `solveStage` and recovers it after Newton. It still has
the solved stage PH coordinates at lines 185–189, but supplies only M/V/U/guess
through `recover`. A future caller certificate could originate here, explicitly;
it does not currently cross the interface. Returned states differing by more
than 1e-6 bar / 1e-4 kJ/kg / 1e-4 K throw `solver`.

Newton retains original signed finite differences, branch checks and line search.
Failed line searches wrap a last `domain` cause into `domainCause`; derivative
failures can propagate their error directly. No unsupported probe alone proves
a trajectory exit. At `advance` catch, every exception rejects the trial and
halves dt. Domain labels/domainCause affect counters, diagnostics and growth
history reset. Only a `solver` error with a finite actual nonlinearResidual and
without domainCause teaches failure-aware growth; a property failure must not
invent that residual. The original 1e-9 s minimum and 100000 attempts remain.

At the retry floor `domainEvidence` starts unconfirmed. It independently
rechecks an exact thermal-boundary outward-direction claim; this established
protective proof remains valid. At dt<=1e-6 it also evaluates physical rates
at the accepted state and attempts conservative directional refrigerant recovery.
**Any recovery error labeled domain confirms refrigerant domain exit at line
257.** A B5B strict-guard numerical/representation error can therefore contaminate
that proof. A generic solver failure is not automatically safe either: accepted
state coordinate evaluation/recovery can itself fail during evidence gathering,
initialization, or final record construction. Those paths have no universal
uncertainty-aware result envelope. A classification-only property change must
be tested there; this report does not claim the live solver already handles
every persistent unresolved state gracefully.

When evidence is unconfirmed the terminal stop kind is solver; confirmed proof
yields domain. Retry/attempt metadata may change, but rejected trials do not
commit cells, thermal energies, physical ledgers, clock, events, boundary history
or accepted-step count. Both half steps are prepared against detached
ledgers/events before `Object.assign(s,accepted)` at line 320. A failure while
preparing a commit is outside the main trial catch, yet detached preparation
protects installation; a future result interface must preserve this property.
Retained stops freeze subsequent advance/update under the accepted contract.
These are source/accepted-test findings, not newly run B5B rollback results.

| Property-layer situation | Required treatment under the proposed contract |
|---|---|
| Genuinely unsupported physical trajectory, independently resolved | Reject; retain A2's true proof and protective domain stop with exact rollback. Do not convert it to an accepted state. |
| Numerical inverse failure | Reject and halve; report numerical property failure, retain underlying evidence; persistent unproved failure ends numerically rather than claiming physical exit. |
| Unresolved boundary / rounded conflict | Same refusal/rollback protection; retain C and its explanation through retries and terminal reporting. Halving may never solve an exact fixed-inventory conflict. No long-duration progression claim is justified. |
| Supported successful recovery | Only supplies a candidate property result. All unchanged stage, temporal, event, thermal and conservation gates still decide trial acceptance. |

The existing `faultKind`, `evidence` and `domainCause` have enough transport
capacity for a conservative numerical refusal plus diagnostic fields, but
**current meanings and wrapping are insufficient for a complete distinction**.
A typed input rejection is not identical to a certified trajectory exit. A
separate review must specify how a property result's scope and proof are
preserved and independently consumed by A2. No change to `domainEvidence`,
retry floors, rollback, stops or growth learning is authorized in B5B.

`wet` is the existing equilibrium indicator: mixture quality<1 or a liquid
phase string. It is derived after successful property operations and reported
at the terminal section. No accepted high-level vessel protection or operational
wet-suction interlock is implemented in this dependency closure. Failed/C states
cannot supply a new wet/high-level decision; do not infer “dry” from failure or
invent new protection behavior. Actual operational protection design lies outside
this property classification milestone.
