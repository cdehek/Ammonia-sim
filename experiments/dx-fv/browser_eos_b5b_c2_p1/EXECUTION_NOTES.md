# Preserved execution incidents, failures and unresolved work

1. The initial ordinary clone could not reach the configured session proxy.
   Retrying with the supported per-command network capability succeeded. No
   credential values were read or printed and no proxy bypass was used.
2. The exact clean checkpoint had no local python-flint installation. The same
   pinned 0.8.0 wheel as C2 was installed in `/tmp/p1-venv`; FLINT reports 3.3.1.
   This was an arithmetic dependency installation, not a CoolProp build.
3. The inherited identity audit initially stopped because a single-branch clone
   lacked the unrelated UI commit object. Fetching that exact GitHub object
   read-only allowed the full audit: 143 artifacts, five patch hashes and 12
   accepted A2 snapshots pass. No protected branch/ref moved.
4. C2 local proofs reproduced before P1 numerical extension. All 17 focused
   diagnostic cases subsequently completed at both diagnostic precisions and
   seeds. No failed diagnostic case was removed.
5. An initial verification assertion expected independently rounded 256-bit
   Arb boxes to nest inside 192-bit boxes. It failed. Arb's fixed-size radius
   representation can give equal or slightly shifted hull radii around slightly
   shifted midpoints, so nesting is not a valid generic expectation. The failed
   traceback is retained in `evidence/initial-run/failed-verification-nesting.log`.
   The revised audit revalidates each exact original rational box at 256 bits,
   with its original parameter interval; all 33 pass. Independent hull nesting
   results remain recorded, including 22 nonnested pressure hulls.
6. The initial run and successful revised audit were moved intact to
   `evidence/initial-run/`. Final code adds explicit cp/compressibility checks,
   fresh-output selection, and detailed evidence on failed inclusion proposals.
   The final 17-case run and independent audit are retained separately at the
   evidence root, bound to their prototype hashes. This rerun adds no formulation
   and uses no higher validated precision. Timings differ normally by run.
7. Expected negative proposals fail numerically for non-enclosing root box,
   singular preconditioner, equal-density root, negative density, zero/nonfinite
   T, inadequate full parameter coverage and a bad seed. Their reasons and,
   where computed, failed residual/J/K enclosures are retained in attempts and
   verification JSON. These failures are not physical unsupported-state claims.
8. Algebraic roots with Q<0 or Q>1 are retained as successfully enclosed roots
   with inadmissible quality. A deliberately wide validated endpoint box has
   unresolved quality sign and is withheld. No clipping or exact-endpoint claim.
9. An `apply_patch` documentation command initially failed validation because a
   new-file line lacked its patch prefix. It made no file changes and was
   corrected; no numerical evidence or historical file was affected.

Essential unresolved obligation: no complete bounded convex-envelope or
entropy-maximum proof excludes every relevant competing state for the primary
inventories. Expected ammonia topology remains diagnostic category C, with no
externally justified category B theorem imported. The positive controls have
validated local results but not full stable-equilibrium qualification. No exact
endpoint equality is established; Gate B independent-reference issues remain.

No recursive topology work, critical-region analysis, CoolProp/WASM compilation,
runtime integration, production/UI/Live Plant change or deployment was attempted.
Numerical work stops with partial results under the two-formulation budget.
The remaining proof is not declared impossible. Recommend parking certification
pending independent mathematical scope/review, and separately prioritizing the
rejected-PT loader repair under new authorization. Stop for engineering review.
