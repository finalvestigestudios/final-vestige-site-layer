#!/usr/bin/env python3
"""Stable source + browser evidence archive for R283. No deployment side effects."""
import hashlib, json, sys, zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
TARGET=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/Apollo_R283_HARD_HOLD.zip')
QA=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/tmp/fv-r283-qa')
paths=[
 'experience2/apollo-r281/apollo-source-experience.php',
 'experience2/apollo-r281/assets/apollo-source-experience.css',
 'experience2/apollo-r281/qa/committed_gate.py',
 'experience2/apollo-r283/build_archive.py',
 'experience2/apollo-r283/README.md',
]
files={path:(BASE/path).read_bytes() for path in paths}
for item in QA.iterdir():
 if item.is_file():files['QA/'+item.name]=item.read_bytes()
manifest={'status':'UNMERGED_STAGING_HARD_HOLD','files':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(files.items())}}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
TARGET.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,body in sorted(files.items()):
  info=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  z.writestr(info,body,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('files',len(files),'SHA256',hashlib.sha256(TARGET.read_bytes()).hexdigest())
