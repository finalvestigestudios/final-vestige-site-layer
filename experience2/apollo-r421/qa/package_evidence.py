#!/usr/bin/env python3
"""Fixed-time sorted archive, independently rerunnable."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib
root=Path(__file__).resolve().parents[1]
paths=sorted([p for p in root.rglob('*') if p.is_file() and p.suffix!='.zip' and '__pycache__' not in p.parts])
target=root/'QA/Apollo_R421_Local_Evidence.zip'
target.parent.mkdir(exist_ok=True)
with ZipFile(target,'w') as z:
 for p in paths:
  info=ZipInfo(p.relative_to(root).as_posix(),date_time=(1980,1,1,0,0,0))
  info.compress_type=ZIP_DEFLATED;info.external_attr=(0o644<<16)
  z.writestr(info,p.read_bytes())
print(f'{len(paths)} archive entries; SHA-256 {hashlib.sha256(target.read_bytes()).hexdigest()}')
