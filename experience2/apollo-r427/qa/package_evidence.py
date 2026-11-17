"""Reproducible time-independent archive and digest: staging-only offline QA, not production receipt."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARCH=ROOT/'QA'/'Apollo_R427_Local_Evidence.zip'
allowed=[]
for folder in ('assets','qa'):
    allowed += [p for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix not in ('.pyc',)]
allowed += [ROOT/'staging-source-chain.php',ROOT/'README.md']
allowed += [p for p in (ROOT/'QA').rglob('*') if p.is_file() and p!=ARCH]
allowed=sorted(set(allowed),key=lambda x:x.relative_to(ROOT).as_posix())
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in allowed}
manifest_data=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
ARCH.parent.mkdir(parents=True,exist_ok=True)
def build():
    with zipfile.ZipFile(ARCH,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in allowed:
            zi=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16
            z.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        zi=zipfile.ZipInfo('sha256-manifest.json',date_time=(1980,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16
        z.writestr(zi,manifest_data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(ARCH.read_bytes()).hexdigest()
a=build();b=build();assert a==b
print(f'{len(allowed)+1} entries, byte-identical double-build sha256={a}')
