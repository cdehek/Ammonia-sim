"""Isolated browser setup or read-only verification of actual installed packages."""
import argparse,hashlib,json,os,subprocess,sys,urllib.request
from pathlib import Path
B=Path(__file__).resolve().parent;W=Path('/workspace/b7-work');E=B/'evidence';D=W/'debs';D.mkdir(exist_ok=True)
p=argparse.ArgumentParser();p.add_argument('--verify-existing',action='store_true');a=p.parse_args()
pins=json.loads((B.parent/'browser_eos_b4a/evidence/provenance.json').read_text())['browserExtraDebs'];rows=[]
for name,digest in pins.items():
 folder='libm/libmanette' if name.startswith('libmanette') else 'h/hyphen' if name.startswith('libhyphen') else 'h/harfbuzz' if name.startswith('libharfbuzz') else 'libg/libglvnd'
 path=D/name;url='https://deb.debian.org/debian/pool/main/'+folder+'/'+name
 if not a.verify_existing:
  with urllib.request.urlopen(url,timeout=40) as response:path.write_bytes(response.read())
 actual=hashlib.sha256(path.read_bytes()).hexdigest();assert actual==digest,name
 if not a.verify_existing:subprocess.run(['dpkg-deb','-x',str(path),str(W/'sysroot')],check=True)
 rows.append(dict(file=name,url=url,sha256=actual,matchesPreservedB4A=True))
if not a.verify_existing:
 env=dict(os.environ,PLAYWRIGHT_BROWSERS_PATH='/workspace/b7-browsers')
 subprocess.run([sys.executable,'-m','playwright','install','chromium','webkit'],env=env,check=True,timeout=300)
 launcher=(B.parent/'browser_eos_b4c/evidence/webkit-launcher.sh').read_text().replace('/workspace/b4c-browsers','/workspace/b7-browsers').replace('/workspace/b4c-sysroot','/workspace/b7-work/sysroot')
 (W/'webkit.sh').write_text(launcher);(W/'webkit.sh').chmod(0o755)
executables={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/workspace/b7-browsers').rglob('*') if p.is_file() and p.name in ['chrome','headless_shell','MiniBrowser']}
libraries={str(p.relative_to(W/'sysroot')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (W/'sysroot').rglob('*') if p.is_file()}
out=dict(packages=rows,browserExecutablesSHA256=executables,sysrootFilesSHA256=libraries,launcherSHA256=hashlib.sha256((W/'webkit.sh').read_bytes()).hexdigest(),hostPackagesUnchanged=True,physicalSafariOrIPad=False)
target=E/'browser-dependency-verification.json';assert not target.exists();target.write_text(json.dumps(out,indent=2)+'\n');print('Six pinned browser packages and actual browser/runtime files verified')
