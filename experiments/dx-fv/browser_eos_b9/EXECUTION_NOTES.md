# Execution notes and scope limits

All failed/superseded receipts are retained; none changes a scientific result.

1. Workspace initially had no checkout. First clone without sandbox network access
   failed connecting to the configured proxy. Repeating with the supported network
   permission succeeded. Clean detached B8 HEAD was verified before branch creation.
   No network policy or proxy was bypassed/changed.
2. Browser setup downloaded Playwright's Chromium/WebKit and six previously pinned
   Debian packages to `/workspace/b9-runtime`. Dependencies were extracted locally;
   no host package install. Exact six package hashes, launcher and browser binary
   identities are recorded. Desktop WPE WebKit is not physical Safari/iPad.
3. Initial parity automation completed browser numerical comparisons but its
   object-by-object Playwright transport spent excessive time serializing the full
   diagnostic graph. That process was explicitly terminated before its 180-s bound;
   no scientific mismatch was observed or replaced. Corrected evidence exports a
   JSON string AFTER exact f64 tagging and in-browser comparisons. Scientific
   main/worker messages remain structured clone. `parity-*-serialized.json.gz` passes.
4. C1 diagnostic transport was started while the first large parity receipt was
   still being exported. Both table comparisons had executed; this was sequencing
   overlap in evidence collection, not permission to run downstream performance
   on a failed baseline. All timing campaigns started only after BOTH actual
   browser parity receipts passed. No physics campaigns overlap during timings.
5. Initial lifecycle test simulated a late response by incrementing the test
   client's sequence without sending it to the owner. Subsequent dispose correctly
   refused the gap. Corrected test restores that test-only counter; real sequencing
   logic/solver did not need relaxation. Failed `lifecycle-chromium.json.gz` and
   passing corrected/concurrent/final results are retained.
6. Initial heartbeat samples labeled phases at callback time, misattributing
   synchronous main-thread blocking to a later phase. Phase spans were added;
   corrected summaries assign largest time overlap. Preliminary and phase-span
   samples remain. Disposal was tightened to clear cached snapshot references;
   concurrent duplicate requests coalesce in the client. Lifecycle tests pass.
7. Final timing adds actual minimal DOM snapshot rendering and per-run exact
   scientific baseline hashes. Use ONLY `benchmark-*-rendered.json.gz` for headline
   tables. Earlier benchmark, phase-spans and final-tag samples are superseded,
   not pooled to obtain favorable numbers. Frozen scientific work never changed.
8. Optional B7 initially asserted a phase field that evaluate does not return.
   The original loader instead exposes its existing phase getter (as used by B7
   matrix.mjs). B9 reads that getter only after successful updates. The original
   raw values/artifacts/loader/guards are unchanged. The failed initial receipt
   remains; `b7-*-phase-getter.json.gz` passes in both engines.
9. B7 native observational callbacks expose raw ABI details locally. B9 serializes
   only whitelisted count/catch outcomes and stack DELTA; no native pointer/header,
   callback args, module/state handles or live Error crosses the worker boundary.
10. Frame summaries omit the first RAF timestamp per session because it is not an
    interval between two callbacks; the raw data retains it, including one negative
    startup sample. All later large frame delays remain. Some coarse cross-realm
    one-way estimates are slightly negative; they are retained and qualified.
11. Memory samples use current summed browser-child RSS, which double-counts shared
    pages, plus available coarse page heap. No unique worker heap or forced GC is
    measured. High-water growth is not called a leak or proof of leak freedom.
12. Short frozen trajectories contain no natural phase/boundary events. Empty
    lists compare exactly; original event source and C1 accepted-history rollback
    are preserved. No full event, long-duration or EOS-backed A2 campaign occurs.

Per-command client deadlines are 30 s; diagnostic probes 90 s. Browser launches/
navigation are 30 s. Source/build checks 15–120 s; scientific browser processes
120–240 s; matched benchmark processes 180–300 s. Shell/automation logs preserve
actual failures. No timeout changes any scientific acceptance setting or input.

13. Final bounded-cache review found that an exhausted cache could refuse before
    consuming the client's valid sequence, preventing a following dispose. B9
    consumes that refusal's sequence and tests 256 cached refusals, exhaustion and
    successful disposal. Eight-pending backpressure and concurrent duplicate
    advances also pass. This is a protocol-only boundary correction; normal
    measured sessions never reach the cap, and the scientific/timed path is unchanged.

Delivery records include a committed post-first-push preservation receipt and a
final separate postpush receipt. The final receipt cannot be embedded in the
commit whose SHA it checks without changing that SHA; its separate location is
reported at delivery. Both pushes target only the authorized B9 branch.

14. Final display review additionally guards monotonic command sequence for equal
    accepted-state versions, so a delayed snapshot cannot replace newer stop/fault
    metadata when no physical step committed. Both actual browsers pass the
    deterministic stale equal-version case. A sealed-harness matched matrix is
    then collected against `timed-harness-source-manifest.json`. Headline evidence
    is now `benchmark-*-sealed.json.gz`; rendered-tag receipts remain superseded.
