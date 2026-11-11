#!/usr/bin/env python3
"""Deterministic Apollo R278 hard-hold evidence archive; run from reviewed QA tree.
Usage: python experience2/apollo-r278/qa/build_archive.py <40-character-exact-head>
"""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib, json, sys

root=Path(__file__).resolve().parents[3]
head=sys.argv[1] if len(sys.argv)>1 else ''
if len(head)!=40 or any(c not in '0123456789abcdef' for c in head):
    raise SystemExit('An exact GitHub 40-character HEAD SHA is required')
files=sorted(
    (p for folder in ('experience2','QA-A','QA-B')
       for p in (root/folder).rglob('*')
       if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'),
    key=lambda p:p.relative_to(root).as_posix())
manifest={
 'program':'Apollo R278 source pin/recursion correction — HARD HOLD',
 'repository':'finalvestigestudios/final-vestige-site-layer',
 'head':head,
 'parent':'77c80117d591aa0482f16062b9d6b375c0d44193',
 'QA':{'wp_api_mock':'26/26 PASS','R278_custom_php':'16/16 PASS',
       'source_missing_changed_authentic':'3/3 PASS',
       'offline_chromium':'14/14 x 2 PASS',
       'local_http_csp_headers':'PASS; browser enforcement BLOCKED'},
 'not_accepted':['installed WordPress','Chromium HTTP/CSP navigation','genuine axe-core',
                 'manual screen-reader','cross-browser','field CWV',
                 'hosted CI','merchant eligibility','founder release'],
 'release':'UNMERGED DRAFT HARD HOLD',
 'file_sha256':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
}
(root/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\\n')
files.append(root/'EVIDENCE-MANIFEST.json')
files.sort(key=lambda p:p.relative_to(root).as_posix())
for label in ('A','B'):
    out=root/f'Apollo_R278_Source_Pin_Reusable_Depth_HARD_HOLD_{label}.zip'
    with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            zi=ZipInfo(p.relative_to(root).as_posix(),date_time=(1980,1,1,0,0,0))
            zi.compress_type=ZIP_DEFLATED
            zi.external_attr=0o100644<<16
            z.writestr(zi,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    print(out.name,len(files),'files',hashlib.sha256(out.read_bytes()).hexdigest())
