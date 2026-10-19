# Source identity and minimal-diff review

PASS. Gate 0 hashes all 2,791 historical tracked files; fourteen accepted source
bodies match exact A2 Git objects. Later root coupled-model/Newton are excluded.
Control-bundle contains unchanged source bodies. Candidate changes only the
B9C-owned isolated/coupled-model.cjs and adds a table-only ownership wrapper.
No original accepted snapshot, property source, solver, UI, Live Plant or hosting
file is edited. The prototype is not a replacement accepted A2 implementation.

BOUNDARY_PH_PROTOTYPE.patch is the complete functional source diff. It adds the
owned-engine guard, optional private evaluate callback, two stage-local slots,
Object.is exact checks, lazy original thermo.ph, residual-exception clear and one
endpoint plumbing argument. All original arithmetic expressions and evaluation
order remain. verify-source.py independently removes ONLY these declared changes
and restores the exact accepted bytes, then verifies the other thirteen bodies.
table-only.cjs recursively freezes the actual private table and freezes/weakly
registers engines. This guard excludes injected/mutable/experimental engines.

prototype-source-manifest.json identifies all source bodies and four generated
bundles. diagnostic-{control,candidate}.patch shows the separate observations;
none enters primary timing. Runtime receipts identify browser engines/launchers;
final runtime-manifest.json additionally hashes installed browser binaries and
all delivered research sources. Original saved B9/B9A/B9B/C1/B6/B7 artifacts are
Git-verified, not rebuilt or requalified. The final preservation receipt checks
every historical file, full starting remote map and PR #3 identities/metadata.
