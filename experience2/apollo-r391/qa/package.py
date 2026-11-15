#!/usr/bin/env python3
"""Deterministic R391 evidence archive. Requires completed local fixture tests."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
R=Path(__file__).resolve().parents[2]
paths=[
'apollo-r384/document-gallery.php', 'apollo-r384/assets/gallery.css',
'apollo-r389/qa/staging_smoke.py', 'apollo-r389/qa/browser.py',
'apollo-r389/qa/contract.php', 'apollo-r389/qa/test_staging_guard.py',
'apollo-r389/QA/browser-results.json', 'apollo-r389/QA/php-results.json',
'apollo-r389/QA/320-mobile.png','apollo-r389/QA/390-mobile.png',
'apollo-r389/QA/768-tablet.png','apollo-r389/QA/1440-desktop.png',
'apollo-r389/QA/1920-wide.png','apollo-r389/QA/320-nojs.png',
'apollo-r389/QA/390-touch.png','apollo-r389/QA/390-reduced.png',
'apollo-r389/QA/320-forced.png','apollo-r389/QA/320-root4x.png',
'apollo-r389/QA/Apollo_R389_Complete_Source_Print.pdf',
'apollo-r390/qa/test_network_boundary.py','apollo-r390/QA/network-boundary-results.json',
'apollo-r391/README.md','apollo-r391/qa/test_readonly_boundary.py',
'apollo-r391/qa/package.py','apollo-r391/QA/network-boundary-results.json',
]
items={}
for p in sorted(paths):
    file=R/p
    if not file.exists():raise SystemExit('MISSING: '+str(file))
    items[p]=file.read_bytes()
manifest={'sprint':'Apollo R391','status':'LOCAL_FIXTURE_TESTED_STAGING_NOT_EXECUTED',
          'source_commit':'RECORD_GITHUB_SHA_FROM_COMMIT_AFTER_PUSH',
          'original_nasa_publications':2,'evidence_questions':6,
          'tests':{'php':59,'chromium_fixture':399,'staging_guard':7,'r390_mock':23,'r391_mock':50},
          'files':{p:{'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)} for p,data in sorted(items.items())}}
items['apollo-r391/QA/MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
zip_path=R/'apollo-r391/QA/Apollo_R391_Evidence.zip';zip_path.parent.mkdir(parents=True,exist_ok=True)
with ZipFile(zip_path,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for p,data in sorted(items.items()):
        inf=ZipInfo(p,date_time=(1980,1,1,0,0,0));inf.compress_type=ZIP_DEFLATED
        inf.external_attr=0o100644 << 16
        z.writestr(inf,data,compress_type=ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(zip_path),'entries':len(items),'bytes':zip_path.stat().st_size,
                  'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()},indent=2))
