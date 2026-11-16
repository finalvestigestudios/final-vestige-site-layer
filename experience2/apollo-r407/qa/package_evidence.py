#!/usr/bin/env python3
"""Reproducible source+QA ZIP with stable timestamps/order/permissions. Local evidence only."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA/Apollo_R407_Local_Evidence.zip'
excludes={'QA/Apollo_R407_Local_Evidence.zip','QA/SHA256_MANIFEST.json'}
files=sorted((p for p in ROOT.rglob('*') if p.is_file() and str(p.relative_to(ROOT)) not in excludes),key=lambda p:p.as_posix())
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(ROOT/'QA/SHA256_MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
files.append(ROOT/'QA/SHA256_MANIFEST.json')
files.sort(key=lambda p:p.as_posix())
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:
  entry=zipfile.ZipInfo(str(p.relative_to(ROOT)).replace('\\','/'),date_time=(1980,1,1,0,0,0))
  entry.compress_type=zipfile.ZIP_DEFLATED
  entry.external_attr=(0o100644 & 0xffff)<<16
  z.writestr(entry,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(f'{len(files)} entries, sha256={hashlib.sha256(OUT.read_bytes()).hexdigest()}')
