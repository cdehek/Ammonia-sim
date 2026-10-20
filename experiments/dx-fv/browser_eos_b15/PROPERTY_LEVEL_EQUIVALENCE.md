# Property equivalence

PASS: 60,274 comparisons across 963 pressure positions and 206 original cold/warm/transition states. Every pressure knot, its immediately adjacent representable pressures, interval geometric midpoint and support endpoints is tested. Enthalpies cover hf/hg ±1e-8 band and adjacent representable values, equilibrium, near-zero/moderate/high superheat, and upper support edge. Original PT/PS/PX paths are also compared.

`property-tests.mjs` compares all returned fields/order with binary64 encodings, including p/T/h/s/rho/quality/phase and wrapper superheat/wet fields. Undefined/null and signed zero stay distinct. Engine PH does not return u; full model M/U/V and recovered u are covered by coupled tests. Error comparisons include constructor/type, message and every own field except runtime stack; coercion traces test deterministic failure order. No fabricated finite success replaces original invalid results.

Full exact receipts: `evidence/property-binary64.json.gz`; summary/hash: `property-summary.json`. Run `property-node.mjs` to regenerate B15 receipts. Chromium repeats the browser-compatible suite (without Node-loaded historical extras), retained in `browser-properties.json`. A finite deterministic corpus complements the immutable-table/same-arithmetic argument; it is not an exhaustive proof over every binary64 input.

Final interface regression: 18 extra-argument comparisons and public arity 3 pass. Preliminary v1 exposed the fourth internal PT parameter to callers; a forged holder changed its PT result. `interface-regression.json.gz` retains original/v1/corrected binary64 outputs and root cause. The final public entry forwards only the original three parameters. Browser repeats this counterexample/fix. No failing comparison was removed.
