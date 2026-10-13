# Pinned upstream assets and notices

The `7.2.0` and `8.0.0` folders contain unchanged official CoolProp JavaScript
and WebAssembly downloads. SHA-256 values, URLs and byte sizes are recorded in
`../evidence/assets.json`. Each folder retains CoolProp's MIT license, which
permits free use, modification and redistribution, including commercial use,
with the copyright and permission notice retained.

The ammonia HEOS calculations use the open CoolProp implementation of Gao,
Wu, Bell and Lemmon (2020). They do not call a licensed REFPROP installation.
The presence of MIT-licensed REFPROP interface headers in the source tree does
not provide or require REFPROP for this HEOS prototype.

Dependency notices are retained in `notices/`, with downloaded source URLs in
`../evidence/license-sources.json` and its follow-up. The primary CMake dependency
pins and build workflows are retained in `../upstream/`:

| Component | Source versions/pins | License / retained notice |
| --- | --- | --- |
| Eigen | 7.2 submodule `68f4e58...`; 8.0 uses 5.0.1 | MPL 2.0; both notices retained |
| MessagePack | `919908742...` | Boost 1.0; copyright and full license retained |
| fmt | 7.2 `e424e3f...`; 8.0 12.0.0 | MIT; both notices retained |
| miniz | 3.0.2 / 3.1.1 | MIT; license retained |
| RapidJSON | 7.2 `24b5e7a...` | MIT and accompanying dependency notices retained |
| nlohmann/json | 8.0 3.12.0 | MIT; notice retained |
| Valijson | 8.0 1.0.6 | BSD; notice retained |
| Boost headers | 8.0 `c681046...` | Boost 1.0 full license retained |
| IF97 / REFPROP headers | pinned by both upstream builds | MIT notices retained; not the selected ammonia EOS |
| Emscripten | upstream workflow specifies 4.0.12 | MIT/NCSA notice and musl MIT notice retained |
| LLVM libc++ | toolchain dependency | Apache 2.0 with LLVM exceptions; notice retained |

Eigen's covered source remains available from the original, unmodified upstream
pins: [7.2 dependency source](https://gitlab.com/libeigen/eigen/-/tree/68f4e58cfacc686583d16cff90361f0b43bc2c1b)
and [5.0.1 source archive](https://gitlab.com/libeigen/eigen/-/archive/5.0.1/eigen-5.0.1.tar.gz).
The MPL obligation applies to its covered files; this experiment changes none
of them. Keep notices and source availability when redistributing the assets.

Source provenance for CoolProp itself:

- [7.2.0 exact source commit](https://github.com/CoolProp/CoolProp/tree/98b3523d5daa98454618d381d2ae53f7471d216b)
- [8.0.0 exact source commit](https://github.com/CoolProp/CoolProp/tree/ae81610e7d23efc57f9d051c8e70a4d66e87537f)

The binaries' runtime version/git metadata agree with the pinned Python packages.
They were not rebuilt in this experiment. The source workflow is evidence of
the upstream build recipe, not a verified compiler attestation. The WASM files
omit producer metadata. The LLVM notice is retained as a toolchain notice, not
an assertion that its illustrative 20.1.4 source URL identifies the exact
compiler used for these official artifacts. Optional test/development
components in the source tree are not asserted to be linked into these binaries.
