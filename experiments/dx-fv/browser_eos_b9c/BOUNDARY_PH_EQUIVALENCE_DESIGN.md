# Gate 1: exact stage-local boundary PH reuse

Decision: **GATE 1 PASS — REUSE EQUIVALENCE ESTABLISHED**, restricted to the
unchanged accepted table engine, privately owned fixed table, and synchronous
original five-section stages. This document is committed before prototype code.
It is a source-based engineering review, not independent third-party approval.

## Source identity and dependency proof

Starting B9B is ec2df3f9ee3efd7faef3d129282ad1dd7bdc896f. The fourteen-file
closure in evidence/accepted-source-manifest.json is independently compared to
A2 be9eb35a4ddf5098e685182f8104685127c6a6ee Git objects. Later root model and
Newton sources are excluded. Gate 0 hashes all 2,791 historical tracked files and
checks original B9/B9A/B9B/C1/B6/B7 trees against their commits.
The supplied C2 identifier is noncanonical; the canonical Git/ref/previous B8
audit identity is 7c75d9538d57080a01dffbf7e06128a27e2b9ccd. No ref is corrected.

Accepted engine.js::createEngine captures data and eps=1e-8. ph delegates to
lexical inverse(p,h,'h'), which uses sat, statePX or branchLimit/branch/statePT.
These transitively use only their arguments, captured data/logs/eps, local loop
variables, arithmetic and fixed JS Math intrinsics. They read no clock, random
source, DOM, environment, previous lookup, global phase flag, writable memo or
external backend. All arrays created by bracket/mixRow and objects returned by
sat/statePX/statePT are fresh. inverse writes only result[key] on its own fresh
result. No table reference escapes through a PH result. thermo.ph spreads that
flat primitive-valued object and adds primitive superheatK/wet. No nested object
aliases exist. Arithmetic and branch order are deterministic in one JS engine
for exactly identical finite binary64 inputs and fixed table/intrinsics.

The table is NOT intrinsically immutable: createEngine(data) accepts a caller
reference, and public engine methods are replaceable. Therefore this proof is
conditional on ownership, not a claim that arbitrary createEngine users are pure.
The isolated entry will construct its own exact table engine from the verified
registry, recursively freeze its table and freeze its exported engine object.
A module-private WeakSet will recognize only engines constructed by that entry;
the candidate factory will refuse all other objects, including proxies, injected
backends and CoolProp. No scientific property implementation is modified.
The control uses the same owned table construction, with unchanged A2 model.

## Consumers and object identity

Accepted coupled-model.cjs::evaluate (137–150) validates thermal temperatures
first, then builds [inlet,...states,outlet]. connectionFlow in hydraulics.cjs
reads p/rho, chooses donor by pressure sign, and calls coefficients reading rho.
C.flux reads donor.h and returns new mass/enthalpy-flux values. Neither writes
nodes, compares identity, retains a node, invokes a user callback or exposes a
boundary object. Thermal work reads only section T. evaluate returns rates, not
boundary references. blend, residual assembly, solveStage, commit and record
consume those new rates. Therefore replacement of repeated boundary objects by
the first exact result has no scientifically observable identity effect.
The five section PH objects and their preexisting Map remain untouched.

All evaluate callers were inspected: solveStage endpoint; trial direction and
initial rates; domainEvidence exact-boundary confirmation and small-dt evidence;
record current rates. Only the solveStage endpoint receives the new closure.
Other direct boundary calls occur in create, patchSpec, and record's outlet
diagnostic. These and all non-stage evaluate calls remain genuine evaluations.
trial, advance, applyBoundary/update and record retain their original source.

## Lifetime, exact identity, and evaluation order

One closure with two slots is allocated by each solveStage invocation, beside
the existing section Map. evaluate receives it only at the original stage
endpoint call. Each slot stores {p,h,value} only AFTER successful thermo.ph.
Lookup uses Object.is on the ORIGINAL Number p and h, without keys, rounding,
conversion or epsilon. +0 and -0 are distinct; pressure zero is already invalid.
NaN/nonfinite inputs fail original validation and cannot install a slot. Even
though Object.is(NaN,NaN), no successful NaN entry exists. Signed-zero enthalpy
retains its original identity and all original engine endpoint behavior.
The object is read only and never part of authoritative M/U/V or thermal state.

Lazy lookup remains at each original inlet/outlet expression, after thermal
validation, in inlet/sections/outlet construction order. A failing inlet prevents
outlet evaluation. Failed results never install. On an input mismatch, the old
slot is invalidated before calling the original function. Any property exception
clears both slots before rethrowing the original Error, preserving message,
faultKind and evidence. There is no fallback, clone, substitute state or new
physical acceptance. No asynchronous callback executes inside a stage.

solveStage returns no cache reference. Every subsequent stage, coarse/fine
trial, retry, accepted step, scheduled patch, manual patch, record and worker
session starts without those slots. Rejected line-search/FD work may reuse only
successful exact boundary values in the SAME stage; it cannot freeze section
coordinates. A failed property evaluation clears the slots, including if caught
inside Newton. Other exceptions cannot leave the stage closure reachable after
its invocation. Thermal failures before boundary work retain their precedence.

## Validation and refusal equivalence

thermodynamics.cjs::ph first rejects nonfinite p/h and strict p<.3 or p>35 with
domain / 'Thermodynamic state outside the bounded property domain.'. Otherwise
engine.ph must succeed, followed by engine.sat. The same fixed table determines
all validation/phase decisions; successful identical input cannot become invalid
without an excluded dependency mutation. Reuse therefore bypasses no required
new validation. A changed input always invokes the original checks.

engine.inverse uses original inclusive hf-eps/hg+eps mixture tests and original
quality clamp. No endpoint assumption is added. Original subcool refusal is
'Subcooled liquid exceeds the bounded property table.'. Superheat engine text
'Compressor discharge exceeds the property table (250 K superheat). Use a lower
ratio or higher efficiency.' is rewritten by thermo.ph to 'Section enthalpy
exceeds the bounded property table (250 K superheat).'. Missing liquid rows throw
'Liquid state below the property table temperature limit.'. bracket throws
'State outside the validated property domain.'. thermo.ph supplies original
domain faultKind for these untyped table errors. No failure is cached or relabeled.

## Review before implementation

Review obligations checked independently of any proposed implementation: actual
transitive property dependencies; table ownership gap; primitive PH shape; every
consumer and evaluate caller; strict pressure and original enthalpy/phase paths;
thermal/inlet/outlet failure precedence; synchronous lifetime; exact-key semantics;
no external PH savings. This review establishes the narrow source contract.
An independent audit script will reject any functional source diff outside the
documented factory guard, stage closure, optional evaluate parameter and endpoint
plumbing. Runtime qualification remains mandatory and can overturn this PASS.

Predeclared qualification: unchanged frozen cold/warm .0001/.0004/.0005 advances,
initial plus mandatory and extra snapshot records; actual Chromium and desktop
WebKit; exact full science/observer/residual/FD/matrix/correction/stage parity;
property sequence projection removes ONLY proven duplicate stage boundaries;
bounded phase/support/reversal/patch/retry/failure/C1 and fresh-worker tests.
After these pass, five sequential C→candidate→C timing rounds per fixture/engine,
fresh workers and original observer cadence, separate diagnostic counting/timing
passes, all samples retained. No simultaneous computational workloads. No horizon
extension or full A2 qualification. Performance may improve, regress or be noisy.

All inherited physical, numerical, backend and device blockers remain. No merge,
deployment, production use or CoolProp optimization is authorized.
