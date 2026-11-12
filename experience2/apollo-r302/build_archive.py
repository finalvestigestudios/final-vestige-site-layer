#!/usr/bin/env python3
"""Repeatable R302 evidence bundle: source + checks + local Chromium artifacts."""
import hashlib
import json
import zipfile
from pathlib import Path

script = Path(__file__).resolve()
site = script.parents[1]
root = script.parents[2]
qa = root / 'QA'
out = root / 'Apollo_R302_Evidence.zip'
sources = [
  site/'apollo-r281/apollo-source-experience.php',
  site/'apollo-r281/assets/apollo-source-experience.css',
  site/'apollo-r301/qa/local_http_fixture.php',
  site/'apollo-r301/qa/source_controlled_browser_gate.py',
  site/'apollo-r302/qa/source_controlled_browser_gate.py',
  site/'apollo-r302/qa/verify_source_egress.py',
  site/'apollo-r302/build_archive.py',
  site/'apollo-r302/README.md',
]
outputs = [qa/f'r302-{w}-nojs.png' for w in (320,390,768,1440,1920)]
outputs += [qa/'r302-390-print.pdf', qa/'r302-browser-receipt.json']
files = sorted(sources + outputs, key=lambda f: str(f.relative_to(root)))
assert all(f.is_file() for f in files), 'Required source, QA or artifact missing'
manifest = {
 'sprint':'R302', 'status':'SOURCE-CONTROLLED DRAFT STAGING / HARD HOLD / NOT LIVE',
 'reproduce':'python experience2/apollo-r302/qa/source_controlled_browser_gate.py && python experience2/apollo-r302/qa/verify_source_egress.py',
 'test_limit':'actual PHP offline Chromium; NOT installed WordPress, HTTP browser/CSP or axe-core',
 'payloads': {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
}
entries={str(f.relative_to(root)):f.read_bytes() for f in files}
entries['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in sorted(entries):
  zi=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
  zi.compress_type=zipfile.ZIP_DEFLATED
  zi.create_system=3
  zi.external_attr=0o644 << 16
  z.writestr(zi,entries[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('R302 archive',hashlib.sha256(out.read_bytes()).hexdigest(),'payloads',len(files))
