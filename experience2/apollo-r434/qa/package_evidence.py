"""Reproducible source + evidence ZIP, fixed timestamps, sorted paths, no environment secrets."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib,json
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parent.parent
OUT=HERE/'QA/Apollo_R434_Local_Evidence.zip'
EXCLUDE={'QA/Apollo_R434_Local_Evidence.zip','QA/package-report.json'}

def build(target):
    items=[]
    for f in HERE.rglob('*'):
        if f.is_file():
            relative=f.relative_to(HERE).as_posix()
            if relative in EXCLUDE or '__pycache__' in relative or relative.endswith('.pyc'):
                continue
            items.append(f)
    with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(items,key=lambda f:f.relative_to(HERE).as_posix()):
            name='experience2/apollo-r434/'+f.relative_to(HERE).as_posix()
            info=ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=(0o100644<<16)
            z.writestr(info,f.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    return len(items)

if __name__=='__main__':
    n=build(OUT)
    one=OUT.read_bytes()
    other=OUT.with_suffix('.rebuild.zip')
    build(other)
    assert one==other.read_bytes(), 'non-deterministic ZIP evidence'
    other.unlink()
    meta={'entries':n,'sha256':hashlib.sha256(one).hexdigest(),'byte_identical_second_build':True}
    (HERE/'QA/package-report.json').write_text(json.dumps(meta,sort_keys=True,indent=2)+'\n')
    # Report written after archive intentionally excluded from archive to avoid self-referential hash.
    print(f'{n} entries, deterministic ZIP SHA256 {meta["sha256"]}')
