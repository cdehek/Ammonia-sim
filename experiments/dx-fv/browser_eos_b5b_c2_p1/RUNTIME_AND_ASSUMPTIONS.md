# Runtime, numerical assumptions and bounded cost

This is a Python/Linux standalone verifier. It is not imported by the adapter,
loader, accepted A2, UI or any production module. It returns evidence dictionaries,
never simulator property states. No certificate consumer or acceptance policy
is implemented.

## Actual arithmetic and trusted infrastructure

- Python 3.12.14, python-flint 0.8.0, FLINT 3.3.1, Arb real balls, mpmath 1.3.0.
- Linux x86_64, glibc 2.41; actual platform, FLINT/GMP/MPFR shared-library hashes
  and script/EOS identities are in `evidence/runtime.json`.
- Initial SymPy 1.14.0, NumPy 2.3.5 and SciPy 1.17.0 are recorded but unused.
- Exact binary64 promotion uses Python's Fraction on decoded floats; exact
  rational conversion to `fmpq` precedes `arb`. All powers, exp, expm1 and log
  in proofs use Arb, including coefficient powers and derived constants.
- Default original ammonia JSON reference, unchanged a1/a2, no external setter.

The trusted base is the correctness of the formula translation, Python and its
binary64 decoding/Fraction behavior, python-flint bindings, FLINT/Arb validated
arithmetic and transcendental implementations, GMP/MPFR as used by that build,
and the host execution/library integrity. Wheel compiler flags were not
independently reconstructed or proved. Library hashes identify the build; they
are not proofs of its correctness. Finite audits cannot certify every compiler
path or an entire numerical library.

Existence uses continuity plus IVT for homogeneous inversion and a uniform
contraction theorem for the two coupled formulations. Full details and actual
hypotheses are in `FORMULATION.md`; no point Jacobian is treated as a proof.
Local uniqueness means uniqueness only in the serialized box at the specified
parameter value. No global EOS-topology theorem is assumed to have been proved.
Thermodynamic rejection by entropy comparison assumes additive macroscopic bulk
phase properties and equilibrium entropy maximization; interface/gravity/kinetic
effects are outside the EOS mixture model.

## Serialization and independent checks

Every authoritative bound is a rational lower/upper pair returned from Arb's
outward endpoint operations. Decimal displays may include extra display rounding
and must not be parsed back as evidence. No f64 midpoint is used to form a
proof interval. Proposed centers and inverse matrices are rationalized diagnostic
strings, independently checked by the theorem. The proof never assumes that
those proposals approximate the right root closely enough.

192/256-bit results each prove their claims. Independently rounded Arb hulls
are not required to nest. The exact rational 192-bit boxes, including original
temperature parameter bounds, are separately revalidated at 256 bits. All 33
pass. Independent mpmath diagnostics repeat at 65/90 decimal digits and a
displaced seed; 105 digits are used for derivative audits only. Agreement is
diagnostic correspondence, not the root-existence argument.

Invalid/nonfinite density/T, overlapping endpoint densities, singular C,
denominator intervals containing zero, nonfinite residual/Jacobian entries,
failed strict inclusion, failed contraction and residual exclusion of zero
are rejected. Stability must have positive finite lower bounds. A quality
interval crossing an endpoint remains unresolved. Failed attempts retain their
reason; computed failed K/J/residual evidence is retained when available.

## Budget and measured cost

Exactly two new solver formulations are used: a parameterized 2D saturation
root and a volume-eliminated 3D mixture root. C2's existing scalar bracket is
reused. Each experimental attempt has a 20-second SIGALRM timeout on this Unix
host. A bounded retry is a rerun after a documented verification expectation/
evidence-output improvement, not a precision or topology expansion. Both initial
and final numerical evidence are retained. No attempt times out and no Arb
precision exceeds 256 bits. The roughly 90-minute planning ceiling is not spent
on broad additional cases once the topology obligation becomes decisive.

The final numerical run takes about 17.73 seconds; independent verification
about 4.34 seconds. Per-case combined validation includes homogeneous bracketing
where applicable, parameterized saturation, mixture proof, stability checks,
entropy comparison where applicable and serialization. At 192 bits its median
is 64.29 ms (18.00–82.19 ms); at 256 bits 64.30 ms (17.41–76.93 ms), 17 attempts
at each precision. Mixture-only work is smaller, so these are not homogeneous
benchmarks. Setup, installation, file preservation, writing/reviewing reports,
global phase proof and any browser costs are excluded. Timings are observational
and host-specific, not real-time guarantees or compiled implementation forecasts.

## Portability and operational limit

No C++ or WASM implementation is built; no new browser replay, worker latency,
memory measurement or physical iPad test occurs. C2's historical browser evidence
is preserved as historical evidence. Native Arb proof success cannot qualify
JavaScript/WASM f64 arithmetic or ordinary browser Math transcendental functions.
A future port needs a validated arithmetic implementation and measured artifact/
compiler/worker behavior. Such a port is not authorized or started here.

No certificate is attached to C1/A2. Nothing changes classification, pressure
support, phase admission, retries, nonlinear residuals, domain stops or rollback.
Any future certificate would have to bind exact inventory, EOS/reference,
arithmetic build, caller/trial lineage and every separate proof gate. The present
method has no complete physical branch proof to attach.
