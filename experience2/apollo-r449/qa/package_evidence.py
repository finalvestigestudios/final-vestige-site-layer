"""Deterministic offline R449 code/screenshots archive, no external services."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
DEST=QA/'Apollo_R449_Deterministic_Offline_QA.zip'
STAMP=(2026,11,17,0,0,0)
def sha(x):return hashlib.sha256(x).hexdigest()
def build():
    QA.mkdir(parents=True,exist_ok=True)
    files=sorted(p for p in ROOT.rglob('*') if p.is_file()
        and '__pycache__' not in p.parts and not p.name.endswith('.zip')
        and p.name not in ('MANIFEST.json',) and p.suffix!='.pyc')
    manifest={'schema':'fv-apollo-r449-offline-evidence-v1','timestamp_policy':'fixed 2026-11-17; not a claim of run date',
              'files':[{ 'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in files]}
    (QA/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    files.append(QA/'MANIFEST.json')
    with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            i=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),STAMP);i.compress_type=zipfile.ZIP_DEFLATED
            i.external_attr=(0o100644<<16);z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return {'zip':str(DEST),'files':len(files),'sha256':sha(DEST.read_bytes()),'bytes':DEST.stat().st_size}
if __name__=='__main__':print(json.dumps(build(),indent=2))
