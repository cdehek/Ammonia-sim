# Mechanics

`BRACKET_REUSE_DESIGN_AND_OWNERSHIP.md` records the actual pre-change call graph and was committed before implementation. `build.py` uses unique anchors and verifies exact B9C bytes; module-level SHA-256 proves only engine.js/table-only.cjs differ. `ORIGINAL_VS_CANDIDATE_SOURCE_DIFF.md` shows every statement.

`inverse` receives one primitive p and never assigns to it. The original table factory deep-freezes all arrays/rows before construction. A new holder is scoped to one finite numeric vapor PH call. `branch` still locates the offset first, then uses/constructs the exact [pressure index,weight]. Final `statePT` computes original saturation and temperature-offset classification before passing the same holder to vapor branch. All interpolation math, density logs, bisections, comparisons and h overwrite retain order. No bracket escapes or is installed after failure.

Successful vapor PH: initial saturation bracket + first branch bracket + final saturation bracket = 3, versus 42 original. The two saturation calls deliberately remain. PS/liquid/equilibrium/ordinary PT and nonfinite/coercing inputs bypass reuse. Factory default disables it; candidate table-only explicitly enables it after freezing. Direct opt-in with mutable custom data is outside this experiment's supported ownership path. The original default factory preserves mutable-table behavior.

| Advance-only measurement | Cold control → candidate | Warm control → candidate |
|---|---:|---:|
| phCalls | 5,028 → 5,028 | 17,416 → 17,416 |
| branches | 8,400 → 8,400 | 703,306 → 703,306 |
| bisections | 7,980 → 7,980 | 598,082 → 598,082 |
| pressureBrackets | 27,324 → 19,134 | 764,565 → 150,744 |
| pressureLogs | 27,324 → 19,134 | 764,565 → 150,744 |
| pressureComparisons | 218,592 → 153,072 | 6,116,520 → 1,205,952 |
| pressureAxisReads | 382,536 → 267,876 | 10,703,910 → 2,110,416 |
| offsetAxisReads | 106,680 → 106,680 | 8,921,192 → 8,921,192 |
| bracketArrays | 35,724 → 27,534 | 1,467,871 → 854,050 |


Offset-axis reads, four branch table-row read sites and six component reads per mixRow remain unchanged. Construction counts describe source sites, not JIT allocations or byte savings. There is one new holder per eligible call; 39 pressure-bracket array constructions are removed. No thermodynamic work is skipped.

The final public PT export forwards only p/T/kind to the internal helper, preserving arity 3 and ignoring extra public arguments. One wrapper function is constructed per engine. The local holder remains private to PH.
