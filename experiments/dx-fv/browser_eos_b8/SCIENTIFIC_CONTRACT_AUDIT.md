# Original scientific contract audit

B8 makes no functional source change. Historical byte identity, Git-verified accepted snapshots, unchanged C1 patch, B6 loader and B7 artifact seals are the preservation proof. This audit preserves requirements; it does not independently requalify the complete EOS/model from a short trace.

| Contract | Unchanged requirement | Evidence / scope |
|---|---|---|
| Canonical property recovery | Δp ≤0.1 Pa, Δh ≤0.1 J/kg, ΔT ≤1e-4 K | Original B5A/B7 science audits retained. Raw return alone is not acceptance. Accepted stage also retains its original bar/kJ PH-versus-MVU checks. |
| Normalized fluid mass/energy residual | ≤1e-11 | Exact accepted Newton source and original signed FD rules preserved. New trace retains original converged-stage and final record values. |
| Standalone comparison | Pressure **strictly <10 Pa**, h **strictly <50 J/kg**, T **strictly <0.01 K** | No replacement tolerance, endpoint exemption or “close enough” rule. |
| Independent scientific reference | Pressure 1e-5 Pa, energy 1e-8 J/kg resolution | Four endpoint phase decisions remain unresolved; 65/90-digit same-EOS diagnostics are not substitute physical qualification. |
| Domain | Upper 35 bar absolute, lower 0.3 bar absolute; original temperature/property support | Strict adapter comparisons unchanged. No pressure correction/rounding certificate/epsilon added. Original 195.495 K floor, 30 K subcool / 250 K superheat support retained; finite thermal nodes 200–400 K. |
| Conserved inventory | Exact original M/U/V arithmetic and operation order | `conservation.cjs:3`, `thermodynamics.cjs:12`, adapter stateMVU; all original bit identities retained. Exact rational MUV distinguished from rounded DU. |
| Conservation | Section/aggregate mass <1e-8 kg; section/fluid/node/combined required energy <1e-6 kJ | Accepted ledgers unchanged. C1 subset and B8 short trace meet applicable original checks; no invented latent-liquid reservoir or ledger correction. |
| Thermal | Finite tube/fin/air accounting; nonlinear thermal closure ≤1e-12 K | Accepted physical capacities, links and exact/FD options unchanged. No conductance calibration or new phase/heat-transfer algorithm. |
| Numerical method | Signed FD, original epsilon/shrink/sign/branch rules, Newton 30 iterations, original line search, TR-BDF2 coarse/two-half-step and temporal acceptance | Sources byte-identical. Default versus opt-in A1/A2 modes remain distinct. No tolerance/step growth change. |
| Failure / rollback | dt/2; minimum step 1e-9 s; exact accepted rollback; detached two-half commit; stop freeze | Existing C1 20-attempt/19-halving evidence reused; no full campaign. Synthetic error transport is explicitly labeled. |
| Phase / wet suction | Original admissibility, signed physical phase events, original x/phase wet logic | Invalid equilibrium Q is refused scientifically. Homogeneous Q=10000 is labeled sentinel. No forced phase/dry-vapor substitution; A2 port diagnostic is not a compressor-protection certificate. |
| Physical stop | Independent domain-stop proof; unproved property error cannot create a physical trajectory exit | C1 B/C solver classification preserved; genuine thermal outward-direction checks retained; exact refrigerant boundary proof remains absent. |

At rounded DU, C2's seven historical refusals are two mathematical inside / five outside. At exact rational M/U/V, one inside / six outside. These are distinct saved mathematical questions. The two inward hazards, complete phase/topology certification and independent physical trajectory-exit proof remain unresolved. A returned pressure within support is not a certificate.

B8 writes no EOS patch, algorithm, new acceptance path or accepted A2 edit. No quality clipping, density snap, energy substitution, preferred phase, boundary correction or changed scientific budget occurs. All invalid DP states remain scientifically refused; table DP-like internal computation is distinguished from raw CoolProp DP without excusing the latter.
