#!/usr/bin/env python3
"""Deterministic R277 evidence archive builder; call from QA-inclusive working dir.
Usage: python experience2/apollo-r277/qa/build_archive.py <exact-github-head-sha>
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo
import hashlib
import json
import sys

root=Path(__file__).resolve().parents[3]
sha=sys.argv[1] if len(sys.argv)>1 else ''
if len(sha)!=40 or not all(c in '0123456789abcdef' for c in sha):
    raise SystemExit('Provide exact 40-character HEAD SHA')
files=sorted((p for folder in ('experience2','QA-A','QA-B') for p in (root/folder).rglob('*') if p.is_file()),
    key=lambda p:p.relative_to(root).as_posix())
manifest={
    'package':'Apollo R277 staging WordPress no-approval bridge / HARD HOLD',
    'repo':'finalvestigestudios/final-vestige-site-layer',
    'pull_request':1998,
    'HEAD':sha,
    'parent':'a330aeafc0a1ed1ad670608eb8ef52fdd0ccc62c',
    'source_controlled_files':7,
    'QA':{'wp_api_simulation':'20/20 PASS; NOT installed WordPress',
          'chromium':'14/14 x 2 PASS',
          'missing_source':'PHP + Chromium no-JS PASS',
          'screenshot_pairs':'4/4 identical',
          'stable_receipt_sha256':'85b6e8c9ad13f4246bb84a59c12274ec8778ef7a734e972d1e5f2f7c65197e2d'},
    'not_tested':['genuine axe-core','installed WordPress','actual HTTP/CSP','browser UI zoom','screen readers','field CWV','CI'],
    'release':'HARD HOLD / no live writes',
    'file_sha256':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
}
(root/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
files.append(root/'EVIDENCE-MANIFEST.json')
files.sort(key=lambda p:p.relative_to(root).as_posix())
for suffix in ('A','B'):
    out=root/f'Apollo_R277_WordPress_Review_Custody_Staging_HARD_HOLD_{suffix}.zip'
    with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            zi=ZipInfo(p.relative_to(root).as_posix(),date_time=(1980,1,1,0,0,0))
            zi.compress_type=ZIP_DEFLATED
            zi.external_attr=0o100644<<16
            z.writestr(zi,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    print(out.name,len(files),'files',hashlib.sha256(out.read_bytes()).hexdigest())
