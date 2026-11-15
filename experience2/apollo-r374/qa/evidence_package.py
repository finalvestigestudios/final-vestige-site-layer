#!/usr/bin/env python3
"""Deterministic R374 source + browser QA evidence ZIP. Offline; no publishing."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[3]
STAGE=ROOT/'experience2/apollo-r374'
SOURCE=[
 'experience2/apollo-r372/qa/fixture.php',
 'experience2/apollo-r372/assets/evidence-path.css',
 'experience2/apollo-r372/evidence-path.php',
 'experience2/apollo-r373/qa/staging_acceptance.py',
 'experience2/apollo-r374/qa/staging_acceptance.py',
 'experience2/apollo-r374/qa/test_stage_custody.py',
 'experience2/apollo-r374/qa/evidence_package.py',
]
QA=sorted(str(p.relative_to(ROOT)) for p in (STAGE/'QA').glob('*') if p.is_file())
PATHS=sorted(SOURCE+QA)

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def build(destination):
    files={}
    manifest={'status':'LOCAL_CHROMIUM_CUSTODY_PASS_NOT_STAGING',
      'installed_wordpress_assembler':'NOT_EXECUTED',
      'genuine_axe_http_csp':'NOT_EXECUTED',
      'settled_paid_revenue':'NOT VERIFIED',
      'files':{}}
    for name in PATHS:
        data=(ROOT/name).read_bytes()
        files[name]=data
        manifest['files'][name]={'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                                 'git_blob_sha1':git_blob(data)}
    files['R374_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    with zipfile.ZipFile(destination,'w') as z:
        for name in sorted(files):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,files[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(destination.read_bytes()).hexdigest(),len(files)

main=STAGE/'Apollo_R374_Evidence.zip'
sha,count=build(main)
other=STAGE/'QA'/'_repeat.zip'
try:
    sha2,count2=build(other)
    assert sha==sha2 and count==count2,'archive bytes changed on repeat'
finally:
    other.unlink(missing_ok=True)
print('DETERMINISTIC_ARCHIVE_PASS',count,'entries; SHA-256',sha)
