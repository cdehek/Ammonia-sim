# Pressure lookup work reduction

PASS, detached equivalent counting. `count-*` and `observe-*` builds insert the same source counters without changing arithmetic. Successful engine PH at (4 bar,1700 kJ/kg) retains 38 bisections, 40 branches, 120 mixRows, 160 branch-row reads and 720 mix component reads. Pressure brackets/logs 42 → 3; pressure-axis search comparisons 336 → 24; pressure-axis indexed reads 588 → 42. Branch-only pressure calculations 40 → 1. Total reduction is 39 per eligible call, **92.857%** of all engine-inverse pressure searches, preserving the two original saturation lookups. Wrapper's further saturation work is included in integrated counts.

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


Independent initialization captures are subtracted only after exact initial-state verification. Warm advance: 17,416 PH calls, of which 15,739 vapor calls / 629,560 vapor branch interpolations, all unchanged. Savings are exactly 15,739 × 39 = **613,821** pressure searches/logs and **4,910,568** binary-search comparisons. Overall warm pressure-search reduction is **80.28%**, because saturation and M/U/V recovery still need their own lookups. Cold 210 vapor calls save 8,190 searches.

`property-work-counts.json` and `integrated-work-counts.json` retain every count. `branchRowReads4` / `mixComponentReads6` are site counts multiplied by 4/6, not literal read totals. Only selected reliable source construction sites are counted: bracket arrays drop by 39/call; one holder is added. JIT elimination, allocated bytes and GC causality are unmeasured. Required offset interpolation and thermodynamic table reads stay unchanged.
