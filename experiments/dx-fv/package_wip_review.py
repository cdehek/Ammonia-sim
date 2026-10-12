"""Build a focused, hashed review ZIP without running or changing any model.

python package_wip_review.py OUTPUT.zip JOINT_EVIDENCE_DIR STATIC_EVIDENCE_DIR
Only explicit research sources/context and compact existing evidence are copied.
No credentials, .git, runtime binaries, full work traces or large grid outputs.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
PREFIX='experiments/dx-fv/'
ADDITIONS=[PREFIX+n for n in ['RESEARCH_WIP_HANDOFF.md','ASTRA_REVIEW_BRIEF.md',
                              'RESEARCH_WIP_EVIDENCE.json','package_wip_review.py']]
CONTEXT=['engine.js','properties.json','tools/generate_properties.py']+[PREFIX+n for n in [
    'thermodynamics.cjs','conservation.cjs','hydraulics.cjs','coupled-fixtures.cjs',
    'thermal-geometry.cjs','thermal-network.cjs','COUPLED_STAGE_2A.md',
    'COUPLED_STAGE_2A_R.md','ROADMAP_A2.md','DEVELOPMENT_HANDOFF.md','RESTORE_POINTS.md']]
EVIDENCE={
 'ammonia-joint-property-evidence':['audit.json','conditioning.json','conditioning-native.json',
                                  'analysis.json','properties.json','legacy-liquid.json'],
 'ammonia-static-property-evidence':['audit.json','roots-refined.json','baseline-ph.json',
                                   'derivatives.json','baseline-performance.json','performance.json',
                                   'continuity.json','qualification-near-saturation-ambiguity.log',
                                   'audit-raw-roundtrip-failure.log','audit-folded-density-failure.log']}

def main():
    if len(sys.argv)!=4:raise SystemExit(__doc__)
    output=Path(sys.argv[1]).resolve();joint=Path(sys.argv[2]).resolve();static=Path(sys.argv[3]).resolve()
    if output.is_relative_to(ROOT):raise ValueError('Review package belongs outside the repository')
    meta=json.loads((ROOT/PREFIX/'RESEARCH_WIP_EVIDENCE.json').read_text())
    original=meta['originalResearchPaths'];preserved=original+ADDITIONS
    assert len(original)==32 and len(preserved)==36 and len(set(preserved))==36
    assert all(p.startswith(PREFIX) for p in preserved)
    entries={};kinds={};missing=[]
    def add(name,data,kind):
        assert name not in entries and not name.startswith('/') and '..' not in Path(name).parts
        entries[name]=data;kinds[name]=kind
    for name in preserved+CONTEXT:
        data=(ROOT/name).read_bytes()
        if name in original:assert hashlib.sha256(data).hexdigest()==meta['originalResearchSHA256'][name],name
        if name in CONTEXT:
            baseline=subprocess.check_output(['git','show',meta['acceptedA2SHA']+':'+name],cwd=ROOT)
            assert data==baseline,('Protected/read-only context changed',name)
        add('source/'+name,data,'preserved research' if name in preserved else 'unchanged accepted context')
    for label,source in [('ammonia-joint-property-evidence',joint),('ammonia-static-property-evidence',static)]:
        for name in EVIDENCE[label]:
            path=source/name
            if not path.is_file():missing.append(label+'/'+name);continue
            add(label+'/'+name,path.read_bytes(),'compact existing evidence; not newly qualified')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    clean=not subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=ROOT,text=True)
    readme=f'''# Ammonia Lab — Astra review package

UNQUALIFIED WIP research preservation. No candidate is adopted.
Snapshot commit: {head}
Snapshot branch: {branch}
Working tree clean when packaged: {clean}
Accepted A2 restore: {meta['acceptedA2SHA']}

Start with source/experiments/dx-fv/RESEARCH_WIP_HANDOFF.md and ASTRA_REVIEW_BRIEF.md.
They specify the mathematical questions, failed methods and next user decision.
Original research reports remain historical snapshots; this handoff supersedes
their old current-status/authorization language. No Astra review has yet occurred.

source/ contains only the preserved research, relevant property/thermal/coupled
source and selected historical reports. engine.js, properties.json and the table
generator are read-only copies of unchanged accepted context. The two evidence
directories are compact selections of actual existing outputs, not complete
standalone audit inputs. Historical audit scripts need a full Git checkout and
original provenance manifests; see the handoff's disposable overlay instructions.
No algorithms or EOS data were generated while packaging.

MANIFEST.json hashes every other ZIP member. PRESERVED_FILES.txt lists all 36
changed paths relative to A2. RESEARCH_WIP_EVIDENCE.json permanently records compact
metrics and the original dirty-state source hashes. Large 30,006-state interior
and 7,234-knot raw arrays, full work traces and runtime binaries are excluded.
Full available archives are supplied separately. Earlier ephemeral Stage 2B
multi-hour queues are unavailable here; their reports/scripts/reference survive.

Remaining candidates are rejected: monotonic fields violate Maxwell, and potential
fits fail stability/uniqueness and pressure accuracy. Evidence audit success is
not property qualification. Review only; no fit, coupling, default promotion or
scientific-limit change is authorized by this package.
'''
    add('README.md',readme.encode(),'generated review index')
    add('PRESERVED_FILES.txt',('\n'.join(preserved)+'\n').encode(),'complete preservation file list')
    manifest=dict(schemaVersion=1,status='UNQUALIFIED WIP; preservation only',
        repository=meta['repository'],snapshotCommit=head,snapshotBranch=branch,workingTreeClean=clean,
        acceptedA2SHA=meta['acceptedA2SHA'],originalResearchFiles=len(original),preservedChangedFiles=len(preserved),
        omittedUnavailableSelectedEvidence=missing,
        members={name:dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),kind=kinds[name])
                 for name,data in sorted(entries.items())})
    entries['MANIFEST.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in sorted(entries.items()):
            info=ZipInfo(name,date_time=(2026,10,12,0,0,0));info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,data,compresslevel=9)
    with ZipFile(output) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(set(archive.namelist()))==len(entries)
        for name,record in manifest['members'].items():
            data=archive.read(name)
            assert len(data)==record['bytes'] and hashlib.sha256(data).hexdigest()==record['sha256']
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(output.suffix+'.sha256').write_text(digest+'  '+output.name+'\n')
    print(json.dumps(dict(package=str(output),bytes=output.stat().st_size,sha256=digest,
          snapshotCommit=head,workingTreeClean=clean,members=len(entries),missingSelectedEvidence=missing)))

if __name__=='__main__':main()
