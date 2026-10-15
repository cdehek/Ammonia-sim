# Preserved native research binaries

The four `.so.xz` archives preserve Linux x86_64 shared libraries for the pinned
unmodified 30-bit source, the exact historical B1 44-bit variant, and each one's
diagnostic instrumentation variant. They are inputs to native diagnostic
reproduction, with no product/backend integration. Decompress to an external
directory and use `native.py` or `trace-probes.py --library ...`.

Uncompressed and compressed SHA256 values are in
[native-binaries.json](../evidence/native-binaries.json). `B3_TRACE=1` enables
stderr JSONL logging only in the diagnostic variants. Both variants still report
the upstream version: identify them by provenance and hashes.

CoolProp is MIT licensed. Source is pinned at
[ae81610e7d23efc57f9d051c8e70a4d66e87537f](https://github.com/CoolProp/CoolProp/tree/ae81610e7d23efc57f9d051c8e70a4d66e87537f).
The exact B3 diffs and B1 historical patch are preserved in this repository.
All applicable dependency notices, upstream source/archive links and licenses
are preserved in [B1 third-party notices](../../browser_eos_backend/vendor/THIRD_PARTY.md)
and its notice files. Eigen and the other dependency sources are unmodified.
Their resolved commits, archive pins and content digests are in the B1 and B3
provenance records. These archives do not assert a cross-platform bitwise build.
