#!/usr/bin/env python3
"""Deterministic R394 QA archive; same source/QA bytes yield identical ZIP bytes."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
EXPERIENCE=ROOT.parent
FILES=[
 'apollo-r377/custody.json',
 'apollo-r392/qa/semantic_custody.py',
 'apollo-r393/qa/topology.py',
 'apollo-r393/QA/local-php-fixture.html',
 *('apollo-r394/'+x for x in [
  'README.md', 'assets/root4x-overflow-candidate.css', 'qa/visibility_custody.py',
  'qa/staging_gate.py', 'qa/test_visibility.py', 'qa/package.py',
  'QA/visibility-results.json','QA/320-mobile.png','QA/1440-desktop.png',
  'QA/320-nojs.png','QA/320-root4x-before.png','QA/320-root4x.png'])]
MANIFEST='apollo-r394/QA/MANIFEST.json'
TARGET=ROOT/'QA'/'Apollo_R394_Local_Evidence.zip'
records={p:hashlib.sha256((EXPERIENCE/p).read_bytes()).hexdigest() for p in FILES}
manifest={'scope':'LOCAL_ONLY_NO_STAGING_NO_RELEASE','file_sha256':records,
 'source_commit':'PENDING_GITHUB_COMMIT_VERIFICATION', 'tests':'85/85 Chromium; 12/12 R393 bypasses rejected; 8px->0px candidate CSS'}
files={p:(EXPERIENCE/p).read_bytes() for p in FILES}
files[MANIFEST]=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
def pack(path):
 with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
  for name in sorted(files):
   meta=ZipInfo(name,date_time=(1980,1,1,0,0,0));meta.compress_type=ZIP_DEFLATED;meta.external_attr=0o100644<<16
   z.writestr(meta,files[name],compress_type=ZIP_DEFLATED,compresslevel=9)
pack(TARGET)
first=hashlib.sha256(TARGET.read_bytes()).hexdigest()
pack(TARGET)
assert first==hashlib.sha256(TARGET.read_bytes()).hexdigest()
(ROOT/'QA'/'zip-sha256.txt').write_text(first+'  '+TARGET.name+'\n')
print(json.dumps({'file_count':len(files),'sha256':first,'deterministic_double_build':True,'path':str(TARGET)},indent=2))
