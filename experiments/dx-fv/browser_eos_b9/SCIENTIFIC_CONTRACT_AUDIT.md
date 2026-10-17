# Preserved original scientific contracts

No B9 acceptance budget or source equation changes. Historical tracked-file
hashes, direct Git comparisons, literal package audit, within-engine exact value
comparisons and original ledger assertions provide separate preservation evidence.
This is bounded worker architecture evidence, not a new backend qualification.

| Requirement | Original unchanged contract |
|---|---|
| Canonical recovery | pressure <=0.1 Pa; enthalpy <=0.1 J/kg; temperature <=1e-4 K |
| Fluid normalization | mass/energy <=1e-11 |
| Standalone properties | pressure strictly <10 Pa; h strictly <50 J/kg; T strictly <0.01 K |
| Independent reference resolution | pressure 1e-5 Pa; internal energy 1e-8 J/kg |
| Explicit support | 0.3–35 bar absolute; original property phase/temperature checks, 195.495 K floor, 30 K subcool and 250 K superheat |
| Thermal domain | original 200–400 K |
| Inventory arithmetic | V=.003/5; M=rho*V; U_kJ=M*(h/1000)-100*(P/1e5)*V where coordinates are SI; original accepted kJ/bar implementation stays literal; DU uses original M/V and (U/M)*1000 operations |
| Conservation | each section and aggregate mass <1e-8 kg; fluid/thermal/combined and section/node energy <1e-6 kJ |
| Thermal nonlinear closure | 1e-12 K, original normalized residual scales retained |
| Solver | original TR-BDF2/coarse/two-half-step acceptance; 30 Newton iterations; signed FD/shrinking/line search; original growth/rejection/event rules |
| Retry/floor | dt/2; minimum 1e-9 s; persistent scenario 20 attempts, 19 halvings to 1.9073486328125e-9 s |
| Physical meaning | original physical event logic; independent trajectory proof required; no numerical refusal relabeled as a trip |
| Rollback | exact physical values AND original cell/thermal/ledger identities within each realm; allowed original diagnostic counters/stop bookkeeping |

The direct browser-to-browser comparison uses the original accepted coupled
browser contract (<1e-4 bar, <.05 kJ/kg, <.01 K refrigerant/thermal, <.001 s event
times) when engines differ. Same-engine main/worker comparisons require exact
bits. A2's own unchanged canonical stage cross-checks remain in source; original
property standalone/reference qualification is inherited, not rerun as a full
campaign. Optional B7 reapplies canonical and quality checks to its supported
subset and replays existing qualified liquid identities without expanding scope.

No pressure epsilon, phase/quality clamp, substitute state, inventory/energy
correction, alternate EOS for a failed case, altered budget, production safety
rule, or nine-section implementation is introduced.

Unresolved: four Gate B endpoints; eleven invalid DP identities/44 observations;
seven historical 35-bar refusals per browser; two inward false-acceptance hazards;
exact-inventory phase/branch/topology certification; full experimental backend;
full/long-duration A2; nine-section convergence; production protection; physical
iPadOS Safari. A short empty-event trajectory does not certify every future event.
