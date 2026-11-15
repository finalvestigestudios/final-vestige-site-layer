#!/usr/bin/env python3
"""Byte-stable ZIP of R379 source, tests and local screenshots; no uploads/writes outside QA."""
import hashlib,json,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'experience2/apollo-r379'
SIBLING=BASE/'experience2/apollo-r377'
files=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix not in ('.zip','.pyc') and '__pycache__' not in p.parts]
files += [SIBLING/'assets/source-role.css',SIBLING/'custody.json',SIBLING/'source-role-desk.php']
files=sorted(set(files),key=lambda p:str(p.relative_to(BASE)))
sha={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest=(json.dumps({'schema':'fv.apollo.r379.qa-manifest.v1','sha256':sha},sort_keys=True,indent=2)+'\n').encode()
path=ROOT/'QA/Apollo_R379_Evidence.zip'
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in [('R379_MANIFEST.json',manifest)]+[(str(p.relative_to(BASE)),p.read_bytes()) for p in files]:
  info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o100644<<16
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'entries':len(files)+1},sort_keys=True))
