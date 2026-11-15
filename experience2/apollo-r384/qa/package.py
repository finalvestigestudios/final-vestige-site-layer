#!/usr/bin/env python3
"""Reproducible artifact bundle with fixed ZIP timestamps and full SHA-256 manifest."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/'README.md',ROOT/'document-gallery.php',ROOT/'assets/gallery.css']
paths+=sorted((ROOT/'qa').glob('*.py'))+sorted((ROOT/'qa').glob('*.php'))
paths+=sorted((ROOT/'QA').glob('*.png'))+sorted((ROOT/'QA').glob('*.json'))
paths+=sorted((ROOT/'QA').glob('*.html'))+sorted((ROOT/'QA').glob('*.pdf'))
custody=ROOT.parent/'apollo-r377/custody.json'
paths.append(custody)
assert all(p.exists() for p in paths)
manifest=[{'path':str(p.relative_to(ROOT.parent)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':len(p.read_bytes())} for p in paths]
arch=ROOT/'QA/Apollo_R384_Evidence.zip'
with zipfile.ZipFile(arch,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for file in paths:
  entry=zipfile.ZipInfo(str(file.relative_to(ROOT.parent)),(1980,1,1,0,0,0));entry.external_attr=0o644<<16;entry.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(entry,file.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 entry=zipfile.ZipInfo('MANIFEST.json',(1980,1,1,0,0,0));entry.external_attr=0o644<<16;entry.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(entry,(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(arch),'files':len(paths),'sha256':hashlib.sha256(arch.read_bytes()).hexdigest()}))
