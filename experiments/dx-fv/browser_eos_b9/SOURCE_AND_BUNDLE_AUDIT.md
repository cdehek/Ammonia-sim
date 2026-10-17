# Source and browser package audit

Accepted A2 is `be9eb35a4ddf5098e685182f8104685127c6a6ee`, not later root research
model files. Gate 0 verifies all fourteen scientific files directly against Git.
`evidence/source-bundle-manifest.json` lists original paths, exact snapshot paths,
SHA256, byte lengths and all nineteen relative import edges. The twelve accepted
CommonJS snapshots are consumed from `browser_eos_backend/accepted/`; engine.js
and properties.json are original root files verified byte-for-byte against A2.

`build.py` generates `accepted-bundle.mjs` with literal unchanged function bodies.
Only a function(module,exports,require) boundary is added. The resolver strips
one `./`, admits exact manifest names, caches before evaluation and throws for
unresolved imports. No extension guessing, Node built-in, browser shim, dependency
replacement, minification, transpilation or numerical rewrite occurs. The original
UMD engine chooses its existing CommonJS export path. Original property JSON text
is supplied to JSON.parse once per loader instance, retaining Number parsing and
operation order. There is no network-dependent scientific fallback.

Both main control and dedicated worker dynamically import the SAME generated
package and call the SAME service. The main page does not import the accepted
package in worker mode. Package creation does not execute physics in the page.
Worker code uses no DOM API. Table operation uses no WASM, CoolProp or DP.

`node-baseline.mjs` compares direct original CommonJS require with the literal
browser package for both frozen fixtures, all checkpoint records, complete final
state and observer attempts. Every binary64 value agrees exactly. Actual browser
main versus worker tests separately compare complete state, records, attempts,
FD/line-search events and public property call counts. Timed runs recheck every
state/record hash against their own engine's frozen parity evidence. No JSON
roundtrip is used in scientific messaging. Evidence JSON uses explicit f64 bit
strings for exact scientific comparisons; plain JSON estimates are size-only.

`c1-bundle.mjs` contains exact unchanged C1 source strings and the unchanged B6
`a2-subset.cjs`. Its original harness uses new Function with a local CommonJS
resolver and wraps Newton only to inject explicitly synthetic faults. B9 adds
separate exact-bit/identity checks without editing C1. This is an error-handling
experiment, separate from the accepted table baseline.

Optional B7 uses unchanged `loadQualifiedEOS`, verified Gate A JS/WASM identities,
original default/full-VLE configuration machinery and unchanged C1 adapter.
No generated ABI transform, EOS rebuild or source patch occurs. Scientific
artifact: WASM `2af8363686c402d6dcd9775355e829a5f3257de56372f290c66ed9285db8db45`;
JS `ebd02f5721abc10fee3e6560b0d96c1a17b8ae1f01bc144a4f9a1af8cf1e3217`.
Raw evaluation exposes no phase field; B9 reads the existing phase getter only
after a completed successful update, matching B7 matrix.mjs. Rejected updates
never supply a state. Only immutable pointer-free exception observations leave
the worker; native headers/addresses and raw ABI event arguments stay inside.

The pre-implementation design is commit `81e43e4`. Later measurement refinements
add phase time spans, minimal DOM snapshot rendering, disposal reference release
and timed-run hash verification. They do not change the frozen scientific work,
fixtures, reporting cadence, numerical options or package bytes. Superseded and
failed harness attempts are retained and documented in EXECUTION_NOTES.md.
