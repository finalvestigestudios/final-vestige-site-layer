#!/usr/bin/env python3
"""Deterministic QA artifact bundle; excludes itself and mutable timestamps."""
from pathlib import Path
import hashlib,json,zipfile
base=Path(__file__).resolve().parents[1]
paths=[base/'README.md',base/'reusable-atlas-assets.php']
paths+=sorted((base/'qa').glob('*'))
paths+=sorted((base/'QA').glob('*'))
paths=[x for x in paths if x.is_file() and x.suffix not in ('.pyc','.zip')]
manifest=[{'file':str(p.relative_to(base)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths]
archive=base/'QA/Apollo_R383_Evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in paths:
  info=zipfile.ZipInfo(str(p.relative_to(base)),date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 info=zipfile.ZipInfo('MANIFEST.json',date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
 z.writestr(info,(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'files':len(paths),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive':str(archive)}))
