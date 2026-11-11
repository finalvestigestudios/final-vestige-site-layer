#!/usr/bin/env python3
"""Deterministic release-HOLD research evidence bundle; includes tested source and browser receipts."""
import hashlib, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parents[1]
TARGET=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/Apollo_R281_HARD_HOLD.zip')
QA=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/tmp/fv-r281-qa')
files={}
for path in [ROOT/'apollo-source-experience.php',ROOT/'assets/apollo-source-experience.css',ROOT/'qa/committed_gate.py',ROOT/'qa/build_archive.py']:
    files[path.relative_to(BASE).as_posix()]=path.read_bytes()
for path in QA.glob('*'):
    if path.is_file():
        files['QA/'+path.name]=path.read_bytes()
manifest={'release':'HARD_HOLD','files':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(files.items())}}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
TARGET.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,content in sorted(files.items()):
        info=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644<<16
        z.writestr(info,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('files',len(files),'archive_sha256',hashlib.sha256(TARGET.read_bytes()).hexdigest())
