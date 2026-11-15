#!/usr/bin/env python3
"""Reproducible evidence bundle, fixed metadata, sorted entries and sha256 manifest."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experience2/apollo-r380'
FILES=[
 'experience2/apollo-r377/assets/source-role.css',
 'experience2/apollo-r377/custody.json',
 'experience2/apollo-r377/source-role-desk.php',
 'experience2/apollo-r378/guarded-reusable-assets.php',
 'experience2/apollo-r379/prehead-template-parts.php',
 'experience2/apollo-r379/qa/wp_stub.php',
 'experience2/apollo-r379/qa/browser_qa.py',
 'experience2/apollo-r380/README.md',
 'experience2/apollo-r380/qa/run.py',
 'experience2/apollo-r380/qa/package.py',
]
FILES += ['experience2/apollo-r380/QA/'+p.name for p in sorted((BASE/'QA').glob('*.png'))]
FILES += ['experience2/apollo-r380/QA/results.json']
FILES=sorted(set(FILES))
OUTPUT=BASE/'QA/Apollo_R380_Evidence.zip'

def generate():
    checks={x:hashlib.sha256((ROOT/x).read_bytes()).hexdigest() for x in FILES}
    manifest=json.dumps({'schema':'fv.apollo.r380.artifact.v1','files':checks},sort_keys=True,indent=2).encode() + b'\n'
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(['R380_MANIFEST.json']+FILES):
            data=manifest if name=='R380_MANIFEST.json' else (ROOT/name).read_bytes()
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),len(FILES)+1

if __name__=='__main__':
    x,n=generate()
    y,_=generate()
    assert x==y
    print('DETERMINISTIC_PASS',n,'ZIP entries','SHA256',x)
