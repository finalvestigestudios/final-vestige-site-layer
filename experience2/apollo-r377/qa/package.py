#!/usr/bin/env python3
"""Create reproducible R377 evidence archive: fixed timestamp/ordering, SHA-256 manifest."""
import argparse,hashlib,json,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SRC=ROOT.parent.parent
EXCLUDE={'qa/r377_local_fixture.html','QA/root4x-first-1200.png'}

def package(path):
    files=[]
    for p in ROOT.rglob('*'):
        if (p.is_file() and p.relative_to(ROOT).as_posix() not in EXCLUDE
            and '__pycache__' not in p.parts and 'pdf_render' not in p.parts):
            files.append(p)
    manifest={'release':'R377','scope':'local source and chromium fixture only, no WordPress staging',
      'source_root':'experience2/apollo-r377/','files':{p.relative_to(SRC).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}for p in sorted(files)}}
    def add(z,name,data):
        info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,data,compresslevel=9)
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'w') as z:
        add(z,'R377_MANIFEST.json',(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode())
        for p in sorted(files):add(z,p.relative_to(SRC).as_posix(),p.read_bytes())
    return path
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',required=True,type=Path);args=a.parse_args()
    p=package(args.out)
    print(p,'sha256',hashlib.sha256(p.read_bytes()).hexdigest(),'bytes',p.stat().st_size)
