"""Read-only historical preservation verification; outputs stay in B5B."""
import hashlib,json,lzma,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[2];X=B.parent;E=B/'evidence'
def read(p):return json.loads(p.read_text())
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(n,v):(E/n).write_text(json.dumps(v,indent=2)+'\n')
def verify():
    start=read(E/'starting-file-hashes.json')
    bad=[n for n,h in start.items() if sha((R/n).read_bytes())!=h]
    assert not bad,bad
    artifacts=[]
    for folder in ['browser_eos_b3','browser_eos_b4a','browser_eos_b4b','browser_eos_b4c','browser_eos_b5','browser_eos_b5a']:
        for label,v in read(X/folder/'evidence/native-binaries.json').items():
            p=X/folder/v['archive'];raw=p.read_bytes();binary=lzma.decompress(raw)
            assert sha(raw)==v['archiveSHA256'] and sha(binary)==v['sha256'],p
            artifacts.append(dict(file=str(p.relative_to(R)),sha256=sha(raw),decompressedSHA256=sha(binary)))
    for folder,manifest in [('browser_eos_backend','build-provenance.json'),('browser_eos_b4a','provenance.json'),('browser_eos_b4b','provenance.json'),('browser_eos_b4c','provenance.json')]:
        for n,v in read(X/folder/'evidence'/manifest)['artifacts'].items():
            p=X/folder/n;assert sha(p.read_bytes())==v['sha256'],p
            artifacts.append(dict(file=str(p.relative_to(R)),sha256=v['sha256']))
    a2=[]
    for n,h in read(X/'browser_eos_b4c/evidence/accepted-a2-verification.json')['files'].items():
        raw=subprocess.check_output(['git','show','be9eb35a4ddf5098e685182f8104685127c6a6ee:experiments/dx-fv/'+n],cwd=R)
        assert sha(raw)==h==sha((X/'browser_eos_backend/accepted'/n).read_bytes()),n
        a2.append(dict(file=n,sha256=h))
    patches=[]
    expectedPatches={v['file']:v['sha256'] for v in read(X/'browser_eos_b5a_gate_b/evidence/start-audit.json')['patches']}
    for n in ['browser_eos_backend/flash-44.patch','browser_eos_b4a/liquid-classification.patch','browser_eos_b4b/pt-cache-consistency.patch','browser_eos_b4c/upper-quality-classification.patch','browser_eos_b5a/gate-a.patch']:
        p=X/n;assert sha(p.read_bytes())==expectedPatches[n];patches.append(dict(file=str(p.relative_to(R)),sha256=sha(p.read_bytes())))
    protected=['be9eb35a4ddf5098e685182f8104685127c6a6ee','ef1562ae1680fccf3323391e9ec83788c5ae1e69','6a220dd6c94bff08e00e0107cfec71854166ede2','4e1295be9493d8bce4ca35ee0cf61accb7465226','94f77bb062b75ffebf17a1c9758d11c1adc61711','d0d11d59756c4dc32bbfdb22a5975fd6f4527e05','3622000309cacdd35aaaebbb805ae40d27c75603','e30ad9d76bc892aa355126339997d6184c8729d2','cc2ec6b54d40cabea93fa761d10a2ecab59def25','14b8b386148c687fcb549d5f17003fa9e63fbca8','262b6092b2ed694073ad9ffd41265f44dd0b6ca0']
    for c in protected:subprocess.run(['git','cat-file','-e',c+'^{commit}'],cwd=R,check=True)
    return dict(startingFiles=len(start),mismatches=bad,artifacts=artifacts,patches=patches,acceptedA2=a2,protectedCommits=protected,sourceVerification='Historical source manifests and patch bytes preserved; no new external CoolProp source reconstruction or dependency build. Artifact digests independently reverified before browser load.',allPass=True)
if __name__=='__main__':
    out=verify();name='start-audit.json' if '--start' in sys.argv else 'final-preservation.json'
    if '--start' not in sys.argv:
        changes=subprocess.check_output(['git','diff','--name-status','14b8b386148c687fcb549d5f17003fa9e63fbca8'],cwd=R,text=True)
        assert all(x.startswith('A\texperiments/dx-fv/browser_eos_b5b/') for x in changes.splitlines()),changes
        out['trackedChanges']=changes
        before=dict(x.split()[::-1] for x in (E/'refs-before.txt').read_text().splitlines())
        after=dict(x.split()[::-1] for x in (E/'refs-after.txt').read_text().splitlines())
        target='refs/heads/research/browser-eos-b5b-boundary-contract-design-20261016'
        drift={k:[v,after.get(k)] for k,v in before.items() if k!=target and after.get(k)!=v}
        assert not drift,drift
        out.update(remoteRefDrift=drift,remoteRefsChecked=len(before),onlyAllowedNewRemoteRef=target)
        assert set(after)-set(before)<={target},set(after)-set(before)
    write(name,out);print(name,out['startingFiles'],'files,',len(out['artifacts']),'artifact identities,',len(out['acceptedA2']),'A2 snapshots verified')
