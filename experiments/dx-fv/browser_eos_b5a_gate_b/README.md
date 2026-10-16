# B5A Gate B diagnostic research

**CONDITIONALLY FEASIBLE. Backend qualification remains incomplete.**

- [Engineering findings and case-specific A/B/C conclusions](ENGINEERING_REPORT.md)
- [Fixed-inventory equilibrium equations and admissibility](FORMULATION.md)
- [Candidate comparison and future acceptance gates](STRATEGIES.md)
- [Every bounded neighboring-state result](NEIGHBORS.md)
- [🔧 Ammonia Lab — The Mechanic’s Report](MECHANICS_REPORT.md)
- [Reproduction instructions](REPRODUCE.md)

Starting point: exact B5A `cc2ec6b54d40cabea93fa761d10a2ecab59def25`.
Only additions in this directory are authorized. Scripts are standalone
diagnostics; their properties never enter the accepted solver/backend.
Original evidence, source patches, numerical contracts, loader/support policy,
production, UI and Live Plant remain unchanged. No merge or deployment.

Machine-readable evidence:

| File in `evidence/` | Role |
|---|---|
| checkpoint, starting-file-hashes, refs-before, start-audit | Exact start, historical integrity, remote refs, inherited source/artifact/A2 checks |
| fixed-inputs, cases | Seven saved inventories decoded from bits and 40 explicitly modified neighbors |
| native-results, native-trace-results, native-trace.jsonl | New seven-case uninstrumented/instrumented native reproduction |
| four-case-reproduction-and-controls | Internal molar bits, saturation/Brent/phase events, errors/returns, fresh DT audits, homogeneous candidates |
| mathematical-references, seed-sensitivity | 65/90-digit exact-EOS roots, stability, residuals, original inventory and displaced seeds |
| binary64-results, binary64-repeat | 282 attempted solves with all iterations, stop reasons, residuals, admissibility and timing; separate-process determinism |
| coordinate-grid, temperature-brackets | Adjacent state-coordinate and physical saturation-bracket evidence |
| native-neighbors | All 47 raw native fresh/reused outcomes, including 13 exceptions |
| supplement | Fresh EOS audits of refused extrapolations, repeatability, wheel hashes, setup/correction notes |
| scientific-audit | Per-case classification, precision convergence, independently reevaluated equations, matrix summary and timings |
| final-preservation, refs-before-commit, evidence-sha256 | Historical/source/remote preservation and evidence manifest at commit preparation |

The initial scaled-coordinate grid is retained as
`coordinate-grid-initial-scaled-roundtrip.json`. Use corrected `coordinate-grid.json`
for direct adjacent-coordinate interpretation. No failed case is removed.

The exact research delivery SHA is the commit containing this package
(`git rev-parse HEAD`) and the final delivery response. Stop for engineering
review and explicit approval before functional Gate B work.
