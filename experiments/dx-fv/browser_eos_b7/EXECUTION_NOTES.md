# Attempts, corrections, bounds and omissions

All EOS source/hash checks pass. Both scientific builds and both diagnostic
increments finish within their explicit deadlines. No EOS equation, input
inventory, scientific budget, domain guard, iteration limit or quality acceptance
condition changes in response to a failure. The following setup/harness incidents
are retained rather than counted as scientific passes.

The full control build retains three upstream warnings: two captured-structured-
binding C++20-extension warnings in SBTL under the original C++17 settings, and
the existing miniz large-file I/O pragma. The source and flags are not changed to
silence them. Incremental builds emit no further warnings. See
`evidence/build-warning-index.json` and the complete logs.

1. The empty-workspace clone first ran in the default network sandbox, which
   could not reach the proxy. Explicit network access succeeded. The exact clean
   B6 HEAD was then verified before creating B7. No pre-existing checkout was
   discarded.
2. The original dependency CMake configuration reached its 240-second deadline
   while fetching sources/submodules. A separate unchanged 240-second continuation
   completed. Both logs are retained. A separately attempted shallow JSON clone
   is retained in setup logs but is **not** selected as a build dependency. The
   actual nine selected dependency trees all match the inherited digests/pins.
3. Playwright reported host-library requirements. Six isolated Debian package
   downloads match the preserved B4A SHA256 values and are extracted into the
   external sysroot. The preserved WPE-launcher pattern works without changing host
   packages. Actual Chromium and WPE WebKit launch checks succeed.
4. The isolated mpmath 1.4.1 install reports the host SymPy version's incompatible
   preference. SymPy is not used. The reference evaluator uses the pinned isolated
   mpmath, exact binary64 coefficients and unchanged code; 65/90-digit independent
   roots pass. No host mathematical package is substituted into the calculation.
5. The first canonical-provenance extractor incorrectly assigned historical B4B
   inventories the later B4C originating PH state. It stopped at `native-ledger-1`.
   The corrected extractor follows each preserved record's actual B4B origin and
   A/C inventory identity, including independently resolved A states. It then
   reproduces all 250 original M/U/V/rho/u bits. Original inputs were never changed
   or regenerated. This was not an EOS source-hash verification failure.
6. The first ABI browser harness copied its options object while the B6 observer
   installed `runtimeStatus` on the copy. It failed before its test sequence.
   `abi-chromium.json` and `abi-webkit.json` retain that TypeError. Keeping the
   original options object fixes the harness; `abi-*-corrected.json` completes the
   actual ownership audit. No exception-cleanup algorithm changes.
7. The first complete Chromium lifecycle execution could not serialize deliberately
   nonfinite synthetic requests with strict JSON. Its Python traceback remains in
   `logs/lifecycle-browser.log`. The runner now records nonfinite observations as
   explicit `nonfiniteBinary64` tags **after execution**. It still actually submits
   NaN/Infinity to the original validation tests. `lifecycle-*-serialized.json`
   retains successful complete reruns. Finite scientific inputs are unaffected.
8. The first supplemental explicit-pressure guard test converted the adjacent Pa
   value `29999.999999999996` to bar; that division rounds to exactly 0.3. It was
   therefore an incorrect test of an outward input to the bar-based adapter. The
   original error receipts remain `c1-*.json`. Corrected supplemental inputs are
   actual outward bar ULPs `.29999999999999993` and `35.00000000000001`;
   `c1-*-explicit-bar.json` refuses them. None of the seven saved inventories or
   their calls was altered, and no runtime pressure rounding/epsilon was added.
9. The first support-attribution lookup expected a separate C2 proof key for each
   WebKit identity. C2 stores a shared exact-bit proof under the Chromium key.
   Lookup now requires an exact match of all saved input bits and records the
   proof source key while retaining both browser record identities. No scientific
   outcome is deduplicated or promoted into a physical certificate.
10. A final metadata-collection command omitted the isolated PYTHONPATH and could
    not locate installed CoolProp metadata. The collected logs/source hashes were
    intact; the delivered collection script uses the documented isolated path and
    completes tool/runtime identity capture. This involved no property execution.
11. The first additional native/shared auditor demanded identical phase labels
    even at original unresolved endpoint controls. It stopped at
    `PS-30298.937123458254-hf`: native reports Q=0/two-phase while the browser
    reports its historical homogeneous-liquid label. The actual browser values
    match archived B4C exactly. The final auditor retains all eleven such endpoint
    identities and 44 duplicated cross-runtime comparisons without issuing phase
    certificates; resolved controls still require phase agreement and all numeric
    limits remain unchanged. Full-VLE controls and the three resolved Gate A
    liquids have no such phase mismatch. The initial failure log and successful
    endpoint-aware comparison log are both retained. No runtime fixture filter,
    source edit, quality adjustment or solver-acceptance change follows.
12. The final all-return quality predicate exposes invalid **raw DP** endpoint
    diagnostics. This is a retained failed physical-admissibility result, not a
    serialization or tolerance issue. The strict census refuses 44 comparisons
    representing 11 path/input identities, identical in control/candidate. Eight
    full-VLE DP cases reproduce preserved native invalid Q values; three default
    browser DP cases differ from native endpoint rounding. No invalid raw DP
    result is accepted scientifically or consumed by A2. DP physical qualification
    remains **FAIL / NOT QUALIFIED**, separately from the focused three-liquid DU
    success. `quality-disposition.json` contains every failed quality predicate
    and source/native comparison. No clamp, guard change or new DP repair is made.

Full builds: 900-second deadline, at most two compiler jobs; diagnostic increments:
300 seconds. Each browser campaign has a 180-second outer deadline, selection
checks 60 seconds, worker jobs a 120-second internal deadline, and native/property
audits 120 or 180 seconds as shown in BUILD.md. The successful lifecycle campaign
finishes within its bound. Performance runs with no concurrent compiler or property
campaign; five rounds and actual raw outcomes are retained. Native fresh/extra
verification finishes separately, not concurrently with timing.

Omissions are deliberate scope limits: no Gate B functional patch, C3/global EOS
topology proof, new pressure certificate, full accepted A2 campaign, broad fluid/
critical-region qualification, arbitrary raw-module exception safety proof,
long-duration/leak proof, physical Safari/iPadOS/device test, merge, deployment,
UI/Live Plant work or production integration. No failed or omitted scientific
state is reclassified as a physical success. `evidence/acceptance.json` lists all
remaining qualification blockers. Stop for engineering review.
