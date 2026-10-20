# B14-A0 — Phase-boundary temporal error and Jacobian cost

**B14-A0 PHASE/JACOBIAN DIAGNOSTIC PASS** — diagnostic research only, ready for engineering review. No optimization was implemented.

Baseline `eddb2e7add904238162ead68ef9e2c1b8874f04d`; branch `research/b14-phase-jacobian-diagnostics-20261019`. First design checkpoint `12dae83` preceded instrumentation. The final delivery SHA is the branch tip containing this report (`git rev-parse HEAD`) and is supplied in the delivery message; a commit cannot embed its own hash.

The original warm event is **superheated vapor → liquid + vapor**, cooling direction. The request's opposite direction is contradicted by the pinned original trace. Actual accepted bracket: **0.0053591276016748427–0.0053820385212110817 s**, width 22.911 µs. Event 0.0053754278169825922 s is interpolated, not root-solved.

The unchanged temporal estimator is a maximum over **31 scalar checks**, derived from 21 nonlinear coordinates. Extra trials reflect refrigerant inventory/pressure dynamics near a constitutive slope change and subsequent internal flow reversal; thermal errors do not lead. All original normal-fixture Newton solves converged with unit line searches and first positive derivatives. Original schedules reproduce B13 bit exactly through **0.01 s**; scientific qualification remains **0.001 s**.

Thermal Jacobian columns make zero PH calls because the existing stage cache works. Warm public PH calls: 17,416; 15,739 vapor calls each perform 38 bisections and 40 branch interpolations. The next proposed experiment is **exact pressure-bracket reuse inside a single vapor PH inversion**, with no cross-call cache and exact-or-reject gates. It is a proposal only.

Read [ENGINEERING_REPORT.md](ENGINEERING_REPORT.md), [MECHANICS_REPORT.md](MECHANICS_REPORT.md), and [NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md](NEXT_CONTROLLED_EXPERIMENT_PROPOSAL.md). Detailed source, phase, estimator, scheduling, column, residual, PH, conservation, equivalence and limitations reports accompany machine-readable evidence.

## Reproduce and verify

From repository root:

```sh
python3 experiments/dx-fv/browser_eos_b14/audit.py
python3 experiments/dx-fv/browser_eos_b14/verify-protected.py
python3 experiments/dx-fv/browser_eos_b14/validate.py
# Optional fresh bounded replay, all outputs inside B14/.runtime, one process at a time:
python3 experiments/dx-fv/browser_eos_b14/campaign.py --repeats 1
# Three timing samples per original fixture require --repeats 3.
```

Node built-ins and Python standard library suffice for solves/audits; Matplotlib is required only for `plot.py`. `run.py --help` exposes individual bounded cases and refuses to overwrite receipts. `contracts.py` replays the separate domain witness and also refuses overwrite. Default outputs already exist; use a new B14 directory for replay (campaign handles this). No historical scripts that regenerate receipts are executed.

`receipts.mjs` resolves exact content references introduced by `compact.py`; repeated vectors are deduplicated only after exact verification. Canonical original/schedule traces and first observed detailed diagnostic vectors remain retained. `receipt-compaction.json` records transformations. Counts are stronger evidence than heavily instrumented submillisecond timings. No browser/Worker/Cloudflare testing or deployment occurred.
