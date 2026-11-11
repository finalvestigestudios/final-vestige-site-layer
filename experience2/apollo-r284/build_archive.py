#!/usr/bin/env python3
"""Build reproducible source + QA custody archive for the R284 Apollo staging sprint.

Run from an extracted R284 work root (with QA-A/QA-B) or a repo checkout.
Zip bytes and included JSON manifest are deterministic: sorted paths, fixed timestamps,
UTF-8 manifest serialization, no runtime timestamps, absolute paths, or PDF metadata.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'Apollo_R284_Source_Roundtrip_HARD_HOLD.zip'
SOURCE=[
 'experience2/apollo-r281/apollo-source-experience.php',
 'experience2/apollo-r281/assets/apollo-source-experience.css',
 'experience2/apollo-r281/qa/committed_gate.py',
 'experience2/apollo-r284/build_archive.py',
]
OPTIONAL=[
 'experience2/apollo-r284/verify_source_roundtrip.py',
 'experience2/apollo-r284/r283-baseline.php',
 'QA-A/receipt.json','QA-B/receipt.json',
 'QA-A/r284-390-nojs-source-focus.png','QA-B/r284-390-nojs-source-focus.png',
 'QA-A/r284-1440-nojs-source-focus.png','QA-B/r284-1440-nojs-source-focus.png',
 'QA-new-gate-final/receipt.json'
]
files=sorted(SOURCE+[path for path in OPTIONAL if (ROOT/path).is_file()])
assert all((ROOT/p).is_file() for p in SOURCE), 'Missing required source; refuse incomplete archive'
sha={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
meta={'release':'HARD_HOLD','stage':'local PHP+Chromium QA only','files_sha256':sha,
      'limits':['No real HTTP browser navigation','No axe-core','No installed WordPress',
                'No field CWV','No approved paid merchant attribution']}
manifest=(json.dumps(meta,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted([(p,(ROOT/p).read_bytes()) for p in files]+[('EVIDENCE-MANIFEST.json',manifest)]):
        info=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o100644<<16)
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('FILE_COUNT',len(files)+1)
print('ARCHIVE_SHA256',hashlib.sha256(OUT.read_bytes()).hexdigest())
