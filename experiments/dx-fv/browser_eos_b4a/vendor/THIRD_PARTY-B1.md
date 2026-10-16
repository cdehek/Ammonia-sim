# Experimental B1 assets and required notices

`build30` and `build44` are separately identified local research builds, not
official CoolProp downloads. Both use CoolProp 8.0.0 source commit
`ae81610e7d23efc57f9d051c8e70a4d66e87537f` and Emscripten 4.0.12. `build44`
contains the exact `../flash-44.patch`. Embedded version/revision strings remain
upstream strings; use `../evidence/build-provenance.json` and artifact hashes.

CoolProp is MIT licensed. Each build carries its license. Retain all copyright
and permission notices on redistribution. This experiment does not alter the
ammonia HEOS formulation, coefficients, reference convention or fluid data.
There is no proprietary REFPROP library or licensed property service.

Dependency source revisions and content digests are in the build provenance;
archive URLs/hashes are in `../source/upstream-dependencies.cmake`. Unmodified
Eigen 5.0.1 is MPL 2.0: keep its covered source available at
https://gitlab.com/libeigen/eigen/-/archive/5.0.1/eigen-5.0.1.tar.gz
(SHA256 `e9c326dc8c05cd1e044c71f30f1b2e34a6161a3b6ecf445d56b53ff1669e3dec`).
No Eigen file is modified. The original and modified CoolProp flash source and
patch are supplied under `../source/` and `../flash-44.patch`; the complete
unmodified source is https://github.com/CoolProp/CoolProp/tree/ae81610e7d23efc57f9d051c8e70a4d66e87537f.

Notices retain Boost/MessagePack BSL, fmt/json/miniz/IF97/REFPROP-header MIT,
Valijson BSD, Eigen MPL, incbin Unlicense and Emscripten MIT/NCSA. Exact installed
toolchain copies of Emscripten, musl, libc++, libc++abi, compiler-rt and libunwind
notices are retained. Other notices copied from the historical study are
conservatively included for the separately bundled official 7.2/8.0 comparison.
Optional Multicomplex/pybind11 are fetched by upstream CMake but included only by
the CatchTestRunner target, which is disabled here; they are not asserted to be
part of the delivered WASM. No test framework is enabled. Incbin's code path is
disabled by the upstream `COOLPROP_NO_INCBIN` build definition.

These are engineering provenance and notice records, not a legal warranty.
