#!/usr/bin/env python3
"""Deterministic ZIP: no generated ZIP or hash file is allowed to enter itself."""
import hashlib
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'; OUT.mkdir(exist_ok=True)
ZIP=OUT/'Apollo_R442_QA.zip'
PATHS=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.suffix in ('.pyc','.zip'):
        continue
    if p.name in ('archive_manifest.json',):continue
    PATHS.append(p)
with zipfile.ZipFile(ZIP,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in PATHS:
        arc=p.relative_to(ROOT).as_posix()
        info=zipfile.ZipInfo(arc,date_time=(1980,1,1,0,0,0))
        info.external_attr=0o644<<16
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
manifest={'archive_sha256':hashlib.sha256(ZIP.read_bytes()).hexdigest(),
          'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in PATHS},
          'claim':'local contract and PHP fixture QA only; not navigated staging, axe or field CWV'}
(OUT/'archive_manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
print(json.dumps({'entries':len(PATHS),'sha256':manifest['archive_sha256'],'file':str(ZIP)}))
