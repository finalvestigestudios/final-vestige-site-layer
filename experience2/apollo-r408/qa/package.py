#!/usr/bin/env python3
"""Deterministic ZIP excluding self; SHA-256 manifest covers all included items."""
import json,hashlib,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];qa=root/'QA';qa.mkdir(exist_ok=True)
files=sorted(x for x in root.rglob('*') if x.is_file() and x.suffix not in ('.zip','.pyc') and x.name != 'SHA256_MANIFEST.json' and '__pycache__' not in x.parts)
manifest={str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}
(qa/'SHA256_MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
files.append(qa/'SHA256_MANIFEST.json')
dest=qa/'Apollo_R408_Local_Evidence.zip'
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(files):
  info=zipfile.ZipInfo(str(f.relative_to(root)),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'entries':len(files)},sort_keys=True))
