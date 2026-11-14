#!/usr/bin/env python3
"""Make reproducible ZIP of frozen artifacts, not reproducible browser executions."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[3]
ex=root/'experience2'
files=[p for p in (ex/'apollo-r360').rglob('*') if p.is_file() and p.name != 'http_csp_gate.py' and p.name!='build_evidence.py']
for segment in ['apollo-r339','apollo-r340','apollo-r345','apollo-r347','apollo-r348','apollo-r349','apollo-r350','apollo-r355','apollo-r356','apollo-r357','apollo-r358','apollo-r359']:
    files.extend(p for p in (ex/segment).rglob('*') if p.is_file() and '/QA/' not in str(p) and p.suffix in ('.php','.js','.css'))
files=sorted(set(files),key=lambda x:x.relative_to(root).as_posix())
manifest={'scope':'R360 frozen local QA artifacts, not installed WP acceptance','files':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
archive=root/'Apollo_R360_Evidence.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:
        info=zipfile.ZipInfo(p.relative_to(root).as_posix(),(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    info=zipfile.ZipInfo('R360_MANIFEST.json',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
    z.writestr(info,(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'zip':str(archive),'files':len(files),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
