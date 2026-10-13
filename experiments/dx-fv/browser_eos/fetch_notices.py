"""Retain notices from pinned upstream dependencies; no build or production edits."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;O=B/'vendor/notices';O.mkdir(exist_ok=True)
refs=[
('Eigen-7.2-MPL2','https://gitlab.com/libeigen/eigen/-/raw/68f4e58cfacc686583d16cff90361f0b43bc2c1b/COPYING.MPL2'),
('Eigen-8.0-MPL2','https://gitlab.com/libeigen/eigen/-/raw/5.0.1/COPYING.MPL2'),
('msgpack-Boost','https://raw.githubusercontent.com/msgpack/msgpack-c/919908742b4fdbc575e77fe1a8657e70c9573c44/COPYING'),
('nlohmann-json-MIT','https://raw.githubusercontent.com/nlohmann/json/v3.12.0/LICENSE.MIT'),
('valijson-BSD','https://raw.githubusercontent.com/tristanpenman/valijson/v1.0.6/LICENSE'),
('IF97-MIT','https://raw.githubusercontent.com/CoolProp/IF97/7aaced024a702f0985474bf293cdaae9c8d06521/LICENSE'),
('REFPROP-headers','https://raw.githubusercontent.com/CoolProp/REFPROP-headers/b4faab1b73911c32c4b69c526c7e92f74edb67de/LICENSE'),
('boost-headers','https://raw.githubusercontent.com/CoolProp/boost-headers/c68104660ca4bd80d0d5cb34c4eba0cf5bab3f73/LICENSE_1_0.txt'),
('fmt-8.0-MIT','https://raw.githubusercontent.com/fmtlib/fmt/12.0.0/LICENSE'),
('fmt-7.2','https://raw.githubusercontent.com/fmtlib/fmt/e424e3f2e607da02742f73db84873b8084fc714c/LICENSE.rst'),
('rapidjson-MIT','https://raw.githubusercontent.com/Tencent/rapidjson/24b5e7a8b27f42fa16b96fc70aade9106cf7102f/license.txt'),
('miniz-MIT','https://raw.githubusercontent.com/CoolProp/CoolProp/ae81610e7d23efc57f9d051c8e70a4d66e87537f/externals/miniz-3.1.1/LICENSE'),
('emscripten-MIT-NCSA','https://raw.githubusercontent.com/emscripten-core/emscripten/4.0.12/LICENSE'),
('LLVM-Apache','https://raw.githubusercontent.com/llvm/llvm-project/llvmorg-20.1.4/libcxx/LICENSE.TXT')]
rows=[]
for name,url in refs:
 p=O/(name+'.txt')
 if p.exists():status='retained existing'
 else:
  r=subprocess.run(['curl','-fsSL','--max-time','25',url,'-o',str(p)],capture_output=True,text=True);status='downloaded' if r.returncode==0 else r.stderr.strip()
  if r.returncode and p.exists():p.unlink()
 row=dict(name=name,url=url,status=status)
 if p.exists():row.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 rows.append(row)
 print(name,status,flush=True)
(B/'evidence/license-sources.json').write_text(json.dumps(rows,indent=2)+'\n')
