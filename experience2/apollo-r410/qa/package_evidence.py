#!/usr/bin/env python3
"""Reproducible local QA receipts, deterministic ZIP. No network, CMS or Git writes."""
import hashlib, json, zipfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ROOT=R.parent
QA=R/'QA';QA.mkdir(exist_ok=True)
FILES=[R/'README.md',R/'qa/semantic_custody.py',R/'qa/test_semantic_custody.py',R/'qa/package_evidence.py']
FILES += sorted(p for p in QA.glob('*.log'))
FILES += sorted((ROOT/'apollo-r408'/'QA').glob('*.png'))
FILES += sorted((ROOT/'apollo-r408'/'QA').glob('*.json'))
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
entries={str(p.relative_to(ROOT)):p.read_bytes() for p in FILES}
entries['apollo-r410/QA/SHA256_MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
output=QA/'Apollo_R410_Local_Evidence.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(entries.items()):
        info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'entries':len(entries)},sort_keys=True))
