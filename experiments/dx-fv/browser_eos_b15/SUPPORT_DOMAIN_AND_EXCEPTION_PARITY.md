# Support domain and exceptions

PASS for direct-engine and original thermodynamics-wrapper contracts separately. Tests include nonfinite, undefined/null, booleans, strings, objects/arrays/functions, Symbols/BigInts, signed zeros, negative/out-of-range pressures, extreme enthalpies, exact support boundaries, liquid missing regions, malformed frozen table rows, invalid quality and unsupported phase requests. Original own error metadata and coercion event ordering match; stack locations are runtime diagnostic detail and excluded.

The wrapper checks finite inputs and 0.3–35 bar before PH. The raw historical engine has weaker validation: some NaN/type inputs can return nonphysical/NaN objects. B15 preserves these quirks exactly and does not relabel them validated physical states. No support-band or error-message cleanup is included.

Pressure positivity/log-domain failure remains in initial saturation. Offset checks remain before branch pressure work. Excess enthalpy refusal remains after first branch support interpolation. The local holder is never reached on earlier failures and is discarded on later exceptions. Genuine model update rollback and thermal-domain failures, and actual C1 wrapper metadata, are retained in `regressions.json.gz`; all compare exactly. C1 synthetic fault injection is labeled synthetic and is not natural trajectory evidence.

Final interface regression: 18 extra-argument comparisons and public arity 3 pass. Preliminary v1 exposed the fourth internal PT parameter to callers; a forged holder changed its PT result. `interface-regression.json.gz` retains original/v1/corrected binary64 outputs and root cause. The final public entry forwards only the original three parameters. Browser repeats this counterexample/fix. No failing comparison was removed.
