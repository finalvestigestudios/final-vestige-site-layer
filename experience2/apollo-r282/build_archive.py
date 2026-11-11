#!/usr/bin/env python3
"""Deterministic Apollo R282 hard-hold evidence archive (offline, no release)."""
from pathlib import Path
import hashlib,json,sys,zipfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
TARGET=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/Apollo_R282_HARD_HOLD.zip')
QA=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/tmp/fv-r282-qa')
paths=['experience2/apollo-r281/apollo-source-experience.php','experience2/apollo-r281/assets/apollo-source-experience.css','experience2/apollo-r281/qa/committed_gate.py','experience2/apollo-r282/README.md','experience2/apollo-r282/build_archive.py']
files={path:(BASE/path).read_bytes() for path in paths}
for p in QA.glob('*'):
    if p.is_file(): files['QA/'+p.name]=p.read_bytes()
manifest={'status':'STAGING_HARD_HOLD','files':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(files.items())}}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
TARGET.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(files.items()):
        i=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16
        z.writestr(i,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('files',len(files),'zip_sha256',hashlib.sha256(TARGET.read_bytes()).hexdigest())
