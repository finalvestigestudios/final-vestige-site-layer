#!/usr/bin/env python3
"""Deterministic R395 local evidence pack (excludes its own ZIP/hash)."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'apollo-r395'
QA=HERE/'QA'
files=[
 'apollo-r377/custody.json',
 'apollo-r384/assets/gallery.css',
 'apollo-r392/qa/semantic_custody.py',
 'apollo-r393/qa/topology.py',
 'apollo-r393/QA/local-php-fixture.html',
 'apollo-r394/qa/visibility_custody.py',
 'apollo-r395/staging-prepaint.php',
 'apollo-r395/assets/mobile-fit.css',
 'apollo-r395/qa/enable.php',
 'apollo-r395/qa/php_contract.php',
 'apollo-r395/qa/browser.py',
 'apollo-r395/qa/package.py',
 'apollo-r395/README.md',
 'apollo-r395/QA/prepaint-results.json',
 'apollo-r395/QA/320-mobile.png',
 'apollo-r395/QA/1440-desktop.png',
 'apollo-r395/QA/320-nojs.png',
 'apollo-r395/QA/320-root4x-prepaint.png',
]
for f in files:
 if not (ROOT/f).is_file(): raise SystemExit('Missing required evidence '+f)
items={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
manifest={'scope':'LOCAL_ONLY_NOT_STAGING_NOT_PRODUCTION','sources':items,
 'browser':'Chromium via Playwright page.set_content; 11 contexts, 136 assertions',
 'php':'Default opt-out 4; simulated opt-in 16',
 'release_allowed':False}
mp=QA/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
files.append('apollo-r395/QA/MANIFEST.json')
archive=QA/'Apollo_R395_Local_Evidence.zip'
def build():
 with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
  for f in sorted(files):
   b=(ROOT/f).read_bytes()
   info=zipfile.ZipInfo(f,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED; info.external_attr=0o100644<<16
   z.writestr(info,b)
build();sha=hashlib.sha256(archive.read_bytes()).hexdigest();build()
if hashlib.sha256(archive.read_bytes()).hexdigest()!=sha:raise SystemExit('Archive not deterministic')
(QA/'zip-sha256.txt').write_text(sha+'  Apollo_R395_Local_Evidence.zip\n')
print(json.dumps({'status':'DOUBLE_BUILD_IDENTICAL','sha256':sha,'entries':len(files)}))
