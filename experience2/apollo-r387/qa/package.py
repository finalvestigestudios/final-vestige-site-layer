#!/usr/bin/env python3
"""Deterministically bundle source, real local browser screenshots/PDFs, and QA results."""
import hashlib
import json
import zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
S=BASE/'apollo-r387'
QA=S/'QA'
source_files=[BASE/'apollo-r384/document-gallery.php',BASE/'apollo-r384/assets/gallery.css',
              BASE/'apollo-r377/custody.json',S/'README.md',S/'qa/print_states.py',S/'qa/package.py',
              BASE/'apollo-r386/QA/php-results.json',BASE/'apollo-r386/QA/browser-results.json',
              QA/'print-state-results.json']
qa_files=sorted([*QA.glob('*.png'),*QA.glob('*.pdf')])
files=source_files+qa_files
missing=[str(p) for p in files if not p.is_file()]
if missing:raise SystemExit('Missing QA inputs: '+', '.join(missing))
manifest={'release':'R387 local proof only','files':{str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
manifest_path=QA/'MANIFEST.json'
manifest_path.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
files.append(manifest_path)
archive=QA/'Apollo_R387_Evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files,key=lambda x:str(x.relative_to(BASE))):
  info=zipfile.ZipInfo(str(p.relative_to(BASE)),date_time=(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'entries':len(files),'zip':str(archive),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2))
