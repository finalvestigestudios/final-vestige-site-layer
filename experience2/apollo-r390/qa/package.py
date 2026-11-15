#!/usr/bin/env python3
"""Build deterministic evidence archive after R389 fixture QA and R390 boundary QA.

Run from a complete source checkout. PNG/PDF are fixture only, never staged proof.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[2]
FILES=[
 'apollo-r384/document-gallery.php',
 'apollo-r384/assets/gallery.css',
 'apollo-r389/qa/staging_smoke.py',
 'apollo-r389/qa/browser.py',
 'apollo-r389/qa/contract.php',
 'apollo-r389/QA/browser-results.json',
 'apollo-r389/QA/php-results.json',
 'apollo-r389/QA/320-mobile.png',
 'apollo-r389/QA/1440-desktop.png',
 'apollo-r389/QA/Apollo_R389_Complete_Source_Print.pdf',
 'apollo-r390/README.md',
 'apollo-r390/qa/test_network_boundary.py',
 'apollo-r390/qa/package.py',
 'apollo-r390/QA/network-boundary-results.json',
]
manifest={'release':'R390','status':'BUILT+LOCAL_TESTED_NOT_STAGING','git_head':'SET_FROM_COMMITTED_GITHUB_HEAD_SEPARATELY',
 'original_sources':2,'evidence_questions':6,'files':{}}
contents={}
for name in sorted(FILES):
    source=ROOT/name
    if not source.is_file(): raise SystemExit('Missing tested artifact: '+str(source))
    data=source.read_bytes()
    contents[name]=data
    manifest['files'][name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
contents['apollo-r390/QA/MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode('utf8')
output=ROOT/'apollo-r390/QA/Apollo_R390_Evidence.zip'
output.parent.mkdir(exist_ok=True,parents=True)
with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in sorted(contents.items()):
    info=ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED
    info.external_attr=0o100644<<16
    z.writestr(info,data,compress_type=ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(output),'entries':len(contents),'bytes':output.stat().st_size,
                  'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2))
