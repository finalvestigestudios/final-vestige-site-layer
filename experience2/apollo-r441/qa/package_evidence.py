#!/usr/bin/env python3
"""Byte-reproducible evidence ZIP; self-excluding with normalised timestamps."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

root=Path(__file__).resolve().parents[1]; qa=root/'QA';qa.mkdir(exist_ok=True)
source=sorted(p for p in root.rglob('*') if p.is_file() and 'QA/' not in p.relative_to(root).as_posix() and '__pycache__' not in str(p))
outputs=sorted(p for p in qa.rglob('*') if p.is_file() and p.suffix in ('.json','.png') and p.name != 'manifest.json')
entries=source+outputs
manifest={'files':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in entries}}
(qa/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
entries.append(qa/'manifest.json');target=qa/'Apollo_R441_Integrity_QA.zip'
with ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(entries):
  name=p.relative_to(root).as_posix();info=ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'files':len(entries),'zip_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'path':str(target)}))
