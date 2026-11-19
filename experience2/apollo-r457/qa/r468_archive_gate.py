#!/usr/bin/env python3
"""Build identical R468 offline QA bundles from identical reviewed inputs.
Run after r468_custody_gate.py and r468_browser_gate.py; no network or paid service.
"""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'QA'/'r468'
ARTIFACT=ROOT.parent/'Apollo_R468_Custody_QA.zip'
names=[
 'apollo_rights_gallery.php','evidence_plates.php','assets/gallery.css',
 'assets/gallery.js','qa/r468_custody_gate.py','qa/r468_browser_gate.py',
 'qa/r468_archive_gate.py','qa/r467_contract_gate.py','qa/r466_integrity_gate.py',
 'QA/r468/results.json','QA/r468/390-r468.png','QA/r468/1920-r468.png'
]
records={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in names}
manifest={
 'build':'R468 immutable offline QA, not hosted staging',
 'source_files':records,
 'browser':'Chromium Playwright set_content, 14 viewport/JS cases',
 'axe':'HOLD_NOT_RUN',
 'navigated_LCP_CLS':'HOLD_NOT_RUN',
 'field_CWV':'HOLD_NOT_RUN',
 'merchant_orders':'HOLD_NOT_VERIFIED'
}
payload={'MANIFEST.json':(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()}
payload.update({p:(ROOT/p).read_bytes() for p in names})
with zipfile.ZipFile(ARTIFACT,'w') as z:
 for p,data in sorted(payload.items()):
  info=zipfile.ZipInfo(p,date_time=(2026,11,18,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.create_system=3
  info.external_attr=(0o644<<16)
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(ARTIFACT)
print(hashlib.sha256(ARTIFACT.read_bytes()).hexdigest())
