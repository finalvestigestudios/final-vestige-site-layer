#!/usr/bin/env python3
"""Deterministic R303 code+QA source bundle, no network or site modifications."""
from pathlib import Path
import hashlib
import json
import zipfile

script=Path(__file__).resolve();site=script.parents[1];root=script.parents[2]
qa=root/'QA';out=root/'Apollo_R303_Evidence.zip'
sources=[site/x for x in (
    'apollo-r281/apollo-source-experience.php',
    'apollo-r281/assets/apollo-source-experience.css',
    'apollo-r301/qa/local_http_fixture.php',
    'apollo-r301/qa/source_controlled_browser_gate.py',
    'apollo-r302/qa/source_controlled_browser_gate.py',
    'apollo-r302/qa/verify_source_egress.py',
    'apollo-r303/qa/test_integrity_recovery.py',
    'apollo-r303/build_archive.py',
    'apollo-r303/README.md',
)]
outputs=[qa/f'r302-{w}-nojs.png' for w in (320,390,768,1440,1920)]
outputs += [qa/'r302-390-print.pdf',qa/'r302-browser-receipt.json']
outputs += [site/'apollo-r303/QA'/f'r303-{w}-recovery-nojs.png' for w in (390,1440)]
outputs += [site/'apollo-r303/QA/r303-test-receipt.json']
files=sorted(sources+outputs,key=lambda p:str(p.relative_to(root)))
assert all(p.is_file() for p in files), 'missing source or QA; run listed suites before archiving'
manifest={'sprint':'R303','status':'DRAFT, HARD HOLD, NOT LIVE',
 'limitations': ['offline Chromium not installed WordPress','genuine axe not run','field CWV not measured','no verified commercial orders'],
 'sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
entries={str(p.relative_to(root)):p.read_bytes() for p in files}
entries['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name in sorted(entries):
        item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
        item.create_system=3;item.external_attr=0o644 << 16
        z.writestr(item,entries[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(f'R303 archive {hashlib.sha256(out.read_bytes()).hexdigest()} payloads {len(files)}')
