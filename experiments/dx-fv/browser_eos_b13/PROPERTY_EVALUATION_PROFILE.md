# Original-table property workload

No EOS substitution, new thermodynamics or table adjustment is used. Counts/times below exclude initialization and include six advance calls plus their records. They come from one observed replay per fixture; all canonical science/attempt hashes match.

| Fixture | PH calls | M/U/V recovery calls | Public sat calls | PH ms | Recovery ms | Sat ms | Public property share |
|---|---|---|---|---|---|---|---|
| cold | 5028 | 795 | 6483 | 21.18 | 6.894 | 6.946 | 19.29% |
| warm | 17416 | 2325 | 21621 | 475.6 | 55.13 | 25.66 | 57% |

Lexical counts cold/warm: saturation 18,924 / 61,259; inverse 5,028 / 17,416; branch interpolation 8,400 / 703,306. These are nested internal counts, not extra public calls. Warm PH inversion repeatedly traverses the original vapor table's iterative inverse; average branch work is much higher than in the wet cold fixture. Lexical counts support attribution, while public timing establishes measured cost. Recovery also includes nested inverse work and is not free.

| Fixture | Section requests | Section hits / misses | Boundary requests | Boundary hits / misses |
|---|---|---|---|---|
| cold | 26360 | 22373 / 3987 | 10760 | 10340 / 420 |
| warm | 96900 | 82461 / 14439 | 39384 | 38148 / 1236 |

Stage-local section caching already avoids many repeated PH evaluations during unchanged-coordinate probes. B9C exact-input boundary caching also avoids most boundary requests. Boundary misses outside implicit stages include required original trial/record evaluations; hit percentages are not a proposal to cache across changed inputs or stages. No failed public property call was observed in either normal probe. Warm phase transition remains supported by the original table in this experiment.

Thermodynamics is a major warm cost (about 57% of observed wall time); it is only about 19% cold. Therefore “property evaluation alone limits all simulation” is not supported. PH timing includes wrappers and runtime effects; repeated fresh production/browser measurements are required before quantifying an optimization opportunity. Replacing inverse results or changing stopping criteria could change science and is not authorized.
