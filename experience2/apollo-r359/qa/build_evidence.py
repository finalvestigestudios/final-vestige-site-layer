#!/usr/bin/env python3
"""Deterministic archival ZIP of R359 local evidence; no live install, CI, or deployment."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
EX=ROOT/'experience2'
OUT=ROOT/'Apollo_R359_Evidence.zip'
paths=[p for p in (EX/'apollo-r359').rglob('*') if p.is_file() and not p.name.endswith('.zip')]
for d in ('apollo-r339','apollo-r340','apollo-r345','apollo-r347','apollo-r348','apollo-r349','apollo-r350','apollo-r355','apollo-r356','apollo-r357','apollo-r358'):
    paths += [p for p in (EX/d).rglob('*') if p.is_file() and ('/QA/' not in str(p)) and ('/qa/' not in str(p))]
paths=sorted(set(paths),key=lambda p:p.relative_to(ROOT).as_posix())
files={p.relative_to(ROOT).as_posix():p.read_bytes() for p in paths}
manifest={'evidence_scope':'Local PHP API stubs and browser fixture only; not live WordPress, axe, or CI',
          'files':{k:{'size':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in sorted(files.items())}}
files['R359_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(files.items()):
        entry=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
        entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o644<<16
        z.writestr(entry,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'path':str(OUT),'file_count':len(files),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))
