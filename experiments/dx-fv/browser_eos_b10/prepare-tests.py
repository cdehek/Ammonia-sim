"""Create disposable pinned/candidate test trees; never edit historical checkout."""
import io,subprocess,tarfile,shutil,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];W=B/'.runtime';W.mkdir(exist_ok=True)
raw=subprocess.check_output(['git','archive','262b6092b2ed694073ad9ffd41265f44dd0b6ca0'],cwd=R)
for name in ['pinned','candidate']:
 p=W/name;p.mkdir(exist_ok=True)
 with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(p,filter='data')
if '--install-node' in sys.argv:subprocess.run(['npm','ci','--prefix',str(W/'pinned'),'--cache',str(W/'npm-cache')],check=True)
if not (W/'candidate/node_modules').exists():(W/'candidate/node_modules').symlink_to('../pinned/node_modules',target_is_directory=True)
shutil.copyfile(B/'index.html',W/'candidate/index.html')
print('Literal pinned tests prepared; only candidate index.html is replaced')
