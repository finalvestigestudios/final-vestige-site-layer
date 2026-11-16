#!/usr/bin/env python3
"""Build a deterministic, fixture-labelled R401 review bundle (no live data)."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'QA'/'Apollo_R401_Local_Evidence.zip'
SOURCES=[ROOT/'README.md',ROOT/'qa'/'custody_overlay.py',ROOT/'qa'/'test_custody_overlay.py',ROOT/'qa'/'pack_evidence.py']
PROOFS=[ROOT/'QA'/'report.json']+sorted((ROOT/'QA').glob('*.png'))
for p in SOURCES+PROOFS:
    if not p.is_file():raise SystemExit('HOLD missing evidence: '+str(p))
report=json.loads((ROOT/'QA'/'report.json').read_text())
if report.get('status')!='PASS_LOCAL_FIXTURE_SHADOW_DEPENDENCY_ONLY' or report.get('exact_remote_upstream'):
    raise SystemExit('HOLD: unexpected verification scope')
entries={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES+PROOFS}
manifest={'scope':'LOCAL_CHROMIUM_FIXTURE_NOT_INSTALLED_STAGING', 'release_allowed':False,
          'screenshots':len(list((ROOT/'QA').glob('*.png'))),
          'qa_status':report['status'],'exact_remote_upstream':False,
          'provenance':'R401 local R392/R400 archived equivalents, GitHub remote mismatch recorded',
          'entries_sha256':entries}
manifest_bytes=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
(ROOT/'QA'/'MANIFEST.json').write_bytes(manifest_bytes)
def build():
    with zipfile.ZipFile(TARGET,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,content in sorted([(k,(ROOT/k).read_bytes()) for k in entries]+[('QA/MANIFEST.json',manifest_bytes)]):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16; z.writestr(info,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(TARGET.read_bytes()).hexdigest()
a=build();b=build()
if a!=b:raise SystemExit('HOLD non-deterministic bundle')
print(json.dumps({'archive':str(TARGET),'sha256':a,'files':len(entries)+1,'byte_identical_rebuild':True}))
