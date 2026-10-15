# B1 precision-controlled browser EOS experiment

Research only. No production integration, deployment or solver-budget change.
Start: `7736625b3de8e901f4a305a16ffeb16aa27d3de4`.
Branch: `research/browser-eos-precision-backend-20261015`.

The original research directories and all starting files are immutable. New
measurements go to this directory's `evidence/`; historical evidence remains in
`../browser_eos_precision/evidence/` and is explicitly identified as historical.

**PROMISING: precision improves, with additional scientific qualification required.**

- [Engineering report](ENGINEERING_REPORT.md): precision, independent residuals,
  derivatives, 30 coupled operating runs, temporal/conservation audits and costs.
- [🔧 The Mechanic’s Report](MECHANICS_REPORT.md): plain-English findings.
- [Build/source/patch reproduction](BUILD.md) and [accepted solver contract](SOLVER_CONTRACT.md).
- [Physical iPad instructions](IPAD_TEST_INSTRUCTIONS.md); no physical iPad result.
- [Boundary/scientific audit](evidence/audit.json), [build provenance](evidence/build-provenance.json),
  [coupled summary](evidence/coupled-summary.json) and [runtime summary](evidence/performance-summary.json).

The preserved derivative ratio changes from 20.1904555 to 0.999959589 in both
engines. Original 30-bit source and official 8.0 measurements agree exactly;
the patched build repeats byte-for-byte after a full recompilation. Synthetic
closures pass 16/16 per engine and the five operating fixtures complete at all
three unchanged accuracy regimes. A near-saturation vapor caloric residual,
full A2 verification and actual iPad testing remain unresolved qualification work.

Experimental binaries have distinct directory names; their embedded upstream
version alone does not identify the precision patch. Full raw evidence is retained
under `evidence/`. Stop for engineering review; no merge, application integration
or publication is performed.
