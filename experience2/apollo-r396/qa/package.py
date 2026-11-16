#!/usr/bin/env python3
"""Deterministic local evidence bundle, not a deployable WordPress plugin."""
from __future__ import annotations
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
R=ROOT/'apollo-r396';Q=R/'QA';Q.mkdir(exist_ok=True)
files=[ROOT/'apollo-r377/custody.json',ROOT/'apollo-r384/assets/gallery.css',ROOT/'apollo-r395/assets/mobile-fit.css',ROOT/'apollo-r393/QA/local-php-fixture.html',
 R/'staging-custody.php',R/'README.md',R/'qa/php_contract.php',R/'qa/enable.php',R/'qa/browser.py',R/'qa/package.py',Q/'browser-results.json']
files+=sorted(Q.glob('*.png'))
manifest={'status':'LOCAL_ONLY_NOT_INSTALLED','source_files':[
 {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
 for p in sorted(files,key=lambda p:str(p.relative_to(ROOT)))]}
manifest_path=Q/'MANIFEST.json';manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
files.append(manifest_path)
archive=Q/'Apollo_R396_Local_Evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files,key=lambda p:str(p.relative_to(ROOT))):
  info=zipfile.ZipInfo(str(p.relative_to(ROOT)),date_time=(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(archive),'files':len(files),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
