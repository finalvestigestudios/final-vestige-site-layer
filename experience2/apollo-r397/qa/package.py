#!/usr/bin/env python3
"""Build stable R397 local QA archive. Must be identical across runs on same source."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'apollo-r397/QA'; QA.mkdir(exist_ok=True)
files=[
 'apollo-r377/custody.json',
 'apollo-r384/assets/gallery.css',
 'apollo-r393/QA/local-php-fixture.html',
 'apollo-r393/qa/topology.py',
 'apollo-r394/qa/visibility_custody.py',
 'apollo-r395/assets/mobile-fit.css',
 'apollo-r396/staging-custody.php',
 'apollo-r397/staging-delivery-guard.php',
 'apollo-r397/README.md',
 'apollo-r397/qa/enable.php',
 'apollo-r397/qa/contract.php',
 'apollo-r397/qa/reproduce_r396_gap.php',
 'apollo-r397/qa/browser.py',
 'apollo-r397/qa/package.py',
 'apollo-r397/QA/browser-results.json',
 'apollo-r397/QA/320.png',
 'apollo-r397/QA/1440.png',
 'apollo-r397/QA/320-nojs.png',
 'apollo-r397/QA/320-text4x.png',
 'apollo-r397/QA/390-touch.png',
]
manifest={'mode':'LOCAL_FIXTURE_ONLY','release':'HARD_HOLD','files':{}}
for filename in files:
 p=ROOT/filename
 manifest['files'][filename]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
raw=json.dumps(manifest,sort_keys=True,indent=2)+'\n';(QA/'MANIFEST.json').write_text(raw)
files.append('apollo-r397/QA/MANIFEST.json')
out=QA/'Apollo_R397_Local_Evidence.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for filename in sorted(files):
  info=zipfile.ZipInfo(filename,(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o100644<<16
  z.writestr(info,(ROOT/filename).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(f'R397 archive {len(files)} files, {out.stat().st_size} bytes, sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}')
